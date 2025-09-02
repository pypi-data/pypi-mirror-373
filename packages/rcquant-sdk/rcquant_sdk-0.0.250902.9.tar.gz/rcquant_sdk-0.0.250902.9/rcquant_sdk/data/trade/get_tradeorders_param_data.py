from typing import List
from ...interface import IData
from .tradeorder_data import TradeOrderData
from ...packer.trade.get_tradeorders_param_data_packer import GetTradeOrdersParamDataPacker


class GetTradeOrdersParamData(IData):
    def __init__(self, trade_name: str = ''):
        super().__init__(GetTradeOrdersParamDataPacker(self))
        self._TradeName = trade_name
        self._DataList: List[TradeOrderData] = []

    @property
    def TradeName(self):
        return self._TradeName

    @TradeName.setter
    def TradeName(self, value: str):
        self._TradeName = value

    @property
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value: List[TradeOrderData]):
        self._DataList: List[TradeOrderData] = value
