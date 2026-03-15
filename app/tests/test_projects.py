import pytest

from app.tests.helpers import create_authenticated_user, create_project


pytestmark = pytest.mark.anyio


async def test_client_can_create_project_and_freelancer_cannot(client):
    client_headers = await create_authenticated_user(
        client,
        username="client1",
        email="client1@example.com",
        password="client123",
        role="client",
    )
    freelancer_headers = await create_authenticated_user(
        client,
        username="freelancer1",
        email="freelancer1@example.com",
        password="freelancer123",
        role="freelancer",
    )

    create_response = await create_project(
        client,
        headers=client_headers,
        title="Build a landing page",
        budget=1200,
    )
    forbidden_response = await create_project(
        client,
        headers=freelancer_headers,
        title="Freelancer should not create this",
        budget=700,
    )

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "open"
    assert forbidden_response.status_code == 403


async def test_project_list_supports_search_and_budget_filters(client):
    client_headers = await create_authenticated_user(
        client,
        username="client1",
        email="client1@example.com",
        password="client123",
        role="client",
    )
    freelancer_headers = await create_authenticated_user(
        client,
        username="freelancer1",
        email="freelancer1@example.com",
        password="freelancer123",
        role="freelancer",
    )

    await create_project(
        client,
        headers=client_headers,
        title="Website design",
        budget=500,
    )
    await create_project(
        client,
        headers=client_headers,
        title="API integration",
        budget=1500,
    )

    response = await client.get(
        "/api/projects",
        headers=freelancer_headers,
        params={"search": "website", "min_budget": 400, "max_budget": 700},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["title"] == "Website design"
