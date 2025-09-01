from ...interface import IData
from ...packer.market.market_param_data_packer import MarketParamDataPacker


class MarketParamData(IData):
    def __init__(self, market_names: str = ''):
        super().__init__(MarketParamDataPacker(self))
        self._MarketNames = market_names

    @property
    def MarketNames(self):
        return self._MarketNames

    @MarketNames.setter
    def MarketNames(self, value: str):
        self._MarketNames = value
