from typing import List
from ...interface import IData
from .ohlc_data import OHLCData
from ...packer.market.history_ohlc_param_data_packer import HistoryOHLCParamDataPacker


class HistoryOHLCParamData(IData):
    def __init__(self, market_name: str = '', exchange_id: str = '', instrument_id: str = '', range: str = "60",
                 start_date: str = '', end_date: str = '', ohlc_list: list = [], is_return_list: bool = False):
        super().__init__(HistoryOHLCParamDataPacker(self))
        self._MarketName: str = market_name
        self._ExchangeID: str = exchange_id
        self._InstrumentID: str = instrument_id
        self._Range: str = range
        self._StartDate: str = start_date
        self._EndDate: str = end_date
        self._OHLCList: list = ohlc_list
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
    def Range(self):
        return self._Range

    @Range.setter
    def Range(self, value: str):
        self._Range = value

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
    def OHLCList(self):
        return self._OHLCList

    @OHLCList.setter
    def OHLCList(self, value: List[OHLCData]):
        self._OHLCList = value

    @property
    def IsReturnList(self):
        return self._IsReturnList

    @IsReturnList.setter
    def IsReturnList(self, value: bool):
        self._IsReturnList = value
