import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.core.config import settings
settings.USE_SQLITE = True

from main import app
from app.proto import user_pb2
from app.core import database


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Initialisiert vor jedem Test eine saubere Datenbank."""
    from app.models.base import Base
    await database.init_db()
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_root_status(client: AsyncClient):
    """Testet den Status-Endpunkt."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "rest" in data["interfaces"]
    assert "graphql" in data["interfaces"]
    assert "protobuf" in data["interfaces"]


@pytest.mark.asyncio
async def test_rest_api_workflow(client: AsyncClient):
    """Testet den kompletten REST API Workflow (User & Item anlegen, abrufen)."""
    # 1. User via REST anlegen
    user_payload = {
        "username": "rest_user",
        "email": "rest_user@example.com",
        "role": "engineer",
    }
    create_res = await client.post("/api/v1/users", json=user_payload)
    assert create_res.status_code == 201, create_res.text
    user_data = create_res.json()
    assert user_data["username"] == "rest_user"
    user_id = user_data["id"]

    # 2. Item via REST anlegen
    item_payload = {
        "title": "ThinkPad X1",
        "description": "Dev Laptop",
        "price": 1899.50,
        "owner_id": user_id,
    }
    item_res = await client.post("/api/v1/items", json=item_payload)
    assert item_res.status_code == 201
    item_data = item_res.json()
    assert item_data["title"] == "ThinkPad X1"
    assert item_data["owner_id"] == user_id

    # 3. User mit Items abrufen
    get_res = await client.get(f"/api/v1/users/{user_id}")
    assert get_res.status_code == 200
    fetched_user = get_res.json()
    assert len(fetched_user["items"]) >= 1
    assert fetched_user["items"][0]["title"] == "ThinkPad X1"


@pytest.mark.asyncio
async def test_graphql_workflow(client: AsyncClient):
    """Testet GraphQL Mutation und Query über Strawberry."""
    # 1. User via GraphQL Mutation anlegen
    mutation = """
    mutation CreateUser($input: CreateUserInput!) {
        createUser(input: $input) {
            id
            username
            email
            role
            isActive
        }
    }
    """
    variables = {
        "input": {
            "username": "graphql_user",
            "email": "graphql_user@example.com",
            "role": "architect",
        }
    }
    gql_res = await client.post("/graphql", json={"query": mutation, "variables": variables})
    assert gql_res.status_code == 200, gql_res.text
    gql_data = gql_res.json()
    assert "errors" not in gql_data, gql_data.get("errors")
    created_user = gql_data["data"]["createUser"]
    assert created_user["username"] == "graphql_user"
    user_id = created_user["id"]

    # 2. Item via GraphQL anlegen
    item_mutation = """
    mutation CreateItem($input: CreateItemInput!) {
        createItem(input: $input) {
            id
            title
            price
            ownerId
        }
    }
    """
    item_vars = {
        "input": {
            "title": "Mechanical Keyboard",
            "description": "Ergonomic keyboard",
            "price": 159.00,
            "ownerId": user_id,
        }
    }
    item_res = await client.post("/graphql", json={"query": item_mutation, "variables": item_vars})
    assert item_res.status_code == 200
    item_res_data = item_res.json()
    assert "errors" not in item_res_data
    assert item_res_data["data"]["createItem"]["title"] == "Mechanical Keyboard"

    # 3. Query ausführen
    query = """
    query {
        users {
            id
            username
            items {
                title
                price
            }
        }
    }
    """
    query_res = await client.post("/graphql", json={"query": query})
    assert query_res.status_code == 200
    users_list = query_res.json()["data"]["users"]
    assert any(u["username"] == "graphql_user" for u in users_list)


@pytest.mark.asyncio
async def test_protobuf_workflow(client: AsyncClient):
    """Testet binäres Protocol Buffers Senden und Empfangen."""
    # 1. Protobuf Request binär serialisieren
    proto_req = user_pb2.CreateUserRequest(
        username="proto_user",
        email="proto_user@example.com",
        role="devops",
    )
    raw_bytes = proto_req.SerializeToString()

    # 2. POST mit Content-Type: application/x-protobuf
    res = await client.post(
        "/api/v1/proto/users",
        content=raw_bytes,
        headers={"Content-Type": "application/x-protobuf"},
    )
    assert res.status_code == 201, res.text
    assert res.headers["content-type"] == "application/x-protobuf"

    # 3. Binäre Antwort parsen
    user_res_proto = user_pb2.UserMessage()
    user_res_proto.ParseFromString(res.content)
    assert user_res_proto.username == "proto_user"
    assert user_res_proto.email == "proto_user@example.com"
    assert user_res_proto.role == "devops"
    assert user_res_proto.id > 0

    # 4. Alle User via Protobuf abrufen und parsen
    list_res = await client.get("/api/v1/proto/users")
    assert list_res.status_code == 200
    assert list_res.headers["content-type"] == "application/x-protobuf"

    list_proto = user_pb2.UserListResponse()
    list_proto.ParseFromString(list_res.content)
    assert list_proto.total >= 1
    usernames = [u.username for u in list_proto.users]
    assert "proto_user" in usernames
