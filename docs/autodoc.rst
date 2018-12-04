Automatic Documentation Generation from Solidity Source
=======================================================

Configuration
-------------

By default, ``sphinxcontrib.soliditydomain`` assumes that associated Solidity source files may be found in the directory ``../contracts`` relative to the root of the Sphinx project::

    .               # project root
    ├── docs/       # root of the Sphinx project
    ├── contracts/  # root of all contracts
    └── ...

This may be changed with the following configuration variable:

.. describe:: autodoc_lookup_path

    A path to Solidity files to be indexed for autodocumentation purposes. By default, this is :code:`../contracts` relative to the documentation directory.

.. note:: ``sphinxcontrib.soliditydomain`` will crawl the contract lookup directory, collecting ``.sol`` files, parsing the source content with an `ANTLR 4 <https://www.antlr.org>`_ parser using `this Solidity grammar definition <https://github.com/solidityj/solidity-antlr4>`_, and building a database of Solidity language objects for which the documentation tool will be able to automatically generate documentation.

.. note:: If a Solidity source file cannot be parsed by this package, a warning will be issued and the Sphinx build will continue trying to build the rest of the documentation.

Autodoc Directives By Example
-----------------------------

All of the formatting directives admit corresponding autodocumentation directives accessible by prepending ``autosol`` to the formatting directive name.

Let's suppose that the following code is found in a Solidity source file:

.. literalinclude:: example.sol
    :language: solidity

The following directives may be used:

.. rst:directive::
    .. autosolcontract:: Name
    .. autosollibrary:: Name
    .. autosolinterface:: Name

    These directive require the targetted object's name and will render to a corresponding :rst:dir:`sol:contract`, :rst:dir:`sol:library`, or :rst:dir:`sol:interface` block. The following ReST:

    .. code-block:: rst

        .. autosolcontract:: BugBunny

    will render like so:

    .. autosolcontract:: BugBunny

    Furthermore, the ``:noindex:``, ``:members:`` and ``:exclude-members:`` options may be used as expected, with

    .. code-block:: rst

        .. autosolcontract:: BugBunny
            :noindex:
            :members: doesEat, constructor

    yielding

    .. autosolcontract:: BugBunny
        :noindex:
        :members: doesEat, constructor

    and

    .. code-block:: rst

        .. autosolcontract:: BugBunny
            :noindex:
            :members:
            :exclude-members: ballerz, Consumption, eat, doesEat, <fallback>

    yielding

    .. autosolcontract:: BugBunny
        :noindex:
        :members:
        :exclude-members: ballerz, Consumption, eat, doesEat, <fallback>

    .. note:: Contract members will appear in the order they were indexed by the Solidity source crawler.
