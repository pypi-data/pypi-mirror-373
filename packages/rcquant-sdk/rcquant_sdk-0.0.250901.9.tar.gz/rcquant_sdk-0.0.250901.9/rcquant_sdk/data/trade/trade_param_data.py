from ...interface import IData
from ...packer.trade.trade_param_data_packer import TradeParamDataPacker


class TradeParamData(IData):
    def __init__(self, trade_names: str = ''):
        super().__init__(TradeParamDataPacker(self))
        self._TradeNames = trade_names

    @property
    def TradeNames(self):
        return self._TradeNames

    @TradeNames.setter
    def TradeNames(self, value: str):
        self._TradeNames = value
