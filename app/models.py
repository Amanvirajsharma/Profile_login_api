from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID
from enum import Enum
import re


# ============ ENUMS (Dropdowns) ============

class RoleEnum(str, Enum):
    """User roles"""
    USER = "user"
    INSTITUTION = "institution"


class CountryEnum(str, Enum):
    """Available countries"""
    INDIA = "India"


class StateEnum(str, Enum):
    """Available states"""
    MADHYA_PRADESH = "Madhya Pradesh"


class CityEnum(str, Enum):
    """Available cities"""
    BHOPAL = "Bhopal"
    INDORE = "Indore"


class GenderEnum(str, Enum):
    """Gender options"""
    MALE = "Male"
    FEMALE = "Female"


# ============ AUTH MODELS ============

class UserRegister(BaseModel):
    """Registration ke liye"""
    name: str = Field(..., min_length=2, max_length=100, examples=["Rahul Sharma"])
    email: str = Field(..., examples=["rahul@example.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["secret123"])
    role: RoleEnum = Field(default=RoleEnum.USER, examples=["user", "institution"])
    gender: Optional[GenderEnum] = Field(None, examples=["Male", "Female"])
    city: Optional[CityEnum] = Field(None, examples=["Bhopal", "Indore"])
    state: StateEnum = Field(default=StateEnum.MADHYA_PRADESH, examples=["Madhya Pradesh"])
    country: CountryEnum = Field(default=CountryEnum.INDIA, examples=["India"])
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserLogin(BaseModel):
    """Login ke liye"""
    email: str = Field(..., examples=["rahul@example.com"])
    password: str = Field(..., examples=["secret123"])
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.lower()


class UserResponse(BaseModel):
    """User response (password ke bina)"""
    id: UUID
    name: str
    email: str
    role: str
    gender: Optional[str] = None
    city: Optional[str] = None
    state: str
    country: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Login success response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class AuthResponse(BaseModel):
    """Standard auth response"""
    success: bool
    message: str
    data: Optional[dict] = None


# ============ PROFILE MODELS ============

class ProfileCreate(BaseModel):
    """Naya profile banane ke liye"""
    full_name: str = Field(..., min_length=2, max_length=100, examples=["Rahul Sharma"])
    email: str = Field(..., examples=["rahul@example.com"])
    phone: Optional[str] = Field(None, max_length=15, examples=["9876543210"])
    bio: Optional[str] = Field(None, examples=["Software Developer"])
    avatar_url: Optional[str] = Field(None, examples=["https://example.com/avatar.jpg"])
    date_of_birth: Optional[date] = Field(None, examples=["1995-05-15"])
    gender: Optional[GenderEnum] = Field(None, examples=["Male", "Female"])  # Dropdown
    address: Optional[str] = Field(None, examples=["123, MG Road"])
    city: Optional[CityEnum] = Field(None, examples=["Bhopal", "Indore"])  # Dropdown
    state: StateEnum = Field(default=StateEnum.MADHYA_PRADESH, examples=["Madhya Pradesh"])  # Dropdown with default
    country: CountryEnum = Field(default=CountryEnum.INDIA, examples=["India"])  # Dropdown with default
    role: RoleEnum = Field(default=RoleEnum.USER, examples=["user", "institution"])  # Dropdown
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v.lower()


class ProfileUpdate(BaseModel):
    """Profile update karne ke liye"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None  # Dropdown
    address: Optional[str] = None
    city: Optional[CityEnum] = None  # Dropdown
    state: Optional[StateEnum] = None  # Dropdown
    country: Optional[CountryEnum] = None  # Dropdown
    is_active: Optional[bool] = None
    role: Optional[RoleEnum] = None  # Dropdown


class ProfileResponse(BaseModel):
    """Profile response"""
    id: UUID
    full_name: str
    email: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[dict | list] = None


class PaginatedResponse(BaseModel):
    """Paginated response"""
    success: bool
    message: str
    data: list
    total: int
    page: int
    limit: int


class RoleStats(BaseModel):
    """Role wise count"""
    total_users: int
    total_institutions: int
    total_profiles: int