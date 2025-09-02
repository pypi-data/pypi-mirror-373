from ...interface import IPacker
from typing import Tuple


class AccountDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.AccountID), float(self._obj.PreBalance), float(self._obj.PreCredit), float(self._obj.PreMortgage),
                float(self._obj.Mortgage), float(self._obj.Withdraw), float(self._obj.Deposit), float(self._obj.StaticBalance),
                float(self._obj.CloseProfit), float(self._obj.PositionProfit), float(self._obj.Commission), float(self._obj.Balance),
                float(self._obj.CurrMargin), float(self._obj.MaintenanceMargin), float(self._obj.DeliveryMargin), float(self._obj.FrozenMargin),
                float(self._obj.FrozenCommission), float(self._obj.FrozenCash), float(self._obj.CreditLimit), float(self._obj.Available),
                float(self._obj.RoyaltyIn), float(self._obj.RoyaltyOut), float(self._obj.FrozenRoyalty), float(self._obj.OrderCommission),
                float(self._obj.RoyaltyPositionProfit), float(self._obj.MarketBalance), float(self._obj.MarketRiskDegree), float(self._obj.RiskDegree),
                str(self._obj.CurrencyNo))

    def tuple_to_obj(self, t):
        if len(t) >= 29:
            self._obj.AccountID = t[0]
            self._obj.PreBalance = t[1]
            self._obj.PreCredit = t[2]
            self._obj.PreMortgage = t[3]
            self._obj.Mortgage = t[4]
            self._obj.Withdraw = t[5]
            self._obj.Deposit = t[6]
            self._obj.StaticBalance = t[7]
            self._obj.CloseProfit = t[8]
            self._obj.PositionProfit = t[9]
            self._obj.Commission = t[10]
            self._obj.Balance = t[11]
            self._obj.CurrMargin = t[12]
            self._obj.MaintenanceMargin = t[13]
            self._obj.DeliveryMargin = t[14]
            self._obj.FrozenMargin = t[15]
            self._obj.FrozenCommission = t[16]
            self._obj.FrozenCash = t[17]
            self._obj.CreditLimit = t[18]
            self._obj.Available = t[19]
            self._obj.RoyaltyIn = t[20]
            self._obj.RoyaltyOut = t[21]
            self._obj.FrozenRoyalty = t[22]
            self._obj.OrderCommission = t[23]
            self._obj.RoyaltyPositionProfit = t[24]
            self._obj.MarketBalance = t[25]
            self._obj.MarketRiskDegree = t[26]
            self._obj.RiskDegree = t[27]
            self._obj.CurrencyNo = t[28]

            return True
        return False
