from pandas import DataFrame
from ..core import BaseDataEncoder, ResultDataFrames, Category


class DeletedDataEncoder(BaseDataEncoder):
    def __init__(self):
        super().__init__()
        self.category=Category.DELETED

        self.collection_info:DataFrame = DataFrame()
        self.data_sources:DataFrame = DataFrame()
        self.mft_deleted_files:DataFrame = DataFrame()
        self.recycle_bin_files:DataFrame = DataFrame()
        self.statistics:DataFrame = DataFrame()

    def get_result_dfs(self) -> ResultDataFrames:
        result = super().get_result_dfs()

        if not self.collection_info.empty:
            result.add("collection_info", self.collection_info)
        if not self.data_sources.empty:
            result.add("data_sources", self.data_sources)
        if not self.mft_deleted_files.empty:
            result.add("mft_deleted_files", self.mft_deleted_files)
        if not self.recycle_bin_files.empty:
            result.add("recycle_bin_files", self.recycle_bin_files)
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
                case "data_sources":
                    df = self._dict_data_to_df(first_depth)
                    self.data_sources = df
                case "statistics":
                    df = self._dict_data_to_df(first_depth)
                    self.statistics = df
                case "mft_deleted_files":
                    df = self._list_data_to_df(first_depth)
                    self.mft_deleted_files = df
                case "recycle_bin_files":
                    df = self._list_data_to_df(first_depth)
                    self.recycle_bin_files = df
                case _:
                    pass
                
        return True
    
