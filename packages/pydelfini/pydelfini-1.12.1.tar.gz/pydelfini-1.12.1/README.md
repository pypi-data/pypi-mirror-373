# PyDelfini

PyDelfini is an easy-to-use Python client for the Delfini data commons
platform. It's great for scripts, notebooks, or as a foundation for
other clients to interact with Delfini's public API.

# Quickstart

```
$ pip install pydelfini
$ python
>>> from pydelfini import login
>>> client = login('delfini.bioteam.net')
To activate your session, visit the URL below:
   https://delfini.bioteam.net/login/activate/........

Waiting for session activation...
>>> collection = client.get_collection_by_name('MHSVI')
>>> collection
<DelfiniCollection: name=MHSVI version=LIVE id=...>
```

# Features

* Interact with collections, folders, and items
* Read and write data streams (raw files)
* Read and write data tables via Pandas DataFrames

Coming soon:

* Work with data elements
    * Persist data elements through DataFrames
* Work with dataviews (create, edit using simple construction tools)
