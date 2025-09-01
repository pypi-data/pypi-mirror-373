from ...interface import IData
from ...packer.market.tick_data_packer import TickDataPacker


class TickData(IData):
    def __init__(self, exchange_id: str = '', instrument_id: str = '', action_day: str = '',
                 action_time: str = '', update_milli_sec: int = 0, last_price: float = 0.0, last_volume: int = 0,
                 bid_price: float = 0.0, bid_volume: int = 0, ask_price: float = 0.0, ask_volume: int = 0,
                 total_turnover: float = 0.0, total_volume: int = 0, open_interest: float = 0.0,
                 pre_close_price: float = 0.0, pre_settlement_price: float = 0.0, pre_open_interest: float = 0.0):
        super().__init__(TickDataPacker(self))
        self._ExchangeID: str = exchange_id
        self._InstrumentID: str = instrument_id
        self._ActionDay: str = action_day
        self._ActionTime: str = action_time
        self._UpdateMilliSec: float = update_milli_sec
        self._LastPrice: float = last_price
        self._LastVolume: int = last_volume
        self._BidPrice: float = bid_price
        self._BidVolume: int = bid_volume
        self._AskPrice: float = ask_price
        self._AskVolume: int = ask_volume
        self._TotalTurnover: float = total_turnover
        self._TotalVolume: int = total_volume
        self._OpenInterest: float = open_interest
        self._PreClosePrice: float = pre_close_price
        self._PreSettlementPrice: float = pre_settlement_price
        self._PreOpenInterest: float = pre_open_interest

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: str):
        self._ExchangeID = value

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def ActionDay(self):
        return self._ActionDay

    @ActionDay.setter
    def ActionDay(self, value: str):
        self._ActionDay = value

    @property
    def ActionTime(self):
        return self._ActionTime

    @ActionTime.setter
    def ActionTime(self, value: str):
        self._ActionTime = value

    @property
    def UpdateMillisec(self):
        return self._UpdateMillisec

    @UpdateMillisec.setter
    def UpdateMillisec(self, value: int):
        self._UpdateMillisec = value

    @property
    def LastPrice(self):
        return self._LastPrice

    @LastPrice.setter
    def LastPrice(self, value: float):
        self._LastPrice = value

    @property
    def LastVolume(self):
        return self._LastVolume

    @LastVolume.setter
    def LastVolume(self, value: int):
        self._LastVolume = value

    @property
    def BidPrice(self):
        return self._BidPrice

    @BidPrice.setter
    def BidPrice(self, value: float):
        self._BidPrice = value

    @property
    def BidVolume(self):
        return self._BidVolume

    @BidVolume.setter
    def BidVolume(self, value: int):
        self._BidVolume = value

    @property
    def AskPrice(self):
        return self._AskPrice

    @AskPrice.setter
    def AskPrice(self, value: float):
        self._AskPrice = value

    @property
    def AskVolume(self):
        return self._AskVolume

    @AskVolume.setter
    def AskVolume(self, value: int):
        self._AskVolume = value

    @property
    def TotalTurnover(self):
        return self._TotalTurnover

    @TotalTurnover.setter
    def TotalTurnover(self, value: float):
        self._TotalTurnover = value

    @property
    def TotalVolume(self):
        return self._TotalVolume

    @TotalVolume.setter
    def TotalVolume(self, value: int):
        self._TotalVolume = value

    @property
    def OpenInterest(self):
        return self._OpenInterest

    @OpenInterest.setter
    def OpenInterest(self, value: float):
        self._OpenInterest = value

    @property
    def PreClosePrice(self):
        return self._PreClosePrice

    @PreClosePrice.setter
    def PreClosePrice(self, value: float):
        self._PreClosePrice = value

    @property
    def PreSettlementPrice(self):
        return self._PreSettlementPrice

    @PreSettlementPrice.setter
    def PreSettlementPrice(self, value: float):
        self._PreSettlementPrice = value

    @property
    def PreOpenInterest(self):
        return self._PreOpenInterest

    @PreOpenInterest.setter
    def PreOpenInterest(self, value: float):
        self._PreOpenInterest = value
