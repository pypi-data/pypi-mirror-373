import os, requests
from .database_manager import DatabaseManager
import json
from .configuration import ConfigurationManager


class Dataflow:
    """
    Dataflow class to interact with Dataflow services.
    """
    def auth(self, session_id: str):
        """
        Retrieve and return user information using their session ID.
        
        Args:
            session_id (str): User's session ID from cookies
            
        Returns:
            dict: User information including username, name, email, and role
        """
        try:
            dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
            auth_api = dataflow_config.get_config_value('auth', 'ui_auth_api')
            response = requests.get(
                auth_api,
                cookies={"dataflow_session": session_id, "jupyterhub-hub-login": ""}
            )
            
            if response.status_code != 200:
                return response.json()
            
            user_data = response.json()
            user_dict = {
                "user_name": user_data["user_name"], 
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"] if user_data.get("last_name") else "",
                "email": user_data["email"],
                "role": user_data["base_role"]
            }
            return user_dict
                  
        except Exception as e:
            return e
    
    def variable(self, variable_name: str):
        """
        Retrieve a Dataflow variable.
        
        Args:
            variable_name (str): Name of the variable to retrieve
            
        Returns:
            str or None: Variable value if found, None otherwise
        """
        try:
            host_name = os.environ.get("HOSTNAME", "")
            runtime = os.environ.get("RUNTIME")
            slug = os.environ.get("SLUG")

            dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')

            variable_api = None
            if runtime and slug:
                variable_api = dataflow_config.get_config_value("auth", "variable_ui_api")
            elif host_name:
                variable_api = dataflow_config.get_config_value("auth", "variable_manager_api")
            else:
                raise Exception("Cannot run dataflow methods here!") 
            
            if not variable_api:
                print("[Dataflow.variable] Variable Unreachable")
                return None

            if runtime:
                query_params = {
                    "key": variable_name,
                    "runtime": runtime,
                    "slug": slug
                }
                response = requests.get(variable_api, params=query_params)
                if response.status_code == 200:
                    response_text = response.text.strip().strip('"')
                    return response_text
                
                query_params["slug"] = "global"
                response = requests.get(variable_api, params=query_params)
                if response.status_code == 200:
                    response_text = response.text.strip().strip('"')
                    return response_text
                else: 
                    return None

            query_params = {
                "key": variable_name,
            }
            response = requests.get(variable_api, params=query_params)
            
            # Handle different HTTP status codes gracefully
            if response.status_code == 404:
                return None  # Variable not found
            elif response.status_code >= 500:
                response.raise_for_status()  # Let server errors propagate
            elif response.status_code >= 400:
                print(f"[Dataflow.variable] Client error {response.status_code} for variable '{variable_name}'")
                return None
            elif response.status_code != 200:
                print(f"[Dataflow.variable] Unexpected status {response.status_code} for variable '{variable_name}'")
                return None

            return response.text.strip().strip('"')
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"[Dataflow.variable] Failed to fetch variable '{variable_name}'") from e
        
        except Exception as e:
            print(f"[Dataflow.variable] Exception occurred: {e}")
            return None
        
    def secret(self, secret_name: str):
        """
        Retrieve a Dataflow secret value.
        
        Args:
            secret_name (str): Name of the secret to retrieve
            
        Returns:
            str or None: Secret value if found, None otherwise
        """
        try:
            host_name = os.environ.get("HOSTNAME", "")
            runtime = os.environ.get("RUNTIME")
            slug = os.environ.get("SLUG")

            dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
            if runtime:
                secret_api = dataflow_config.get_config_value("auth", "secret_ui_api")
            else:
                secret_api = dataflow_config.get_config_value("auth", "secret_manager_api")
            if not secret_api:
                print("[Dataflow.secret] Secret API Unreachable")
                return None

            query_params = {
                "key": secret_name
            }

            if runtime:
                query_params["runtime"] = runtime
            if slug:
                query_params["slug"] = slug

            response = requests.get(secret_api, params=query_params)
            
            # Handle different HTTP status codes gracefully
            if response.status_code == 404:
                return None  # Secret not found
            elif response.status_code >= 500:
                response.raise_for_status()  # Let server errors propagate
            elif response.status_code >= 400:
                print(f"[Dataflow.secret] Client error {response.status_code} for secret '{secret_name}'")
                return None
            elif response.status_code != 200:
                print(f"[Dataflow.secret] Unexpected status {response.status_code} for secret '{secret_name}'")
                return None

            return response.text.strip().strip('"')
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"[Dataflow.secret] Failed to fetch secret '{secret_name}'") from e
        except Exception as e:
            print(f"[Dataflow.secret] Exception occurred: {e}")
            return None

    def connection(self, conn_id: str, mode="session"):
        """
        Connects with a Dataflow connection.
        
        Args:
            conn_id (str): Connection identifier
            mode (str): Return type - "session" (default) or "engine" or "url"
            
        Returns:
            Session or Engine: SQLAlchemy session or engine based on mode
        """
        try:
            host_name = os.environ["HOSTNAME"]
            runtime = os.environ.get("RUNTIME")
            slug = os.environ.get("SLUG")
            
            dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
            if runtime:
                connection_api = dataflow_config.get_config_value("auth", "connection_ui_api")
            elif host_name:
                connection_api = dataflow_config.get_config_value("auth", "connection_manager_api")
            else:
                raise Exception("Cannot run dataflow methods here! HOSTNAME or RUNTIME env variable not set.")
            
            query_params = {
                "conn_id": conn_id
            }

            if runtime:
                query_params["runtime"] = runtime
            if slug:
                query_params["slug"] = slug

            response = requests.get(connection_api, params=query_params)
            
            # Handle different HTTP status codes gracefully
            if response.status_code == 404:
                raise RuntimeError(f"[Dataflow.connection] Connection '{conn_id}' not found!")
            elif response.status_code >= 500:
                response.raise_for_status()  # Let server errors propagate
            elif response.status_code >= 400:
                raise RuntimeError(f"[Dataflow.connection] Client error {response.status_code} for connection '{conn_id}'")
            elif response.status_code != 200:
                raise RuntimeError(f"[Dataflow.connection] Unexpected status {response.status_code} for connection '{conn_id}'")
                
            connection_details = response.json()

            if not connection_details:
                raise RuntimeError(f"[Dataflow.connection] Connection '{conn_id}' not found!")
            
            if mode == "dict":
                return dict(connection_details)

            conn_type = connection_details['conn_type'].lower()
            username = connection_details['login']
            password = connection_details.get('password', '')
            host = connection_details['host']
            port = connection_details['port']
            database = connection_details.get('schemas', '')

            user_info = f"{username}:{password}@" if password else f"{username}@"
            db_info = f"/{database}" if database else ""

            connection_string = f"{conn_type}://{user_info}{host}:{port}{db_info}"

            extra = connection_details.get('extra', '')            
            if extra:
                try:
                    extra_params = json.loads(extra)
                    if extra_params:
                        extra_query = "&".join(f"{key}={value}" for key, value in extra_params.items())
                        connection_string += f"?{extra_query}"
                except json.JSONDecodeError:
                    # If 'extra' is not valid JSON, skip adding extra parameters
                    pass

            if mode == "url":
                return connection_string
    
            connection_instance = DatabaseManager(connection_string)
            if mode == "engine":
                return connection_instance.get_engine()
            elif mode == "session":
                return next(connection_instance.get_session())
            else:
                raise ValueError(f"Unsupported mode: {mode}. Use 'session', 'engine', 'url'.")
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"[Dataflow.connection] Failed to fetch connection '{conn_id}'") from e

        except Exception as e:
            raise RuntimeError(f"[Dataflow.connection] Error connecting to '{conn_id}': {str(e)}") from e
        
    def variable_or_secret(self, key: str):
        """
        Retrieve a variable or secret by key.
        
        Args:
            key (str): Key of the variable or secret
            
        Returns:
            str or None: Value if found, None otherwise
        """
        try:
            host_name = os.environ.get("HOSTNAME", "")
            runtime = os.environ.get("RUNTIME")
            slug = os.environ.get("SLUG")

            dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
            if runtime and slug:
                variableorsecret_api = dataflow_config.get_config_value("auth", "variableorsecret_ui_api")
                query_params = {
                    "key": key,
                    "runtime": runtime,
                    "slug": slug
                }
            elif host_name:
                variableorsecret_api = dataflow_config.get_config_value("auth", "variableorsecret_manager_api")
                query_params = {
                    "key": key
                }
            else:
                raise Exception("Cannot run dataflow methods here!") 

            if not variableorsecret_api:
                print("[Dataflow.variable_or_secret] Variable/Secret Unreachable")
                return None
            
            response = requests.get(variableorsecret_api, params=query_params)
            
            # Handle different HTTP status codes gracefully
            if response.status_code == 404:
                return None  # Variable/secret not found
            elif response.status_code >= 500:
                response.raise_for_status()  # Let server errors propagate
            elif response.status_code >= 400:
                print(f"[Dataflow.variable_or_secret] Client error {response.status_code} for key '{key}'")
                return None
            elif response.status_code != 200:
                print(f"[Dataflow.variable_or_secret] Unexpected status {response.status_code} for key '{key}'")
                return None

            response_text = response.text.strip().strip('"')
            return response_text
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"[Dataflow.variable_or_secret] Failed to fetch '{key}'") from e