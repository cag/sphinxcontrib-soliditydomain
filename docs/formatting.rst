Formatting Solidity Elements
============================

.. rst:directive::
    .. sol:contract:: Name is Parent1, Parent2, ...
    .. sol:interface:: Name is Parent1, Parent2, ...
    .. sol:library:: Name

    These directives describe top-level Solidity objects. The following:

    .. code-block:: rst

        .. sol:library:: SafeMath

            Provides arithemetic operations guarded against overflow

    renders as

    .. sol:library:: SafeMath

        Provides arithemetic operations guarded against overflow

    Likewise, the following:

    .. code-block:: rst

        .. sol:contract:: MintableBurnableToken is MintableToken, StandardBurnableToken

            A token which can both be minted and burnt.

    renders as

    .. sol:contract:: MintableBurnableToken is MintableToken, StandardBurnableToken

        A token which can both be minted and burnt.

.. rst:directive:: .. sol:statevar:: type visibility name

    State variables in Solidity:

    .. code-block:: rst

        .. sol:statevar:: int128 public widgetSocket

            A socket for a widget.

    yields

    .. sol:statevar:: int128 public widgetSocket

        A socket for a widget.

    Visibility modifiers are optional and include the following:

    - public
    - private
    - internal

.. rst:directive:: .. sol:constructor:: (type mod arg1, type mod arg2, ...) mod1 mod2 ...

    Constructors for contracts. May be used in the context of a :rst:dir:`sol:contract` directive. For example,

    .. code-block:: rst

        .. sol:contract:: FooFactory

            Produces instances of Foo.

            .. sol:constructor:: (uint a, int b, bytes32 c) public restrictedTo(a)

                Creates a FooFactory, initializing with supplied parameters.

    yields

    .. sol:contract:: FooFactory

        Produces instances of Foo.

        .. sol:constructor:: (uint a, int b, bytes32 c) public restrictedTo(a)

            Creates a FooFactory, initializing the new instance with supplied parameters.

.. rst:directive:: .. sol:function:: name(type mod arg1, ...) mod1 ... returns (type r1, ...)

    Solidity functions. May be used in the context of a :rst:dir:`sol:contract`, :rst:dir:`sol:library`, or :rst:dir:`sol:interface` directive. For example,

    .. code-block:: rst

        .. sol:interface:: ERC20

            .. sol:function:: balanceOf(address tokenOwner) \
                public constant returns (uint balance)

            Get the token balance for account ``tokenOwner``.

    yields

    .. sol:interface:: ERC20

        .. sol:function:: balanceOf(address tokenOwner) \
            public constant returns (uint balance)

        Get the token balance for account ``tokenOwner``.

.. rst:directive:: .. sol:modifier:: name(type mod arg1, ...)

    Solidity function modifiers. For example:

    .. code-block:: rst

        .. sol:contract:: Ownable

            .. sol:modifier:: onlyOwner()

                Throws if called by any account other than the owner.

    yields

    .. sol:contract:: Ownable

        .. sol:modifier:: onlyOwner()

            Throws if called by any account other than the owner.

.. rst:directive:: .. sol:event:: name(type mod arg1, ...)

    Solidity events. For example:

    .. code-block:: rst

        .. sol:contract:: RefundVault is Ownable

            .. sol:event:: Refunded(address indexed beneficiary, uint256 weiAmount)

                Emitted when ``weiAmount`` gets refunded to a ``beneficiary``.

    yields

    .. sol:contract:: RefundVault is Ownable

        .. sol:event:: Refunded(address indexed beneficiary, uint256 weiAmount)

            Emitted when ``weiAmount`` gets refunded to a ``beneficiary``.

.. rst:directive:: .. sol:struct:: Name

    Solidity structs. Members of the struct are represented by a ``member`` field. For example:

    .. code-block:: rst

        .. sol:struct:: DreamMachine

            Some archetypical madness.

            :member uint widget: Funky lil' widget.
            :member FunkUtils.Orientation orientation: Which way the machine is pointing.
            :member typelessThing: Type information is optional.

    yields

    .. sol:struct:: DreamMachine

        Some archetypical madness.

        :member uint widget: Funky lil' widget.
        :member FunkUtils.Orientation orientation: Which way the machine is pointing.
        :member typelessThing: Type information is optional.

.. rst:directive:: .. sol:enum:: Name

    Solidity enum definitions. Like :rst:dir:`struct`, members are represented by a ``member`` field, but for enums, this field is typeless. For example:

    .. code-block:: rst

        .. sol:enum:: Direction

            Which way to go.

            :member North: Where Santa's at.
            :member South: Where penguins're at.
            :member East: Get tricky.
            :member West: Get funky.

    yields

    .. sol:enum:: Direction

        Which way to go.

        :member North: Where Santa's at.
        :member South: Where penguins're at.
        :member East: Get tricky.
        :member West: Get funky.
