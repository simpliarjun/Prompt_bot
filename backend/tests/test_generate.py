"""
Tests for POST /generate endpoint.
Mocks the AI service — never calls the real Gemini API.
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from tests.conftest import SAMPLE_GRIEVANCE_INPUT, MOCK_GENERATED_CONTENT

pytestmark = pytest.mark.asyncio


class TestGenerate:
    async def test_generate_success(
        self, client: AsyncClient, auth_headers, mock_ai_service
    ):
        resp = await client.post(
            "/api/generate", json=SAMPLE_GRIEVANCE_INPUT, headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "input" in data
        assert "generated" in data
        assert data["generated"]["subject_line"] == MOCK_GENERATED_CONTENT["subject_line"]
        assert data["generated"]["severity"] == "medium"
        mock_ai_service.assert_called_once()

    async def test_generate_requires_auth(self, client: AsyncClient, mock_ai_service):
        resp = await client.post("/api/generate", json=SAMPLE_GRIEVANCE_INPUT)
        assert resp.status_code == 401

    async def test_generate_validation_error(
        self, client: AsyncClient, auth_headers, mock_ai_service
    ):
        # raw_description too short
        bad_input = {**SAMPLE_GRIEVANCE_INPUT, "raw_description": "short"}
        resp = await client.post(
            "/api/generate", json=bad_input, headers=auth_headers
        )
        assert resp.status_code == 422

    async def test_generate_ai_timeout(self, client: AsyncClient, auth_headers):
        from services.ai_service import AITimeoutError

        with patch(
            "routers.generate.generate_grievance_letter",
            new_callable=AsyncMock,
            side_effect=AITimeoutError("Timed out"),
        ):
            resp = await client.post(
                "/api/generate", json=SAMPLE_GRIEVANCE_INPUT, headers=auth_headers
            )
            assert resp.status_code == 502
            assert "unavailable" in resp.json()["detail"].lower()

    async def test_generate_ai_safety_block(self, client: AsyncClient, auth_headers):
        from services.ai_service import AISafetyBlockError

        with patch(
            "routers.generate.generate_grievance_letter",
            new_callable=AsyncMock,
            side_effect=AISafetyBlockError("Safety blocked"),
        ):
            resp = await client.post(
                "/api/generate", json=SAMPLE_GRIEVANCE_INPUT, headers=auth_headers
            )
            assert resp.status_code == 502

    async def test_generate_ai_malformed_output(
        self, client: AsyncClient, auth_headers
    ):
        from services.ai_service import AIMalformedOutputError

        with patch(
            "routers.generate.generate_grievance_letter",
            new_callable=AsyncMock,
            side_effect=AIMalformedOutputError("Bad output"),
        ):
            resp = await client.post(
                "/api/generate", json=SAMPLE_GRIEVANCE_INPUT, headers=auth_headers
            )
            assert resp.status_code == 502

    async def test_generate_rate_limit(self, client: AsyncClient, auth_headers):
        from fastapi import HTTPException

        with patch(
            "routers.generate.check_and_increment",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=429, detail="Rate limit exceeded"),
        ):
            resp = await client.post(
                "/api/generate", json=SAMPLE_GRIEVANCE_INPUT, headers=auth_headers
            )
            assert resp.status_code == 429
