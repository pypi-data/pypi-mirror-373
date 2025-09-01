from pandas import DataFrame
from ..core import BaseDataEncoder, ResultDataFrames, Category


class PrefetchEncoder(BaseDataEncoder):
    def __init__(self):
        super().__init__()
        self.category=Category.PREFETCH

        self.collection_info:DataFrame = DataFrame()
        self.prefetch_files:DataFrame = DataFrame()

    def get_result_dfs(self) -> ResultDataFrames:
        result = super().get_result_dfs()

        if not self.collection_info.empty:
            result.add("collection_info", self.collection_info)
        if not self.prefetch_files.empty:
            result.add("prefetch_files", self.prefetch_files)
        
        return result
        
    def convert_data(self, data: dict) -> bool:
        super().convert_data(data)
        for first_depth in self.data.keys():
            match first_depth:
                case "collection_info":
                    df = self._dict_data_to_df(first_depth)
                    self.collection_info = df
                case "prefetch_files":
                    df = self._list_data_to_df(first_depth)
                    self.prefetch_files = df
                case _:
                    self.logger.log(first_depth)
                    pass
        
        return True
    
