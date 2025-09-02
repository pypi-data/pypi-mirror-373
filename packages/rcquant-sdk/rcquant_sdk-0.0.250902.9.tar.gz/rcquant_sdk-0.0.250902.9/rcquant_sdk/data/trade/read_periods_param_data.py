from typing import List
from ...interface import IData
from ...packer.trade.read_periods_param_data_packer import ReadPeriodsParamDataPacker


class ReadPeriodsParamData(IData):
    def __init__(self, instrument_id: List[str] = []):
        super().__init__(ReadPeriodsParamDataPacker(self))
        self._InstrumentID: List[str] = instrument_id.copy()
        self._DataList = {}

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: List[str]):
        self._InstrumentID = value

    @property
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value):
        self._DataList = value
