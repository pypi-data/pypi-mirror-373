from typing import List
from ...interface import IData
from ...packer.trade.read_financial_param_data_packer import ReadFinancialParamDataPacker
from .financial_filed_data import FinancialFiledData


class ReadFinancialParamData(IData):
    def __init__(self, instrument_id: str = '', begin_date: int = 0, end_date: int = 0, type: int = 0):
        super().__init__(ReadFinancialParamDataPacker(self))
        self._InstrumentID: str = instrument_id
        self._BeginDate: int = begin_date
        self._EndDate: int = end_date
        self._Type: int = type
        self._DataList: List[FinancialFiledData] = []

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def BeginDate(self):
        return self._BeginDate

    @BeginDate.setter
    def BeginDate(self, value: int):
        self._BeginDate = value

    @property
    def EndDate(self):
        return self._EndDate

    @EndDate.setter
    def EndDate(self, value: int):
        self._EndDate = value

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, value: int):
        self._Type = value

    @property
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value: List[FinancialFiledData]):
        self._DataList = value
