pragma solidity ^0.4.23;

import "./TimedUpdatableProxy.sol";

contract KombuchaHeader {
    event FilledKombucha(uint amountAdded, uint newFillAmount);
    event DrankKombucha(uint amountDrank, uint newFillAmount);
}

contract KombuchaDataInternal is TimedUpdatableProxyDataInternal, KombuchaHeader {
    uint internal fillAmount;
    uint internal capacity;
    string internal flavor;
}

contract KombuchaData is TimedUpdatableProxyData, KombuchaHeader {
    uint public fillAmount;
    uint public capacity;
    string public flavor;
}

contract KombuchaProxy is Proxy, KombuchaDataInternal {
    constructor(address proxied, address owner, string _flavor, uint _fillAmount, uint _capacity)
        public
        Proxy(proxied)
        OwnableData(owner)
    {
        // the body is identical to our original constructor!
        require(_fillAmount <= _capacity && _capacity > 0);
        flavor = _flavor;
        fillAmount = _fillAmount;
        capacity = _capacity;
    }
}

contract Kombucha is TimedUpdatableProxyImplementation, KombuchaData {
    function fill(uint amountToAdd) public {
        uint newAmount = fillAmount + amountToAdd;
        require(newAmount > fillAmount && newAmount <= capacity);
        fillAmount = newAmount;
        emit FilledKombucha(amountToAdd, newAmount);
    }
    function drink(uint amountToDrink) public returns (bytes32) {
        uint newAmount = fillAmount - amountToDrink;
        require(newAmount < fillAmount);
        fillAmount = newAmount;
        emit DrankKombucha(amountToDrink, newAmount);
        // this mess of hashes just here to pad out the bytecode
        return keccak256(keccak256(keccak256(keccak256(keccak256(
            keccak256(keccak256(keccak256(keccak256(keccak256(
            keccak256(keccak256(keccak256(keccak256(keccak256(
            keccak256(keccak256(keccak256(keccak256(keccak256(
            keccak256(keccak256(keccak256(keccak256(keccak256(
            keccak256(keccak256(keccak256(keccak256(keccak256(
            keccak256(keccak256(keccak256(keccak256(keccak256(
            keccak256(keccak256(keccak256(keccak256(keccak256(
            keccak256(keccak256(keccak256(keccak256(keccak256(
            keccak256(keccak256(keccak256(keccak256(keccak256(
                amountToDrink
            ))))))))))))))))))))))))))))))))))))))))))))))))));
    }
}

contract KombuchaFactory {
    Kombucha private masterCopy;
    constructor(Kombucha _masterCopy) public {
        masterCopy = _masterCopy;
    }
    function createKombucha(string flavor, uint fillAmount, uint capacity)
        public
        returns (Kombucha)
    {
        return Kombucha(new KombuchaProxy(masterCopy, msg.sender, flavor, fillAmount, capacity));
    }
}

contract Kombucha2DataInternal is KombuchaDataInternal {
    bool internal capped;
}

contract Kombucha2Data is KombuchaData {
    bool public capped;
}

contract Kombucha2Proxy is KombuchaProxy, Kombucha2DataInternal {
    constructor(address proxied, address owner, string flavor, uint fillAmount, uint capacity)
        public
        KombuchaProxy(proxied, owner, flavor, fillAmount, capacity)
    {
        capped = true;
    }
}

contract Kombucha2 is Kombucha, Kombucha2Data {
    function uncap() public {
        require(capped);
        capped = false;
    }
    
    function fill(uint amountToAdd) public {
        require(!capped);
        super.fill(amountToAdd);
    }
    function drink(uint amountToDrink) public returns (bytes32) {
        require(!capped);
        return keccak256(super.drink(amountToDrink));
    }
}

contract Kombucha2Update is
    KombuchaDataInternal,
    Kombucha2DataInternal,
    Update
{
    Kombucha internal kombucha;
    Kombucha2 internal kombucha2;

    constructor(Kombucha _kombucha, Kombucha2 _kombucha2)
        public
        OwnableData(0)
    {
        kombucha = _kombucha;
        kombucha2 = _kombucha2;
    }

    function implementationBefore() external view returns (address) {
        return kombucha;
    }
    
    function implementationAfter() external view returns (address) {
        return kombucha2;
    }
    
    function migrateData() external {
        capped = true;
    }
}
