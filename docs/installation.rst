Installation
============

This package provides a Solidity domain for Sphinx, as well as source autodocumenting functionality. Install this package via pip::

    pip install sphinxcontrib-soliditydomain

and add it to your Sphinx configuration file:

.. code-block:: python

    extensions = [
        'sphinx.ext.autodoc',
        'sphinxcontrib.soliditydomain',
    ]

.. note:: This package was written in Python 3 and will not work in Python 2. If you are using Read the Docs, be sure to set interpreter for the project to the CPython 3.x interpreter.

Configuration
-------------

.. describe:: autodoc_lookup_path

    A path to Solidity files to be indexed for autodocumentation purposes. By default, this is :code:`../contracts` relative to the documentation directory.
