from typing import List
from ...interface import IData
from ...packer.trade.read_history_tradeorder_param_data_packer import ReadHistoryTradeOrderParamDataPacker
from .tradeorder_data import TradeOrderData


class ReadHistoryTradeOrderParamData(IData):
    def __init__(self, start_date: str = '', end_date: str = ''):
        super().__init__(ReadHistoryTradeOrderParamDataPacker(self))
        self._StartDate: str = start_date
        self._EndDate: str = end_date
        self._DataList: List[TradeOrderData] = []

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
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value: List[TradeOrderData]):
        self._DataList = value
