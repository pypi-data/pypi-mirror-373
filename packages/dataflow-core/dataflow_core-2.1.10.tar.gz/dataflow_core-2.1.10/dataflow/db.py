import dataflow
from .database_manager import DatabaseManager
from .configuration import ConfigurationManager
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from .utils.logger import CustomLogger
import os
import pwd
import grp
from urllib.parse import urlparse

logger = CustomLogger().get_logger(__name__)

dataflow_config = ConfigurationManager('/dataflow/app/config/dataflow.cfg')
dataflow_local_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
db_url = dataflow_config.get_config_value('database', 'database_url')
local_db_url = dataflow_local_config.get_config_value('database', 'single_user_db_url')

db_manager = DatabaseManager(db_url)
local_db_manager = None

Base = declarative_base()
Local_Base = declarative_base()

def create_tables(local_db=False):
    """
    Create all tables in the database.
    This is called at the start of the application.
    """
    try:
        if local_db:
            if local_db_url and local_db_url.startswith('sqlite:///'):
                parsed_url = urlparse(local_db_url)
                db_file_path = parsed_url.path
                db_dir = os.path.dirname(db_file_path)
                logger.info(f"Creating local database at: {db_file_path}")
                
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                    logger.info(f"Created directory for local database: {db_dir}")
                
                # Set ownership for database directory and file
                nb_user = os.environ.get("NB_USER")
                if nb_user:
                    try:
                        uid = pwd.getpwnam(nb_user).pw_uid
                        gid = grp.getgrnam(nb_user).gr_gid
                        
                        # Set ownership for database directory
                        if os.path.exists(db_dir):
                            os.chown(db_dir, uid, gid)
                        
                        global local_db_manager
                        if local_db_manager is None:
                            local_db_manager = DatabaseManager(local_db_url) 
                        Local_Base.metadata.create_all(bind=local_db_manager.get_engine())
                        
                        if os.path.exists(db_file_path):
                            os.chown(db_file_path, uid, gid)
                        logger.info(f"Ownership set for local database files")
                    except (KeyError, OSError) as e:
                        logger.warning(f"Could not set ownership for database files: {e}")
                else:
                    logger.error("NB_USER environment variable is not set. Cannot set ownership for local database files.")
                    raise ValueError("Can only use local database with a valid NB_USER environment variable")
            else:
                logger.error("Local database URL must be a valid SQLite URL starting with 'sqlite:///'")
                raise ValueError("Local database URL must be a valid SQLite URL starting with 'sqlite:///'")
            
        else:
            Base.metadata.create_all(bind=db_manager.get_engine())
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        error_message = f"Failed to create tables: {str(e)}"
        logger.error(error_message)
        raise e
    
def get_local_db():
    """
    Get a local database session.
    
    Yields:
        Session: Local database session
    """
    global local_db_manager
    if local_db_manager is None:
        local_db_manager = DatabaseManager(local_db_url)
    yield from local_db_manager.get_session()

def get_db():
    yield from db_manager.get_session()
