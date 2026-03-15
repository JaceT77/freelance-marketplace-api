async def register_user(
    client,
    *,
    username: str,
    email: str,
    password: str,
    role: str,
    bio: str | None = None,
):
    return await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": role,
            "bio": bio,
        },
    )


async def login_user(client, *, username: str, password: str):
    return await client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )


async def create_authenticated_user(
    client,
    *,
    username: str,
    email: str,
    password: str,
    role: str,
    bio: str | None = None,
) -> dict[str, str]:
    register_response = await register_user(
        client,
        username=username,
        email=email,
        password=password,
        role=role,
        bio=bio,
    )
    assert register_response.status_code == 201, register_response.text

    login_response = await login_user(client, username=username, password=password)
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def create_project(
    client,
    *,
    headers: dict[str, str],
    title: str,
    description: str = "A detailed project description for the marketplace.",
    budget: float = 1000,
    deadline: str = "2030-01-01",
):
    return await client.post(
        "/api/projects",
        headers=headers,
        json={
            "title": title,
            "description": description,
            "budget": budget,
            "deadline": deadline,
        },
    )


async def create_bid(
    client,
    *,
    headers: dict[str, str],
    project_id: int,
    price: float = 900,
    message: str = "I can deliver this project on time.",
):
    return await client.post(
        f"/api/projects/{project_id}/bids",
        headers=headers,
        json={"price": price, "message": message},
    )


async def accept_bid(client, *, headers: dict[str, str], bid_id: int):
    return await client.post(f"/api/bids/{bid_id}/accept", headers=headers)


async def finish_contract(client, *, headers: dict[str, str], contract_id: int):
    return await client.post(f"/api/contracts/{contract_id}/finish", headers=headers)
