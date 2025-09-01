from ...interface import IData
from ...packer.chart.base_graph_param_data_packer import BaseGraphParamDataPacker


class BaseGraphParamData(IData):
    def __init__(self, id: str = '', name: str = '', plot_index: int = 0, value_axisid: int = -1, visible: bool = True):
        super().__init__(BaseGraphParamDataPacker(self))
        self._ID: str = id
        self._Name: str = name
        self._PlotIndex: int = plot_index
        self._ValueAxisID: int = value_axisid
        self._Visible: bool = visible
        self._UserData = {}

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value: str):
        self._ID = value

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, value: str):
        self._Name = value

    @property
    def PlotIndex(self):
        return self._PlotIndex

    @PlotIndex.setter
    def PlotIndex(self, value: int):
        self._PlotIndex = value

    @property
    def ValueAxisID(self):
        return self._ValueAxisID

    @ValueAxisID.setter
    def ValueAxisID(self, value: int):
        self._ValueAxisID = value

    @property
    def Visible(self):
        return self._Visible

    @Visible.setter
    def Visible(self, value: bool):
        self._Visible = value

    @property
    def UserData(self):
        return self._UserData

    @UserData.setter
    def UserData(self, value):
        self._UserData = value
