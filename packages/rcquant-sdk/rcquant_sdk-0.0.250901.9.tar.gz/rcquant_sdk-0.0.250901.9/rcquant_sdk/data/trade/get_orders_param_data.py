from typing import List
from ...interface import IData
from .order_data import OrderData
from ...packer.trade.get_orders_param_data_packer import GetOrdersParamDataPacker


class GetOrdersParamData(IData):
    def __init__(self, trade_name: str = ''):
        super().__init__(GetOrdersParamDataPacker(self))
        self._TradeName = trade_name
        self._DataList: List[OrderData] = []

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
    def DataList(self, value: List[OrderData]):
        self._DataList: List[OrderData] = value
