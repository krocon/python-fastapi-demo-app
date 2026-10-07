import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.proto import user_pb2
from app.services.user_service import UserService
from app.services.item_service import ItemService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/proto", tags=["Protobuf API"])

PROTOBUF_MEDIA_TYPE = "application/x-protobuf"


def user_to_proto(user) -> user_pb2.UserMessage:
    """Konvertiert ein SQLAlchemy User-Model in eine Protobuf UserMessage."""
    user_msg = user_pb2.UserMessage(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )
    if hasattr(user, "items") and user.items:
        for item in user.items:
            item_msg = user_pb2.ItemMessage(
                id=item.id,
                title=item.title,
                description=item.description or "",
                price=float(item.price),
                owner_id=item.owner_id,
            )
            user_msg.items.append(item_msg)
    return user_msg


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    summary="Neuen Benutzer über binäres Protobuf anlegen",
    description="Erwartet CreateUserRequest als binäres Protobuf (application/x-protobuf) und liefert UserMessage zurück.",
    responses={
        201: {"content": {PROTOBUF_MEDIA_TYPE: {}}, "description": "Erstellter Benutzer als UserMessage"},
        400: {"description": "Ungültiges Protobuf oder Duplikat"},
    },
)
async def create_user_proto(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    proto_req = user_pb2.CreateUserRequest()
    try:
        proto_req.ParseFromString(body)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Konnte Protobuf Payload nicht parsen: {e}",
        )

    if not proto_req.username or not proto_req.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pflichtfelder 'username' und 'email' fehlen im Protobuf Request.",
        )

    if await UserService.get_by_username(db, proto_req.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{proto_req.username}' existiert bereits.",
        )
    if await UserService.get_by_email(db, proto_req.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{proto_req.email}' existiert bereits.",
        )

    user = await UserService.create(
        db,
        username=proto_req.username,
        email=proto_req.email,
        role=proto_req.role or "user",
    )

    proto_res = user_to_proto(user)
    return Response(
        content=proto_res.SerializeToString(),
        media_type=PROTOBUF_MEDIA_TYPE,
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/users",
    summary="Alle Benutzer als Protobuf-Liste (UserListResponse) abrufen",
    description="Gibt eine binäre UserListResponse zurück.",
    responses={200: {"content": {PROTOBUF_MEDIA_TYPE: {}}}},
)
async def list_users_proto(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    users = await UserService.get_all(db, skip=skip, limit=limit)
    proto_list = user_pb2.UserListResponse()
    for u in users:
        proto_list.users.append(user_to_proto(u))
    proto_list.total = len(users)

    return Response(
        content=proto_list.SerializeToString(),
        media_type=PROTOBUF_MEDIA_TYPE,
    )


@router.get(
    "/users/{user_id}",
    summary="Einzelnen Benutzer als binäre Protobuf UserMessage abrufen",
    responses={
        200: {"content": {PROTOBUF_MEDIA_TYPE: {}}},
        404: {"description": "Benutzer nicht gefunden"},
    },
)
async def get_user_proto(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benutzer mit ID {user_id} wurde nicht gefunden.",
        )

    proto_user = user_to_proto(user)
    return Response(
        content=proto_user.SerializeToString(),
        media_type=PROTOBUF_MEDIA_TYPE,
    )
