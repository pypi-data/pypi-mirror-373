from pandas import DataFrame
from ..core import BaseDataEncoder, ResultDataFrames, Category


class UsbDataEncoder(BaseDataEncoder):
    def __init__(self):
        super().__init__()
        self.category=Category.USB

        self.collection_info:DataFrame = DataFrame()
        self.usb_devices:DataFrame = DataFrame()

    def get_result_dfs(self) -> ResultDataFrames:
        result = super().get_result_dfs()

        if not self.collection_info.empty:
            result.add("collection_info", self.collection_info)
        if not self.usb_devices.empty:
            result.add("usb_devices", self.usb_devices)
        
        return result
        
    def convert_data(self, data: dict) -> bool:
        super().convert_data(data)
        for first_depth in self.data.keys():
            match first_depth:
                case "collection_info":
                    df = self._dict_data_to_df(first_depth)
                    self.collection_info = df
                case "usb_devices":
                    df = self._list_data_to_df(first_depth)
                    self.usb_devices = df
                case _:
                    self.logger.log(first_depth)
                    pass
        
        return True
    
