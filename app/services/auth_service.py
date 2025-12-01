from app.database import db_client
from app.models import UserRegister
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.config import get_settings
from typing import Optional
from datetime import timedelta
from uuid import UUID

settings = get_settings()


class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.client = db_client
        self.table = "users"
    
    def register_user(self, user_data: UserRegister) -> Optional[dict]:
        """
        New user register karta hai
        Password hash karke store karta hai
        """
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Prepare data
        data = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hashed_password,
            "role": user_data.role.value if hasattr(user_data.role, 'value') else user_data.role
        }
        
        # Insert into database
        response = self.client.from_(self.table).insert(data).execute()
        
        if response.data:
            user = response.data[0]
            # Remove password_hash from response
            user.pop('password_hash', None)
            return user
        
        return None
    
    def login_user(self, email: str, password: str) -> Optional[dict]:
        """
        User login karta hai
        Returns token and user data if successful
        """
        # Get user by email
        response = self.client.from_(self.table)\
            .select("*")\
            .eq("email", email)\
            .execute()
        
        if not response.data:
            return None
        
        user = response.data[0]
        
        # Verify password
        if not verify_password(password, user.get("password_hash", "")):
            return None
        
        # Check if user is active
        if not user.get("is_active", True):
            return None
        
        # Update last login
        self.update_last_login(user["id"])
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user["id"]), "role": user["role"]},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        # Remove password_hash from user data
        user.pop('password_hash', None)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,  # in seconds
            "user": user
        }
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Email se user dhundta hai"""
        response = self.client.from_(self.table)\
            .select("*")\
            .eq("email", email)\
            .execute()
        
        if response.data:
            user = response.data[0]
            user.pop('password_hash', None)
            return user
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """ID se user dhundta hai"""
        response = self.client.from_(self.table)\
            .select("*")\
            .eq("id", user_id)\
            .execute()
        
        if response.data:
            user = response.data[0]
            user.pop('password_hash', None)
            return user
        
        return None
    
    def update_last_login(self, user_id: str) -> None:
        """Last login time update karta hai"""
        from datetime import datetime
        
        self.client.from_(self.table)\
            .update({"last_login": datetime.utcnow().isoformat()})\
            .eq("id", user_id)\
            .execute()
    
    def email_exists(self, email: str) -> bool:
        """Check karta hai email already registered hai ya nahi"""
        response = self.client.from_(self.table)\
            .select("id")\
            .eq("email", email)\
            .execute()
        
        return len(response.data) > 0
    
    def change_password(self, user_id: str, new_password: str) -> bool:
        """Password change karta hai"""
        hashed_password = hash_password(new_password)
        
        response = self.client.from_(self.table)\
            .update({"password_hash": hashed_password})\
            .eq("id", user_id)\
            .execute()
        
        return len(response.data) > 0
    
    def deactivate_user(self, user_id: str) -> bool:
        """User account deactivate karta hai"""
        response = self.client.from_(self.table)\
            .update({"is_active": False})\
            .eq("id", user_id)\
            .execute()
        
        return len(response.data) > 0
    
    def get_all_users(self, page: int = 1, limit: int = 10, role: Optional[str] = None) -> tuple[list, int]:
        """All users fetch karta hai"""
        offset = (page - 1) * limit
        
        query = self.client.from_(self.table)\
            .select("id, name, email, role, is_active, is_verified, created_at, last_login", count="exact")
        
        if role:
            query = query.eq("role", role)
        
        response = query\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        total = response.count if response.count else len(response.data)
        return response.data, total


# Singleton instance
auth_service = AuthService()