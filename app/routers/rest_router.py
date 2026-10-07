from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate, UserRead
from app.schemas.item import ItemCreate, ItemRead
from app.services.user_service import UserService
from app.services.item_service import ItemService

router = APIRouter(prefix="/api/v1", tags=["REST API"])


# ===================== USER ENDPOINTS =====================

@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Neuen Benutzer anlegen (REST)",
)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    # Prüfe auf Duplikate
    if await UserService.get_by_username(db, payload.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{payload.username}' existiert bereits.",
        )
    if await UserService.get_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{payload.email}' existiert bereits.",
        )
    return await UserService.create(
        db,
        username=payload.username,
        email=payload.email,
        role=payload.role,
    )


@router.get(
    "/users",
    response_model=List[UserRead],
    summary="Alle Benutzer abrufen (REST)",
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await UserService.get_all(db, skip=skip, limit=limit)


@router.get(
    "/users/{user_id}",
    response_model=UserRead,
    summary="Einzelnen Benutzer nach ID abrufen (REST)",
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {user_id} wurde nicht gefunden.",
        )
    return user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Benutzer löschen (REST)",
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    success = await UserService.delete(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {user_id} existiert nicht.",
        )
    return None


# ===================== ITEM ENDPOINTS =====================

@router.post(
    "/items",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Neues Item/Produkt für einen Benutzer anlegen (REST)",
)
async def create_item(payload: ItemCreate, db: AsyncSession = Depends(get_db)):
    # Existiert der Eigentümer?
    user = await UserService.get_by_id(db, payload.owner_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {payload.owner_id} existiert nicht.",
        )
    return await ItemService.create(
        db,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        owner_id=payload.owner_id,
    )


@router.get(
    "/items",
    response_model=List[ItemRead],
    summary="Alle Items abrufen (REST)",
)
async def list_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await ItemService.get_all(db, skip=skip, limit=limit)


@router.get(
    "/users/{user_id}/items",
    response_model=List[ItemRead],
    summary="Items eines bestimmten Benutzers abrufen (REST)",
)
async def list_user_items(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {user_id} wurde nicht gefunden.",
        )
    return await ItemService.get_by_owner(db, user_id)
