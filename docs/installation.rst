Installation
============

This package provides a Solidity domain for Sphinx, as well as source autodocumenting functionality. Install this package via pip::

    pip install sphinxcontrib-soliditydomain

and add it to your Sphinx configuration file:

.. code-block:: python

    extensions = [
        # ...,
        'sphinxcontrib.soliditydomain',
    ]

If the ``autodoc`` features of this package are desired, be sure that the ``sphinx.ext.autodoc`` extension is also enabled:

.. code-block:: python

    extensions = [
        # ...,
        'sphinx.ext.autodoc',
        'sphinxcontrib.soliditydomain',
    ]

.. warning:: This package was written in Python 3 and **will not** work in Python 2.

    If you are using Read the Docs, be sure to set the *Python interpreter* used for the project to the CPython 3.x interpreter. This setting may be found in the *Admin > Advanced Settings* menu.
