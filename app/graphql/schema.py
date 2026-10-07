from typing import List, Optional
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.user_service import UserService
from app.services.item_service import ItemService
from app.graphql.types import UserType, ItemType, CreateUserInput, CreateItemInput


def to_item_type(item) -> ItemType:
    return ItemType(
        id=item.id,
        title=item.title,
        description=item.description or "",
        price=float(item.price),
        owner_id=item.owner_id,
    )


def to_user_type(user) -> UserType:
    return UserType(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else "",
        items=[to_item_type(i) for i in (user.items or [])],
    )


@strawberry.type
class Query:
    @strawberry.field(description="Alle Benutzer inklusive zugeordneter Items abrufen")
    async def users(
        self,
        info: strawberry.Info,
        skip: int = 0,
        limit: int = 100,
    ) -> List[UserType]:
        db: AsyncSession = info.context["db"]
        users = await UserService.get_all(db, skip=skip, limit=limit)
        return [to_user_type(u) for u in users]

    @strawberry.field(description="Einzelnen Benutzer nach ID abrufen")
    async def user(self, info: strawberry.Info, id: int) -> Optional[UserType]:
        db: AsyncSession = info.context["db"]
        user = await UserService.get_by_id(db, id)
        if not user:
            return None
        return to_user_type(user)

    @strawberry.field(description="Alle Items abrufen")
    async def items(
        self,
        info: strawberry.Info,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ItemType]:
        db: AsyncSession = info.context["db"]
        items = await ItemService.get_all(db, skip=skip, limit=limit)
        return [to_item_type(i) for i in items]


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Einen neuen Benutzer über GraphQL erstellen")
    async def create_user(
        self,
        info: strawberry.Info,
        input: CreateUserInput,
    ) -> UserType:
        db: AsyncSession = info.context["db"]
        existing_user = await UserService.get_by_username(db, input.username)
        if existing_user:
            raise ValueError(f"Username '{input.username}' existiert bereits.")

        existing_email = await UserService.get_by_email(db, input.email)
        if existing_email:
            raise ValueError(f"Email '{input.email}' existiert bereits.")

        user = await UserService.create(
            db,
            username=input.username,
            email=input.email,
            role=input.role or "user",
        )
        return to_user_type(user)

    @strawberry.mutation(description="Ein neues Item über GraphQL erstellen")
    async def create_item(
        self,
        info: strawberry.Info,
        input: CreateItemInput,
    ) -> ItemType:
        db: AsyncSession = info.context["db"]
        owner = await UserService.get_by_id(db, input.owner_id)
        if not owner:
            raise ValueError(f"Benutzer mit ID {input.owner_id} existiert nicht.")

        item = await ItemService.create(
            db,
            title=input.title,
            description=input.description or "",
            price=input.price,
            owner_id=input.owner_id,
        )
        return to_item_type(item)


schema = strawberry.Schema(query=Query, mutation=Mutation)


async def get_context(db: AsyncSession = Depends(get_db)):
    """Injected die SQLAlchemy-Session in den Strawberry-Kontext."""
    return {"db": db}


graphql_router = GraphQLRouter(schema, context_getter=get_context)
