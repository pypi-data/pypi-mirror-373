from ...interface import IData
from ...packer.trade.exc_product_time_data_packer import ExcProductTimeDataPacker


class ExcProductTimeData(IData):
    def __init__(self, start_time: str = '', end_time: str = '', index: int = 0, add_day: int = 0, instrument_status_kind: int = 14):
        super().__init__(ExcProductTimeDataPacker(self))
        self._StartTime: str = start_time
        self._EndTime: str = end_time
        self._Index: int = index
        self._AddDay: int = add_day
        self._InstrumentStatusKind: int = instrument_status_kind

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, value: str):
        self._StartTime = value

    @property
    def EndTime(self):
        return self._EndTime

    @EndTime.setter
    def EndTime(self, value: str):
        self._EndTime = value

    @property
    def Index(self):
        return self._Index

    @Index.setter
    def Index(self, value: int):
        self._Index = value

    @property
    def AddDay(self):
        return self._AddDay

    @AddDay.setter
    def AddDay(self, value: int):
        self._AddDay = value

    @property
    def InstrumentStatusKind(self):
        return self._InstrumentStatusKind

    @InstrumentStatusKind.setter
    def InstrumentStatusKind(self, value: int):
        self._InstrumentStatusKind = value
