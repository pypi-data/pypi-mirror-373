pydelfini Client
===============

The :py:mod:`pydelfini` module offers a set of high-level interfaces,
helper classes, and methods for interacting with a Delfini instance. It
has been designed specifically for ease-of-use, performance, and
familiarity relative to other modules in the ecosystem.

The features of PyDelfini currently include:

* Browsing, locating, and creating collections
* Browsing items within collections
* Reading and writing item contents as binary or text file-like streams
* Reading and writing tabular item contents as Pandas DataFrames

Future features would likely include:

* Searching for data
* Reading and updating data elements and item column definitions
* Creating, previewing, and updating dataviews
* Updating permissions and requesting access to data


Logging in
----------

Most operations in PyDelfini require a logged-in session with a Delfini
instance. Logging in is simple and does not require providing
credentials through your script or notebook -- instead, the
:py:func:`~pydelfini.client.login` method generates a one-time URL
which will take you to your Delfini instance to activate the session.

.. code-block:: python

  from pydelfini import login
  client = login('delfini.bioteam.net')  # Your Delfini hostname

The typical output looks like this::

  To activate your session, visit the URL below:
     https://delfini.bioteam.net/login/activate/fd8wefnef....

  Waiting for session activation...

At this point, visit the provided URL, log in if necessary, and click
to approve the session activation. The
:py:func:`~pydelfini.client.login` method will return with an instance
of :py:class:`~pydelfini.client.DelfiniClient` and you can continue.

If you are working with a long-running script or some other use case
that does not allow for interactive login, you will need to establish
a logged-in client using the mid-level
:py:class:`pydelfini.delfini_core.login.Login` routines, and pass the
resulting :py:class:`~pydelfini.delfini_core.client.AuthenticatedClient`
to the constructor of :py:class:`~pydelfini.client.DelfiniClient`.

In the future, we plan to add support for unauthenticated, read-only
interactions with a Delfini instance.


General operations
------------------

Once logged in, your :py:class:`~pydelfini.client.DelfiniClient`
interface allows you to perform basic operations:

* Get a single collection with
  :py:meth:`~pydelfini.client.DelfiniClient.get_collection_by_name`

  .. code-block:: python

    collection = client.get_collection_by_name('MHSVI')

* List all collections with
  :py:meth:`~pydelfini.client.DelfiniClient.all_collections`

  .. code-block:: python

    for collection in client.all_collections():
        print(collection.name)

* Create a new collection with
  :py:meth:`~pydelfini.client.DelfiniClient.new_collection`

  .. code-block:: python

    collection = client.new_collection('Demo 1', 'A simple demo')


Each of the methods above returns an instance of (or an iterator over)
:py:class:`~pydelfini.collections.DelfiniCollection`.


Items and Folders
-----------------

The :py:class:`~pydelfini.collections.DelfiniCollection` interface
offers a range of methods for working with items and folders.

Retrieving an existing item is as simple as specifying its name as a
key on the collection or folder object::

  item = collection['item-name.txt']

Navigating folders can be done by using the
:py:meth:`~pydelfini.collections.FolderMixin.folder` method, or using
the key-based method mentioned earlier::

  folder = collection.folder('folder-name')
  # or
  folder = collection['folder-name']

Nested folders can be navigated either with chained key lookups or
with slashes in the requested key::

  subfolder = collection['folder-name/subfolder']
  item = collection['folder-name/subfolder/item-name.csv']

Getting a list of items in a collection or folder can be done by
iterating through the object::

  items = list(collection)
  # or
  for item in collection['folder-name']:
      print(item.name)

A recursive listing can be done on collections or folders using
:py:meth:`~pydelfini.collections.FolderMixin.walk`::

  # will print the full path to every item in the collection
  for item in collection.walk():
      print(item.path)

Reading and Writing Items
-------------------------

An item can be opened to a file-like object using the :py:meth:`open`
method on either the collection or the item itself::

  # these are equivalent:
  with collection.open('folder/item.txt', 'r') as fp:
      stuff = fp.read()

  with collection['folder/item.txt'].open('r') as fp:
      stuff = fp.read()

While both methods allow for reading and writing to existing items,
only the first method is supported for creating a new item::

  # this works:
  with collection.open('a-new-item.txt', 'w') as fp:
      fp.write('my new item contents')

  # this will return an "item not found" error:
  with collection['a-new-item.txt'].open('w') as fp:
      fp.write('my new item contents')

When reading or writing to items, it is very important to either use
the resulting stream in a context manager, or else close the stream as
soon as your code is done with the read or write operation. If this is
neglected, the read or write may not complete fully. This is
particularly an issue with writing large items, as failure to close
the stream can result in incomplete writes and/or corruption.

.. code-block:: python

  # recommended:
  with collection.open('a-large-item', 'wb') as fp:
      fp.write(large_item_contents)

  # also ok, but don't forget the close:
  fp = collection.open('a-large-item', 'wb')
  fp.write(large_item_contents)
  fp.close()

  # DON'T DO THIS
  fp = collection.open('a-large-item', 'wb')
  fp.write(large_item_contents)
  # missed the close! Danger!

The collection-level
:py:meth:`~pydelfini.collections.DelfiniCollection.open` method also
allows you to set key item metadata, such as content type, parser, and
column definitions::

  with collection.open(
      'data.csv', 'w',
      parser='csv',
      metadata={'content-type': 'text/csv'},
  ) as fp:
      fp.write('A,B,C\n1,1,1\n2,4,8\n3,9,27\n')


Tables and Dataframes
---------------------

An item that can be parsed as a table (those items that have their
``parser`` attribute set) can be retrieved as a
:py:class:`pandas.DataFrame` from the collection, folder, or the item
level::

  # these are equivalent
  df = collection.get_table('folder/item.csv')

  df = collection['folder/item.csv'].table()

The dataframe will have the appropriate columns and column types as
defined in the source item. Note that retrieval of large item tables
may take time to complete.

Writing a dataframe to a collection can be done at the collection or
folder level using
:py:meth:`~pydelfini.collections.FolderMixin.write_table`::

  collection['folder'].write_table('new-item.csv', p_df, format='csv')

Currently, CSV and Parquet output formats are supported.


Documentation
-------------

Detailed documentation for the PyDelfini client interface can be found
in the :py:mod:`pydelfini` API documentation section.

.. autosummary::
   :toctree: generated
   :template: custom-module-template.rst
   :recursive:

   pydelfini.client
   pydelfini.collections
   pydelfini.item_io
