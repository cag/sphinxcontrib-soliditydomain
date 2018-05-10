Solidity Domain Acceptance Tests
================================

.. default-domain:: sol

.. contract:: Thing is Something, SomeOtherThing, Ohman

   fjieafdsa

   :title: It does a thing
   :author: Some guy

   .. statevar:: uint private  thing
   .. statevar::   mapping(  uint=>OutcomeToken     [ ] [5] [])public outcomeTokens    
   .. statevar:: mapping (address => mapping (address => mapping (uint => mapping (address => uint)))) sellerBalances

   .. modifier:: onlySeller()    

   .. event:: Consumption(address indexed payer, uint amount)

   .. event:: AnonEvent() anonymous

   .. constructor:: (address proxy, address _creator, Event _eventContract, MarketMaker _marketMaker, uint24 _fee) \
        Proxy(proxy) \
        public

      This constructor does some stuff yo

      :param proxy: address to proxy to

   .. function:: () external payable

      Takes the ether for something

   .. function:: realTalk(string []cool,bytes32 [  8]storage beans) \
          public \
          onlyThing(cool, beans) \
          bladedeebloop \
          shooop() \
          returns(uint, int shoop)

      This does some stuff

      :param string cool: oh snap
      :param beans: aaaahhhhh
      :return [0]: some stuff
      :return int shoop: some more stuff
      :type cool: string
      :type beans: bytes32[] storage
      :rtype [0]: uint

   .. function:: createCampaign( \
        Event eventContract, \
        StandardMarketFactory marketFactory, \
        MarketMaker marketMaker, \
        uint24 fee, \
        uint funding, \
        uint deadline \
      ) \
        public view\
        returns (Campaign campaign)

   .. function:: doStuff()


.. interface:: Doable is Able

   stuff and things

   .. function:: doit(address,uint,int) external returns(string)

      Implementers gotta do the thing man...

      :param [0]: addres to do the thing to
      :type [0]: address
      :type [1]: uint
      :type [2]: int


.. library:: ThingLib

   provides implementation

   .. struct:: Campaign

      stuff and things

      :type beneficiary: address
      :member beneficiary: 1
      :type fundingGoal: uint
      :member fundingGoal: 2
      :type numFunders: uint
      :member numFunders:
      :type amount: uint
      :member amount: 4
      :type funders: mapping (uint => Funder)
      :member funders:

   .. enum:: ActionChoices

      :member GoLeft:
      :member GoRight: goes right
      :member GoStraight:
      :member SitStill: when sitting still
