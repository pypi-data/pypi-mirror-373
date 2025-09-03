from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from dataflow.models import user as m_user  
from dataflow.models import session as m_session

def get_user_from_session(session_id: str, db: Session):
    """
    Retrieve a user based on session ID.
    
    Args:
        session_id (str): The unique session identifier
        db (Session): Database session
        
    Returns:
        User: User object if found
        
    Raises:
        HTTPException: If session is invalid or user not found
    """
    session_record = db.query(m_session.Session).filter(m_session.Session.session_id == session_id).first()
    if not session_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    user = db.query(m_user.User).filter(m_user.User.user_id == session_record.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    base_role = user.role_details.base_role
    role_id = user.role_details.id
    role_name = user.role_details.name
    user.base_role = base_role
    user.role = role_name
    user.role_id = role_id
    
    return user


