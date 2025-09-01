from ...interface import IData
from ...packer.trade.account_data_packer import AccountDataPacker


class AccountData(IData):
    def __init__(self, account_id: str = '', pre_balance: float = 0.0, pre_credit: float = 0.0, pre_mortgage: float = 0.0, mortgage: float = 0.0, withdraw: float = 0.0, deposit: float = 0.0,
                 static_balance: float = 0, close_profit: float = 0.0, position_profit: float = 0.0, commission: float = 0.0, balance: float = 0.0, curr_margin: float = 0.0,
                 maintenance_margin: float = 0.0, delivery_margin: float = 0.0, frozen_margin: float = 0.0, frozen_commission: float = 0.0, frozen_cash: float = 0.0, creditlimit: float = 0.0,
                 available: float = 0.0, royalty_in: float = 0.0, royalty_out: float = 0.0, frozen_royalty: float = 0.0, order_commission: float = 0.0, royalty_position_profit: float = 0.0,
                 market_balance: float = 0.0, market_risk_degree: float = 0.0, risk_degree: float = 0.0, currency_no: str = ''):
        super().__init__(AccountDataPacker(self))
        self._AccountID: str = account_id
        self._PreBalance: float = pre_balance
        self._PreCredit: float = pre_credit
        self._PreMortgage: float = pre_mortgage
        self._Mortgage: float = mortgage
        self._Withdraw: float = withdraw
        self._Deposit: float = deposit
        self._StaticBalance: float = static_balance
        self._CloseProfit: float = close_profit
        self._PositionProfit: float = position_profit
        self._Commission: float = commission
        self._Balance: float = balance
        self._CurrMargin: float = curr_margin
        self._MaintenanceMargin: float = maintenance_margin
        self._DeliveryMargin: float = delivery_margin
        self._FrozenMargin: float = frozen_margin
        self._FrozenCommission: float = frozen_commission
        self._FrozenCash: float = frozen_cash
        self._CreditLimit: float = creditlimit
        self._Available: float = available
        self._RoyaltyIn: float = royalty_in
        self._RoyaltyOut: float = royalty_out
        self._FrozenRoyalty: float = frozen_royalty
        self._OrderCommission: float = order_commission
        self._RoyaltyPositionProfit: float = royalty_position_profit
        self._MarketBalance: float = market_balance
        self._MarketRiskDegree: float = market_risk_degree
        self._RiskDegree: float = risk_degree
        self._CurrencyNo: str = currency_no

    @property
    def AccountID(self):
        return self._AccountID

    @AccountID.setter
    def AccountID(self, value: str):
        self._AccountID = value

    @property
    def PreBalance(self):
        return self._PreBalance

    @PreBalance.setter
    def PreBalance(self, value: float):
        self._PreBalance = value

    @property
    def PreCredit(self):
        return self._PreCredit

    @PreCredit.setter
    def PreCredit(self, value: float):
        self._PreCredit = value

    @property
    def PreMortgage(self):
        return self._PreMortgage

    @PreMortgage.setter
    def PreMortgage(self, value: float):
        self._PreMortgage = value

    @property
    def Mortgage(self):
        return self._Mortgage

    @Mortgage.setter
    def Mortgage(self, value: float):
        self._Mortgage = value

    @property
    def Withdraw(self):
        return self._Withdraw

    @Withdraw.setter
    def Withdraw(self, value: float):
        self._Withdraw = value

    @property
    def Deposit(self):
        return self._Deposit

    @Deposit.setter
    def Deposit(self, value: float):
        self._Deposit = value

    @property
    def StaticBalance(self):
        return self._StaticBalance

    @StaticBalance.setter
    def StaticBalance(self, value: float):
        self._StaticBalance = value

    @property
    def CloseProfit(self):
        return self._CloseProfit

    @CloseProfit.setter
    def CloseProfit(self, value: float):
        self._CloseProfit = value

    @property
    def PositionProfit(self):
        return self._PositionProfit

    @PositionProfit.setter
    def PositionProfit(self, value: float):
        self._PositionProfit = value

    @property
    def Commission(self):
        return self._Commission

    @Commission.setter
    def Commission(self, value: float):
        self._Commission = value

    @property
    def Balance(self):
        return self._Balance

    @Balance.setter
    def Balance(self, value: float):
        self._Balance = value

    @property
    def CurrMargin(self):
        return self._CurrMargin

    @CurrMargin.setter
    def CurrMargin(self, value: float):
        self._CurrMargin = value

    @property
    def MaintenanceMargin(self):
        return self._MaintenanceMargin

    @MaintenanceMargin.setter
    def MaintenanceMargin(self, value: float):
        self._MaintenanceMargin = value

    @property
    def DeliveryMargin(self):
        return self._DeliveryMargin

    @DeliveryMargin.setter
    def DeliveryMargin(self, value: float):
        self._DeliveryMargin = value

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
    def FrozenCash(self):
        return self._FrozenCash

    @FrozenCash.setter
    def FrozenCash(self, value: float):
        self._FrozenCash = value

    @property
    def CreditLimit(self):
        return self._CreditLimit

    @CreditLimit.setter
    def CreditLimit(self, value: float):
        self._CreditLimit = value

    @property
    def Available(self):
        return self._Available

    @Available.setter
    def Available(self, value: float):
        self._Available = value

    @property
    def RoyaltyIn(self):
        return self._RoyaltyIn

    @RoyaltyIn.setter
    def RoyaltyIn(self, value: float):
        self._RoyaltyIn = value

    @property
    def RoyaltyOut(self):
        return self._RoyaltyOut

    @RoyaltyOut.setter
    def RoyaltyOut(self, value: float):
        self._RoyaltyOut = value

    @property
    def FrozenRoyalty(self):
        return self._FrozenRoyalty

    @FrozenRoyalty.setter
    def FrozenRoyalty(self, value: float):
        self._FrozenRoyalty = value

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
    def MarketBalance(self):
        return self._MarketBalance

    @MarketBalance.setter
    def MarketBalance(self, value: float):
        self._MarketBalance = value

    @property
    def MarketRiskDegree(self):
        return self._MarketRiskDegree

    @MarketRiskDegree.setter
    def MarketRiskDegree(self, value: float):
        self._MarketRiskDegree = value

    @property
    def RiskDegree(self):
        return self._RiskDegree

    @RiskDegree.setter
    def RiskDegree(self, value: float):
        self._RiskDegree = value

    @property
    def CurrencyNo(self):
        return self._CurrencyNo

    @CurrencyNo.setter
    def CurrencyNo(self, value: str):
        self._CurrencyNo = value
