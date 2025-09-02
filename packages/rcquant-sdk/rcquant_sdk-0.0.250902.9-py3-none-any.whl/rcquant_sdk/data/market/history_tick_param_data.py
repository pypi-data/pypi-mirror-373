from typing import List
from ...interface import IData
from .tick_data import TickData
from ...packer.market.history_tick_param_data_packer import HistoryTickParamDataPacker


class HistoryTickParamData(IData):
    def __init__(self, market_name: str = '', exchange_id: str = '', instrument_id: str = '', start_date: str = '',end_date: str = '', tick_list: List[TickData] = [], is_return_list: bool = False):
        super().__init__(HistoryTickParamDataPacker(self))
        self._MarketName: str = market_name
        self._ExchangeID: str = exchange_id
        self._InstrumentID: str = instrument_id
        self._StartDate: str = start_date
        self._EndDate: str = end_date
        self._TickList: list = tick_list
        self._IsReturnList: bool = is_return_list

    @property
    def MarketName(self):
        return self._MarketName

    @MarketName.setter
    def MarketName(self, value: str):
        self._MarketName = value

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
    def StartDate(self):
        return self._StartDate

    @StartDate.setter
    def StartDate(self, value: str):
        self._StartDate = value

    @property
    def EndDate(self):
        return self._EndDate

    @EndDate.setter
    def EndDate(self, value: str):
        self._EndDate = value

    @property
    def TickList(self):
        return self._TickList

    @TickList.setter
    def TickList(self, value: List[TickData]):
        self._TickList = value

    @property
    def IsReturnList(self):
        return self._IsReturnList

    @IsReturnList.setter
    def IsReturnList(self, value: bool):
        self._IsReturnList = value
