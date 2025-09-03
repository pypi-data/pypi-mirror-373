from flask import redirect, request, jsonify
from flask_appbuilder.security.views import AuthDBView
from flask_appbuilder.security.views import expose
from flask_login import login_user
from flask_jwt_extended import (
    create_access_token
)
from flask_appbuilder.const import (
    API_SECURITY_ACCESS_TOKEN_KEY
)
from superset.security import SupersetSecurityManager
from dataflow.dataflow import Dataflow

class DataflowAuthDBView(AuthDBView):
    def __init__(self):
        self.dataflow = Dataflow()

    def create_user(self, user_details):
        """
        Create a new user in Superset with the given details.

        Returns:
            User object: The newly created user instance
        """
        return self.appbuilder.sm.add_user(
            username=user_details['user_name'], 
            first_name=user_details.get("first_name", ""),
            last_name=user_details.get("last_name", ""), 
            email=user_details.get("email", ""), 
            role=self.appbuilder.sm.find_role('Admin')
        )

    @expose('/login/', methods=['GET', "POST"])
    def login(self):
        """
        Handles both GET and POST login requests.

        - GET: Used for browser-based login. Authenticates using session cookie and redirects to home.
        - POST: Used for API-based login. Returns JWT access token for programmatic access.

        Returns:
            - Redirect to home page (GET)
            - JSON response with access token (POST)
        """
        if request.method == "GET":
            session_id = request.cookies.get('dataflow_session')
            user_details = self.dataflow.auth(session_id)
            user = self.appbuilder.sm.find_user(username=user_details['user_name'])
            try:
                if user:
                    login_user(user, remember=False)
                else:
                    user = self.create_user(user_details)
                login_user(user, remember=False)
                return redirect(self.appbuilder.get_url_for_index)
            except Exception as e:
                return super().login()
        else:
            user_details = request.get_json()
            user = self.appbuilder.sm.find_user(username=user_details["user_name"])
            if user:
                login_user(user, remember=False)
            else:
                user = self.create_user(user_details)
                login_user(user, remember=False)
            resp = {
                API_SECURITY_ACCESS_TOKEN_KEY: create_access_token(
                    identity=str(user.id), fresh=True
                )
            }
            return jsonify(resp)
    
class DataflowSecurityManager(SupersetSecurityManager):
    authdbview = DataflowAuthDBView
    def __init__(self, appbuilder):
        super(DataflowSecurityManager, self).__init__(appbuilder)