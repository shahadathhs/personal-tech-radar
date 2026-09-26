import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Interest, User, UserProfile
from modules.profile.schemas import InterestIn, InterestOut, ProfileUpdate


async def get_or_create_profile(db: AsyncSession, user: User) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


async def update_profile(db: AsyncSession, user: User, payload: ProfileUpdate) -> UserProfile:
    profile = await get_or_create_profile(db, user)
    data = payload.model_dump(exclude_unset=True)
    if data.get("timezone"):
        user.timezone = data.pop("timezone")
    for field, value in data.items():
        setattr(profile, field, value)
    await db.commit()
    await db.refresh(profile)
    return profile


async def list_interests(db: AsyncSession, user_id: uuid.UUID) -> list[InterestOut]:
    result = await db.execute(
        select(Interest).where(Interest.user_id == user_id).order_by(Interest.name)
    )
    rows = result.scalars().all()
    by_id = {r.id: r for r in rows}
    return [
        InterestOut(
            id=r.id,
            name=r.name,
            parent_name=(
                by_id[r.parent_id].name
                if r.parent_id is not None and r.parent_id in by_id
                else None
            ),
            weight=r.weight,
            enabled=r.enabled,
        )
        for r in rows
    ]


async def add_interest(db: AsyncSession, user: User, payload: InterestIn) -> InterestOut:
    parent_id: uuid.UUID | None = None
    if payload.parent_name:
        result = await db.execute(
            select(Interest).where(
                Interest.user_id == user.id, Interest.name == payload.parent_name
            )
        )
        parent = result.scalar_one_or_none()
        if parent is None:
            parent = Interest(user_id=user.id, name=payload.parent_name)
            db.add(parent)
            await db.flush()
        parent_id = parent.id

    row = Interest(
        user_id=user.id,
        parent_id=parent_id,
        name=payload.name,
        weight=payload.weight,
        enabled=payload.enabled,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return InterestOut(
        id=row.id,
        name=row.name,
        parent_name=payload.parent_name,
        weight=row.weight,
        enabled=row.enabled,
    )


async def remove_interest(db: AsyncSession, user: User, interest_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Interest).where(Interest.id == interest_id, Interest.user_id == user.id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        return False
    await db.delete(row)
    await db.commit()
    return True
