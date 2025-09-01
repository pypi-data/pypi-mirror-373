from pandas import DataFrame
from ..core import BaseDataEncoder, ResultDataFrames, Category


class MessengerEncoder(BaseDataEncoder):
    def __init__(self):
        super().__init__()
        self.category=Category.MESSENGER

        self.collection_info:DataFrame = DataFrame()
        self.collection_options:DataFrame = DataFrame()
        self.messenger_data:DataFrame = DataFrame()
        self.statistics:DataFrame = DataFrame()

    def get_result_dfs(self) -> ResultDataFrames:
        result = super().get_result_dfs()

        if not self.collection_info.empty:
            result.add("collection_info", self.collection_info)
        if not self.collection_options.empty:
            result.add("collection_options", self.collection_options)
        if not self.messenger_data.empty:
            result.add("messenger_data", self.messenger_data)
        if not self.statistics.empty:
            result.add("statistics", self.statistics)
        
        return result
        
    def convert_data(self, data: dict) -> bool:
        super().convert_data(data)
        for first_depth in self.data.keys():
            match first_depth:
                case "collection_info":
                    df = self._dict_data_to_df(first_depth)
                    self.collection_info = df
                case "collection_options":
                    df = self._dict_data_to_df(first_depth)
                    self.collection_options = df
                case "statistics":
                    df = self._dict_data_to_df(first_depth)
                    self.statistics = df
                case "messenger_data":
                    df = self._list_data_to_df(first_depth)
                    self.messenger_data = df
                case _:
                    self.logger.log(first_depth)
                    pass
        
        return True
    
