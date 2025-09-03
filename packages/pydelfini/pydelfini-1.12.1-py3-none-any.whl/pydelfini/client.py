"""Login and general Delfini operations"""
from collections.abc import Iterator
from urllib.parse import urlunparse

from .collections import DelfiniCollection
from .delfini_core import AuthenticatedClient as CoreAuthClient
from .delfini_core import Client as CoreClient
from .delfini_core import Login
from .delfini_core import Paginator
from .delfini_core.api.auth import auth_new_session
from .delfini_core.api.collections import collections_create_collection
from .delfini_core.api.collections import collections_get_collections
from .delfini_core.models import CollectionsGetCollectionsCollectionList
from .delfini_core.models import NewCollection
from .delfini_core.models import NewCollectionMetadata
from .delfini_core.types import UNSET


class DelfiniClient:
    """Main class for interacting with a Delfini instance."""

    def __init__(self, core: CoreAuthClient) -> None:
        self._client = core

    def __del__(self) -> None:
        if self._client._client:
            self._client._client.close()

    def get_collection_by_name(self, collection_name: str) -> DelfiniCollection:
        """Retrieve a single collection given its name.

        Raises:
            ValueError: if the collection could not be found or if more than one
                collection was found with the given name
        """
        collections = collections_get_collections.sync(
            client=self._client, name=collection_name
        )
        if len(collections.collections) == 1:
            return DelfiniCollection(collections.collections[0], self._client)

        raise ValueError(f"could not find collection: {collection_name}")

    def all_collections(self) -> Iterator[DelfiniCollection]:
        """Iterate over all collections visible to the user."""
        paginator = Paginator[CollectionsGetCollectionsCollectionList](
            collections_get_collections,
            self._client,
        )
        for page in paginator.paginate():
            for collection in page.collections:
                yield DelfiniCollection(collection, self._client)

    def new_collection(
        self, name: str, description: str, metadata: dict[str, str] = {}
    ) -> DelfiniCollection:
        """Create a new collection.

        Args:
            name: The short name of the collection
            description: A longer plain text description of the collection
            metadata: Optional key-value pairs of metadata on the collection

        """
        collection = collections_create_collection.sync(
            client=self._client,
            body=NewCollection(
                name=name,
                description=description,
                metadata=(
                    NewCollectionMetadata.from_dict(metadata) if metadata else UNSET
                ),
            ),
        )
        return DelfiniCollection(collection, self._client)


def make_base_url(host: str, scheme: str = "https") -> str:
    """Create a base URL for a Delfini instance.

    Args:
        host: The hostname of your Delfini instance, such as 'delfini.bioteam.net'.
        scheme: either 'https' or 'http'

    Returns:
        the Delfini API base URL

    """
    return urlunparse([scheme, host, "/api/v1", None, None, None])


def login(host: str, scheme: str = "https") -> DelfiniClient:
    """Login to a Delfini instance.

    This interactive login method will print a URL that you will need
    to visit in order to activate the login session. The function will
    wait to return until the session has successfully been activated.

    Args:
        host: The hostname of your Delfini instance, such as 'delfini.bioteam.net'.
        scheme: either 'https' or 'http'

    Returns:
        A :py:class:`DelfiniClient`

    """

    # get a session ID
    core = CoreClient(base_url=make_base_url(host, scheme))
    session_token = auth_new_session.sync(client=core)

    # construct the URL to activate the session
    activation_url = urlunparse(
        [
            scheme,
            host,
            f"/login/activate/{session_token.activation_code}",
            None,
            None,
            None,
        ]
    )

    print("To activate your session, visit the URL below:")
    print("  ", activation_url)
    print()
    print("Waiting for session activation...")

    # wait for the session to be activated
    authenticated = Login(core).with_session_id(session_token.session_id, wait=True)

    return DelfiniClient(authenticated)
