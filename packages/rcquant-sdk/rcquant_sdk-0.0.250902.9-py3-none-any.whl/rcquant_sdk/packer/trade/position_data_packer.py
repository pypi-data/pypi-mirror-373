from ...interface import IPacker
from typing import Tuple


class PositionDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.InvestorID), str(self._obj.BrokerID), str(self._obj.ExchangeID), str(self._obj.ProductID),
                str(self._obj.InstrumentID), str(self._obj.InstrumentName), str(self._obj.DeliveryMonth), int(self._obj.PositionBuyToday),
                int(self._obj.PositionBuyYesterday), int(self._obj.PositionBuy), int(self._obj.PositionSellToday), int(self._obj.PositionSellYesterday),
                int(self._obj.PositionSell), int(self._obj.PositionTotal), int(self._obj.CanceledOrderCount), int(self._obj.AddOrderCount),
                int(self._obj.SumTradeVolume), int(self._obj.SelfTradeCount), int(self._obj.ErrorOrderCount), int(self._obj.BuyOpenSum),
                int(self._obj.SellOpenSum), int(self._obj.BuySum), int(self._obj.SellSum), float(self._obj.BuySumPrice),
                float(self._obj.SellSumPrice), int(self._obj.UnTradeBuy), int(self._obj.UnTradeSell), int(self._obj.UntradeOpen),
                int(self._obj.UntradeBuyOpen), int(self._obj.UntradeSellOpen), int(self._obj.UntradeClose), int(self._obj.UntradeBuyClose),
                int(self._obj.UntradeSellClose), int(self._obj.BuyYdPosition), int(self._obj.SellYdPosition), float(self._obj.BuyPreSettlementPrice),
                float(self._obj.SellPreSettlementPrice), float(self._obj.LongAvgPrice), float(self._obj.ShortAvgPrice), float(self._obj.FrozenMargin),
                float(self._obj.LongFrozenMargin), float(self._obj.ShortFrozenMargin), float(self._obj.FrozenCommission), float(self._obj.OpenFrozenCommission),
                float(self._obj.CloseFrozenCommission), float(self._obj.CloseTodayFrozenCommission), float(self._obj.CloseProfit), float(self._obj.LongCloseProfit),
                float(self._obj.ShortCloseProfit), float(self._obj.CurrMargin), float(self._obj.LongCurrMargin), float(self._obj.ShortCurrMargin),
                float(self._obj.ShortBaseMargin), float(self._obj.ShortPosMargin), float(self._obj.Commission), float(self._obj.OpenCommission),
                float(self._obj.CloseCommission), float(self._obj.CloseTodayCommission), float(self._obj.PositionProfit), float(self._obj.LongPositionProfit),
                float(self._obj.ShortPositionProfit), float(self._obj.OrderCommission), float(self._obj.RoyaltyPositionProfit), float(self._obj.LongRoyaltyPositionProfit),
                float(self._obj.ShortRoyaltyPositionProfit), int(self._obj.LockBuyOpen), int(self._obj.LockBuyClose), int(self._obj.LockBuyCloseToday),
                int(self._obj.LockSellOpen), int(self._obj.LockSellClose), int(self._obj.LockSellCloseToday))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 71:
            self._obj.InvestorID = t[0]
            self._obj.BrokerID = t[1]
            self._obj.ExchangeID = t[2]
            self._obj.ProductID = t[3]
            self._obj.InstrumentID = t[4]
            self._obj.InstrumentName = t[5]
            self._obj.DeliveryMonth = t[6]
            self._obj.PositionBuyToday = t[7]
            self._obj.PositionBuyYesterday = t[8]
            self._obj.PositionBuy = t[9]
            self._obj.PositionSellToday = t[10]
            self._obj.PositionSellYesterday = t[11]
            self._obj.PositionSell = t[12]
            self._obj.PositionTotal = t[13]
            self._obj.CanceledOrderCount = t[14]
            self._obj.AddOrderCount = t[15]
            self._obj.SumTradeVolume = t[16]
            self._obj.SelfTradeCount = t[17]
            self._obj.ErrorOrderCount = t[18]
            self._obj.BuyOpenSum = t[19]
            self._obj.SellOpenSum = t[20]
            self._obj.BuySum = t[21]
            self._obj.SellSum = t[22]
            self._obj.BuySumPrice = t[23]
            self._obj.SellSumPrice = t[24]
            self._obj.UnTradeBuy = t[25]
            self._obj.UnTradeSell = t[26]
            self._obj.UntradeOpen = t[27]
            self._obj.UntradeBuyOpen = t[28]
            self._obj.UntradeSellOpen = t[29]
            self._obj.UntradeClose = t[30]
            self._obj.UntradeBuyClose = t[31]
            self._obj.UntradeSellClose = t[32]
            self._obj.BuyYdPosition = t[33]
            self._obj.SellYdPosition = t[34]
            self._obj.BuyPreSettlementPrice = t[35]
            self._obj.SellPreSettlementPrice = t[36]
            self._obj.LongAvgPrice = t[37]
            self._obj.ShortAvgPrice = t[38]
            self._obj.FrozenMargin = t[39]
            self._obj.LongFrozenMargin = t[40]
            self._obj.ShortFrozenMargin = t[41]
            self._obj.FrozenCommission = t[42]
            self._obj.OpenFrozenCommission = t[43]
            self._obj.CloseFrozenCommission = t[44]
            self._obj.CloseTodayFrozenCommission = t[45]
            self._obj.CloseProfit = t[46]
            self._obj.LongCloseProfit = t[47]
            self._obj.ShortCloseProfit = t[48]
            self._obj.CurrMargin = t[49]
            self._obj.LongCurrMargin = t[50]
            self._obj.ShortCurrMargin = t[51]
            self._obj.ShortBaseMargin = t[52]
            self._obj.ShortPosMargin = t[53]
            self._obj.Commission = t[54]
            self._obj.OpenCommission = t[55]
            self._obj.CloseCommission = t[56]
            self._obj.CloseTodayCommission = t[57]
            self._obj.PositionProfit = t[58]
            self._obj.LongPositionProfit = t[59]
            self._obj.ShortPositionProfit = t[60]
            self._obj.OrderCommission = t[61]
            self._obj.RoyaltyPositionProfit = t[62]
            self._obj.LongRoyaltyPositionProfit = t[63]
            self._obj.ShortRoyaltyPositionProfit = t[64]
            self._obj.LockBuyOpen = t[65]
            self._obj.LockBuyClose = t[66]
            self._obj.LockBuyCloseToday = t[67]
            self._obj.LockSellOpen = t[68]
            self._obj.LockSellClose = t[69]
            self._obj.LockSellCloseToday = t[70]

            return True
        return False
