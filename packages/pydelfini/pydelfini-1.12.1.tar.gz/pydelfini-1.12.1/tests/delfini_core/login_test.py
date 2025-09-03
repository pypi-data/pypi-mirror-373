from pydelfini.delfini_core import Client
from pydelfini.delfini_core import Login
from pydelfini.delfini_core.api.auth import auth_get_session
from pydelfini.delfini_core.api.user import user_get_user_apc_outbox


def test_login_password(httpx_mock):
    httpx_mock.add_response(
        url="https://delfini.test/api/v1/auth/providers",
        json={
            "credentials": {
                "id": "credentials",
                "name": "Credentials",
                "type": "credentials",
                "signinUrl": "https://delfini.test/api/v1/auth/signin",
                "callbackUrl": "https://delfini.test/api/v1/auth/callback/credentials",
            }
        },
    )
    httpx_mock.add_response(
        url="https://delfini.test/api/v1/auth/csrf",
        json={"csrfToken": "a1b2c3d4"},
    )
    httpx_mock.add_response(
        url="https://delfini.test/api/v1/auth/callback/credentials",
        method="POST",
        match_json={
            "user_name": "testuser",
            "password": "testpassword",
            "callbackUrl": "http://null",
            "csrfToken": "a1b2c3d4",
            "json": True,
            "redirect": True,
        },
        json={"url": "http://null"},
        headers={"Set-Cookie": "session=something"},
    )

    client = Client(base_url="https://delfini.test/api/v1")
    client = Login(client).with_password("testuser", "testpassword")
    assert client.token == "something"

    httpx_mock.add_response(
        url="https://delfini.test/api/v1/user/testuser/outbox",
        match_headers={"Authorization": "Bearer something"},
        json={
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": "https://delfini.test/api/v1/user/testuser/outbox",
            "type": "OrderedCollectionPage",
            "totalItems": 0,
            "orderedItems": [],
        },
    )

    response = user_get_user_apc_outbox.sync(user_name="testuser", client=client)
    assert response.type == "OrderedCollectionPage"


def test_login_token(httpx_mock):
    httpx_mock.add_response(
        url="https://delfini.test/api/v1/auth/session",
        match_headers={"Authorization": "Bearer something"},
        json={
            "expires": "2024-01-01T00:00:00+00:00",
            "user": {
                "identity": {
                    "primary_id": "aaaabbbb",
                    "fqda": "someone@localhost",
                    "user_name": "someone",
                },
                "name": "Someone",
                "email": None,
                "image": None,
                "account_id": "xxxxyyyy",
                "metadata": {},
            },
        },
    )

    client = Client(base_url="https://delfini.test/api/v1")
    client = Login(client).with_session_id("something")
    assert client.token == "something"

    response = auth_get_session.sync(client=client)
    assert response.user.name == "Someone"
