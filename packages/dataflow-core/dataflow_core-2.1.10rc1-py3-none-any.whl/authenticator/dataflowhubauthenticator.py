import os
import uuid
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from traitlets import Bool, Unicode
from jupyterhub.auth import Authenticator
from oauthenticator.google import GoogleOAuthenticator
from oauthenticator.azuread import AzureAdOAuthenticator
from dataflow.db import get_db
from dataflow.models import user as m_user, session as m_session, role as m_role

class DataflowBaseAuthenticator(Authenticator):
    enable_dataflow_auth = Bool(True, config=True, help="Enable username/password authentication")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.db = next(get_db())
            m_user.Base.metadata.create_all(bind=self.db.get_bind(), checkfirst=True)
            m_session.Base.metadata.create_all(bind=self.db.get_bind(), checkfirst=True)
            self.log.info("Dataflow database initialized successfully")
        except Exception as e:
            self.log.error(f"Failed to initialize Dataflow database: {str(e)}")
            raise

    def generate_session_id(self):
        return str(uuid.uuid4())

    def set_session_cookie(self, handler, session_id):
        expires = datetime.now(ZoneInfo("UTC")) + timedelta(days=365)
        host = handler.request.host
        domain = '.'.join(host.split('.')[-2:]) if len(host.split('.')) >= 2 else host
        handler.set_cookie(
            "dataflow_session",
            session_id,
            domain=f".{domain}",
            path="/",
            expires=expires,
            secure=True,
            httponly=True,
            samesite="None"
        )
        self.log.info(f"Set session cookie: dataflow_session={session_id} for host={host}")

    def get_or_create_session(self, user_id):
        existing_session = (
            self.db.query(m_session.Session)
            .filter(m_session.Session.user_id == str(user_id))
            .first()
        )
        if existing_session:
            self.log.info(f"Reusing existing session: {existing_session.session_id}")
            return existing_session.session_id
        session_id = self.generate_session_id()
        while self.db.query(m_session.Session).filter(
            m_session.Session.session_id == session_id
        ).first():
            session_id = self.generate_session_id()
        db_item = m_session.Session(user_id=user_id, session_id=session_id)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        self.log.info(f"Created new session: {session_id}")
        return session_id
    
    def check_blocked_users(self, username, authenticated):
        self.log.info(f"Checking blocked users for {username}: authenticated={authenticated}, allowed_users={self.allowed_users}")

        if not authenticated:
            self.log.warning(f"No authenticated data for user: {username}")
            return None

        if isinstance(authenticated, dict) and "session_id" in authenticated:
            self.log.info(f"Allowing Dataflow authentication for user: {username}")
            return username

        return super().check_blocked_users(username, authenticated)

    def get_applicant_role_id(self):
        """Get the role ID for 'Applicant' role"""
        try:
            applicant_role = (
                self.db.query(m_role.Role)
                .filter(m_role.Role.name == "Applicant")
                .first()
            )
            if applicant_role:
                return applicant_role.id
            else:
                self.log.warning("Applicant role not found in database")
                return None
        except Exception as e:
            self.log.error(f"Error getting Applicant role: {str(e)}")
            return None

    def extract_username_from_email(self, email):
        """Extract username from email by removing domain"""
        if '@' in email:
            return email.split('@')[0]
        return email

    def create_new_user(self, email, first_name=None, last_name=None):
        """Create a new user with Applicant role"""
        try:
            role_id = self.get_applicant_role_id()
            if not role_id:
                self.log.error("Cannot create user: Applicant role not found")
                return None

            username = self.extract_username_from_email(email)
            username = re.sub(r'[^a-z0-9]', '', username.lower())
            if not username:
                self.log.error("Cannot create user: Username is empty")
                return None
            existing_user = (
                self.db.query(m_user.User)
                .filter(m_user.User.user_name == username)
                .first()
            )
            if existing_user:
                counter = 1
                original_username = username
                while existing_user:
                    username = f"{original_username}_{counter}"
                    existing_user = (
                        self.db.query(m_user.User)
                        .filter(m_user.User.user_name == username)
                        .first()
                    )
                    counter += 1

            new_user = m_user.User(
                user_name=username,
                first_name=first_name or username,
                last_name=last_name or "",
                email=email,
                role_id=role_id,
                password='user@123',
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            self.log.info(f"Created new user: {username} with email: {email}")
            return new_user
            
        except Exception as e:
            self.log.error(f"Error creating new user: {str(e)}")
            self.db.rollback()
            return None

    async def authenticate_dataflow(self, handler, data):
        if not (self.enable_dataflow_auth and isinstance(data, dict) and data.get("username") and data.get("password")):
            return None
        username = data["username"]
        password = data["password"]
        self.log.info(f"Attempting Dataflow authentication for user: {username}")
        try:
            user = (
                self.db.query(m_user.User)
                .filter(m_user.User.user_name == username)
                .first()
            )
            if not user or user.password != password:
                self.log.warning(f"Dataflow authentication failed for user: {username}")
                return None
            session_id = self.get_or_create_session(user.user_id)
            self.set_session_cookie(handler, session_id)
            self.log.info(f"Dataflow authentication successful for user: {username}")
            return {"name": username, "session_id": session_id, "auth_state": {}}
        except Exception as e:
            self.log.error(f"Dataflow authentication error: {str(e)}")
            return None
        finally:
            self.db.close()

class DataflowGoogleAuthenticator(DataflowBaseAuthenticator, GoogleOAuthenticator):
    dataflow_oauth_type = Unicode(
        default_value="google",
        config=True,
        help="The OAuth provider type for DataflowHub (e.g., github, google)"
    )
    google_client_id = Unicode(config=True, help="Google OAuth client ID")
    google_client_secret = Unicode(config=True, help="Google OAuth client secret")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_id = self.google_client_id
        self.client_secret = self.google_client_secret
        self.dataflow_oauth_type = self.dataflow_oauth_type
        self.log.info(f"DataflowGoogleAuthenticator initialized with google_client_id={self.google_client_id}, "
                      f"oauth_callback_url={self.oauth_callback_url}, "
                      f"enable_dataflow_auth={self.enable_dataflow_auth}")

    async def authenticate(self, handler, data):
        self.log.info(f"Authenticate called with data: {data}, request_uri: {handler.request.uri}")
        result = await self.authenticate_dataflow(handler, data)
        if result:
            return result
        try:
            user = await super().authenticate(handler, data)
            self.log.info(f"Google OAuth authentication returned: {user}")
            if not user:
                self.log.warning("Google OAuth authentication failed: No user data returned")
                return None
            
            email = user["name"]
            db_user = (
                self.db.query(m_user.User)
                .filter(m_user.User.email == email)
                .first()
            )
            
            if not db_user:
                self.log.info(f"User with email {email} not found in Dataflow database, creating new user")
                # Extract additional info from user data if available
                auth_state = user.get("auth_state", {})
                user_info = auth_state.get("user", {}) if auth_state else {}
                
                first_name =  user_info.get("name")
                last_name =  user_info.get("last_name")
                
                db_user = self.create_new_user(email, first_name, last_name)
                if not db_user:
                    self.log.error(f"Failed to create new user for email: {email}")
                    return None
            
            username = db_user.user_name
            session_id = self.get_or_create_session(db_user.user_id)
            self.set_session_cookie(handler, session_id)
            self.log.info(f"Google OAuth completed for user: {username}, session_id={session_id}")
            return {
                "name": username,
                "session_id": session_id,
                "auth_state": user.get("auth_state", {})
            }
        except Exception as e:
            self.log.error(f"Google OAuth authentication error: {str(e)}", exc_info=True)
            return None
        finally:
            self.db.close()

class DataflowAzureAuthenticator(DataflowBaseAuthenticator, AzureAdOAuthenticator):
    azure_client_id = Unicode(config=True, help="Azure AD OAuth client ID")
    azure_client_secret = Unicode(config=True, help="Azure AD OAuth client secret")
    azure_tenant_id = Unicode(config=True, help="Azure AD tenant ID")
    azure_scope = Unicode("openid profile email", config=True, help="Azure AD OAuth scopes")
    dataflow_oauth_type = Unicode(
        default_value="google",
        config=True,
        help="The OAuth provider type for DataflowHub (e.g., github, google)"
    )
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_id = self.azure_client_id
        self.client_secret = self.azure_client_secret
        self.tenant_id = self.azure_tenant_id
        self.scope = self.azure_scope.split()
        self.dataflow_oauth_type = self.dataflow_oauth_type
        self.log.info(f"DataflowAzureAuthenticator initialized with azure_client_id={self.azure_client_id}, "
                      f"oauth_callback_url={self.oauth_callback_url}, "
                      f"enable_dataflow_auth={self.enable_dataflow_auth}")

    async def authenticate(self, handler, data):
        result = await self.authenticate_dataflow(handler, data)
        if result:
            return result
        try:
            user = await super().authenticate(handler, data)
            self.log.info(f"Azure AD OAuth authentication returned: {user}")
            if not user:
                self.log.warning("Azure AD OAuth authentication failed: No user data returned")
                return None

            auth_state = user.get("auth_state", {})
            user_info = auth_state.get("user", {}) if auth_state else {}
            email = user_info.get("upn")
            if not email:
                self.log.warning("Azure AD OAuth authentication failed: No upn in user data")
                return None

            db_user = (
                self.db.query(m_user.User)
                .filter(m_user.User.email == email)
                .first()
            )

            if not db_user:
                self.log.info(f"User with email {email} not found in Dataflow database, creating new user")
                
                first_name = user_info.get("name") or user.get("name")
                
                db_user = self.create_new_user(email, first_name, last_name=None)
                if not db_user:
                    self.log.error(f"Failed to create new user for email: {email}")
                    return None

            username = db_user.user_name
            session_id = self.get_or_create_session(db_user.user_id)
            self.set_session_cookie(handler, session_id)
            self.log.info(f"Azure AD OAuth completed for user: {username}, session_id={session_id}")
            return {
                "name": username,
                "session_id": session_id,
                "auth_state": user.get("auth_state", {})
            }

        except Exception as e:
            self.log.error(f"Azure AD OAuth authentication error: {str(e)}", exc_info=True)
            return None
        finally:
            self.db.close()

auth_type = os.environ.get("DATAFLOW_OAUTH_TYPE", "google")

if auth_type == "google":
    BaseAuthenticator = DataflowGoogleAuthenticator
else:
    BaseAuthenticator = DataflowAzureAuthenticator

class DataflowHubAuthenticator(BaseAuthenticator):
    pass