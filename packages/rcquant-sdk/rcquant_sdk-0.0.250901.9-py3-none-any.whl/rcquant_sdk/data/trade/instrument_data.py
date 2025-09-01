from ...interface import IData
from ...packer.trade.instrument_data_packer import InstrumentDataPacker


class InstrumentData(IData):
    def __init__(self, instrumentid: str = '', exchangeid: str = '', instrumentname: str = '', unicode: str = '', productid: str = '', producttype: int = 1, deliveryyear: str = '', deliverymonth: str = '', createdate: str = '', opendate: str = '', expiredate: str = '', startdelivdate: str = '', enddelivdate: str = '', maxmarketordervolume: int = 0, minmarketordervolume: int = 0, maxlimitordervolume: int = 0, minlimitordervolume: int = 0, volumemultiple: int = 0,
                 pricetick: float = 0.0, priceprecision: int = 0, istrading: bool = False, maxmarginsidealgorithm: bool = False, productgroupid: str = '', strikeprice: float = 0.0, optionstype: int = 0, underlyinginstrid: str = "", underlyingmultiple: float = 0.0, combinationtype: int = 0, strikemodetype: int = 0, objectprice: float = 0.0, objectmarginratiobymoney: float = 0.0, objectmarginratiobyvolume: float = 0.0, ensureratio1: float = 0.0, ensureratio2: float = 0.0, isclosetoday: bool = False):
        super().__init__(InstrumentDataPacker(self))
        self._InstrumentID: str = instrumentid
        self._ExchangeID: str = exchangeid
        self._InstrumentName: str = instrumentname
        self._UniCode: str = unicode
        self._ProductID: str = productid
        self._ProductType: int = producttype
        self._DeliveryYear: str = deliveryyear
        self._DeliveryMonth: str = deliverymonth
        self._CreateDate: str = createdate
        self._OpenDate: str = opendate
        self._ExpireDate: str = expiredate
        self._StartDelivDate: str = startdelivdate
        self._EndDelivDate: str = enddelivdate
        self._MaxMarketOrderVolume: int = maxmarketordervolume
        self._MinMarketOrderVolume: int = minmarketordervolume
        self._MaxLimitOrderVolume: int = maxlimitordervolume
        self._MinLimitOrderVolume: int = minlimitordervolume
        self._VolumeMultiple: int = volumemultiple
        self._PriceTick: float = pricetick
        self._PricePrecision: int = priceprecision
        self._IsTrading: bool = istrading
        self._MaxMarginSideAlgorithm: bool = maxmarginsidealgorithm
        self._ProductGroupID: str = productgroupid
        self._StrikePrice: float = strikeprice
        self._OptionsType: int = optionstype
        self._UnderlyingInstrID: str = underlyinginstrid
        self._UnderlyingMultiple: float = underlyingmultiple
        self._CombinationType: int = combinationtype
        self._StrikeModeType: int = strikemodetype
        self._ObjectPrice: float = objectprice
        self._ObjectMarginRatioByMoney: float = objectmarginratiobymoney
        self._ObjectMarginRatioByVolume: float = objectmarginratiobyvolume
        self._EnsureRatio1: float = ensureratio1
        self._EnsureRatio2: float = ensureratio2
        self._IsCloseToday: bool = isclosetoday
        self._Times = []

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: str):
        self._ExchangeID = value

    @property
    def InstrumentName(self):
        return self._InstrumentName

    @InstrumentName.setter
    def InstrumentName(self, value: str):
        self._InstrumentName = value

    @property
    def UniCode(self):
        return self._UniCode

    @UniCode.setter
    def UniCode(self, value: str):
        self._UniCode = value

    @property
    def ProductID(self):
        return self._ProductID

    @ProductID.setter
    def ProductID(self, value: str):
        self._ProductID = value

    @property
    def ProductType(self):
        return self._ProductType

    @ProductType.setter
    def ProductType(self, value: int):
        self._ProductType = value

    @property
    def DeliveryYear(self):
        return self._DeliveryYear

    @DeliveryYear.setter
    def DeliveryYear(self, value: str):
        self._DeliveryYear = value

    @property
    def DeliveryMonth(self):
        return self._DeliveryMonth

    @DeliveryMonth.setter
    def DeliveryMonth(self, value: str):
        self._DeliveryMonth = value

    @property
    def CreateDate(self):
        return self._CreateDate

    @CreateDate.setter
    def CreateDate(self, value: str):
        self._CreateDate = value

    @property
    def OpenDate(self):
        return self._OpenDate

    @OpenDate.setter
    def OpenDate(self, value: str):
        self._OpenDate = value

    @property
    def ExpireDate(self):
        return self._ExpireDate

    @ExpireDate.setter
    def ExpireDate(self, value: str):
        self._ExpireDate = value

    @property
    def StartDelivDate(self):
        return self._StartDelivDate

    @StartDelivDate.setter
    def StartDelivDate(self, value: str):
        self._StartDelivDate = value

    @property
    def EndDelivDate(self):
        return self._EndDelivDate

    @EndDelivDate.setter
    def EndDelivDate(self, value: str):
        self._EndDelivDate = value

    @property
    def MaxMarketOrderVolume(self):
        return self._MaxMarketOrderVolume

    @MaxMarketOrderVolume.setter
    def MaxMarketOrderVolume(self, value: int):
        self._MaxMarketOrderVolume = value

    @property
    def MinMarketOrderVolume(self):
        return self._MinMarketOrderVolume

    @MinMarketOrderVolume.setter
    def MinMarketOrderVolume(self, value: int):
        self._MinMarketOrderVolume = value

    @property
    def MaxLimitOrderVolume(self):
        return self._MaxLimitOrderVolume

    @MaxLimitOrderVolume.setter
    def MaxLimitOrderVolume(self, value: int):
        self._MaxLimitOrderVolume = value

    @property
    def MinLimitOrderVolume(self):
        return self._MinLimitOrderVolume

    @MinLimitOrderVolume.setter
    def MinLimitOrderVolume(self, value: int):
        self._MinLimitOrderVolume = value

    @property
    def VolumeMultiple(self):
        return self._VolumeMultiple

    @VolumeMultiple.setter
    def VolumeMultiple(self, value: int):
        self._VolumeMultiple = value

    @property
    def PriceTick(self):
        return self._PriceTick

    @PriceTick.setter
    def PriceTick(self, value: float):
        self._PriceTick = value

    @property
    def PricePrecision(self):
        return self._PricePrecision

    @PricePrecision.setter
    def PricePrecision(self, value: int):
        self._PricePrecision = value

    @property
    def IsTrading(self):
        return self._IsTrading

    @IsTrading.setter
    def IsTrading(self, value: bool):
        self._IsTrading = value

    @property
    def MaxMarginSideAlgorithm(self):
        return self._MaxMarginSideAlgorithm

    @MaxMarginSideAlgorithm.setter
    def MaxMarginSideAlgorithm(self, value: bool):
        self._MaxMarginSideAlgorithm = value

    @property
    def ProductGroupID(self):
        return self._ProductGroupID

    @ProductGroupID.setter
    def ProductGroupID(self, value: str):
        self._ProductGroupID = value

    @property
    def StrikePrice(self):
        return self._StrikePrice

    @StrikePrice.setter
    def StrikePrice(self, value: float):
        self._StrikePrice = value

    @property
    def OptionsType(self):
        return self._OptionsType

    @OptionsType.setter
    def OptionsType(self, value: int):
        self._OptionsType = value

    @property
    def UnderlyingInstrID(self):
        return self._UnderlyingInstrID

    @UnderlyingInstrID.setter
    def UnderlyingInstrID(self, value: str):
        self._UnderlyingInstrID = value

    @property
    def UnderlyingMultiple(self):
        return self._UnderlyingMultiple

    @UnderlyingMultiple.setter
    def UnderlyingMultiple(self, value: float):
        self._UnderlyingMultiple = value

    @property
    def CombinationType(self):
        return self._CombinationType

    @CombinationType.setter
    def CombinationType(self, value: int):
        self._CombinationType = value

    @property
    def StrikeModeType(self):
        return self._StrikeModeType

    @StrikeModeType.setter
    def StrikeModeType(self, value: int):
        self._StrikeModeType = value

    @property
    def ObjectPrice(self):
        return self._ObjectPrice

    @ObjectPrice.setter
    def ObjectPrice(self, value: float):
        self._ObjectPrice = value

    @property
    def ObjectMarginRatioByMoney(self):
        return self._ObjectMarginRatioByMoney

    @ObjectMarginRatioByMoney.setter
    def ObjectMarginRatioByMoney(self, value: float):
        self._ObjectMarginRatioByMoney = value

    @property
    def ObjectMarginRatioByVolume(self):
        return self._ObjectMarginRatioByVolume

    @ObjectMarginRatioByVolume.setter
    def ObjectMarginRatioByVolume(self, value: float):
        self._ObjectMarginRatioByVolume = value

    @property
    def EnsureRatio1(self):
        return self._EnsureRatio1

    @EnsureRatio1.setter
    def EnsureRatio1(self, value: float):
        self._EnsureRatio1 = value

    @property
    def EnsureRatio2(self):
        return self._EnsureRatio2

    @EnsureRatio2.setter
    def EnsureRatio2(self, value: float):
        self._EnsureRatio2 = value

    @property
    def IsCloseToday(self):
        return self._IsCloseToday

    @IsCloseToday.setter
    def IsCloseToday(self, value: bool):
        self._IsCloseToday = value

    @property
    def Times(self):
        return self._Times

    @Times.setter
    def Times(self, value):
        self._Times = value
