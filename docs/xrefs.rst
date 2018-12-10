Cross Referencing Solidity Objects
==================================

.. rst:role::
    sol:contract
    sol:lib
    sol:interface
    sol:svar
    sol:cons
    sol:func
    sol:mod
    sol:event
    sol:struct
    sol:enum

    These roles aid in cross referencing Solidity objects in the same project. For example,

    .. code-block:: rst

        :sol:func:`balanceOf`

    will render as :sol:func:`balanceOf`, which will link to where in the documentation this function has been documented. Likewise, autodoc generated documentation can be cross-referenced as well. For example,

    .. code-block:: rst

        :sol:contract:`BugBunny`

    will refer to the :sol:contract:`BugBunny` documentation which has been indexed.

    Using the ``:noindex:`` option will prevent a Solidity object description from being cross-referenced.
