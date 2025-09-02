from ...interface import IData
from ...packer.trade.exc_product_data_packer import ExcProductDataPacker


class ExcProductData(IData):
    def __init__(self, exchange_id: str = '', product_id: str = '', product_name: str = '',
                 volume_multiple: float = -1.0, price_tick: float = -1.0,
                 max_market_order_volume: int = -1, max_limit_order_volume: int = -1):
        super().__init__(ExcProductDataPacker(self))
        self._ExchangeID: str = exchange_id
        self._ProductID: str = product_id
        self._ProductName: str = product_name
        self._VolumeMultiple: float = volume_multiple
        self._PriceTick: float = price_tick
        self._MaxMarketOrderVolume: int = max_market_order_volume
        self._MaxLimitOrderVolume: int = max_limit_order_volume
        self._Times = []

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: str):
        self._ExchangeID = value

    @property
    def ProductID(self):
        return self._ProductID

    @ProductID.setter
    def ProductID(self, value: str):
        self._ProductID = value

    @property
    def ProductName(self):
        return self._ProductName

    @ProductName.setter
    def ProductName(self, value: str):
        self._ProductName = value

    @property
    def VolumeMultiple(self):
        return self._VolumeMultiple

    @VolumeMultiple.setter
    def VolumeMultiple(self, value: float):
        self._VolumeMultiple = value

    @property
    def PriceTick(self):
        return self._PriceTick

    @PriceTick.setter
    def PriceTick(self, value: float):
        self._PriceTick = value

    @property
    def MaxMarketOrderVolume(self):
        return self._MaxMarketOrderVolume

    @MaxMarketOrderVolume.setter
    def MaxMarketOrderVolume(self, value: int):
        self._MaxMarketOrderVolume = value

    @property
    def MaxLimitOrderVolume(self):
        return self._MaxLimitOrderVolume

    @MaxLimitOrderVolume.setter
    def MaxLimitOrderVolume(self, value: int):
        self._MaxLimitOrderVolume = value

    @property
    def Times(self):
        return self._Times

    @Times.setter
    def Times(self, value):
        self._Times = value
