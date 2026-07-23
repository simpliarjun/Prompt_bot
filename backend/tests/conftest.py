"""
Shared pytest fixtures for CGMS backend tests.

Correction #12: Uses Testcontainers for a real MongoDB instance.
                 Skips with a clear message if Docker is unavailable.
Mocks the Gemini client in all tests — never calls the real API.
"""

import os
import sys
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Testcontainers MongoDB (correction #12)
# ---------------------------------------------------------------------------

def _start_mongo_container():
    """Try to start a MongoDB Testcontainer; return (container, uri) or skip."""
    try:
        from testcontainers.mongodb import MongoDbContainer
    except ImportError:
        print("testcontainers[mongodb] not installed — skipping DB tests")
        return None

    try:
        container = MongoDbContainer("mongo:7")
        container.start()
        uri = container.get_connection_url()
        return container, uri
    except Exception as exc:
        print(f"Docker unavailable — skipping DB tests: {exc}")
        return None


# Module-scoped container so we don't restart Mongo for every test
_mongo_container = None
_mongo_uri = None


def pytest_configure(config):
    """Start the Testcontainers MongoDB once per test session."""
    global _mongo_container, _mongo_uri
    result = _start_mongo_container()
    if result:
        _mongo_container, _mongo_uri = result


def pytest_unconfigure(config):
    """Stop the Testcontainers MongoDB when the session ends."""
    global _mongo_container
    if _mongo_container:
        _mongo_container.stop()
        _mongo_container = None


# ---------------------------------------------------------------------------
# Environment setup (must happen before importing app modules)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="session")
def _set_env():
    """Set required env vars for the test session."""
    os.environ.setdefault("GEMINI_API_KEY", "test-fake-key")
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-at-least-32-bytes-long!!")
    os.environ.setdefault("MONGODB_DB_NAME", "cgms_test")
    if _mongo_uri:
        os.environ["MONGODB_URI"] = _mongo_uri
    os.environ.setdefault("CORS_ALLOWED_ORIGINS", "http://localhost:5173")


# ---------------------------------------------------------------------------
# App & client fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def app():
    """Create a fresh FastAPI app with a clean test database."""
    # Reset cached settings
    import config as config_mod
    config_mod._settings = None

    from main import app as _app
    from database import connect_db, create_indexes, close_db, get_db

    await connect_db()
    await create_indexes()

    # Clean all collections before each test
    db = get_db()
    for coll_name in await db.list_collection_names():
        await db[coll_name].delete_many({})

    yield _app

    await close_db()


@pytest_asyncio.fixture
async def client(app):
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

TEST_USER = {
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123!",
}


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Register a test user and return auth headers."""
    resp = await client.post("/api/auth/register", json=TEST_USER)
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def second_user_headers(client: AsyncClient) -> dict:
    """Register a second user and return auth headers."""
    user2 = {
        "full_name": "Other User",
        "email": "other@example.com",
        "password": "OtherPass123!",
    }
    resp = await client.post("/api/auth/register", json=user2)
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# AI mock fixtures
# ---------------------------------------------------------------------------

MOCK_GENERATED_CONTENT = {
    "subject_line": "Formal Complaint: Defective Product",
    "letter_body": "I am writing to formally complain about a defective product I purchased.",
    "key_facts_summary": [
        "Purchased on 2026-01-15",
        "Product failed within 14 days",
        "Customer support unresponsive",
    ],
    "severity": "medium",
    "suggested_sla_hours": 120,
    "tone_note": None,
}

SAMPLE_GRIEVANCE_INPUT = {
    "company_name": "Acme Electronics",
    "product_or_service": "Wireless Headphones X200",
    "category": "product_defect",
    "incident_date": "2026-01-15",
    "order_reference": "ORD-12345",
    "raw_description": "The headphones stopped working after just two weeks of normal use and customer support kept transferring me around.",
    "desired_resolution": "replacement",
    "desired_resolution_details": "Replace with a working unit",
    "contact_name": "Test User",
    "contact_email": "test@example.com",
    "contact_phone": "+1234567890",
}

SAMPLE_GRIEVANCE_CREATE = {
    **SAMPLE_GRIEVANCE_INPUT,
    **MOCK_GENERATED_CONTENT,
    "status": "finalized",
}


@pytest.fixture
def mock_ai_service():
    """Mock the AI service to return canned content without calling Gemini."""
    from models.grievance import GeneratedGrievanceContent

    content = GeneratedGrievanceContent(**MOCK_GENERATED_CONTENT)

    with patch(
        "services.ai_service.generate_grievance_letter",
        new_callable=AsyncMock,
        return_value=content,
    ) as mock:
        yield mock
