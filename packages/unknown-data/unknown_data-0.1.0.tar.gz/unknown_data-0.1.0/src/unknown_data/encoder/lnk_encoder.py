from pandas import DataFrame
from ..core import BaseDataEncoder, ResultDataFrames, Category


class LnkDataEncoder(BaseDataEncoder):
    def __init__(self):
        super().__init__()
        self.category=Category.LNK

        self.collection_info:DataFrame = DataFrame()
        self.lnk_files:DataFrame = DataFrame()
        self.search_directories:DataFrame = DataFrame()

    def get_result_dfs(self) -> ResultDataFrames:
        result = super().get_result_dfs()

        if not self.collection_info.empty:
            result.add("collection_info", self.collection_info)
        if not self.lnk_files.empty:
            result.add("lnk_files", self.lnk_files)
        if not self.search_directories.empty:
            result.add("search_directories", self.search_directories)
        
        return result
        
    def convert_data(self, data: dict) -> bool:
        super().convert_data(data)
        for first_depth in self.data.keys():
            match first_depth:
                case "collection_info":
                    df = self._dict_data_to_df(first_depth)
                    self.collection_info = df
                case "lnk_files":
                    df = self._list_data_to_df(first_depth)
                    self.lnk_files = df
                case "search_directories":
                    df = self._dict_data_to_df(first_depth)
                    self.search_directories = df
                case _:
                    pass
                
        return True
    
