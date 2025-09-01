from ..interface import IData
from ..packer.message_data_packer import MessageDataPacker


class MessageData(IData):
    def __init__(self, mid: int = -1, action_id: int = 1, request_id: int = 0, is_last: bool = True, rsp_success: bool = True, rsp_msg: str = '', udata: bytes = b'', compresstype: int = -1) -> None:
        super().__init__(MessageDataPacker(self))
        self._MID = mid
        self._ActionID: int = action_id
        self._RequestID: int = request_id
        self._IsLast: bool = is_last
        self._RspSuccess: bool = rsp_success
        self._RspMsg: str = rsp_msg
        self._UData: bytes = udata
        self._CompressType: int = compresstype

    @property
    def MID(self):
        return self._MID

    @MID.setter
    def MID(self, value: int):
        self._MID = value

    @property
    def ActionID(self):
        return self._ActionID

    @ActionID.setter
    def ActionID(self, value: int):
        self._ActionID = value

    @property
    def RequestID(self):
        return self._RequestID

    @RequestID.setter
    def RequestID(self, value: int):
        self._RequestID = value

    @property
    def IsLast(self):
        return self._IsLast

    @IsLast.setter
    def IsLast(self, value: bool):
        self._IsLast = value

    @property
    def RspSuccess(self):
        return self._RspSuccess

    @RspSuccess.setter
    def RspSuccess(self, value: bool):
        self._RspSuccess = value

    @property
    def RspMsg(self):
        return self._RspMsg

    @RspMsg.setter
    def RspMsg(self, value: str):
        self._RspMsg = value

    @property
    def UData(self):
        return self._UData

    @UData.setter
    def UData(self, value: bytes):
        self._UData = value

    @property
    def CompressType(self):
        return self._CompressType

    @CompressType.setter
    def CompressType(self, value: int):
        self._CompressType = value
