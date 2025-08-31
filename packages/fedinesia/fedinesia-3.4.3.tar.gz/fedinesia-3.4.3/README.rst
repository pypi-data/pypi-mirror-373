""""""""""""""""""""""""""
Fedinesia
""""""""""""""""""""""""""

|Repo| |CI| |Downloads|

|Checked against| |Checked with|

|Code style| |Version| |Wheel|

|AGPL|


***!!! BEWARE, THIS TOOL WILL DELETE SOME OF YOUR POSTS ON THE FEDIVERSE !!!***

Fedinesia is a command line (CLI) tool to delete old statuses from Mastodon or Pleroma instances.
It respects rate limits imposed by servers.

Install and run from `PyPi <https://pypi.org>`_
=================================================

It's ease to install Fedinesia from Pypi using the following command::

    pip install fedinesia

Once installed Fedinesia can be started by typing ``fedinesia`` into the command line.

Configuration / First Run
-------------------------

Fedinesia will ask for all necessary parameters when run for the first time and store them in ```config.json``
file in the current directory.

Podman / Docker Container
=========================

Fedinesia can also be run using `Podman`_ or `Docker`_ as follows:

.. code-block:: shell

   podman run \                                                                                                                                                                                                                                                          nixos Wednesday @ 11:37:45
      --env AUDIT_LOG_FILE=/logging/audit.log \
      --env PAUSE_IN_SECONDS=300 \
      --replace \
      --volume ./config:/config \
      --volume ./logging:/logging \
      --name fedinesia \
      codeberg.org/marvinsmastodontools/fedinesia

Podman / Docker Environment Variables
-------------------------------------

* `PAUSE_IN_SECONDS` (mandatory)

  This must be set to a positive integer. This value is the number of seconds to wait between
  successive runs of `fedinesia`.

* `AUDIT_LOG_FILE` (optional)

  Full path to where audit log file should be written to. It is intended that logfiles will be
  written to `/logging` directory.

  No audit log file will be generated / updated if this value has not been set.

* `AUDIT_STYLE` (optional)

  What style of audit log file to write. Possible options are `PLAIN` or `CSV`.
  Defaults to `PLAIN`.

  Has no effect if `AUDIT_LOG_FILE` has not been set.

* `LIMIT` (optional)

  If set to a positive integer will make `fedinesia` stop processing any further deletions once
  this number of statuses have been deleted in the current execution.

* `DRY_RUN` (optional)

  If set to any value, eg `DRY_RUN=true` will make `fedinesia` not actually delete any status.
  Statuses that would be deleted are shown instead.

* `PROGRESS_FILE` (optional)

  If set to a filename will store the progress of deleted statuses to that file. This is intended
  to be used together with the `CONTINUE_PROGRESS` variable. This allows `fedinesia` to process
  a large number of status deletions over multiple executions while keeping track of progress.

* `CONTINUE_PROGRESS` (optional)

  If set to any value, eg `CONTINUE_PROGRESS=true` will make `fedinesia` continue with deleting
  statuses from last successfully deleted status in reverse historical order.

  Setting this variable implies that `PROGRESS_FILE` has been set as well.

* `LOGGING_CONFIG` (optional)

  Can be set to file name containing logging configuration definition. Below is a sample of the
  logging config file I use during development:

  .. code-block:: toml

    [[handlers]]
    sink = "sys.stdout"
    format = "{message}"
    level = "INFO"

    [[handlers]]
    sink = "/logging/dev-fedinesia-debug.log"
    rotation = "1 day"
    retention = 3
    level = "DEBUG"
    format = "{time} - {level} - {name} - {function}({line}) - {message}"
    colorize = "none"

Licensing
=========
Fedinesia is licensed under the `GNU Affero General Public License v3.0 <http://www.gnu.org/licenses/agpl-3.0.html>`_

Supporting Fedinesia
==========================

There are a number of ways you can support Fedinesia:

- Create an issue with problems or ideas you have with/for Fedinesia
- Create a pull request if you are more of a hands on person.
- You can `buy me a coffee <https://www.buymeacoffee.com/marvin8>`_.
- You can send me small change in Monero to the address below:

Monero donation address
-----------------------
``86ZnRsiFqiDaP2aE3MPHCEhFGTeiFixeQGJZ1FNnjCb7s9Gax6ZNgKTyUPmb21WmT1tk8FgM7cQSD5K7kRtSAt1y7G3Vp98nT``


.. |AGPL| image:: https://www.gnu.org/graphics/agplv3-with-text-162x68.png
    :alt: AGLP 3 or later
    :target:  https://codeberg.org/MarvinsMastodonTools/fedinesia/src/branch/main/LICENSE.md

.. |Repo| image:: https://img.shields.io/badge/repo-Codeberg.org-blue
    :alt: Repo at Codeberg.org
    :target: https://codeberg.org/MarvinsMastodonTools/fedinesia

.. |Downloads| image:: https://pepy.tech/badge/fedinesia
    :alt: Download count
    :target: https://pepy.tech/project/fedinesia

.. |Code style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code Style: Black
    :target: https://github.com/psf/black

.. |Checked against| image:: https://img.shields.io/badge/Safety--DB-Checked-green
    :alt: Checked against Safety DB
    :target: https://pyup.io/safety/

.. |Checked with| image:: https://img.shields.io/badge/pip--audit-Checked-green
    :alt: Checked with pip-audit
    :target: https://pypi.org/project/pip-audit/

.. |Version| image:: https://img.shields.io/pypi/pyversions/fedinesia
    :alt: PyPI - Python Version

.. |Wheel| image:: https://img.shields.io/pypi/wheel/fedinesia
    :alt: PyPI - Wheel

.. |CI| image:: https://ci.codeberg.org/api/badges/MarvinsMastodonTools/fedinesia/status.svg
    :alt: CI / Woodpecker
    :target: https://ci.codeberg.org/MarvinsMastodonTools/fedinesia

.. _Podman: https://podman.io/
.. _Docker: https://www.docker.com/
