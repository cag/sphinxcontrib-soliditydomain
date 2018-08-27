Solidity Domain for Sphinx
==========================

This package provides a Solidity domain for Sphinx, as well as source autodocumenting functionality. Install this package via pip::

    pip install sphinxcontrib.soliditydomain

and add it to your Sphinx configuration file:

.. code-block:: python

    extensions = [
        'sphinx.ext.autodoc',
        'sphinxcontrib.soliditydomain',
    ]


This package was written in Python 3 and will not work in Python 2. If you are using Read the Docs, be sure to set interpreter for the project to the CPython 3.x interpreter.

Further documentation can be found `here <https://solidity-domain-for-sphinx.readthedocs.io/en/latest/>`_.
