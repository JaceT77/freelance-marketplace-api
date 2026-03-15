import pytest

from app.tests.helpers import login_user, register_user


pytestmark = pytest.mark.anyio


async def test_register_and_login_returns_bearer_token(client):
    register_response = await register_user(
        client,
        username="client1",
        email="client1@example.com",
        password="client123",
        role="client",
        bio="I hire freelancers.",
    )

    assert register_response.status_code == 201
    assert register_response.json()["role"] == "client"

    login_response = await login_user(client, username="client1", password="client123")

    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["user"]["username"] == "client1"


async def test_register_rejects_duplicate_username(client):
    first_response = await register_user(
        client,
        username="client1",
        email="client1@example.com",
        password="client123",
        role="client",
    )
    second_response = await register_user(
        client,
        username="client1",
        email="client2@example.com",
        password="client123",
        role="client",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Username is already taken."
