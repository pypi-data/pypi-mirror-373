Ctitools
========

Work with cti index files for the Heise papers c’t and iX

Description
-----------

This project provides different tool for processing index files from
Heise papers c’t and iX.

Saving the current base dataset, downloaded from Heise and extractng to
data, the command

.. code:: console

  > cti2bibtex data/inhalt.frm result.bibtex

creates a ``.bib`` file with 82100 entries. Importing this result in
Zotero took more than 28h and use more than 7GB of RAM.

``cti2bibtex`` works with the zip files directly now, so the commands

.. code:: console

  > cti2bibtex ctin2328.zip
  > cti2bibtex register-kurz.zip

create the files ``ctin2328.bib`` and ``register-kurz.bib``.

Installation
------------

``ctitools`` are on pypi now, so

.. code:: console

  > pip install ctitools

installs the last version.

It can also be installed from the source repository on gitlab

.. code:: console

  > pip install git+https://gitlab.com/berhoel/python/ctitools.git

Documentation
-------------

Documentation can be found `here <https://python.höllmanns.de/ctitools/>`_

Authors
-------

- Berthold Höllmann <berthold@xn--hllmanns-n4a.de>

Project status
--------------

The projects works for converting the `cti` and `frm` file, provided
by Heise, to `bib` files.
