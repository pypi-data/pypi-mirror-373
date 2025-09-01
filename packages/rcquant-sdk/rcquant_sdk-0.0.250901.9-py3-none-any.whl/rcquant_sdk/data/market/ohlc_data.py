from ...interface import IData
from ...packer.market.ohlc_data_packer import OHLCDataPacker


class OHLCData(IData):
    def __init__(self, exchange_id: str = '', instrument_id: str = '', trading_day: str = '',
                 trading_time: str = '', start_time: str = '', end_time: str = '', action_day: str = '',
                 action_time_span: int = -1, range: int = 60, index: int = -1, open_price: float = 0.0,
                 highest_price: float = 0.0, lowest_price: float = 0.0, close_price: float = 0.0, total_turnover: float = 0.0,
                 total_volume: int = 0, open_interest: float = 0.0, pre_settlement_price: float = 0.0, change_rate: float = 0.0,
                 change_value: float = 0.0, open_bid_price: float = 0.0, open_ask_price: float = 0.0, open_bid_volume: int = 0,
                 open_ask_volume: int = 0, highest_bid_price: float = 0.0, highest_ask_price: float = 0.0, highest_bid_volume: int = 0,
                 highest_ask_volume: int = 0, lowest_bid_price: float = 0.0, lowest_ask_price: float = 0.0, lowest_bid_volume: int = 0,
                 lowest_ask_volume: int = 0, close_bid_price: float = 0.0, close_ask_price: float = 0.0, close_bid_volume: int = 0,
                 close_ask_volume: int = 0):
        super().__init__(OHLCDataPacker(self))
        self._ExchangeID: str = exchange_id
        self._InstrumentID: str = instrument_id
        self._TradingDay: str = trading_day
        self._TradingTime: str = trading_time
        self._StartTime: str = start_time
        self._EndTime: str = end_time
        self._ActionDay: str = action_day
        self._ActionTimeSpan: int = action_time_span
        self._Range: int = range
        self._Index: int = index
        self._OpenPrice: float = open_price
        self._HighestPrice: float = highest_price
        self._LowestPrice: float = lowest_price
        self._ClosePrice: float = close_price
        self._TotalTurnover: float = total_turnover
        self._TotalVolume: int = total_volume
        self._OpenInterest: float = open_interest
        self._PreSettlementPrice: float = pre_settlement_price
        self._ChangeRate: float = change_rate
        self._ChangeValue: float = change_value
        self._OpenBidPrice: float = open_bid_price
        self._OpenAskPrice: float = open_ask_price
        self._OpenBidVolume: int = open_bid_volume
        self._OpenAskVolume: int = open_ask_volume
        self._HighestBidPrice: float = highest_bid_price
        self._HighestAskPrice: float = highest_ask_price
        self._HighestBidVolume: int = highest_bid_volume
        self._HighestAskVolume: int = highest_ask_volume
        self._LowestBidPrice: float = lowest_bid_price
        self._LowestAskPrice: float = lowest_ask_price
        self._LowestBidVolume: int = lowest_bid_volume
        self._LowestAskVolume: int = lowest_ask_volume
        self._CloseBidPrice: float = close_bid_price
        self._CloseAskPrice: float = close_ask_price
        self._CloseBidVolume: int = close_bid_volume
        self._CloseAskVolume: int = close_ask_volume

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
    def TradingDay(self):
        return self._TradingDay

    @TradingDay.setter
    def TradingDay(self, value: str):
        self._TradingDay = value

    @property
    def TradingTime(self):
        return self._TradingTime

    @TradingTime.setter
    def TradingTime(self, value: str):
        self._TradingTime = value

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, value: str):
        self._StartTime = value

    @property
    def EndTime(self):
        return self._EndTime

    @EndTime.setter
    def EndTime(self, value: str):
        self._EndTime = value

    @property
    def ActionDay(self):
        return self._ActionDay

    @ActionDay.setter
    def ActionDay(self, value: str):
        self._ActionDay = value

    @property
    def ActionTimeSpan(self):
        return self._ActionTimeSpan

    @ActionTimeSpan.setter
    def ActionTimeSpan(self, value: int):
        self._ActionTimeSpan = value

    @property
    def Range(self):
        return self._Range

    @Range.setter
    def Range(self, value: int):
        self._Range = value

    @property
    def Index(self):
        return self._Index

    @Index.setter
    def Index(self, value: int):
        self._Index = value

    @property
    def OpenPrice(self):
        return self._OpenPrice

    @OpenPrice.setter
    def OpenPrice(self, value: float):
        self._OpenPrice = value

    @property
    def HighestPrice(self):
        return self._HighestPrice

    @HighestPrice.setter
    def HighestPrice(self, value: float):
        self._HighestPrice = value

    @property
    def LowestPrice(self):
        return self._LowestPrice

    @LowestPrice.setter
    def LowestPrice(self, value: float):
        self._LowestPrice = value

    @property
    def ClosePrice(self):
        return self._ClosePrice

    @ClosePrice.setter
    def ClosePrice(self, value: float):
        self._ClosePrice = value

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
    def PreSettlementPrice(self):
        return self._PreSettlementPrice

    @PreSettlementPrice.setter
    def PreSettlementPrice(self, value: float):
        self._PreSettlementPrice = value

    @property
    def ChangeRate(self):
        return self._ChangeRate

    @ChangeRate.setter
    def ChangeRate(self, value: float):
        self._ChangeRate = value

    @property
    def ChangeValue(self):
        return self._ChangeValue

    @ChangeValue.setter
    def ChangeValue(self, value: float):
        self._ChangeValue = value

    @property
    def OpenBidPrice(self):
        return self._OpenBidPrice

    @OpenBidPrice.setter
    def OpenBidPrice(self, value: float):
        self._OpenBidPrice = value

    @property
    def OpenAskPrice(self):
        return self._OpenAskPrice

    @OpenAskPrice.setter
    def OpenAskPrice(self, value: float):
        self._OpenAskPrice = value

    @property
    def OpenBidVolume(self):
        return self._OpenBidVolume

    @OpenBidVolume.setter
    def OpenBidVolume(self, value: int):
        self._OpenBidVolume = value

    @property
    def OpenAskVolume(self):
        return self._OpenAskVolume

    @OpenAskVolume.setter
    def OpenAskVolume(self, value: int):
        self._OpenAskVolume = value

    @property
    def HighestBidPrice(self):
        return self._HighestBidPrice

    @HighestBidPrice.setter
    def HighestBidPrice(self, value: float):
        self._HighestBidPrice = value

    @property
    def HighestAskPrice(self):
        return self._HighestAskPrice

    @HighestAskPrice.setter
    def HighestAskPrice(self, value: float):
        self._HighestAskPrice = value

    @property
    def HighestBidVolume(self):
        return self._HighestBidVolume

    @HighestBidVolume.setter
    def HighestBidVolume(self, value: int):
        self._HighestBidVolume = value

    @property
    def HighestAskVolume(self):
        return self._HighestAskVolume

    @HighestAskVolume.setter
    def HighestAskVolume(self, value: int):
        self._HighestAskVolume = value

    @property
    def LowestBidPrice(self):
        return self._LowestBidPrice

    @LowestBidPrice.setter
    def LowestBidPrice(self, value: float):
        self._LowestBidPrice = value

    @property
    def LowestAskPrice(self):
        return self._LowestAskPrice

    @LowestAskPrice.setter
    def LowestAskPrice(self, value: float):
        self._LowestAskPrice = value

    @property
    def LowestBidVolume(self):
        return self._LowestBidVolume

    @LowestBidVolume.setter
    def LowestBidVolume(self, value: int):
        self._LowestBidVolume = value

    @property
    def LowestAskVolume(self):
        return self._LowestAskVolume

    @LowestAskVolume.setter
    def LowestAskVolume(self, value: int):
        self._LowestAskVolume = value

    @property
    def CloseBidPrice(self):
        return self._CloseBidPrice

    @CloseBidPrice.setter
    def CloseBidPrice(self, value: float):
        self._CloseBidPrice = value

    @property
    def CloseAskPrice(self):
        return self._CloseAskPrice

    @CloseAskPrice.setter
    def CloseAskPrice(self, value: float):
        self._CloseAskPrice = value

    @property
    def CloseBidVolume(self):
        return self._CloseBidVolume

    @CloseBidVolume.setter
    def CloseBidVolume(self, value: int):
        self._CloseBidVolume = value

    @property
    def CloseAskVolume(self):
        return self._CloseAskVolume

    @CloseAskVolume.setter
    def CloseAskVolume(self, value: int):
        self._CloseAskVolume = value
