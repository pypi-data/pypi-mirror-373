from typing import List
from ...interface import IData
from ...packer.trade.save_Financial_param_data_packer import SaveFinancialParamDataPacker
from .financial_filed_data import FinancialFiledData


class SaveFinancialParamData(IData):
    def __init__(self):
        super().__init__(SaveFinancialParamDataPacker(self))
        self._InstrumentID: str = ''
        self._DataList: List[FinancialFiledData] = []
        self._BasePath: str = ''

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value: List[FinancialFiledData]):
        self._DataList = value

    @property
    def BasePath(self):
        return self._BasePath

    @BasePath.setter
    def BasePath(self, value: str):
        self._BasePath = value
