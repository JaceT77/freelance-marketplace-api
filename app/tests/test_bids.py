import pytest

from app.tests.helpers import (
    create_authenticated_user,
    create_bid,
    create_project,
)


pytestmark = pytest.mark.anyio


async def test_freelancer_can_submit_one_bid_per_project(client):
    client_headers = await create_authenticated_user(
        client,
        username="client1",
        email="client1@example.com",
        password="client123",
        role="client",
    )
    other_client_headers = await create_authenticated_user(
        client,
        username="client2",
        email="client2@example.com",
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

    project_response = await create_project(
        client,
        headers=client_headers,
        title="Build a CRM API",
        budget=2000,
    )
    project_id = project_response.json()["id"]

    bid_response = await create_bid(
        client,
        headers=freelancer_headers,
        project_id=project_id,
        price=1800,
    )
    duplicate_response = await create_bid(
        client,
        headers=freelancer_headers,
        project_id=project_id,
        price=1750,
    )
    list_response = await client.get(
        f"/api/projects/{project_id}/bids",
        headers=client_headers,
    )
    forbidden_list_response = await client.get(
        f"/api/projects/{project_id}/bids",
        headers=other_client_headers,
    )

    assert bid_response.status_code == 201
    assert duplicate_response.status_code == 400
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert forbidden_list_response.status_code == 403
