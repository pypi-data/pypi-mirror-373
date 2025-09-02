from ...interface import IData
from ...packer.market.query_param_data_packer import QueryParamDataPacker


class QueryParamData(IData):
    def __init__(self, market_name: str = '', investor_id: str = '', broker_id: str = '', exchange_id: str = '',
                 exchange_instid: str = '', instrument_id: str = '', product_type: int = 0,
                 product_id: str = '', order_id: str = '', trade_id: str = '', insert_time_start: str = '',
                 insert_time_end: str = '', trade_time_start: str = '', trade_time_end: str = '',
                 currency_id: str = '', hedge_type: int = 0):
        super().__init__(QueryParamDataPacker(self))
        self._MarketName: str = market_name
        self._InvestorID: str = investor_id
        self._BrokerID: str = broker_id
        self._ExchangeID: str = exchange_id
        self._ExchangeInstID: str = exchange_instid
        self._InstrumentID: str = instrument_id
        self._ProductType: int = product_type
        self._ProductID: str = product_id
        self._OrderID: str = order_id
        self._TradeID: str = trade_id
        self._InsertTimeStart: str = insert_time_start
        self._InsertTimeEnd: str = insert_time_end
        self._TradeTimeStart: str = trade_time_start
        self._TradeTimeEnd: str = trade_time_end
        self._CurrencyID: str = currency_id
        self._HedgeType: int = hedge_type

    @property
    def MarketName(self):
        return self._MarketName

    @MarketName.setter
    def MarketName(self, value: str):
        self._MarketName = value

    @property
    def InvestorID(self):
        return self._InvestorID

    @InvestorID.setter
    def InvestorID(self, value: str):
        self._InvestorID = value

    @property
    def BrokerID(self):
        return self._BrokerID

    @BrokerID.setter
    def BrokerID(self, value: str):
        self._BrokerID = value

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: str):
        self._ExchangeID = value

    @property
    def ExchangeInstID(self):
        return self._ExchangeInstID

    @ExchangeInstID.setter
    def ExchangeInstID(self, value: str):
        self._ExchangeInstID = value

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def ProductType(self):
        return self._ProductType

    @ProductType.setter
    def ProductType(self, value: int):
        self._ProductType = value

    @property
    def ProductID(self):
        return self._ProductID

    @ProductID.setter
    def ProductID(self, value: str):
        self._ProductID = value

    @property
    def OrderID(self):
        return self._OrderID

    @OrderID.setter
    def OrderID(self, value: str):
        self._OrderID = value

    @property
    def TradeID(self):
        return self._TradeID

    @TradeID.setter
    def TradeID(self, value: str):
        self._TradeID = value

    @property
    def InsertTimeStart(self):
        return self._InsertTimeStart

    @InsertTimeStart.setter
    def InsertTimeStart(self, value: str):
        self._InsertTimeStart = value

    @property
    def InsertTimeEnd(self):
        return self._InsertTimeEnd

    @InsertTimeEnd.setter
    def InsertTimeEnd(self, value: str):
        self._InsertTimeEnd = value

    @property
    def TradeTimeStart(self):
        return self._TradeTimeStart

    @TradeTimeStart.setter
    def TradeTimeStart(self, value: str):
        self._TradeTimeStart = value

    @property
    def TradeTimeEnd(self):
        return self._TradeTimeEnd

    @TradeTimeEnd.setter
    def TradeTimeEnd(self, value: str):
        self._TradeTimeEnd = value

    @property
    def CurrencyID(self):
        return self._CurrencyID

    @CurrencyID.setter
    def CurrencyID(self, value: str):
        self._CurrencyID = value

    @property
    def HedgeType(self):
        return self._HedgeType

    @HedgeType.setter
    def HedgeType(self, value: int):
        self._HedgeType = value
