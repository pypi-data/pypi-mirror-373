from ..interface import IData
from ..packer.login_data_packer import LoginDataPacker


class LoginData(IData):
    def __init__(self, user_id: str = '', password: str = '') -> None:
        super().__init__(LoginDataPacker(self))
        self._UserID: str = user_id
        self._PassWord: str = password

    @property
    def UserID(self):
        return self._UserID

    @UserID.setter
    def UserID(self, value: str):
        self._UserID = value

    @property
    def PassWord(self):
        return self._PassWord

    @PassWord.setter
    def PassWord(self, value: str):
        self._PassWord = value
