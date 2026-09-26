from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.ai.service import ensure_user
from modules.profile.schemas import InterestIn, InterestOut, ProfileOut, ProfileUpdate
from modules.profile.service.profile import (
    add_interest,
    get_or_create_profile,
    list_interests,
    remove_interest,
    update_profile,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile(db: AsyncSession = Depends(get_db)) -> ProfileOut:
    user = await ensure_user(db)
    profile = await get_or_create_profile(db, user)
    interests = await list_interests(db, user.id)
    return ProfileOut(
        email=user.email,
        timezone=user.timezone,
        role=profile.role,
        experience_level=profile.experience_level,
        digest_time=profile.digest_time,
        digest_length=profile.digest_length,
        excluded_topics=profile.excluded_topics,
        preferred_sources=profile.preferred_sources,
        interests=interests,
    )


@router.put("")
async def put_profile(payload: ProfileUpdate, db: AsyncSession = Depends(get_db)) -> ProfileOut:
    user = await ensure_user(db)
    profile = await update_profile(db, user, payload)
    interests = await list_interests(db, user.id)
    return ProfileOut(
        email=user.email,
        timezone=user.timezone,
        role=profile.role,
        experience_level=profile.experience_level,
        digest_time=profile.digest_time,
        digest_length=profile.digest_length,
        excluded_topics=profile.excluded_topics,
        preferred_sources=profile.preferred_sources,
        interests=interests,
    )


@router.post("/interests")
async def create_interest(payload: InterestIn, db: AsyncSession = Depends(get_db)) -> InterestOut:
    user = await ensure_user(db)
    return await add_interest(db, user, payload)


@router.delete("/interests/{interest_id}")
async def delete_interest(interest_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    user = await ensure_user(db)
    deleted = await remove_interest(db, user, interest_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Interest not found")
    return {"deleted": str(interest_id)}
