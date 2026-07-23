"""
Tests for grievance CRUD endpoints + stats + export.
"""

import pytest
from httpx import AsyncClient

from tests.conftest import SAMPLE_GRIEVANCE_CREATE, SAMPLE_GRIEVANCE_INPUT, MOCK_GENERATED_CONTENT

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


from typing import Optional

async def _create_grievance(
    client: AsyncClient, headers: dict, overrides: Optional[dict] = None
) -> dict:
    """Create a grievance and return the response JSON."""
    data = {**SAMPLE_GRIEVANCE_CREATE, **(overrides or {})}
    resp = await client.post("/api/grievances", json=data, headers=headers)
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# POST /grievances
# ---------------------------------------------------------------------------


class TestCreateGrievance:
    async def test_create_finalized(self, client: AsyncClient, auth_headers):
        data = await _create_grievance(client, auth_headers)
        assert data["status"] == "finalized"
        assert data["company_name"] == "Acme Electronics"
        assert "id" in data

    async def test_create_draft(self, client: AsyncClient, auth_headers):
        """Correction #3: drafts are savable."""
        data = await _create_grievance(
            client, auth_headers, overrides={"status": "draft"}
        )
        assert data["status"] == "draft"

    async def test_create_invalid_status_on_create(
        self, client: AsyncClient, auth_headers
    ):
        """Only draft and finalized allowed on create."""
        resp = await client.post(
            "/api/grievances",
            json={**SAMPLE_GRIEVANCE_CREATE, "status": "sent"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_create_requires_auth(self, client: AsyncClient):
        resp = await client.post("/api/grievances", json=SAMPLE_GRIEVANCE_CREATE)
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /grievances
# ---------------------------------------------------------------------------


class TestListGrievances:
    async def test_list_empty(self, client: AsyncClient, auth_headers):
        resp = await client.get("/api/grievances", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_with_data(self, client: AsyncClient, auth_headers):
        await _create_grievance(client, auth_headers)
        await _create_grievance(
            client,
            auth_headers,
            overrides={"status": "draft", "company_name": "Beta Corp"},
        )

        resp = await client.get("/api/grievances", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_list_filter_by_status(self, client: AsyncClient, auth_headers):
        await _create_grievance(client, auth_headers)
        await _create_grievance(
            client, auth_headers, overrides={"status": "draft"}
        )

        resp = await client.get(
            "/api/grievances?status=draft", headers=auth_headers
        )
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "draft"

    async def test_list_pagination(self, client: AsyncClient, auth_headers):
        for i in range(15):
            await _create_grievance(
                client, auth_headers, overrides={"company_name": f"Company {i}"}
            )

        resp = await client.get(
            "/api/grievances?page=1&page_size=5", headers=auth_headers
        )
        data = resp.json()
        assert data["total"] == 15
        assert len(data["items"]) == 5
        assert data["page"] == 1

    async def test_list_ownership_isolation(
        self, client: AsyncClient, auth_headers, second_user_headers
    ):
        """A user only sees their own grievances."""
        await _create_grievance(client, auth_headers)

        resp = await client.get("/api/grievances", headers=second_user_headers)
        data = resp.json()
        assert data["total"] == 0


# ---------------------------------------------------------------------------
# GET /grievances/{id}
# ---------------------------------------------------------------------------


class TestGetGrievance:
    async def test_get_success(self, client: AsyncClient, auth_headers):
        created = await _create_grievance(client, auth_headers)
        resp = await client.get(
            f"/api/grievances/{created['id']}", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    async def test_get_not_found(self, client: AsyncClient, auth_headers):
        resp = await client.get(
            "/api/grievances/000000000000000000000000", headers=auth_headers
        )
        assert resp.status_code == 404

    async def test_get_invalid_object_id(self, client: AsyncClient, auth_headers):
        """Correction #5: invalid ObjectId → 404, not 500."""
        resp = await client.get(
            "/api/grievances/not-a-valid-id", headers=auth_headers
        )
        assert resp.status_code == 404

    async def test_get_other_users_grievance(
        self, client: AsyncClient, auth_headers, second_user_headers
    ):
        """Returns 404, not 403 — avoids confirming existence."""
        created = await _create_grievance(client, auth_headers)
        resp = await client.get(
            f"/api/grievances/{created['id']}", headers=second_user_headers
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PUT /grievances/{id}
# ---------------------------------------------------------------------------


class TestUpdateGrievance:
    async def test_update_letter_body(self, client: AsyncClient, auth_headers):
        created = await _create_grievance(client, auth_headers)
        resp = await client.put(
            f"/api/grievances/{created['id']}",
            json={"letter_body": "Updated letter content"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["letter_body"] == "Updated letter content"

    async def test_update_status(self, client: AsyncClient, auth_headers):
        created = await _create_grievance(client, auth_headers)
        resp = await client.put(
            f"/api/grievances/{created['id']}",
            json={"status": "sent"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "sent"

    async def test_update_not_found(self, client: AsyncClient, auth_headers):
        resp = await client.put(
            "/api/grievances/000000000000000000000000",
            json={"letter_body": "Test"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /grievances/{id}
# ---------------------------------------------------------------------------


class TestDeleteGrievance:
    async def test_delete_success(self, client: AsyncClient, auth_headers):
        created = await _create_grievance(client, auth_headers)
        resp = await client.delete(
            f"/api/grievances/{created['id']}", headers=auth_headers
        )
        assert resp.status_code == 204

        # Confirm it's gone
        resp2 = await client.get(
            f"/api/grievances/{created['id']}", headers=auth_headers
        )
        assert resp2.status_code == 404

    async def test_delete_not_found(self, client: AsyncClient, auth_headers):
        resp = await client.delete(
            "/api/grievances/000000000000000000000000", headers=auth_headers
        )
        assert resp.status_code == 404

    async def test_delete_other_users_grievance(
        self, client: AsyncClient, auth_headers, second_user_headers
    ):
        created = await _create_grievance(client, auth_headers)
        resp = await client.delete(
            f"/api/grievances/{created['id']}", headers=second_user_headers
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /grievances/stats (correction #7)
# ---------------------------------------------------------------------------


class TestStats:
    async def test_stats_empty(self, client: AsyncClient, auth_headers):
        resp = await client.get("/api/grievances/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    async def test_stats_with_data(self, client: AsyncClient, auth_headers):
        await _create_grievance(client, auth_headers)  # finalized
        await _create_grievance(
            client, auth_headers, overrides={"status": "draft"}
        )

        resp = await client.get("/api/grievances/stats", headers=auth_headers)
        data = resp.json()
        assert data["total"] == 2
        assert data["finalized"] == 1
        assert data["draft"] == 1


# ---------------------------------------------------------------------------
# GET /grievances/{id}/export/pdf
# ---------------------------------------------------------------------------


class TestExportPdf:
    async def test_export_finalized(self, client: AsyncClient, auth_headers):
        created = await _create_grievance(client, auth_headers)
        resp = await client.get(
            f"/api/grievances/{created['id']}/export/pdf", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert b"%PDF" in resp.content  # valid PDF starts with %PDF

    async def test_export_draft_blocked(self, client: AsyncClient, auth_headers):
        """Correction #3: draft export returns 400."""
        created = await _create_grievance(
            client, auth_headers, overrides={"status": "draft"}
        )
        resp = await client.get(
            f"/api/grievances/{created['id']}/export/pdf", headers=auth_headers
        )
        assert resp.status_code == 400
        assert "draft" in resp.json()["detail"].lower()

    async def test_export_not_found(self, client: AsyncClient, auth_headers):
        resp = await client.get(
            "/api/grievances/000000000000000000000000/export/pdf",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_export_unicode_company_name(
        self, client: AsyncClient, auth_headers
    ):
        """§13 Unicode check: non-Latin company name renders without error."""
        created = await _create_grievance(
            client,
            auth_headers,
            overrides={"company_name": "日本電子株式会社"},
        )
        resp = await client.get(
            f"/api/grievances/{created['id']}/export/pdf", headers=auth_headers
        )
        assert resp.status_code == 200
        assert b"%PDF" in resp.content
