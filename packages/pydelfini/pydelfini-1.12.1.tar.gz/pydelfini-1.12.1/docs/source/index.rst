Welcome to PyDelfini's documentation!
====================================

PyDelfini is an easy-to-use client library for interacting with a
Delfini instance via Python.

Quickstart
----------

Install PyDelfini using pip on the command line:

.. code-block:: bash

  pip install pydelfini

Or in a Jupyter notebook cell::

  import sys
  !{sys.executable} -m pip install pydelfini

Then, log in to your Delfini instance and get a client::

  from pydelfini import login
  client = login('delfini.bioteam.net')  # Your Delfini hostname

It will print out a URL to visit to activate your session. Clicking
the URL will take you to your Delfini instance, where you will log in
and confirm that you want to activate this session. Once you do so,
the :py:func:`~pydelfini.client.login` method will return with the
activated client, and you can close your browser page or continue to
use it to navigate Delfini.

With your client ready to go, you can interact with your Delfini
collections, items, and tables::

  # Get a collection...
  collection = client.get_collection_by_name('MHSVI')

  # Get an item from the collection...
  item = collection["mh_svi_county_2018.csv"]

  # Get its table contents as a Pandas DataFrame
  dataframe = item.table()

  # Make a new dataframe
  import pandas as pd
  new_df = pd.DataFrame({"A": [1, 2, 3, 4, 5]})

  # Write the new dataframe as a new item
  collection.write_table("new-dataframe.csv", new_df, format="csv")


User Documentation
==================

PyDelfini offers three user interfaces to choose from:

* A high-level library which is focused on ease of use, available at
  :py:mod:`pydelfini`.

* A command-line utility named ``dcmd`` for scripting and general
  operations not otherwise handled by the Delfini web interface.

* And a low-level library which is auto-generated from the Delfini API
  definition and contains methods for every API endpoint, available at
  :py:mod:`pydelfini.delfini_core`.


High-level :py:mod:`pydelfini` interface
---------------------------------------

.. toctree::
   :maxdepth: 2

   pydelfini_api


``dcmd`` command-line utility
-----------------------------

.. toctree::
   :maxdepth: 2

   dcmd_cli


Low-level :py:mod:`~pydelfini.delfini_core` interface
---------------------------------------------------

.. toctree::
   :maxdepth: 2

   delfini_core



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
