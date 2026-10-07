from typing import List, Optional
import strawberry


@strawberry.type(description="GraphQL Typ für ein Item/Produkt")
class ItemType:
    id: int
    title: str
    description: str
    price: float
    owner_id: int


@strawberry.type(description="GraphQL Typ für einen Benutzer inklusive seiner Items")
class UserType:
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    items: List[ItemType]


@strawberry.input(description="Input zum Erstellen eines neuen Benutzers via GraphQL")
class CreateUserInput:
    username: str
    email: str
    role: Optional[str] = "user"


@strawberry.input(description="Input zum Erstellen eines neuen Items via GraphQL")
class CreateItemInput:
    title: str
    description: Optional[str] = ""
    price: float
    owner_id: int
