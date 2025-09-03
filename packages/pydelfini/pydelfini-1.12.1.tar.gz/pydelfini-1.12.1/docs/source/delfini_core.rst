Delfini Core library
===================

The :py:mod:`pydelfini.delfini_core` module is a set of low-level
endpoints and data models that have been automatically generated from
Delfini's OpenAPI spec. For every Delfini API endpoint, there is a
single API method in :py:mod:`pydelfini.delfini_core.api`, and for every
request and response body, there is a corresponding data model defined
in :py:mod:`pydelfini.delfini_core.models`.

Since this module is automatically generated, any missing or
insubstantial documentation should be addressed by adding the
appropriate fields to the main ``delfini-api.yaml`` file. See the
:ref:`Autogeneration` section for more information.

Usage
-----

First, create a client::

    from pydelfini.delfini_core import Client

    client = Client(base_url="https://delfini.bioteam.net/api/v1")

If the endpoints you're going to hit require authentication, login
using the :py:func:`pydelfini.delfini_core.login.Login` helper::

    from pydelfini.delfini_core import Client
    from pydelfini.delfini_core import Login

    client = Login(
        Client(base_url="https://delfini.bioteam.net/api/v1")
    ).with_password('myuser', 'mypassword')

Now call your endpoint and use your models::

    from pydelfini.delfini_core.models import CollectionsGetCollectionsCollectionList as CollectionList
    from pydelfini.delfini_core.api.collections import collections_get_collections
    from pydelfini.delfini_core.types import Response

    # the context manager is recommended in order to clean up any HTTP connection pool,
    # see https://www.python-httpx.org/advanced/
    with client as client:
        coll_list: CollectionList = collections_get_collections.sync(client=client)

        # or if you need more info (e.g. status_code)
        response: Response[CollectionList] = collections_get_collections.sync_detailed(client=client)

Or do the same thing with an async version::

    from pydelfini.delfini_core.models import CollectionsGetCollectionsCollectionList as CollectionList
    from pydelfini.delfini_core.api.collections import collections_get_collections
    from pydelfini.delfini_core.types import Response

    async with client as client:
        my_data: CollectionList = await collections_get_collections.asyncio(client=client)
        response: Response[CollectionList] = await collections_get_collections.asyncio_detailed(client=client)

By default, when you're calling an HTTPS API it will attempt to verify
that SSL is working correctly. Using certificate verification is
highly recommended most of the time, but sometimes you may need to
authenticate to a server (especially an internal server) using a
custom certificate bundle::

    client = AuthenticatedClient(
        base_url="https://delfini.local/api/v1",
        token="SuperSecretToken",
        verify_ssl="/path/to/certificate_bundle.pem",
    )

You can also disable certificate validation altogether, but beware
that **this is a security risk**::

    client = AuthenticatedClient(
        base_url="https://delfini.local/api/v1",
        token="SuperSecretToken",
        verify_ssl=False
    )

Things to know
--------------

1. Every path/method combo becomes a Python module with four functions:

    1. ``sync``: Blocking request that returns parsed data, if
       successful, or raises an exception otherwise.
    2. ``sync_detailed``: Blocking request that always returns a
       ``Request``, optionally with ``parsed`` set if the request was
       successful.
    3. ``asyncio``: Like ``sync`` but async instead of blocking
    4. ``asyncio_detailed``: Like ``sync_detailed`` but async instead of blocking

2. All path/query params, and bodies become method arguments.
3. If your endpoint had any tags on it, the first tag will be used as
   a module name for the function ("collections" in the above examples)
4. Any endpoint which did not have a tag will be in
   :py:mod:`pydelfini.delfini_core.api.default`

Advanced customizations
-----------------------

There are more settings on the generated ``Client`` class which let you
control more runtime behavior, check out the docstring on that class
for more info. You can also customize the underlying ``httpx.Client`` or
``httpx.AsyncClient`` (depending on your use-case)::

    from pydelfini.delfini_core import Client

    def log_request(request):
        print(f"Request event hook: {request.method} {request.url} - Waiting for response")

    def log_response(response):
        request = response.request
        print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

    client = Client(
        base_url="https://delfini.bioteam.net/api/v1",
        httpx_args={"event_hooks": {"request": [log_request], "response": [log_response]}},
    )

    # Or get the underlying httpx client to modify directly with client.get_httpx_client()
    # or client.get_async_httpx_client()

You can even set the httpx client directly, but beware that this will
override any existing settings (e.g., base_url)::

    import httpx
    from pydelfini.delfini_core import Client

    client = Client(
        base_url="https://delfini.bioteam.net/api/v1",
    )
    # Note that base_url needs to be re-set, as would any shared cookies, headers, etc.
    client.set_httpx_client(
        httpx.Client(
            base_url="https://delfini.bioteam.net/api/v1", proxies="http://localhost:8030"
        )
    )

.. _Autogeneration:

Autogeneration
--------------

The core client code can be regenerated by running ``autogenerate.sh``
in the ``clients/pydelfini`` directory. This is automatically run by
the pre-commit hook system any time that ``delfini-api.yaml`` is
edited, so the client code should always remain in sync with the API
specification.

The ``autogenerate.sh`` script contains several templates and
workarounds for various bugs and strange behavior in
openapi-python-client.

Documentation
-------------

All documentation can be found under the
:py:mod:`pydelfini.delfini_core` API documentation section.

.. autosummary::
   :toctree: generated
   :template: custom-module-template.rst
   :recursive:

   pydelfini.delfini_core.api
   pydelfini.delfini_core.client
   pydelfini.delfini_core.errors
   pydelfini.delfini_core.login
   pydelfini.delfini_core.models
   pydelfini.delfini_core.paginator
   pydelfini.delfini_core.types


Updating Documentation
^^^^^^^^^^^^^^^^^^^^^^

Since the documentation is autogenerated from the code, and the code
is autogenerated from the original ``delfini-api.yaml`` API spec, any
updates to the :py:mod:`~pydelfini.delfini_core` documentation should be
made in ``delfini-api.yaml``. The mapping between fields in the source
OpenAPI document and the outputs in the generated code are:

* ``title:`` is essentially a rename for a given schema or endpoint.
  For example, if a schema is defined with the key
  ``dictionary_search_options:`` it will typically be autogenerated
  with the model title **DictionarySearchOptions**, but by providing
  ``title: Search Options for Dictionaries`` the model title will now
  be **SearchOptionsForDictionaries**. This should be used sparingly
  as it makes it harder to map back from the generated code to the
  original API definition.

* ``summary:`` is a short, one-line summary of a schema or endpoint.

* ``description:`` is a longer, multi-line description of the function
  of a schema or endpoint.
