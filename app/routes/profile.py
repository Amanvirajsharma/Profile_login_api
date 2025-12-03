from fastapi import APIRouter, HTTPException, Query
from app.models import (
    ProfileCreate, 
    ProfileUpdate, 
    APIResponse, 
    PaginatedResponse,
    RoleEnum,
    CityEnum,
    GenderEnum,
    RoleStats
)
from app.services.profile_service import profile_service
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("/", response_model=APIResponse, status_code=201)
def create_profile(profile: ProfileCreate):
    """
    ✨ Naya profile banao
    
    Dropdowns:
    - **role**: user, institution (default: user)
    - **gender**: Male, Female
    - **city**: Bhopal, Indore
    - **state**: Madhya Pradesh (default)
    - **country**: India (default)
    """
    existing = profile_service.get_profile_by_email(profile.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists!")
    
    new_profile = profile_service.create_profile(profile)
    
    if not new_profile:
        raise HTTPException(status_code=500, detail="Failed to create profile")
    
    return APIResponse(
        success=True,
        message=f"Profile created!",
        data=new_profile
    )


@router.get("/", response_model=PaginatedResponse)
def get_all_profiles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    role: Optional[RoleEnum] = Query(None, description="Filter: user or institution"),
    city: Optional[CityEnum] = Query(None, description="Filter: Bhopal or Indore"),
    gender: Optional[GenderEnum] = Query(None, description="Filter: Male or Female")
):
    """
    📋 Saare profiles dekho with filters
    """
    role_value = role.value if role else None
    city_value = city.value if city else None
    gender_value = gender.value if gender else None
    
    profiles, total = profile_service.get_all_profiles(
        page, limit, is_active, role_value, city_value, gender_value
    )
    
    return PaginatedResponse(
        success=True,
        message=f"Found {len(profiles)} profiles",
        data=profiles,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/users", response_model=PaginatedResponse)
def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """👤 Sirf Users dekho"""
    profiles, total = profile_service.get_users(page, limit)
    
    return PaginatedResponse(
        success=True,
        message=f"Found {len(profiles)} users",
        data=profiles,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/institutions", response_model=PaginatedResponse)
def get_all_institutions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """🏛️ Sirf Institutions dekho"""
    profiles, total = profile_service.get_institutions(page, limit)
    
    return PaginatedResponse(
        success=True,
        message=f"Found {len(profiles)} institutions",
        data=profiles,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/stats/roles", response_model=APIResponse)
def get_role_statistics():
    """📊 Role wise statistics"""
    stats = profile_service.get_role_stats()
    
    return APIResponse(
        success=True,
        message="Role statistics fetched!",
        data=stats
    )


@router.get("/search/", response_model=APIResponse)
def search_profiles(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    role: Optional[RoleEnum] = Query(None)
):
    """🔍 Profile search karo"""
    role_value = role.value if role else None
    profiles = profile_service.search_profiles(q, limit, role_value)
    
    return APIResponse(
        success=True,
        message=f"Found {len(profiles)} profiles",
        data=profiles
    )


@router.get("/{profile_id}", response_model=APIResponse)
def get_profile(profile_id: UUID):
    """👤 Ek specific profile dekho"""
    profile = profile_service.get_profile_by_id(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found!")
    
    return APIResponse(
        success=True,
        message="Profile found!",
        data=profile
    )


@router.put("/{profile_id}", response_model=APIResponse)
def update_profile(profile_id: UUID, profile_update: ProfileUpdate):
    """✏️ Profile update karo"""
    existing = profile_service.get_profile_by_id(profile_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found!")
    
    updated_profile = profile_service.update_profile(profile_id, profile_update)
    
    return APIResponse(
        success=True,
        message="Profile updated!",
        data=updated_profile
    )


@router.delete("/{profile_id}", response_model=APIResponse)
def delete_profile(profile_id: UUID):
    """🗑️ Profile delete karo"""
    existing = profile_service.get_profile_by_id(profile_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found!")
    
    deleted = profile_service.delete_profile(profile_id)
    
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete!")
    
    return APIResponse(
        success=True,
        message="Profile deleted!",
        data={"deleted_id": str(profile_id)}
    )