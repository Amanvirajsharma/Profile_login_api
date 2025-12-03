from fastapi import APIRouter, HTTPException, Depends, status
from app.models import (
    UserRegister,
    UserLogin,
    AuthResponse,
    TokenResponse,
    UserResponse,
    RoleEnum,
    GenderEnum,
    CityEnum
)
from app.services.auth_service import auth_service
from app.auth.dependencies import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============ REGISTER ============
@router.post("/register", response_model=AuthResponse, status_code=201)
def register(user_data: UserRegister):
    """
    📝 New User Registration
    
    **Required Fields:**
    - **name**: Full name
    - **email**: Valid email (unique)
    - **password**: Minimum 6 characters
    
    **Dropdown Fields:**
    - **role**: user, institution (default: user)
    - **gender**: Male, Female
    - **city**: Bhopal, Indore
    - **state**: Madhya Pradesh (default)
    - **country**: India (default)
    """
    # Check if email already exists
    if auth_service.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered!"
        )
    
    # Register user
    new_user = auth_service.register_user(user_data)
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )
    
    return AuthResponse(
        success=True,
        message=f"Registration successful! Welcome {new_user['name']}",
        data=new_user
    )


# ============ LOGIN ============
@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin):
    """
    🔑 User Login
    
    - **email**: Registered email
    - **password**: Account password
    
    Returns JWT token on success
    """
    result = auth_service.login_user(credentials.email, credentials.password)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return AuthResponse(
        success=True,
        message="Login successful!",
        data=result
    )


# ============ GET CURRENT USER (ME) ============
@router.get("/me", response_model=AuthResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """
    👤 Get Current User Profile
    
    Requires: Bearer Token in Authorization header
    """
    return AuthResponse(
        success=True,
        message="User profile fetched!",
        data=current_user
    )


# ============ CHANGE PASSWORD ============
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


@router.post("/change-password", response_model=AuthResponse)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    🔒 Change Password
    
    Requires: Bearer Token
    """
    from app.auth.password import verify_password
    
    # Get user with password hash
    user = auth_service.client.from_("users")\
        .select("password_hash")\
        .eq("id", current_user["id"])\
        .execute()
    
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(password_data.current_password, user.data[0]["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Change password
    success = auth_service.change_password(current_user["id"], password_data.new_password)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to change password")
    
    return AuthResponse(
        success=True,
        message="Password changed successfully!"
    )


# ============ LOGOUT ============
@router.post("/logout", response_model=AuthResponse)
def logout(current_user: dict = Depends(get_current_user)):
    """
    🚪 Logout
    
    Note: JWT is stateless, client should delete the token.
    """
    return AuthResponse(
        success=True,
        message="Logged out successfully! Please delete your token.",
        data={"user_id": current_user["id"]}
    )


# ============ GET ALL USERS (Admin) ============
@router.get("/users", response_model=AuthResponse)
def get_all_users(
    page: int = 1,
    limit: int = 10,
    role: RoleEnum = None,
    city: CityEnum = None,
    gender: GenderEnum = None
):
    """
    👥 Get All Users (with filters)
    
    Filter by:
    - **role**: user, institution
    - **city**: Bhopal, Indore
    - **gender**: Male, Female
    """
    role_value = role.value if role else None
    city_value = city.value if city else None
    gender_value = gender.value if gender else None
    
    users, total = auth_service.get_all_users(
        page, limit, role_value, city_value, gender_value
    )
    
    return AuthResponse(
        success=True,
        message=f"Found {total} users",
        data={
            "users": users,
            "total": total,
            "page": page,
            "limit": limit
        }
    )