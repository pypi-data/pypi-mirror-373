============
Installation
============

Dockerhub
---------

Containers for arm64 and amd64 are available on `codeberg <https://codeberg.org/slidge/-/packages?q=&type=container>`_.
The slidge-whatsapp arm64 container is kindly provided by `raver <https://hub.docker.com/u/ravermeister>`_.
See :ref:`Containers` for more details.

debian
------

A debian package containing slidge and a bunch of legacy modules is available at
`<https://codeberg.org/slidge/debian>`_. See the README there for details and
instructions.

See :ref:`Debian packages` for information about how to launch slidge as a daemon via systemd.

pipx
----

.. image:: https://badge.fury.io/py/slidge.svg
  :alt: PyPI package
  :target: https://pypi.org/project/slidge/

Tagged releases are uploaded to `pypi <https://pypi.org/project/slidge/>`_
and should be installable on any distro with `pipx`.

Make sure that ``python3-gdbm`` is available on your system.
You can check that this is the case by running ``python3 -c "import dbm.gnu"``
which will exit with return code 0 if it's available.

.. code-block:: bash

    pipx install slidge
    slidge --legacy-module=your_importable_legacy_module

If you're looking for the bleeding edge, download a package
`here <https://codeberg.org/slidge/-/packages/pypi/slidge/>`_.
