from httpx import AsyncClient

from tests.conftest import Login

PHONE = "+919800000001"


async def test_otp_login_creates_user_and_returns_tokens(client: AsyncClient) -> None:
    r = await client.post("/v1/auth/otp/request", json={"phone": PHONE})
    assert r.status_code == 202
    code = r.json()["dev_code"]

    r = await client.post("/v1/auth/otp/verify", json={"phone": PHONE, "code": code})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"

    me = await client.get("/v1/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["phone"] == PHONE


async def test_wrong_code_is_rejected(client: AsyncClient) -> None:
    code = (await client.post("/v1/auth/otp/request", json={"phone": PHONE})).json()["dev_code"]
    wrong = "111111" if code != "111111" else "222222"
    r = await client.post("/v1/auth/otp/verify", json={"phone": PHONE, "code": wrong})
    assert r.status_code == 401
    assert r.headers["content-type"] == "application/problem+json"
    assert r.json()["code"] == "unauthorized"


async def test_code_is_single_use(client: AsyncClient) -> None:
    code = (await client.post("/v1/auth/otp/request", json={"phone": PHONE})).json()["dev_code"]
    ok = await client.post("/v1/auth/otp/verify", json={"phone": PHONE, "code": code})
    again = await client.post("/v1/auth/otp/verify", json={"phone": PHONE, "code": code})
    assert ok.status_code == 200
    assert again.status_code == 401


async def test_invalid_phone_is_422(client: AsyncClient) -> None:
    r = await client.post("/v1/auth/otp/request", json={"phone": "12345"})
    assert r.status_code == 422


async def test_refresh_token_issues_access_token(client: AsyncClient) -> None:
    code = (await client.post("/v1/auth/otp/request", json={"phone": PHONE})).json()["dev_code"]
    tokens = (await client.post("/v1/auth/otp/verify", json={"phone": PHONE, "code": code})).json()

    r = await client.post("/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    # An access token must not work as a refresh token.
    bad = await client.post("/v1/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert bad.status_code == 401


async def test_me_requires_auth(client: AsyncClient) -> None:
    assert (await client.get("/v1/me")).status_code == 401


async def test_update_me(client: AsyncClient, login: Login) -> None:
    headers = await login()
    r = await client.patch("/v1/me", json={"name": "Pranav R", "gender": "male"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Pranav R"
    assert r.json()["gender"] == "male"
