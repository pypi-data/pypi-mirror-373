import os, shutil, subprocess, datetime, yaml, re
from .models.environment import JobLogs, Environment
import json, asyncio, pkg_resources
from sqlalchemy.orm import Session
from .configuration import ConfigurationManager
from .utils.logger import CustomLogger

class EnvironmentManager:
    def __init__(self):
        """Initialize the EnvironmentManager"""
        self.config = ConfigurationManager('/dataflow/app/config/dataflow.cfg')
        self.env_base_path = self.config.get_config_value('paths', 'env_path')
        self.env_logs_path = self.config.get_config_value('paths', 'env_logs_path')
        self.env_version_path = self.config.get_config_value('paths', 'env_versions_path')
        os.makedirs(self.env_version_path, exist_ok=True)
        self.logger = CustomLogger().get_logger(__name__)
    
    async def create_env(self, env_name, py_version, pip_libraries, conda_libraries, status, env_version='1', user_name=None, db:Session=None):
        """
        Creates a conda environment with specified Python version and packages.
        
        Args:
            env_name (str): Name of the environment
            py_version (str): Python version to use
            py_requirements (list): List of packages to install
            status (str): Environment status ('draft' or 'published')
            env_version (str): Version of the environment (for draft environments)
            user_name (str): Username who initiated the creation
            db (Session): Database session (optional, will create if None)
            
        Returns:
            str: Build status ('success' or 'failed')
        """
        # Set up logging
        log_file_location = None
        if db:
            log_file_location = self._setup_logging(env_name, env_version, user_name, db)

        # Create the conda environment YAML file
        yaml_path = os.path.join(self.env_version_path, f"{env_name}_v{env_version}.yaml")
        self.create_conda_yaml(
            yaml_path=yaml_path,
            env_name=env_name,
            python_version=py_version,
            conda_packages=conda_libraries,
            pip_packages=pip_libraries
        )

        if status == "published":
            return await self._execute_env_operation(
                env_name=env_name,
                status="published",
                mode="create",
                yaml_file_path=yaml_path,
                version=int(env_version)
            )
        elif status == "draft":
            mode = "create" if env_version == '1' else "update"
            build_status = await self._execute_env_operation(
                env_name=env_name,
                status=status,
                mode=mode,
                yaml_file_path=yaml_path,
                log_file_location=log_file_location,
                version=int(env_version)
            )
            
            # Update job log status if db was provided
            if db and log_file_location:
                log_file_name = os.path.basename(log_file_location)
                await self._update_job_status(log_file_name, build_status, log_file_location, db)
                pip_libraries, conda_libraries = self.update_library_versions(yaml_path)
                self.update_environment_db(env_name, env_version, pip_libraries, conda_libraries, build_status, db)

            return build_status
        
        else:
            self.logger.error(f"Invalid status '{status}' provided for environment creation.")
            raise ValueError("Invalid status. Use 'draft' or 'published'.")
    
    async def clone_env(self, source_path, env_name, pip_libraries, conda_libraries, user_name, db=None):
        """
        Clones an existing conda environment.
        
        Args:
            source_path (str): Path to source environment
            target_name (str): Name for the target environment
            status (str): Environment status ('draft' or 'published')
            env_version (str): Version of the environment (for draft environments)
            user_name (str): Username who initiated the clone
            db (Session): Database session (optional, will create if None)
            
        Returns:
            str: Build status ('success' or 'failed')
        """
        # Set up logging
        log_file_location = None
        if db:
            log_file_location = self._setup_logging(env_name, "1", user_name, db)

        yaml_path = f"{self.env_version_path}/{env_name}_v1.yaml"
        
        # Perform the clone operation
        clone_status = await self._execute_env_operation(
            env_name=env_name,
            status="draft",
            mode="clone",
            yaml_file_path=yaml_path,
            source_path=source_path,
            log_file_location=log_file_location,
            version="1"          
        )
        
        # Update job log status if db was provided
        if db and log_file_location:
            log_file_name = os.path.basename(log_file_location)
            await self._update_job_status(log_file_name, clone_status, log_file_location, db)
            self.update_environment_db(
                env_short_name=env_name, 
                version="1", 
                pip_libraries=pip_libraries, 
                conda_libraries=conda_libraries,
                status=clone_status, 
                db=db
            )
            
        return clone_status
    
    async def revert_env(self, env_name, curr_version, revert_version, new_version, user_name, db: Session):
        """
        Reverts an environment to a previous version.
        
        Args:
            env_name (str): Name of the environment
            version (str): Version to revert to
            db (Session): Database session
            
        Returns:
            str: Build status ('success' or 'failed')
        """
        try:            
            # Get the YAML file for the specified version
            old_yaml_path = f"{self.env_version_path}/{env_name}_v{revert_version}.yaml"
            new_yaml_path = f"{self.env_version_path}/{env_name}_v{new_version}.yaml"
            if not os.path.exists(old_yaml_path):
                raise FileNotFoundError(f"YAML file for version {revert_version} does not exist.")
            
            os.symlink(old_yaml_path, new_yaml_path)

            log_file_location = None
            if db:
                log_file_location = self._setup_logging(env_name, new_version, user_name, db)
            
            # Execute the revert operation
            revert_status = await self._execute_env_operation(
                env_name=env_name,
                status="draft",
                mode="update",
                yaml_file_path=new_yaml_path,
                log_file_location=log_file_location,
                version=int(new_version)
            )
            
            log_file_name = os.path.basename(log_file_location)
            await self._update_job_status(log_file_name, revert_status, log_file_location, db)
            pip_libraries, conda_libraries = self.update_library_versions(new_yaml_path)
            self.update_environment_db(env_name, new_version, pip_libraries, conda_libraries, revert_status, db)
        
        except Exception as e:
            self.logger.error(f"Failed to revert environment {env_name}: {e}")
            return "failed"
        
    async def _execute_env_operation(
        self, 
        env_name: str, 
        status: str, 
        mode: str, 
        yaml_file_path: str, 
        version: int,
        source_path=None, 
        log_file_location=None,
    ):
        """
        Executes environment operations (create or clone).
        
        Args:
            env_name (str): Name of the environment
            status (str): Environment status ('draft' or 'published')
            mode (str): Operation mode ('create' or 'clone')
            env_version (str): Version of the environment (for draft environments)
            py_version (str): Python version to use (for create mode)
            py_requirements (list): List of packages to install (for create mode)
            source_path (str): Path to source environment (for clone mode)
            log_file_location (str): Path to log file
            
        Returns:
            str: Build status ('success' or 'failed')
        """
        self.logger.info(f"Executing environment operation: {env_name}, Status: {status}, Mode: {mode}")
        status = status.lower()
        conda_env_path = os.path.join(self.env_base_path, env_name)

        try:
            if os.path.exists(conda_env_path) and mode == "create":
                raise FileExistsError(f"Environment '{env_name}' already exists at {conda_env_path}.")
            
            os.makedirs(conda_env_path, exist_ok=True)

            if mode == "create":                
                create_env_script_path = pkg_resources.resource_filename('dataflow', 'scripts/create_environment.sh')
                command = ["bash", create_env_script_path, yaml_file_path, conda_env_path]

            elif mode == "update":
                update_env_script_path = pkg_resources.resource_filename('dataflow', 'scripts/update_environment.sh')
                command = ["bash", update_env_script_path, yaml_file_path, conda_env_path]
            
            elif mode == "clone":
                clone_env_script_path = pkg_resources.resource_filename('dataflow', 'scripts/clone_environment.sh')
                command = ["bash", clone_env_script_path, source_path, conda_env_path]
                
            else:
                raise ValueError("Invalid mode. Use 'create', 'update', or 'clone'.")

            process = await asyncio.create_subprocess_exec(
                *command, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )

            if not log_file_location:
                return process

            with open(log_file_location, "a") as log_file:
                success_detected = False
                try:
                    # Write an initial log entry to indicate the operation has started
                    start_message = {
                        "timestamp": self.format_timestamp(),
                        "type": "log",
                        "content": f"Starting environment {mode} operation for {env_name}"
                    }
                    log_file.write(json.dumps(start_message) + "\n")
                    log_file.flush()
                    
                    # Process stdout line by line
                    while True:
                        line = await process.stdout.readline()
                        if not line:
                            break
                            
                        line = line.decode()
                        message = {
                            "timestamp": self.format_timestamp(),
                            "type": "log",  
                            "content": line.strip()
                        }
                        log_file.write(json.dumps(message) + "\n")
                        log_file.flush()

                        if "environment creation successful" in line.lower():
                            success_detected = True
                            
                    await process.wait()  # Ensure process is complete
                    
                    if process.returncode != 0:
                        error_message = await process.stderr.read()
                        error_message = error_message.decode().strip()
                        error_message_dict = {
                            "timestamp": self.format_timestamp(),
                            "type": "error",
                            "content": error_message
                        }
                        log_file.write(json.dumps(error_message_dict) + "\n")

                    final_build_status = "failed" if process.returncode != 0 else "success"

                except asyncio.CancelledError:
                    process.kill()
                    msg_content = "Environment operation cancelled due to request cancellation."
                    cancellation_message = {
                        "timestamp": self.format_timestamp(),
                        "type": "error",
                        "content": msg_content
                    }
                    log_file.write(json.dumps(cancellation_message) + "\n")
                    final_build_status = "failed"
                
                finally:
                    if final_build_status != "success" and version == 1:
                        if os.path.exists(conda_env_path):
                            shutil.rmtree(conda_env_path)
                
            return final_build_status
        
        except OSError as e:
            self.logger.error(f"OS error while operating on {conda_env_path}: {e}")
            return "failed"
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Subprocess error during environment operation: {e}")
            return "failed"
        except Exception as e:
            self.logger.error(f"Unexpected error during environment operation for {env_name}: {e}")
            return "failed"
    
    def _setup_logging(self, env_name: str, env_version: str, user_name: str, db: Session):
        """
        Sets up logging for environment operations.
        
        Args:
            env_name (str): Name of the environment
            env_version (str): Version of the environment
            user_name (str): Username who initiated the operation
            db (Session): Database session
            
        Returns:
            str: Path to the log file
        """
        versioned_name = f"{env_name}_v{env_version}"
        log_file_name = f"envlog_{versioned_name}.log"
        log_file_dir = self.config.get_config_value('paths', 'env_logs_path')
        os.makedirs(log_file_dir, exist_ok=True)
        log_file_location = os.path.join(log_file_dir, log_file_name)
        
        # Clear log file if it exists
        if os.path.exists(log_file_location):
            open(log_file_location, "w").close()
        
        # Create job entry
        self.create_job_entry(user_name, db, log_file_name, log_file_location)
        
        return log_file_location
    
    async def _update_job_status(self, log_file_name: str, build_status: str, log_file_location: str, db: Session):
        """
        Updates job status with retry logic.
        
        Args:
            db (Session): Database session
            log_file_name (str): Name of the log file
            build_status (str): Build status ('success' or 'failed') 
            log_file_location (str): Path to the log file
        """
        attempts = 3
        retry_delay = 3
        
        while attempts > 0:
            try:
                self.update_job_log(db, log_file_name, build_status)
                break
            except Exception as e:
                attempts -= 1
                
                with open(log_file_location, "a") as log_file:
                    msg_content = "Failed to commit job completion time to database."
                    error_message = {
                        "timestamp": self.format_timestamp(),
                        "type": "error",
                        "content": msg_content
                    }
                    log_file.write(json.dumps(error_message) + "\n")
                
                if attempts > 0:
                    await asyncio.sleep(retry_delay)
                else:
                    self.logger.error(f"Failed to update job log after multiple attempts: {e}")
    
    def create_job_entry(self, user_name: str, db: Session, log_file_name: str, log_file_location: str):
        """
        Creates or updates a job entry for environment tracking.
        
        Args:
            user_name (str): The user who initiated the job
            db (Session): Database session
            log_file_name (str): Log file name
            log_file_location (str): Log file path
            
        Returns:
            JobLogs: The created or updated job entry
        """
        job = db.query(JobLogs).filter(JobLogs.log_file_name == log_file_name).first()

        if job:
            if job.status == "success":
                self.logger.error(f"Job with log_file_name '{log_file_name}' already completed successfully.")
                raise ValueError(f"Job with log_file_name '{log_file_name}' already completed successfully.")
            if job.status == "failed":
                job.created_at = datetime.datetime.now() 
                job.status = "in_progress"
        else:
            job = JobLogs(
                created_at=datetime.datetime.now(),
                log_file_name=log_file_name,
                log_file_location=log_file_location,
                created_by=user_name,
                status="in_progress"
            )
            db.add(job)

        db.commit()
        return job
    
    def update_job_log(self, db, log_file_name, final_build_status):
        """
        Updates the JobLogs table with completion time and status.
        
        Args:
            db (Session): Database session
            log_file_name (str): Name of the log file
            final_build_status (str): Final status of the build ('success' or 'failed')
        """
        try:
            job_record = db.query(JobLogs).filter(JobLogs.log_file_name == log_file_name).first()
            if job_record:
                job_record.completed_at = datetime.datetime.now()
                job_record.status = final_build_status
                db.commit()
            else:
                self.logger.error(f"No job log found for file: {log_file_name}")
                raise ValueError(f"No job log found for file: {log_file_name}")
        except Exception as e:
            self.logger.error(f"Failed to update job log for {log_file_name}: {e}")
            db.rollback()
            raise

    def format_timestamp(self):
        """
        Generates a formatted timestamp string representing the current date and time.

        Returns:
            str: A string representing the current date and time in the specified format.
        """
        return datetime.datetime.now().strftime("%b %d  %I:%M:%S %p")
    
    def update_environment_db(self, env_short_name, version, pip_libraries, conda_libraries, status, db: Session):
        """
        Updates the environment table with the new version and libraries.
        """
        try:
            if isinstance(pip_libraries, list):
                pip_libraries = ", ".join(pip_libraries)
            if isinstance(conda_libraries, list):
                conda_libraries = ", ".join(conda_libraries)
            current_env = db.query(Environment).filter(Environment.short_name == env_short_name).first()
            if not current_env:
                raise ValueError(f"Environment with short name '{env_short_name}' does not exist.")
            
            env_status = "Draft" if status == "success" else "Failed"

            db.query(Environment).filter(
                Environment.short_name == env_short_name
            ).update({"version": version, "pip_libraries": pip_libraries, "conda_libraries": conda_libraries, "status": env_status})
            db.commit()

        except Exception as e:
            self.logger.error(f"Failed to update environment {env_short_name} in database: {e}")
            db.rollback()
            raise

    def update_library_versions(self, yaml_path: str):
        """
        Updates libraries without version specifications by getting their actual installed versions from a conda YAML file.
        
        Args:
            yaml_path (str): Path to the conda environment YAML file.
            
        Returns:
            tuple: Updated lists of (pip_libraries, conda_libraries) with version specifications.
        """
        try:
            # Define default conda packages to ignore
            default_conda_packages = {
                "_libgcc_mutex", "_openmp_mutex", "bzip2", "ca-certificates", 
                "ld_impl_linux-64", "libexpat", "libffi", "libgcc", "libgcc-ng", 
                "libgomp", "liblzma", "libnsl", "libsqlite", "libuuid", "libxcrypt", 
                "libzlib", "ncurses", "openssl", "readline", "setuptools", "tk", 
                "tzdata", "wheel", "libstdcxx-ng", "python"
            }
            
            # Read the YAML file
            with open(yaml_path, 'r') as f:
                yaml_content = yaml.safe_load(f)
            
            # Extract conda and pip dependencies
            dependencies = yaml_content.get('dependencies', [])
            
            # Process conda libraries
            conda_libraries = []
            pip_libraries = []
            
            for dep in dependencies:
                if isinstance(dep, str):
                    if dep.startswith("python="):
                        continue
                    
                    parts = dep.split('=')
                    package_name = parts[0].strip()
                    
                    if package_name.lower() not in default_conda_packages:
                        if len(parts) >= 2:
                            package_with_version = f"{package_name}={parts[1]}"
                            conda_libraries.append(package_with_version)
                        else:
                            # No version specified, keep as is
                            conda_libraries.append(dep)
                
                elif isinstance(dep, dict) and 'pip' in dep:
                    # This is the pip section
                    for pip_pkg in dep['pip']:
                        pip_libraries.append(pip_pkg)
            
            return pip_libraries, conda_libraries
            
        except Exception as e:
            self.logger.error(f"Error reading YAML file and extracting libraries: {str(e)}")
            return [], []
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running pip freeze: {e.stderr}")
            return pip_libraries
        except Exception as e:
            self.logger.error(f"Error updating library versions: {str(e)}")
            return pip_libraries

    def create_conda_yaml(self, yaml_path, env_name, python_version, conda_packages, pip_packages):
        """
        Creates a conda environment YAML file with specified packages and channels.
        
        Args:
            yaml_path (str): Path where to save the YAML file
            env_name (str): Name of the conda environment
            python_version (str): Python version to use
            conda_channels (list): List of conda channels
            conda_packages (list): List of conda packages to install
            pip_packages (list): List of pip packages to install
        """
        try:
            # Create the environment specification
            env_spec = {
                "name": env_name,
                "channels": ["conda-forge", "defaults"],
                "dependencies": [
                    f"python={python_version}"
                ]
            }
            
            # Add conda packages
            if conda_packages and len(conda_packages) > 0:
                env_spec["dependencies"].extend(conda_packages)

            pip_pattern = re.compile(r"^pip([=]{1,2}.*)?$")  # matches pip, pip=..., pip==...
            pip_found = any(pip_pattern.match(pkg.strip()) for pkg in conda_packages)
            
            # if pip is not already included in conda packages, add it
            if not pip_found:
                env_spec["dependencies"].append("pip")
        
            # Add pip packages if any
            if pip_packages and len(pip_packages) > 0:
                pip_section = {
                    "pip": pip_packages
                }
                env_spec["dependencies"].append(pip_section)
                
            with open(yaml_path, 'w') as yaml_file:
                yaml.dump(env_spec, yaml_file, default_flow_style=False)
                
            return yaml_path
            
        except Exception as e:
            self.logger.error(f"Failed to create conda environment YAML file: {str(e)}")
            raise Exception(f"Failed to create conda environment YAML file: {str(e)}")
       
    def format_py_requirements(self, env):
        """
        Format pip and conda libraries into a standardized list of dictionaries
        sorted alphabetically by library name.
        
        Args:
            env: Environment object containing pip_libraries and conda_libraries strings
            
        Returns:
            list: List of dictionaries with format [{"name":"lib_name", "version":"version", "manager":"pip|conda"}, ...]
        """
        py_requirements = []
        
        # process libraries, handle both '==' and '=' version specifications
        if env.pip_libraries:
            for lib in env.pip_libraries.split(','):
                lib = lib.strip()
                if not lib:
                    continue
                    
                if '==' in lib:
                    name, version = lib.split('==', 1)
                    py_requirements.append({
                        "name": name.strip(),
                        "version": version.strip(),
                        "manager": "pip"
                    })
                elif '=' in lib:
                    name, version = lib.split('=', 1)
                    py_requirements.append({
                        "name": name.strip(),
                        "version": version.strip(),
                        "manager": "pip"
                    })
                else:
                    py_requirements.append({
                        "name": lib,
                        "version": "",
                        "manager": "pip"
                    })
        
        if env.conda_libraries:
            for lib in env.conda_libraries.split(','):
                lib = lib.strip()
                if not lib:
                    continue
                    
                if '==' in lib:
                    name, version = lib.split('==', 1)
                    py_requirements.append({
                        "name": name.strip(),
                        "version": version.strip(),
                        "manager": "conda"
                    })
                elif '=' in lib:
                    name, version = lib.split('=', 1)
                    py_requirements.append({
                        "name": name.strip(),
                        "version": version.strip(),
                        "manager": "conda"
                    })
                else:
                    py_requirements.append({
                        "name": lib,
                        "version": "",
                        "manager": "conda"
                    })

        # sort the requirements list alphabetically by name
        py_requirements.sort(key=lambda x: x["name"].lower())
        
        return py_requirements
