from typing import List
from ...interface import IData
from ...packer.trade.read_exc_product_param_data_packer import ReadExcProductParamDataPacker


class ReadExcProductParamData(IData):
    def __init__(self, exchange_id: List[str] = [], product_id: List[str] = []):
        super().__init__(ReadExcProductParamDataPacker(self))
        self._ExchangeID: List[str] = exchange_id.copy()
        self._ProductID: List[str] = product_id.copy()
        self._DataList = []

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: List[str]):
        self._ExchangeID = value

    @property
    def ProductID(self):
        return self._ProductID

    @ProductID.setter
    def ProductID(self, value: List[str]):
        self._ProductID = value

    @property
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value):
        self._DataList = value
