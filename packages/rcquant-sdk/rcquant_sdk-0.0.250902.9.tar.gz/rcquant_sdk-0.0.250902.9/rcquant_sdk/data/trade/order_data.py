from ...interface import IData
from ...packer.trade.order_data_packer import OrderDataPacker


class OrderData(IData):
    def __init__(self, investor_id: str = '', broker_id: str = '', exchange_id: str = '', product_id: str = '', product_type: int = 0,
                 instrument_id: str = '', order_time: str = '', cancel_time: str = '',
                 trading_day: str = '', insert_date: str = '', update_time: str = '', status_msg: str = '',
                 front_id: int = 0, session_id: int = 0, order_ref: str = '', order_local_no: str = '',
                 order_id: str = '', relative_order_sysid: str = '', broker_order_seq: str = '', price: float = 0.0,
                 stop_price: float = 0.0, volume: int = 0, no_traded_volume: int = 0, status: int = 11,
                 direction: int = 1, open_close_type: int = 0, price_cond: int = 1, time_cond: int = 3, volume_cond: int = 0,
                 hedge_type: int = 0, order_type: int = 0, action_type: int = 0,
                 contingent_cond: int = 0, frozen_margin_price: float = 0.0, frozen_margin: float = 0.0, frozen_commission: float = 0.0,
                 show_volume: int = 0, min_volume: int = 0,
                 price_precision: int = 0, fin_biz_no: str = '', fin_algo_no: str = '', fin_insert_local_time: int = 0,
                 fin_rtn_order_local_time: int = 0, fin_lock_no: str = '',
                 biz_name: str = '', rtn_order_local_time: int = 0):
        super().__init__(OrderDataPacker(self))
        self._InvestorID: str = investor_id
        self._BrokerID: str = broker_id
        self._ExchangeID: str = exchange_id
        self._ProductID: str = product_id
        self._ProductType: int = product_type
        self._InstrumentID: str = instrument_id
        self._OrderTime: str = order_time
        self._CancelTime: str = cancel_time
        self._TradingDay: str = trading_day
        self._InsertDate: str = insert_date
        self._UpdateTime: str = update_time
        self._StatusMsg: str = status_msg
        self._FrontID: int = front_id
        self._SessionID: int = session_id
        self._OrderRef: str = order_ref
        self._OrderLocalNo: str = order_local_no
        self._OrderID: str = order_id
        self._RelativeOrderSysID: str = relative_order_sysid
        self._BrokerOrderSeq: str = broker_order_seq
        self._Price: float = price
        self._StopPrice: float = stop_price
        self._Volume: int = volume
        self._NoTradedVolume: int = no_traded_volume
        self._Status: int = status
        self._Direction: int = direction
        self._OpenCloseType: int = open_close_type
        self._PriceCond: int = price_cond
        self._TimeCond: int = time_cond
        self._VolumeCond: int = volume_cond
        self._HedgeType: int = hedge_type
        self._OrderType: int = order_type
        self._ActionType: int = action_type
        self._ContingentCond: int = contingent_cond
        self._FrozenMarginPrice: float = frozen_margin_price
        self._FrozenMargin: float = frozen_margin
        self._FrozenCommission: float = frozen_commission
        self._ShowVolume: int = show_volume
        self._MinVolume: int = min_volume
        self._PricePrecision: int = price_precision
        self._FinBizNo: str = fin_biz_no
        self._FinAlgoNo: str = fin_algo_no
        self._FinInsertLocalTime: int = fin_insert_local_time
        self._FinRtnOrderLocalTime: int = fin_rtn_order_local_time
        self._FinLockNo: str = fin_lock_no
        self._BizName: str = biz_name
        self._RtnOrderLocalTime: int = rtn_order_local_time

    @property
    def InvestorID(self):
        return self._InvestorID

    @InvestorID.setter
    def InvestorID(self, value: str):
        self._InvestorID = value

    @property
    def BrokerID(self):
        return self._BrokerID

    @BrokerID.setter
    def BrokerID(self, value: str):
        self._BrokerID = value

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
    def ProductType(self):
        return self._ProductType

    @ProductType.setter
    def ProductType(self, value: int):
        self._ProductType = value

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def OrderTime(self):
        return self._OrderTime

    @OrderTime.setter
    def OrderTime(self, value: str):
        self._OrderTime = value

    @property
    def CancelTime(self):
        return self._CancelTime

    @CancelTime.setter
    def CancelTime(self, value: str):
        self._CancelTime = value

    @property
    def TradingDay(self):
        return self._TradingDay

    @TradingDay.setter
    def TradingDay(self, value: str):
        self._TradingDay = value

    @property
    def InsertDate(self):
        return self._InsertDate

    @InsertDate.setter
    def InsertDate(self, value: str):
        self._InsertDate = value

    @property
    def UpdateTime(self):
        return self._UpdateTime

    @UpdateTime.setter
    def UpdateTime(self, value: str):
        self._UpdateTime = value

    @property
    def StatusMsg(self):
        return self._StatusMsg

    @StatusMsg.setter
    def StatusMsg(self, value: str):
        self._StatusMsg = value

    @property
    def FrontID(self):
        return self._FrontID

    @FrontID.setter
    def FrontID(self, value: int):
        self._FrontID = value

    @property
    def SessionID(self):
        return self._SessionID

    @SessionID.setter
    def SessionID(self, value: int):
        self._SessionID = value

    @property
    def OrderRef(self):
        return self._OrderRef

    @OrderRef.setter
    def OrderRef(self, value: str):
        self._OrderRef = value

    @property
    def OrderLocalNo(self):
        return self._OrderLocalNo

    @OrderLocalNo.setter
    def OrderLocalNo(self, value: str):
        self._OrderLocalNo = value

    @property
    def OrderID(self):
        return self._OrderID

    @OrderID.setter
    def OrderID(self, value: str):
        self._OrderID = value

    @property
    def RelativeOrderSysID(self):
        return self._RelativeOrderSysID

    @RelativeOrderSysID.setter
    def RelativeOrderSysID(self, value: str):
        self._RelativeOrderSysID = value

    @property
    def BrokerOrderSeq(self):
        return self._BrokerOrderSeq

    @BrokerOrderSeq.setter
    def BrokerOrderSeq(self, value: str):
        self._BrokerOrderSeq = value

    @property
    def Price(self):
        return self._Price

    @Price.setter
    def Price(self, value: float):
        self._Price = value

    @property
    def StopPrice(self):
        return self._StopPrice

    @StopPrice.setter
    def StopPrice(self, value: float):
        self._StopPrice = value

    @property
    def Volume(self):
        return self._Volume

    @Volume.setter
    def Volume(self, value: int):
        self._Volume = value

    @property
    def NoTradedVolume(self):
        return self._NoTradedVolume

    @NoTradedVolume.setter
    def NoTradedVolume(self, value: int):
        self._NoTradedVolume = value

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, value: int):
        self._Status = value

    @property
    def Direction(self):
        return self._Direction

    @Direction.setter
    def Direction(self, value: int):
        self._Direction = value

    @property
    def OpenCloseType(self):
        return self._OpenCloseType

    @OpenCloseType.setter
    def OpenCloseType(self, value: int):
        self._OpenCloseType = value

    @property
    def PriceCond(self):
        return self._PriceCond

    @PriceCond.setter
    def PriceCond(self, value: int):
        self._PriceCond = value

    @property
    def TimeCond(self):
        return self._TimeCond

    @TimeCond.setter
    def TimeCond(self, value: int):
        self._TimeCond = value

    @property
    def VolumeCond(self):
        return self._VolumeCond

    @VolumeCond.setter
    def VolumeCond(self, value: int):
        self._VolumeCond = value

    @property
    def HedgeType(self):
        return self._HedgeType

    @HedgeType.setter
    def HedgeType(self, value: int):
        self._HedgeType = value

    @property
    def OrderType(self):
        return self._OrderType

    @OrderType.setter
    def OrderType(self, value: int):
        self._OrderType = value

    @property
    def ActionType(self):
        return self._ActionType

    @ActionType.setter
    def ActionType(self, value: int):
        self._ActionType = value

    @property
    def ContingentCond(self):
        return self._ContingentCond

    @ContingentCond.setter
    def ContingentCond(self, value: int):
        self._ContingentCond = value

    @property
    def FrozenMarginPrice(self):
        return self._FrozenMarginPrice

    @FrozenMarginPrice.setter
    def FrozenMarginPrice(self, value: float):
        self._FrozenMarginPrice = value

    @property
    def FrozenMargin(self):
        return self._FrozenMargin

    @FrozenMargin.setter
    def FrozenMargin(self, value: float):
        self._FrozenMargin = value

    @property
    def FrozenCommission(self):
        return self._FrozenCommission

    @FrozenCommission.setter
    def FrozenCommission(self, value: float):
        self._FrozenCommission = value

    @property
    def ShowVolume(self):
        return self._ShowVolume

    @ShowVolume.setter
    def ShowVolume(self, value: int):
        self._ShowVolume = value

    @property
    def MinVolume(self):
        return self._MinVolume

    @MinVolume.setter
    def MinVolume(self, value: int):
        self._MinVolume = value

    @property
    def PricePrecision(self):
        return self._PricePrecision

    @PricePrecision.setter
    def PricePrecision(self, value: int):
        self._PricePrecision = value

    @property
    def FinBizNo(self):
        return self._FinBizNo

    @FinBizNo.setter
    def FinBizNo(self, value: str):
        self._FinBizNo = value

    @property
    def FinAlgoNo(self):
        return self._FinAlgoNo

    @FinAlgoNo.setter
    def FinAlgoNo(self, value: str):
        self._FinAlgoNo = value

    @property
    def FinInsertLocalTime(self):
        return self._FinInsertLocalTime

    @FinInsertLocalTime.setter
    def FinInsertLocalTime(self, value: int):
        self._FinInsertLocalTime = value

    @property
    def FinRtnOrderLocalTime(self):
        return self._FinRtnOrderLocalTime

    @FinRtnOrderLocalTime.setter
    def FinRtnOrderLocalTime(self, value: int):
        self._FinRtnOrderLocalTime = value

    @property
    def FinLockNo(self):
        return self._FinLockNo

    @FinLockNo.setter
    def FinLockNo(self, value: str):
        self._FinLockNo = value

    @property
    def BizName(self):
        return self._BizName

    @BizName.setter
    def BizName(self, value: str):
        self._BizName = value

    @property
    def RtnOrderLocalTime(self):
        return self._RtnOrderLocalTime

    @RtnOrderLocalTime.setter
    def RtnOrderLocalTime(self, value: int):
        self._RtnOrderLocalTime = value
