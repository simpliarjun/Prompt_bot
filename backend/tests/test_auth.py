"""
Tests for auth endpoints (register, login, me).
"""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={
                "full_name": "Alice Smith",
                "email": "alice@example.com",
                "password": "SecurePass1!",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "alice@example.com"
        assert data["user"]["full_name"] == "Alice Smith"
        assert "id" in data["user"]

    async def test_register_duplicate_email(self, client: AsyncClient):
        user = {
            "full_name": "Bob",
            "email": "bob@example.com",
            "password": "SecurePass1!",
        }
        resp1 = await client.post("/api/auth/register", json=user)
        assert resp1.status_code == 201

        resp2 = await client.post("/api/auth/register", json=user)
        assert resp2.status_code == 409
        assert "already registered" in resp2.json()["detail"].lower()

    async def test_register_short_password(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"full_name": "X", "email": "x@example.com", "password": "short"},
        )
        assert resp.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"full_name": "X", "email": "not-an-email", "password": "SecurePass1!"},
        )
        assert resp.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        resp = await client.post("/api/auth/register", json={})
        assert resp.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient, auth_headers):
        resp = await client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "TestPass123!"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"

    async def test_login_wrong_password(self, client: AsyncClient, auth_headers):
        resp = await client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "WrongPass!"},
        )
        assert resp.status_code == 401
        assert "invalid credentials" in resp.json()["detail"].lower()

    async def test_login_nonexistent_email(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "Whatever1!"},
        )
        assert resp.status_code == 401
        # Generic message — must not reveal whether email exists
        assert "invalid credentials" in resp.json()["detail"].lower()


class TestMe:
    async def test_me_authenticated(self, client: AsyncClient, auth_headers):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert "id" in data

    async def test_me_no_token(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

    async def test_me_invalid_token(self, client: AsyncClient):
        resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert resp.status_code == 401
