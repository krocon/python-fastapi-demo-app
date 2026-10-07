from typing import Sequence, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.item import Item


class ItemService:
    @staticmethod
    async def get_by_id(db: AsyncSession, item_id: int) -> Optional[Item]:
        stmt = select(Item).where(Item.id == item_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_owner(db: AsyncSession, owner_id: int) -> Sequence[Item]:
        stmt = select(Item).where(Item.owner_id == owner_id).order_by(Item.id.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Item]:
        stmt = select(Item).offset(skip).limit(limit).order_by(Item.id.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(
        db: AsyncSession,
        title: str,
        description: str,
        price: float,
        owner_id: int,
    ) -> Item:
        item = Item(
            title=title,
            description=description,
            price=price,
            owner_id=owner_id,
        )
        db.add(item)
        await db.flush()
        await db.refresh(item)
        return item
