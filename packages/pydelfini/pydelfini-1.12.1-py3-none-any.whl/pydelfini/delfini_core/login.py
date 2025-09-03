"""Contains functions to log in to a Delfini instance"""
import os
import time
from http.cookiejar import parse_ns_headers  # type: ignore
from typing import Any
from typing import Union

import attrs

from .api.auth import auth_authenticate_user
from .api.auth import auth_get_csrf
from .api.auth import auth_get_session
from .api.auth import auth_providers_req
from .client import AuthenticatedClient
from .client import Client
from .models import AuthAuthenticateUserAuthenticationRequest as AuthRequest
from .models import AuthGetSessionResponse200


ValidFilename = Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]


class LoginError(Exception):
    pass


class Login:
    """Mid-level login routines.

    Users wanting to log in to a Delfini instance will typically use
    :py:func:`pydelfini.login`. The functions in this class are most
    useful if you are working on a specialized Delfini client that
    predominantly uses :py:mod:`pydelfini.delfini_core`, or if you are
    working with workflows that do not support interactive login.

    Typical usage::

        from pydelfini.delfini_core import Client, Login

        # get an unauthenticated client
        client = Client(base_url='https://delfini.bioteam.net/api/v1')

        # log in with password
        auth_client = Login(client).with_password(username, password)

        # or with session ID
        auth_client = Login(client).with_session_id(session_id)

    """

    def __init__(self, client: Client) -> None:
        """A new Login instance."""
        self.client = client

    def _authenticated_client(self, session_id: str) -> AuthenticatedClient:
        client_attrs: dict[str, Any] = {}
        for attrib in attrs.fields(Client):
            if attrib.alias and attrib.init:
                client_attrs[attrib.alias] = getattr(self.client, attrib.name)
        client_attrs["token"] = session_id

        return AuthenticatedClient(**client_attrs)

    def with_password(self, username: str, password: str) -> AuthenticatedClient:
        """Log in using a username and password.

        Args:
            username (str): the user's username
            password (str): the user's password

        Raises:
            LoginError: if the login could not be completed

        Returns:
            a new Client that has been successfully logged in
        """
        cookie: dict[str, str] = {}
        with self.client as client:
            providers = auth_providers_req.sync(client=client)
            if "credentials" not in providers:
                raise LoginError(
                    f"credentials login not supported at {client._base_url}"
                )

            token = auth_get_csrf.sync(client=client)
            request = AuthRequest(
                user_name=username,
                password=password,
                callback_url="http://null",
                csrf_token=token.csrf_token,
                json=True,
            )
            login_response = auth_authenticate_user.sync_detailed(
                client=client, body=request
            )
            if "set-cookie" in login_response.headers:
                parsed_cookie = parse_ns_headers(
                    [login_response.headers["set-cookie"]]
                )[0]
                for k, v in parsed_cookie:
                    if k == "session":
                        cookie[k] = v
            else:
                raise LoginError("login failed")

        return self._authenticated_client(list(cookie.values())[0])

    def with_session_id(
        self, session_id: str, wait: bool = False
    ) -> AuthenticatedClient:
        """Log in using an existing session ID.

        You can get a session ID token by calling
        :py:mod:`.api.auth.auth_new_session` and using the
        :py:attr:`~.models.session_token.SessionToken.session_id`
        attribute of the response. To activate the session, the user
        should visit ``/login/activate/<activation_code>`` where
        ``<activation_code>`` is the value of
        :py:attr:`~.models.session_token.SessionToken.activation_code`
        in the response.


        Args:
            session_id (str): an active session ID
            wait (bool): if True, wait for the session to be activated

        Raises:
            LoginError: if the session could not be verified

        Returns:
            a new Client that has been successfully logged in

        """

        logged_in_client = self._authenticated_client(session_id)

        with logged_in_client as client:
            while True:
                session = auth_get_session.sync(client=client)
                if isinstance(session, AuthGetSessionResponse200):
                    break
                elif not wait:
                    raise LoginError("session token could not be verified")

                time.sleep(2)

        return self._authenticated_client(session_id)

    def from_token_file(self, filename: ValidFilename) -> AuthenticatedClient:
        """Log in using a session ID saved in a token file.

        This is typically used to make CLI interactions smoother,
        since the session has a short lifespan. However, if you need
        to share a session among multiple processes or otherwise want
        to persist a session between invocations, you can use
        :py:func:`to_token_file` to save the session token from an
        instance of :py:class:`~.client.AuthenticatedClient`, then use
        this method to load the token file in a new process.


        Args:
            filename: path to token file

        Raises:
            LoginError: if the session could not be verified

        Returns:
            a new Client that has been successfully logged in

        """

        with open(filename) as fp:
            data = fp.readlines()
            if data:
                session_id = data[-1].strip()
            else:
                raise LoginError("session token could not be read")

        return self.with_session_id(session_id, wait=False)


def to_token_file(client: AuthenticatedClient, filename: ValidFilename) -> None:
    """Save a session token from an AuthenticatedClient to a file.

    Since session tokens have a short lifespan, this is mostly useful
    for CLI interactions or other situations where a session should
    persist across multiple processes. See
    :py:func:`Login.from_token_file` for how to use the token file
    created by this method.


    Args:
        client: a fully-logged-in client, typically from :py:class:`Login`
        filename: path to token file

    """
    try:
        # make sure the file is created with proper permissions
        orig_umask = os.umask(0o077)
        with open(filename, "w") as fp:
            fp.write(f"# {client._base_url}\n{client.token.split(';')[0]}\n")
    finally:
        os.umask(orig_umask)


def token_file_get_base_url(filename: ValidFilename) -> str:
    """Retrieve the base URL of the Delfini session recorded in the token file.

    Args:
        filename: path to token file

    Returns:
        the base URL

    """

    with open(filename) as fp:
        return fp.readlines()[0].lstrip("#").strip()
