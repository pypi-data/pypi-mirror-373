from ...interface import IData
from ...packer.trade.position_data_packer import PositionDataPacker


class PositionData(IData):
    def __init__(self, investor_id: str = '', broker_id: str = '', exchange_id: str = '', product_id: str = '', instrument_id: str = '',
                 instrument_name: str = '', delivery_month: str = '', position_buy_today: int = 0, position_buy_yesterday: int = 0, position_buy: int = 0,
                 position_sell_today: int = 0, position_sell_yesterday: int = 0, position_sell: int = 0, position_total: int = 0, cancele_dorder_count: int = 0,
                 add_order_count: int = 0, sum_trade_volume: int = 0, self_trade_count: int = 0, error_order_count: int = 0,
                 buy_open_sum: int = 0, sell_open_sum: int = 0, buy_sum: int = 0, sell_sum: int = 0, buy_sum_price: float = 0, sell_sum_price: float = 0,
                 untrade_buy: int = 0, untrade_sell: int = 0, untrade_open: int = 0, untrade_buy_open: int = 0, untrade_sell_open: int = 0,
                 untrade_close: int = 0, untrade_buy_close: int = 0, untrade_sell_close: int = 0, buy_ydposition: int = 0, sell_ydposition: int = 0,
                 buy_pre_settlement_price: float = 0.0, sell_pre_settlement_price: float = 0.0, long_avg_price: float = 0.0, short_avg_price: float = 0.0,
                 frozen_margin: float = 0.0, long_frozen_margin: float = 0.0, short_frozen_margin: float = 0.0, frozen_commission: float = 0.0,
                 open_frozen_commission: float = 0.0, close_frozen_commission: float = 0.0, close_today_frozen_commission: float = 0.0,
                 close_profit: float = 0.0, long_close_profit: float = 0.0, short_close_profit: float = 0.0, curr_margin: float = 0.0,
                 long_curr_margin: float = 0.0, short_curr_margin: float = 0.0, short_base_margin: float = 0.0, short_pos_margin: float = 0.0,
                 commission: float = 0.0, open_commission: float = 0.0, close_commission: float = 0.0, close_today_commission: float = 0.0,
                 position_profit: float = 0.0, long_position_profit: float = 0.0, short_position_profit: float = 0.0, order_commission: float = 0.0,
                 royalty_position_profit: float = 0.0, long_royalty_position_profit: float = 0.0, short_royalty_position_profit: float = 0.0,
                 lock_buy_open: int = 0, lock_buy_close: int = 0, lock_buy_close_today: int = 0,
                 lock_sell_open: int = 0, lock_sell_close: int = 0, lock_sell_close_today: int = 0):
        super().__init__(PositionDataPacker(self))
        self._InvestorID: str = investor_id
        self._BrokerID: str = broker_id
        self._ExchangeID: str = exchange_id
        self._ProductID: str = product_id
        self._InstrumentID: str = instrument_id
        self._InstrumentName: str = instrument_name
        self._DeliveryMonth: str = delivery_month
        self._PositionBuyToday: int = position_buy_today
        self._PositionBuyYesterday: int = position_buy_yesterday
        self._PositionBuy: int = position_buy
        self._PositionSellToday: int = position_sell_today
        self._PositionSellYesterday: int = position_sell_yesterday
        self._PositionSell: int = position_sell
        self._PositionTotal: int = position_total
        self._CanceledOrderCount: int = cancele_dorder_count
        self._AddOrderCount: int = add_order_count
        self._SumTradeVolume: int = sum_trade_volume
        self._SelfTradeCount: int = self_trade_count
        self._ErrorOrderCount: int = error_order_count
        self._BuyOpenSum: int = buy_open_sum
        self._SellOpenSum: int = sell_open_sum
        self._BuySum: int = buy_sum
        self._SellSum: int = sell_sum
        self._BuySumPrice: float = buy_sum_price
        self._SellSumPrice: float = sell_sum_price
        self._UnTradeBuy: int = untrade_buy
        self._UnTradeSell: int = untrade_sell
        self._UntradeOpen: int = untrade_open
        self._UntradeBuyOpen: int = untrade_buy_open
        self._UntradeSellOpen: int = untrade_sell_open
        self._UntradeClose: int = untrade_close
        self._UntradeBuyClose: int = untrade_buy_close
        self._UntradeSellClose: int = untrade_sell_close
        self._BuyYdPosition: int = buy_ydposition
        self._SellYdPosition: int = sell_ydposition
        self._BuyPreSettlementPrice: float = buy_pre_settlement_price
        self._SellPreSettlementPrice: float = sell_pre_settlement_price
        self._LongAvgPrice: float = long_avg_price
        self._ShortAvgPrice: float = short_avg_price
        self._FrozenMargin: float = frozen_margin
        self._LongFrozenMargin: float = long_frozen_margin
        self._ShortFrozenMargin: float = short_frozen_margin
        self._FrozenCommission: float = frozen_commission
        self._OpenFrozenCommission: float = open_frozen_commission
        self._CloseFrozenCommission: float = close_frozen_commission
        self._CloseTodayFrozenCommission: float = close_today_frozen_commission
        self._CloseProfit: float = close_profit
        self._LongCloseProfit: float = long_close_profit
        self._ShortCloseProfit: float = short_close_profit
        self._CurrMargin: float = curr_margin
        self._LongCurrMargin: float = long_curr_margin
        self._ShortCurrMargin: float = short_curr_margin
        self._ShortBaseMargin: float = short_base_margin
        self._ShortPosMargin: float = short_pos_margin
        self._Commission: float = commission
        self._OpenCommission: float = open_commission
        self._CloseCommission: float = close_commission
        self._CloseTodayCommission: float = close_today_commission
        self._PositionProfit: float = position_profit
        self._LongPositionProfit: float = long_position_profit
        self._ShortPositionProfit: float = short_position_profit
        self._OrderCommission: float = order_commission
        self._RoyaltyPositionProfit: float = royalty_position_profit
        self._LongRoyaltyPositionProfit: float = long_royalty_position_profit
        self._ShortRoyaltyPositionProfit: float = short_royalty_position_profit
        self._LockBuyOpen: int = lock_buy_open
        self._LockBuyClose: int = lock_buy_close
        self._LockBuyCloseToday: int = lock_buy_close_today
        self._LockSellOpen: int = lock_sell_open
        self._LockSellClose: int = lock_sell_close
        self._LockSellCloseToday: int = lock_sell_close_today

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
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def InstrumentName(self):
        return self._InstrumentName

    @InstrumentName.setter
    def InstrumentName(self, value: str):
        self._InstrumentName = value

    @property
    def DeliveryMonth(self):
        return self._DeliveryMonth

    @DeliveryMonth.setter
    def DeliveryMonth(self, value: str):
        self._DeliveryMonth = value

    @property
    def PositionBuyToday(self):
        return self._PositionBuyToday

    @PositionBuyToday.setter
    def PositionBuyToday(self, value: int):
        self._PositionBuyToday = value

    @property
    def PositionBuyYesterday(self):
        return self._PositionBuyYesterday

    @PositionBuyYesterday.setter
    def PositionBuyYesterday(self, value: int):
        self._PositionBuyYesterday = value

    @property
    def PositionBuy(self):
        return self._PositionBuy

    @PositionBuy.setter
    def PositionBuy(self, value: int):
        self._PositionBuy = value

    @property
    def PositionSellToday(self):
        return self._PositionSellToday

    @PositionSellToday.setter
    def PositionSellToday(self, value: int):
        self._PositionSellToday = value

    @property
    def PositionSellYesterday(self):
        return self._PositionSellYesterday

    @PositionSellYesterday.setter
    def PositionSellYesterday(self, value: int):
        self._PositionSellYesterday = value

    @property
    def PositionSell(self):
        return self._PositionSell

    @PositionSell.setter
    def PositionSell(self, value: int):
        self._PositionSell = value

    @property
    def PositionTotal(self):
        return self._PositionTotal

    @PositionTotal.setter
    def PositionTotal(self, value: int):
        self._PositionTotal = value

    @property
    def CanceledOrderCount(self):
        return self._CanceledOrderCount

    @CanceledOrderCount.setter
    def CanceledOrderCount(self, value: int):
        self._CanceledOrderCount = value

    @property
    def AddOrderCount(self):
        return self._AddOrderCount

    @AddOrderCount.setter
    def AddOrderCount(self, value: int):
        self._AddOrderCount = value

    @property
    def SumTradeVolume(self):
        return self._SumTradeVolume

    @SumTradeVolume.setter
    def SumTradeVolume(self, value: int):
        self._SumTradeVolume = value

    @property
    def SelfTradeCount(self):
        return self._SelfTradeCount

    @SelfTradeCount.setter
    def SelfTradeCount(self, value: int):
        self._SelfTradeCount = value

    @property
    def ErrorOrderCount(self):
        return self._ErrorOrderCount

    @ErrorOrderCount.setter
    def ErrorOrderCount(self, value: int):
        self._ErrorOrderCount = value

    @property
    def BuyOpenSum(self):
        return self._BuyOpenSum

    @BuyOpenSum.setter
    def BuyOpenSum(self, value: int):
        self._BuyOpenSum = value

    @property
    def SellOpenSum(self):
        return self._SellOpenSum

    @SellOpenSum.setter
    def SellOpenSum(self, value: int):
        self._SellOpenSum = value

    @property
    def BuySum(self):
        return self._BuySum

    @BuySum.setter
    def BuySum(self, value: int):
        self._BuySum = value

    @property
    def SellSum(self):
        return self._SellSum

    @SellSum.setter
    def SellSum(self, value: int):
        self._SellSum = value

    @property
    def BuySumPrice(self):
        return self._BuySumPrice

    @BuySumPrice.setter
    def BuySumPrice(self, value: float):
        self._BuySumPrice = value

    @property
    def SellSumPrice(self):
        return self._SellSumPrice

    @SellSumPrice.setter
    def SellSumPrice(self, value: float):
        self._SellSumPrice = value

    @property
    def UnTradeBuy(self):
        return self._UnTradeBuy

    @UnTradeBuy.setter
    def UnTradeBuy(self, value: int):
        self._UnTradeBuy = value

    @property
    def UnTradeSell(self):
        return self._UnTradeSell

    @UnTradeSell.setter
    def UnTradeSell(self, value: int):
        self._UnTradeSell = value

    @property
    def UntradeOpen(self):
        return self._UntradeOpen

    @UntradeOpen.setter
    def UntradeOpen(self, value: int):
        self._UntradeOpen = value

    @property
    def UntradeBuyOpen(self):
        return self._UntradeBuyOpen

    @UntradeBuyOpen.setter
    def UntradeBuyOpen(self, value: int):
        self._UntradeBuyOpen = value

    @property
    def UntradeSellOpen(self):
        return self._UntradeSellOpen

    @UntradeSellOpen.setter
    def UntradeSellOpen(self, value: int):
        self._UntradeSellOpen = value

    @property
    def UntradeClose(self):
        return self._UntradeClose

    @UntradeClose.setter
    def UntradeClose(self, value: int):
        self._UntradeClose = value

    @property
    def UntradeBuyClose(self):
        return self._UntradeBuyClose

    @UntradeBuyClose.setter
    def UntradeBuyClose(self, value: int):
        self._UntradeBuyClose = value

    @property
    def UntradeSellClose(self):
        return self._UntradeSellClose

    @UntradeSellClose.setter
    def UntradeSellClose(self, value: int):
        self._UntradeSellClose = value

    @property
    def BuyYdPosition(self):
        return self._BuyYdPosition

    @BuyYdPosition.setter
    def BuyYdPosition(self, value: int):
        self._BuyYdPosition = value

    @property
    def SellYdPosition(self):
        return self._SellYdPosition

    @SellYdPosition.setter
    def SellYdPosition(self, value: int):
        self._SellYdPosition = value

    @property
    def BuyPreSettlementPrice(self):
        return self._BuyPreSettlementPrice

    @BuyPreSettlementPrice.setter
    def BuyPreSettlementPrice(self, value: float):
        self._BuyPreSettlementPrice = value

    @property
    def SellPreSettlementPrice(self):
        return self._SellPreSettlementPrice

    @SellPreSettlementPrice.setter
    def SellPreSettlementPrice(self, value: float):
        self._SellPreSettlementPrice = value

    @property
    def LongAvgPrice(self):
        return self._LongAvgPrice

    @LongAvgPrice.setter
    def LongAvgPrice(self, value: float):
        self._LongAvgPrice = value

    @property
    def ShortAvgPrice(self):
        return self._ShortAvgPrice

    @ShortAvgPrice.setter
    def ShortAvgPrice(self, value: float):
        self._ShortAvgPrice = value

    @property
    def FrozenMargin(self):
        return self._FrozenMargin

    @FrozenMargin.setter
    def FrozenMargin(self, value: float):
        self._FrozenMargin = value

    @property
    def LongFrozenMargin(self):
        return self._LongFrozenMargin

    @LongFrozenMargin.setter
    def LongFrozenMargin(self, value: float):
        self._LongFrozenMargin = value

    @property
    def ShortFrozenMargin(self):
        return self._ShortFrozenMargin

    @ShortFrozenMargin.setter
    def ShortFrozenMargin(self, value: float):
        self._ShortFrozenMargin = value

    @property
    def FrozenCommission(self):
        return self._FrozenCommission

    @FrozenCommission.setter
    def FrozenCommission(self, value: float):
        self._FrozenCommission = value

    @property
    def OpenFrozenCommission(self):
        return self._OpenFrozenCommission

    @OpenFrozenCommission.setter
    def OpenFrozenCommission(self, value: float):
        self._OpenFrozenCommission = value

    @property
    def CloseFrozenCommission(self):
        return self._CloseFrozenCommission

    @CloseFrozenCommission.setter
    def CloseFrozenCommission(self, value: float):
        self._CloseFrozenCommission = value

    @property
    def CloseTodayFrozenCommission(self):
        return self._CloseTodayFrozenCommission

    @CloseTodayFrozenCommission.setter
    def CloseTodayFrozenCommission(self, value: float):
        self._CloseTodayFrozenCommission = value

    @property
    def CloseProfit(self):
        return self._CloseProfit

    @CloseProfit.setter
    def CloseProfit(self, value: float):
        self._CloseProfit = value

    @property
    def LongCloseProfit(self):
        return self._LongCloseProfit

    @LongCloseProfit.setter
    def LongCloseProfit(self, value: float):
        self._LongCloseProfit = value

    @property
    def ShortCloseProfit(self):
        return self._ShortCloseProfit

    @ShortCloseProfit.setter
    def ShortCloseProfit(self, value: float):
        self._ShortCloseProfit = value

    @property
    def CurrMargin(self):
        return self._CurrMargin

    @CurrMargin.setter
    def CurrMargin(self, value: float):
        self._CurrMargin = value

    @property
    def LongCurrMargin(self):
        return self._LongCurrMargin

    @LongCurrMargin.setter
    def LongCurrMargin(self, value: float):
        self._LongCurrMargin = value

    @property
    def ShortCurrMargin(self):
        return self._ShortCurrMargin

    @ShortCurrMargin.setter
    def ShortCurrMargin(self, value: float):
        self._ShortCurrMargin = value

    @property
    def ShortBaseMargin(self):
        return self._ShortBaseMargin

    @ShortBaseMargin.setter
    def ShortBaseMargin(self, value: float):
        self._ShortBaseMargin = value

    @property
    def ShortPosMargin(self):
        return self._ShortPosMargin

    @ShortPosMargin.setter
    def ShortPosMargin(self, value: float):
        self._ShortPosMargin = value

    @property
    def Commission(self):
        return self._Commission

    @Commission.setter
    def Commission(self, value: float):
        self._Commission = value

    @property
    def OpenCommission(self):
        return self._OpenCommission

    @OpenCommission.setter
    def OpenCommission(self, value: float):
        self._OpenCommission = value

    @property
    def CloseCommission(self):
        return self._CloseCommission

    @CloseCommission.setter
    def CloseCommission(self, value: float):
        self._CloseCommission = value

    @property
    def CloseTodayCommission(self):
        return self._CloseTodayCommission

    @CloseTodayCommission.setter
    def CloseTodayCommission(self, value: float):
        self._CloseTodayCommission = value

    @property
    def PositionProfit(self):
        return self._PositionProfit

    @PositionProfit.setter
    def PositionProfit(self, value: float):
        self._PositionProfit = value

    @property
    def LongPositionProfit(self):
        return self._LongPositionProfit

    @LongPositionProfit.setter
    def LongPositionProfit(self, value: float):
        self._LongPositionProfit = value

    @property
    def ShortPositionProfit(self):
        return self._ShortPositionProfit

    @ShortPositionProfit.setter
    def ShortPositionProfit(self, value: float):
        self._ShortPositionProfit = value

    @property
    def OrderCommission(self):
        return self._OrderCommission

    @OrderCommission.setter
    def OrderCommission(self, value: float):
        self._OrderCommission = value

    @property
    def RoyaltyPositionProfit(self):
        return self._RoyaltyPositionProfit

    @RoyaltyPositionProfit.setter
    def RoyaltyPositionProfit(self, value: float):
        self._RoyaltyPositionProfit = value

    @property
    def LongRoyaltyPositionProfit(self):
        return self._LongRoyaltyPositionProfit

    @LongRoyaltyPositionProfit.setter
    def LongRoyaltyPositionProfit(self, value: float):
        self._LongRoyaltyPositionProfit = value

    @property
    def ShortRoyaltyPositionProfit(self):
        return self._ShortRoyaltyPositionProfit

    @ShortRoyaltyPositionProfit.setter
    def ShortRoyaltyPositionProfit(self, value: float):
        self._ShortRoyaltyPositionProfit = value

    @property
    def LockBuyOpen(self):
        return self._LockBuyOpen

    @LockBuyOpen.setter
    def LockBuyOpen(self, value: int):
        self._LockBuyOpen = value

    @property
    def LockBuyClose(self):
        return self._LockBuyClose

    @LockBuyClose.setter
    def LockBuyClose(self, value: int):
        self._LockBuyClose = value

    @property
    def LockBuyCloseToday(self):
        return self._LockBuyCloseToday

    @LockBuyCloseToday.setter
    def LockBuyCloseToday(self, value: int):
        self._LockBuyCloseToday = value

    @property
    def LockSellOpen(self):
        return self._LockSellOpen

    @LockSellOpen.setter
    def LockSellOpen(self, value: int):
        self._LockSellOpen = value

    @property
    def LockSellClose(self):
        return self._LockSellClose

    @LockSellClose.setter
    def LockSellClose(self, value: int):
        self._LockSellClose = value

    @property
    def LockSellCloseToday(self):
        return self._LockSellCloseToday

    @LockSellCloseToday.setter
    def LockSellCloseToday(self, value: int):
        self._LockSellCloseToday = value
