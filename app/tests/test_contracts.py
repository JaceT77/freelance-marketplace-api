import pytest

from app.tests.helpers import (
    accept_bid,
    create_authenticated_user,
    create_bid,
    create_project,
    finish_contract,
)


pytestmark = pytest.mark.anyio


async def test_accepting_bid_creates_contract_and_updates_related_statuses(client):
    client_headers = await create_authenticated_user(
        client,
        username="client1",
        email="client1@example.com",
        password="client123",
        role="client",
    )
    freelancer1_headers = await create_authenticated_user(
        client,
        username="freelancer1",
        email="freelancer1@example.com",
        password="freelancer123",
        role="freelancer",
    )
    freelancer2_headers = await create_authenticated_user(
        client,
        username="freelancer2",
        email="freelancer2@example.com",
        password="freelancer123",
        role="freelancer",
    )

    project_id = (await create_project(
        client,
        headers=client_headers,
        title="Marketplace backend",
        budget=4000,
    )).json()["id"]
    bid1_id = (await create_bid(
        client,
        headers=freelancer1_headers,
        project_id=project_id,
        price=3600,
    )).json()["id"]
    bid2_id = (await create_bid(
        client,
        headers=freelancer2_headers,
        project_id=project_id,
        price=3500,
    )).json()["id"]

    accept_response = await accept_bid(client, headers=client_headers, bid_id=bid1_id)
    bids_response = await client.get(
        f"/api/projects/{project_id}/bids",
        headers=client_headers,
    )
    project_response = await client.get(
        f"/api/projects/{project_id}",
        headers=client_headers,
    )
    contracts_response = await client.get(
        "/api/contracts",
        headers=freelancer1_headers,
    )

    assert accept_response.status_code == 200
    assert accept_response.json()["status"] == "active"
    statuses = {bid["id"]: bid["status"] for bid in bids_response.json()}
    assert statuses[bid1_id] == "accepted"
    assert statuses[bid2_id] == "rejected"
    assert project_response.json()["status"] == "in_progress"
    assert len(contracts_response.json()) == 1
    assert contracts_response.json()[0]["project_id"] == project_id


async def test_client_can_finish_contract(client):
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
        title="Finishable contract",
        budget=2200,
    )).json()["id"]
    bid_id = (await create_bid(
        client,
        headers=freelancer_headers,
        project_id=project_id,
        price=2100,
    )).json()["id"]
    contract_id = (await accept_bid(
        client,
        headers=client_headers,
        bid_id=bid_id,
    )).json()["id"]

    freelancer_finish_attempt = await finish_contract(
        client,
        headers=freelancer_headers,
        contract_id=contract_id,
    )
    finish_response = await finish_contract(
        client,
        headers=client_headers,
        contract_id=contract_id,
    )
    project_response = await client.get(
        f"/api/projects/{project_id}",
        headers=client_headers,
    )

    assert freelancer_finish_attempt.status_code == 403
    assert finish_response.status_code == 200
    assert finish_response.json()["status"] == "finished"
    assert project_response.json()["status"] == "completed"
