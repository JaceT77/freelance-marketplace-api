import pytest

from app.tests.helpers import (
    accept_bid,
    create_authenticated_user,
    create_bid,
    create_project,
    finish_contract,
)


pytestmark = pytest.mark.anyio


async def test_client_can_review_finished_contract_once(client):
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

    project_id = (await create_project(
        client,
        headers=client_headers,
        title="Reviewed contract",
        budget=1800,
    )).json()["id"]
    bid_id = (await create_bid(
        client,
        headers=freelancer_headers,
        project_id=project_id,
        price=1700,
    )).json()["id"]
    contract_id = (await accept_bid(
        client,
        headers=client_headers,
        bid_id=bid_id,
    )).json()["id"]
    await finish_contract(client, headers=client_headers, contract_id=contract_id)

    review_response = await client.post(
        f"/api/contracts/{contract_id}/reviews",
        headers=client_headers,
        json={"rating": 5, "comment": "Great freelancer and smooth delivery."},
    )
    duplicate_response = await client.post(
        f"/api/contracts/{contract_id}/reviews",
        headers=client_headers,
        json={"rating": 4, "comment": "Second review should fail."},
    )

    assert review_response.status_code == 201
    assert review_response.json()["rating"] == 5
    assert duplicate_response.status_code == 400


async def test_freelancer_cannot_create_review(client):
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

    project_id = (await create_project(
        client,
        headers=client_headers,
        title="Review permissions",
        budget=1600,
    )).json()["id"]
    bid_id = (await create_bid(
        client,
        headers=freelancer_headers,
        project_id=project_id,
        price=1550,
    )).json()["id"]
    contract_id = (await accept_bid(
        client,
        headers=client_headers,
        bid_id=bid_id,
    )).json()["id"]
    await finish_contract(client, headers=client_headers, contract_id=contract_id)

    response = await client.post(
        f"/api/contracts/{contract_id}/reviews",
        headers=freelancer_headers,
        json={"rating": 5, "comment": "Freelancer should not be allowed."},
    )

    assert response.status_code == 403
