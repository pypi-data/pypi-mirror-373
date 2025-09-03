dcmd Command Line Utility
=========================

The ``dcmd`` command-line utility is installed as part of the PyDelfini
package. This tool allows you to interact with a Delfini instance
through the command line or scripts, without needing to use the web
interface or write your own Python code.

Getting Started
---------------

``dcmd`` is installed whenever you have the PyDelfini package
installed, so if you haven't already, install PyDelfini using pip:

.. code-block:: bash

  pip install pydelfini

Next, run ``dcmd --help`` to view the basic usage information.

.. code-block:: bash

  usage: dcmd [-h] [-H HOSTNAME] [--insecure] [-k FN] [-u USERNAME] {auth,cdeset,pdd} ...

  options:
    -h, --help            show this help message and exit
    -H HOSTNAME, --hostname HOSTNAME
                          connect to HOSTNAME
    --insecure            connect using http rather than https
    -k FN, --token-file FN
                          use FN as the file to hold the login token
    -u USERNAME, --username USERNAME
                          disable interactive login; log in with USERNAME

  commands:
    {auth,cdeset,pdd}
      auth                Authentication and authorization operations
      cdeset              Manipulating CDE sets
      pdd                 Operations on PDDs (data dictionaries)

Connecting to a Delfini instance
-------------------------------

The first time you run ``dcmd``, you will need to provide the ``-H
HOSTNAME`` option to specify the hostname of your Delfini instance. If
you are connecting to a local, unsecured instance, add the
``--insecure`` flag.

.. code-block:: bash

  dcmd -H delfini.bioteam.net auth whoami

  # or, for a local connection
  dcmd -H localhost:3000 --insecure auth whoami

It will provide you a URL to visit in order to activate your session.
Open this URL in any web browser, then log in, and approve the session
activation.

.. code-block::

 To activate your session, visit the URL below:
    https://delfini.bioteam.net/login/activate/Ihze00000000Spg7WfnZ8A.CyJ2o544444444OV3YWeg1HH1ww

The login session will be stored in a login token file, by default in
your home directory named ``.dcmd-token``. You can adjust this by
using the ``--token-file`` option, and disable it if needed by setting
the token file to ``""``. While the login session is active, you will
not need to re-activate your session between calls to ``dcmd``.

Alternatively, if you would like to use a username and password
without needing to launch a separate web browser session, specify the
``-u USERNAME`` option. You will be prompted for your password.

Commands and Subcommands
------------------------

``dcmd`` offers a number of operations, grouped into commands and
subcommands. An example of this is:

.. code-block:: bash

  dcmd auth whoami

Which returns:

.. code-block:: yaml

  expires: '2024-01-29T23:54:01.027581+00:00'
  user:
    account_id: 22bacc0a-3715-4423-886c-d4da94b7f0d3
    email: null
    identity:
      fqda: zealous-smelt-5507@localhost
      primary_id: f04558e3-9297-429a-baa0-2917776073f2
      user_name: zealous-smelt-5507
    image: https://avatars.githubusercontent.com/u/6315798?v=4
    name: Karl Gutwin

The ``dcmd --help`` command lists the available commands, while adding
``--help`` to any command will list the available subcommands. Refer
to these outputs for the latest available commands.


``auth`` subcommand
^^^^^^^^^^^^^^^^^^^

``auth whoami``
   Prints out information about your current session.


``cdeset`` subcommand
^^^^^^^^^^^^^^^^^^^^^

``cdeset new cdeset_name description``
   Creates a new CDE set.

   Admin access is required.

   Positional arguments:

   * ``cdeset_name``: the name of the new CDE set
   * ``description``: a short description of the CDE set

``cdeset list``
   Lists current CDE sets.

``cdeset delete cdeset_name``
   Deletes a CDE set.

   Admin access is required.

   Positional arguments:

   * ``cdeset_name``: the name of the CDE set to delete

``cdeset copy-from-pdd cdeset_name collection_id version_id item_id``
   Copy data elements into a CDE set from a PDD.

   Admin access is required, as well as access to the specified PDD.

   Positional arguments:

   * ``cdeset_name``: the name of the CDE set to update
   * ``collection_id``: the collection UUID
   * ``version_id``: the collection version ID (typically "LIVE")
   * ``item_id``: the item UUID

   Optional arguments:

   * ``--description DESCRIPTION``: update the CDE set description


``pdd`` subcommand
^^^^^^^^^^^^^^^^^^

``pdd upload collection_id filename``
   Upload a PDD from a local file.

   Positional arguments:

   * ``collection_id``: the collection UUID
   * ``filename``: the local filename of the PDD to upload

   Optional arguments:

   * ``--item-name``: override the newly generated item name
   * ``--folder-id``: put the new item into the folder specified by UUID
