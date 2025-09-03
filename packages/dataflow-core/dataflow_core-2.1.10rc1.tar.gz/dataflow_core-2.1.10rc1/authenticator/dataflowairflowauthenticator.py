from flask import redirect, request
from flask_appbuilder.security.views import AuthDBView
from flask_appbuilder.security.views import expose
from flask_login import login_user
from airflow.www.security import FabAirflowSecurityManagerOverride
from dataflow.dataflow import Dataflow
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

dataflow = Dataflow()

class DataflowAuthDBView(AuthDBView):    
    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        """
        Override the default login method to handle custom authentication
        """
        try:
            session_id = request.cookies.get('dataflow_session')
            if not session_id:
                logger.info("No session cookie found, falling back to standard login.")
                return super().login()
            
            user_details = dataflow.auth(session_id)
            logger.info(f"User details retrieved for: {user_details['user_name']}")
            user = self.appbuilder.sm.find_user(username=user_details['user_name'])
            if user:
                logger.info(f"User found: {user}")
                login_user(user, remember=False)
            else:
                user = self.appbuilder.sm.add_user(
                    username=user_details['user_name'], 
                    first_name=user_details.get("first_name", ""),
                    last_name=user_details.get("last_name", ""), 
                    email=user_details.get("email", ""), 
                    role=self.appbuilder.sm.find_role(user_details.get("base_role", "user").title())
                )
                logger.info(f"New user created: {user}")
                if user:
                    login_user(user, remember=False)
            
            return redirect(self.appbuilder.get_url_for_index)

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return super().login()

class DataflowAirflowAuthenticator(FabAirflowSecurityManagerOverride):
    authdbview = DataflowAuthDBView
    
    def __init__(self, appbuilder):
        super().__init__(appbuilder)
