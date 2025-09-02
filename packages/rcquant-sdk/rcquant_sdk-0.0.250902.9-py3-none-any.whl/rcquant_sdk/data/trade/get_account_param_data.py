from ...interface import IData
from .account_data import AccountData
from ...packer.trade.get_account_param_data_packer import GetAccountParamDataPacker


class GetAccountParamData(IData):
    def __init__(self, trade_name: str = ''):
        super().__init__(GetAccountParamDataPacker(self))
        self._TradeName = trade_name
        self._Account: AccountData = AccountData()

    @property
    def TradeName(self):
        return self._TradeName

    @TradeName.setter
    def TradeName(self, value: str):
        self._TradeName = value

    @property
    def Account(self):
        return self._Account

    @Account.setter
    def Account(self, value: AccountData):
        self._Account: AccountData = value
