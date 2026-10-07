#!/usr/bin/env python3
"""
Interaktives Demo-Skript zur Veranschaulichung der drei Schnittstellen-Paradigmen:
1. REST API
2. GraphQL API (Strawberry)
3. Protocol Buffers (Protobuf über HTTP)
"""

import asyncio
import json
from datetime import datetime
import httpx
from app.proto import user_pb2

BASE_URL = "http://127.0.0.1:8000"


def print_section(title: str):
    line = "=" * 70
    print(f"\n{line}")
    print(f"  {title}")
    print(f"{line}\n")


def print_sub(title: str):
    print(f"\n--- {title} ---")


async def run_demo():
    print_section("FASTAPI MULTI-PROTOCOL DEMO: REST, GRAPHQL & PROTOBUF")

    # Prüfen, ob Live-Server erreichbar ist
    use_live = False
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=1.0) as check_client:
            r = await check_client.get("/")
            if r.status_code == 200:
                use_live = True
                print("🟢 Verbunden mit laufendem Live-Server unter http://127.0.0.1:8000")
    except Exception:
        pass

    if use_live:
        client_context = httpx.AsyncClient(base_url=BASE_URL)
    else:
        from main import app
        from app.core.database import init_db
        await init_db()
        client_context = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        )
        print("🟡 Kein Server unter http://127.0.0.1:8000 gefunden.")
        print("   Führe Demo im direkten ASGI-In-Memory-Modus aus.")
        print("   (Tipp: Für echten HTTP-Server führe aus: uvicorn main:app --reload)\n")

    async with client_context as client:
        timestamp = int(datetime.now().timestamp())

        # =========================================================================
        # 1. REST API DEMO
        # =========================================================================
        print_section("1. REST API (FastAPI & Pydantic v2)")

        print_sub("POST /api/v1/users (JSON Request & Validierung)")
        rest_user_payload = {
            "username": f"alice_rest_{timestamp}",
            "email": f"alice_{timestamp}@example.com",
            "role": "software_engineer",
        }
        print(f"Sende Payload: {json.dumps(rest_user_payload, indent=2)}")
        res = await client.post("/api/v1/users", json=rest_user_payload)
        print(f"Status Code: {res.status_code}")
        alice_data = res.json()
        print(f"Antwort (Pydantic Model):\n{json.dumps(alice_data, indent=2)}")
        alice_id = alice_data["id"]

        print_sub(f"POST /api/v1/items (Item für Benutzer ID {alice_id} erstellen)")
        item_payload = {
            "title": "MacBook Pro M3 Max",
            "description": "High-End Dev Workstation",
            "price": 3499.00,
            "owner_id": alice_id,
        }
        res_item = await client.post("/api/v1/items", json=item_payload)
        print(f"Status Code: {res_item.status_code}")
        print(f"Erstelltes Item:\n{json.dumps(res_item.json(), indent=2)}")

        print_sub(f"GET /api/v1/users/{alice_id} (Abruf inklusive relationaler Items)")
        res_get = await client.get(f"/api/v1/users/{alice_id}")
        print(f"Ergebnis:\n{json.dumps(res_get.json(), indent=2)}")

        # =========================================================================
        # 2. GRAPHQL API DEMO (Strawberry)
        # =========================================================================
        print_section("2. GRAPHQL API (Strawberry GraphQL)")

        print_sub("Mutation: createUser über /graphql")
        gql_mutation = """
        mutation CreateUser($input: CreateUserInput!) {
            createUser(input: $input) {
                id
                username
                email
                role
                isActive
                createdAt
            }
        }
        """
        gql_vars = {
            "input": {
                "username": f"bob_graphql_{timestamp}",
                "email": f"bob_{timestamp}@example.com",
                "role": "cloud_architect",
            }
        }
        print("GraphQL Mutation:", gql_mutation.strip())
        gql_res = await client.post("/graphql", json={"query": gql_mutation, "variables": gql_vars})
        print(f"Status Code: {gql_res.status_code}")
        bob_data = gql_res.json()["data"]["createUser"]
        print(f"GraphQL Antwort:\n{json.dumps(bob_data, indent=2)}")
        bob_id = bob_data["id"]

        print_sub(f"Mutation: createItem für Bob (ID {bob_id})")
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
                "title": "Ultrawide 49-Zoll Monitor",
                "description": "5120x1440 144Hz",
                "price": 1199.90,
                "ownerId": bob_id,
            }
        }
        item_gql_res = await client.post("/graphql", json={"query": item_mutation, "variables": item_vars})
        print(f"Ergebnis:\n{json.dumps(item_gql_res.json()['data']['createItem'], indent=2)}")

        print_sub("Query: Verschachtelte Abfrage aller Benutzer mit ihren Items")
        gql_query = """
        query GetUsersWithItems {
            users(limit: 5) {
                id
                username
                email
                role
                items {
                    id
                    title
                    price
                }
            }
        }
        """
        query_res = await client.post("/graphql", json={"query": gql_query})
        print(f"GraphQL Query Ergebnis:\n{json.dumps(query_res.json()['data']['users'], indent=2)}")

        # =========================================================================
        # 3. PROTOBUF API DEMO (Protocol Buffers via HTTP)
        # =========================================================================
        print_section("3. PROTOBUF API (Binäre Protocol Buffers über HTTP)")

        print_sub("POST /api/v1/proto/users (Binäre Serialisierung & Übertragung)")
        proto_create_req = user_pb2.CreateUserRequest(
            username=f"charlie_proto_{timestamp}",
            email=f"charlie_{timestamp}@example.com",
            role="site_reliability_engineer",
        )
        raw_proto_bytes = proto_create_req.SerializeToString()
        print(f"Erstelle Protobuf Nachricht:")
        print(f"  username: {proto_create_req.username}")
        print(f"  email:    {proto_create_req.email}")
        print(f"  role:     {proto_create_req.role}")
        print(f"  Binäre Payload-Größe: {len(raw_proto_bytes)} Bytes (extrem kompakt!)")
        print(f"  Raw Hex: {raw_proto_bytes.hex()}")

        proto_res = await client.post(
            "/api/v1/proto/users",
            content=raw_proto_bytes,
            headers={"Content-Type": "application/x-protobuf"},
        )
        print(f"Status Code: {proto_res.status_code}")
        print(f"Response Content-Type: {proto_res.headers.get('content-type')}")
        print(f"Empfangene Binärgröße: {len(proto_res.content)} Bytes")

        # Deserialisieren
        user_msg = user_pb2.UserMessage()
        user_msg.ParseFromString(proto_res.content)
        print("\nErfolgreich deserialisierte Protobuf Antwort:")
        print(f"  ID:         {user_msg.id}")
        print(f"  Username:   {user_msg.username}")
        print(f"  Email:      {user_msg.email}")
        print(f"  Role:       {user_msg.role}")
        print(f"  Is Active:  {user_msg.is_active}")
        print(f"  Created At: {user_msg.created_at}")

        print_sub("GET /api/v1/proto/users (Binäre UserListResponse abrufen)")
        proto_list_res = await client.get("/api/v1/proto/users")
        list_msg = user_pb2.UserListResponse()
        list_msg.ParseFromString(proto_list_res.content)
        print(f"Gesamtanzahl Benutzer im System: {list_msg.total}")
        print("Benutzerliste aus binärem Protobuf-Stream:")
        for u in list_msg.users[-5:]:
            print(f"  • [ID {u.id}] {u.username} ({u.email}) | Rolle: {u.role}")

        # =========================================================================
        # FAZIT & VERGLEICH
        # =========================================================================
        print_section("FAZIT & ARCHITEKTUR-VERGLEICH")
        print("Alle 3 Schnittstellen teilen sich dieselbe Architektur:")
        print("  • Gemeinsame Datenbank: PostgreSQL (mit automatischem SQLite Fallback)")
        print("  • Gemeinsames ORM:       SQLAlchemy 2.0 Async mit Declarative Mapping")
        print("  • Gemeinsame Logik:      UserService & ItemService Schicht")
        print("  • Flexible Schnittstellen:")
        print("      - REST:     Standard HTTP/JSON, OpenAPI/Swagger Dokumentation")
        print("      - GraphQL:  Flexible Abfragen, Over-/Under-fetching Vermeidung")
        print("      - Protobuf: Maximale Geschwindigkeit, minimale Payload-Größe für Microservices")


if __name__ == "__main__":
    asyncio.run(run_demo())
