from typing import Sequence, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserService:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
        stmt = select(User).offset(skip).limit(limit).order_by(User.id.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(
        db: AsyncSession,
        username: str,
        email: str,
        role: str = "user",
    ) -> User:
        user = User(
            username=username,
            email=email,
            role=role,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return False
        await db.delete(user)
        await db.flush()
        return True
