# FastAPI Multi-Protocol Backend Demo

Ein modulares, produktionsnahes Python-Backend, das zeigt, wie moderne Architekturen mit **FastAPI**, **Pydantic v2**, **SQLAlchemy 2.0 (Async)** und **PostgreSQL** aufgebaut werden. 

Das Besondere an dieser Demo ist die gleichzeitige Bereitstellung und Erweiterung von **drei unterschiedlichen Schnittstellen-Paradigmen**, die alle auf dieselbe relationale Datenbasis und dieselbe Business-Logik-Schicht (Services) zugreifen:

1. 🌐 **REST API** (Standard HTTP/JSON mit automatischer OpenAPI/Swagger-Dokumentation)
2. 🔮 **GraphQL API** (Strawberry GraphQL mit GraphiQL-Explorer und typisierten Schemas)
3. ⚡ **Protocol Buffers (Protobuf)** (Binäre High-Performance-Schnittstelle über HTTP für Microservices)

---

## 🏗️ Architektur & Verzeichnisstruktur

```
fastapidemo/
├── app/
│   ├── core/
│   │   ├── config.py          # Pydantic Settings (.env, DB-Verbindungsdaten)
│   │   └── database.py        # SQLAlchemy 2.0 Async Engine & SQLite-Fallback
│   ├── models/                # SQLAlchemy 2.0 Declarative Mapped Entities
│   │   ├── base.py            # DeclarativeBase
│   │   ├── user.py            # User-Entity (1:n zu Items, lazy="selectin")
│   │   └── item.py            # Item-Entity (ForeignKey zu User)
│   ├── schemas/               # Pydantic v2 Schemas (Validierung & Serialisierung)
│   │   ├── user.py            # UserCreate, UserRead, UserUpdate
│   │   └── item.py            # ItemCreate, ItemRead
│   ├── services/              # Protokoll-unabhängige Geschäftslogik (CRUD)
│   │   ├── user_service.py    # Abfragen & Mutationen für Users
│   │   └── item_service.py    # Abfragen & Mutationen für Items
│   ├── routers/               # HTTP-Endpunkte
│   │   ├── rest_router.py     # REST-Routen (/api/v1/users, /api/v1/items)
│   │   └── proto_router.py    # Protobuf-Routen (/api/v1/proto/users)
│   ├── graphql/               # Strawberry GraphQL
│   │   ├── types.py           # GraphQL Typen & Input-Definitionen
│   │   └── schema.py          # Queries, Mutations & FastAPI Router (/graphql)
│   └── proto/                 # Protocol Buffers
│       ├── user.proto         # Schemadefinition (.proto)
│       └── user_pb2.py        # Kompilierter Python-Code
├── tests/
│   └── test_api.py            # Pytest Test-Suite für alle 3 Protokolle
├── docker-compose.yml         # Lokaler PostgreSQL 16 Container
├── demo_client.py             # Interaktiver Test-Client für alle Schnittstellen
├── test_main.http             # PyCharm HTTP Client Datei
├── requirements.txt           # Python-Abhängigkeiten
└── main.py                    # Einstiegspunkt & FastAPI Lifespan
```

---

## 🚀 Schnellstart

### 1. Abhängigkeiten installieren
Die Pakete sind bereits im virtuellen Environment installiert. Falls neu aufgesetzt:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Datenbank
Die Demo unterstützt **PostgreSQL** (über `asyncpg`), besitzt aber einen **automatischen Fallback auf SQLite**, falls kein PostgreSQL-Server läuft. Du kannst die Demo sofort ohne Docker starten!

Möchtest du echten PostgreSQL verwenden:
```bash
docker compose up -d
```

### 3. Server starten
```bash
uvicorn main:app --reload
```
Der Server läuft unter: **`http://127.0.0.1:8000`**

---

## 🔌 Die 3 Schnittstellen im Überblick

### 1. REST API
- **Dokumentation & Swagger UI**: Öffne [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Typisierung**: Pydantic v2 validiert Ein- und Ausgaben strikt.
- **Routen**:
  - `POST /api/v1/users`: Neuen Benutzer anlegen (Status 201)
  - `GET /api/v1/users`: Liste aller Benutzer
  - `GET /api/v1/users/{id}`: Detailansicht inklusive relationaler Items
  - `POST /api/v1/items`: Neues Item für einen Benutzer anlegen
  - `GET /api/v1/items`: Liste aller Items

### 2. GraphQL API (Strawberry)
- **Interaktiver GraphiQL Explorer**: Öffne [http://127.0.0.1:8000/graphql](http://127.0.0.1:8000/graphql)
- **Vorteil**: Clients fordern exakt die Felder an, die sie benötigen (kein Over-/Underfetching).
- **Beispiel-Mutation**:
  ```graphql
  mutation {
    createUser(input: {
      username: "anna_dev",
      email: "anna@example.com",
      role: "frontend_dev"
    }) {
      id
      username
      createdAt
    }
  }
  ```
- **Beispiel-Query mit verschachtelten Relationen**:
  ```graphql
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
  ```

### 3. Protocol Buffers (Protobuf über HTTP)
- **Ziel**: Höchste Geschwindigkeit und minimale Payload-Größe für Microservices oder mobile Clients.
- **Header**: `Content-Type: application/x-protobuf`
- **Endpunkte**:
  - `POST /api/v1/proto/users`: Sendet `CreateUserRequest` als Binär-Stream, empfängt `UserMessage`.
  - `GET /api/v1/proto/users`: Empfängt `UserListResponse` als kompakten Binär-Stream.
- **Kompilierung von `.proto`**:
  Wird `.proto` angepasst, kompiliert `grpcio-tools` direkt im Virtualenv ohne externe Tools:
  ```bash
  python -m grpc_tools.protoc -Iapp/proto --python_out=app/proto app/proto/user.proto
  ```

---

## 🧪 Testen & Vorführen

### Interaktiver Demo-Client (`demo_client.py`)
Führt alle drei Protokolle nacheinander aus und demonstriert, dass alle drei denselben Zustand in der Datenbank manipulieren:
```bash
python demo_client.py
```

### Automatisierte Pytest-Suite
```bash
pytest -v
```

### PyCharm HTTP Client
Öffne `test_main.http` in PyCharm und klicke auf die grünen "Play"-Icons neben den Requests, um REST- und GraphQL-Anfragen live auszuführen.

---

## 🛠️ Erweiterungsanleitung

### Wie füge ich ein neues Feld hinzu? (z.B. `phone` für User)
1. **Model** (`app/models/user.py`):
   ```python
   phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
   ```
2. **Pydantic Schemas** (`app/schemas/user.py`):
   Füge `phone: Optional[str] = None` in `UserBase` ein.
3. **GraphQL Types** (`app/graphql/types.py`):
   Füge `phone: Optional[str] = None` in `UserType` und `CreateUserInput` ein.
4. **Protobuf** (`app/proto/user.proto`):
   Füge `string phone = 8;` hinzu und führe den Kompilierungsbefehl aus.
5. Fertig! Datenbank-Tabellen werden beim nächsten Start automatisch angepasst.
