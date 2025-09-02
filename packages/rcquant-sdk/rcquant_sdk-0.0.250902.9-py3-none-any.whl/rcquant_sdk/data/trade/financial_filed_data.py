from ...interface import IData
from ...packer.trade.financial_filed_data_packer import FinancialFiledDataPacker


class FinancialFiledData(IData):
    def __init__(self, day: int, type: int, json_data: str):
        super().__init__(FinancialFiledDataPacker(self))
        self._ID: int = -1
        self._Day: int = day
        self._Type: int = type
        self._JsonData: str = json_data

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value: int):
        self._ID = value

    @property
    def Day(self):
        return self._Day

    @Day.setter
    def Day(self, value: int):
        self._Day = value

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, value: int):
        self._Type = value

    @property
    def JsonData(self):
        return self._JsonData

    @JsonData.setter
    def JsonData(self, value: str):
        self._JsonData = value
