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

.. warning:: If a Solidity source file cannot be parsed by this package, an error will be thrown and the Sphinx build will halt.

Autodoc Directives By Example
-----------------------------

All of the formatting directives admit corresponding autodocumentation directives accessible by prepending ``autosol`` to the formatting directive name.

Let's suppose that the following code is found in a Solidity source file:

.. literalinclude:: example.sol
    :language: solidity

The following directives may be used:

.. rst:directive:: .. autosolcontract:: Name

    This directive requires a contract name, and will render to a corresponding :rst:dir:`sol:contract` block. The following ReST:

    .. code-block:: rst

        .. autosolcontract:: BugBunny

    will render like so:

    .. autosolcontract:: BugBunny

    Furthermore, the ``:members:`` and ``:exclude-members:`` options may be used as expected, with

    .. code-block:: rst

        .. autosolcontract:: BugBunny
            :members: doesEat

    yielding

    .. autosolcontract:: BugBunny
        :members: doesEat

    and

    .. code-block:: rst

        .. autosolcontract:: BugBunny
            :members:
            :exclude-members: ballerz, Consumption, eat, AnonEvent, doesEat

    yielding

    .. autosolcontract:: BugBunny
        :members:
        :exclude-members: ballerz, Consumption, eat, AnonEvent, doesEat