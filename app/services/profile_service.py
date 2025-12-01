from app.database import db_client
from app.models import ProfileCreate, ProfileUpdate, RoleEnum
from typing import Optional
from uuid import UUID


class ProfileService:
    """Profile CRUD operations"""
    
    def __init__(self):
        self.client = db_client
        self.table = "profiles"
    
    def create_profile(self, profile_data: ProfileCreate) -> Optional[dict]:
        """Create new profile"""
        data = profile_data.model_dump(exclude_none=True)
        
        # Convert date to string
        if 'date_of_birth' in data and data['date_of_birth']:
            data['date_of_birth'] = str(data['date_of_birth'])
        
        # Convert enum to string
        if 'role' in data:
            data['role'] = data['role'].value if hasattr(data['role'], 'value') else data['role']
        
        response = self.client.from_(self.table).insert(data).execute()
        return response.data[0] if response.data else None
    
    def get_profile_by_id(self, profile_id: UUID) -> Optional[dict]:
        """Get profile by ID"""
        response = self.client.from_(self.table)\
            .select("*")\
            .eq("id", str(profile_id))\
            .execute()
        
        return response.data[0] if response.data else None
    
    def get_profile_by_email(self, email: str) -> Optional[dict]:
        """Get profile by email"""
        response = self.client.from_(self.table)\
            .select("*")\
            .eq("email", email)\
            .execute()
        
        return response.data[0] if response.data else None
    
    def get_all_profiles(
        self, 
        page: int = 1, 
        limit: int = 10,
        is_active: Optional[bool] = None,
        role: Optional[str] = None  # NEW PARAMETER
    ) -> tuple[list, int]:
        """Get all profiles with pagination and filters"""
        offset = (page - 1) * limit
        
        query = self.client.from_(self.table).select("*", count="exact")
        
        # Filter by active status
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        # Filter by role - NEW
        if role is not None:
            query = query.eq("role", role)
        
        response = query\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        total = response.count if response.count else len(response.data)
        return response.data, total
    
    def update_profile(self, profile_id: UUID, update_data: ProfileUpdate) -> Optional[dict]:
        """Update profile"""
        data = update_data.model_dump(exclude_none=True)
        
        if not data:
            return self.get_profile_by_id(profile_id)
        
        # Convert date
        if 'date_of_birth' in data and data['date_of_birth']:
            data['date_of_birth'] = str(data['date_of_birth'])
        
        # Convert enum to string - NEW
        if 'role' in data:
            data['role'] = data['role'].value if hasattr(data['role'], 'value') else data['role']
        
        response = self.client.from_(self.table)\
            .update(data)\
            .eq("id", str(profile_id))\
            .execute()
        
        return response.data[0] if response.data else None
    
    def delete_profile(self, profile_id: UUID) -> bool:
        """Delete profile"""
        response = self.client.from_(self.table)\
            .delete()\
            .eq("id", str(profile_id))\
            .execute()
        
        return len(response.data) > 0
    
    def search_profiles(
        self, 
        search_term: str, 
        limit: int = 10,
        role: Optional[str] = None  # NEW PARAMETER
    ) -> list:
        """Search profiles by name or email"""
        query = self.client.from_(self.table)\
            .select("*")\
            .or_(f"full_name.ilike.%{search_term}%,email.ilike.%{search_term}%")
        
        # Filter by role - NEW
        if role is not None:
            query = query.eq("role", role)
        
        response = query.limit(limit).execute()
        return response.data
    
    # ============ NEW METHODS ============
    
    def get_users(self, page: int = 1, limit: int = 10) -> tuple[list, int]:
        """Get only users (role = 'user')"""
        return self.get_all_profiles(page, limit, role="user")
    
    def get_institutions(self, page: int = 1, limit: int = 10) -> tuple[list, int]:
        """Get only institutions (role = 'institution')"""
        return self.get_all_profiles(page, limit, role="institution")
    
    def get_role_stats(self) -> dict:
        """Get count of users and institutions"""
        # Get users count
        users_response = self.client.from_(self.table)\
            .select("id", count="exact")\
            .eq("role", "user")\
            .execute()
        
        # Get institutions count
        institutions_response = self.client.from_(self.table)\
            .select("id", count="exact")\
            .eq("role", "institution")\
            .execute()
        
        users_count = users_response.count if users_response.count else 0
        institutions_count = institutions_response.count if institutions_response.count else 0
        
        return {
            "total_users": users_count,
            "total_institutions": institutions_count,
            "total_profiles": users_count + institutions_count
        }


# Singleton instance
profile_service = ProfileService()