"""Contains a helper to assist with handling paginated responses"""
from collections.abc import Iterator
from types import ModuleType
from typing import Any
from typing import Generic
from typing import get_args
from typing import get_type_hints
from typing import Protocol
from typing import TypeVar
from typing import Union

from .client import AuthenticatedClient
from .client import Client
from .errors import UnexpectedStatus
from .models.pagination import Pagination


class HasPagination(Protocol):
    """A :py:mod:`~typing.Protocol` that matches any model that
    supports :py:mod:`~pydelfini.delfini_core.models.pagination.Pagination`.

    """

    pagination: Pagination


T = TypeVar("T", bound=HasPagination)


class Paginator(Generic[T]):
    """A utility that helps with dealing with paginated API responses.

    Paginated API responses have the property ``pagination`` of type
    :py:mod:`~pydelfini.delfini_core.models.pagination.Pagination`. This
    model has an attribute
    :py:attr:`~pydelfini.delfini_core.models.pagination.Pagination.next_page_url`
    which holds the URL of the next response page; since the
    :py:mod:`~pydelfini.delfini_core` library does not allow you to
    directly interact with URLs, this helper assists with making these
    additional page requests.

    This class takes as arguments the module containing the desired
    API endpoint and the appropriate
    :py:mod:`~pydelfini.delfini_core.client`. Since this is a generic
    class, it is also encouraged for type safety to specify the
    expected return type in brackets. The actual API request is done
    by calling the :py:meth:`paginate` method.

    Example usage::

      from pydelfini.delfini_core.paginator import Paginator
      from pydelfini.delfini_core.api.collections import collections_get_collections
      from pydelfini.delfini_core.models import CollectionsGetCollectionsCollectionList

      pager = Paginator[CollectionsGetCollectionsCollectionList](
          collections_get_collections, client
      )
      for page in pager.paginate(public=True):
          # Note that you still need to iterate through each item
          # in each page
          for collection in page.collections:
              print(collection.name)

    .. warning::

      While the return type of :py:meth:`paginate` is set according to
      the generic class definition, the static type checker cannot
      verify that the provided module's :py:func:`sync` method
      actually returns the provided type. Additionally, the arguments
      to the :py:meth:`paginate` method are not type checked to align
      with the :py:func:`sync` method.

    """

    def __init__(
        self,
        mod: ModuleType,
        client: Union[Client, AuthenticatedClient],
    ) -> None:
        self.mod = mod
        self.client = client
        self.response_type = get_type_hints(mod.sync)["return"]

        # NOTE: this check is currently disabled due to the theory
        # that generic type annotations are not used at runtime, and
        # given that we can parse the proper response type at runtime
        # from `mod.sync` we don't even need this check. It can be
        # enabled, though, if users want more safety checks, as
        # skipping this check could theoretically cause the return
        # type annotation of paginate to not match what is actually
        # returned by the runtime code.
        if False and hasattr(self, "__orig_class__"):  # type: ignore[unreachable]
            annotated_type = get_args(self.__orig_class__)[0]  # type: ignore[unreachable]
            if self.response_type != annotated_type:
                raise RuntimeError("Mismatched type annotation")

    def paginate(self, *args: Any, **kwargs: Any) -> Iterator[T]:
        """Get an iterator over all pages from the response.

        Args:
            *args:
                Positional arguments to be passed to the module's :py:func:`sync`
                function
            **kwargs:
                Keyword arguments to be passed to the module's :py:func:`sync`
                function.

        Returns:
            An iterator over each response page.

        """
        parsed = self.mod.sync(*args, client=self.client, **kwargs)
        assert isinstance(parsed, self.response_type)
        yield parsed

        while parsed.pagination.next_page_url:
            httpx_response = self.client.get_httpx_client().request(
                method="get",
                url=parsed.pagination.next_page_url,
            )
            response = self.mod._build_response(
                client=self.client, response=httpx_response
            )
            parsed = response.parsed

            if isinstance(parsed, self.response_type):
                yield parsed
            else:
                raise UnexpectedStatus(response.status_code, response.content)
