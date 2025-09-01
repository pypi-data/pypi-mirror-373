import os
import json
import datetime as dt
import pandas as pd
from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass, field
from pandas import DataFrame



class Category(Enum):
    BROWSER = 'browser'
    DELETED = 'deleted'
    LNK = 'lnk'
    MESSENGER = 'messenger'
    PREFETCH = 'prefetch'
    USB = 'usb'


class DataKeys:
    def __init__(self):
        self.browser_keys = set(('collected_files', 'collection_time', 'detailed_files', 'discovered_profiles', 'statistics', 'temp_directory'))
        self.deleted_keys = set(('collection_info', 'data_sources', 'mft_deleted_files', 'recycle_bin_files', 'statistics'))
        self.lnk_keys = set(('collection_info', 'lnk_files', 'search_directories'))
        self.messenger_keys = set(('collection_info', 'collection_options', 'messenger_data', 'statistics'))
        self.prefetch_keys = set(('collection_info', 'prefetch_files'))
        self.usb_keys = set(('collection_info', 'usb_devices'))
    
    def get_data_keys(self, category: Category) -> set:
        match category:
            case Category.BROWSER:
                return self.browser_keys
            case Category.DELETED:
                return self.deleted_keys
            case Category.LNK:
                return self.lnk_keys
            case Category.MESSENGER:
                return self.messenger_keys
            case Category.PREFETCH:
                return self.prefetch_keys
            case Category.USB:
                return self.usb_keys
            case _:
                print(category)
                raise TypeError


@dataclass
class ResultDataFrame:
    name:str
    data:DataFrame
    subname:str = field(default_factory=str)


@dataclass
class ResultDataFrames:
    data:list[ResultDataFrame] = field(default_factory=list)

    def add(self, name:str, data:DataFrame, subname=str()):
        if not name:
            raise NameError
        self.data.append(ResultDataFrame(name, data, subname if subname else ""))


class Logger:
    def __init__(self, name) -> None:
        self.name = name
    
    def log(self, message) -> None:
        time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        template = f"[{time}] {self.name} - {message}"
        print(template)


class BaseDataEncoder:
    def __init__(self):
        self.category: Category
        self.success_file_list = []
        self.logger = Logger("DataEncoder")


    def _validate_data_keys(self, keys) -> bool:
        _keys = DataKeys().get_data_keys(self.category)
        return _keys == keys
        
    def _validate_data(self, data: dict) -> bool:
        if not data:
            self.logger.log("There is no data to process.")
            raise NotImplementedError
        
        if not self._validate_data_keys(data.keys()):
            self.logger.log("Data key is not correct.")
            raise NotImplementedError

        return True
    
    def get_result_dfs(self) -> ResultDataFrames:
        return ResultDataFrames()
        
    
    def convert_data(self, data: dict) -> bool:
        self.data = data
        self._validate_data(data)
        return True


    def _dict_data_to_df(self, first_depth:str) -> DataFrame:
        dict_data = self.data.get(first_depth, {})
        return pd.DataFrame([dict_data])
    
    def _list_data_to_df(self, first_depth:str) -> DataFrame:
        data = self.data.get(first_depth, [])
        for i, dict_data in enumerate(data):
            data[i] = self._flatten_dict(dict_data)
        return pd.DataFrame(data)
    
    def _flatten_dict(self, obj: Any, parent_key: str = "", sep: str = "__") -> dict[str, Any]:
        flat: dict[str, Any] = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "execution_times":
                    continue
                if k == "last_run_times":
                    flat.update({f"{k}_{v[i].get('slot')}": v[i].get('formatted_time') for i in range(len(v))})
                    continue
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    flat.update(self._flatten_dict(v, new_key, sep))
                elif isinstance(v, list):
                    flat[new_key] = json.dumps(v, ensure_ascii=False)
                else:
                    flat[new_key] = v
        else:
            flat[parent_key or "value"] = json.dumps(obj, ensure_ascii=False) if isinstance(obj, list) else obj
        return flat


class DataSaver:
    def __init__(self, directory=None) -> None:
        self.logger = Logger("DataSaver")
        self.result_dir = "./data/result"
        if directory:
            self.set_result_dir(directory)
        else:
            self.logger.log("Data will be saved to Default directory")
            self._check_result_dir()
    
    def _check_result_dir(self) -> None:
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir, exist_ok=True)
    
    def set_result_dir(self, directory:str) -> None:
        self.result_dir = directory
        self._check_result_dir()

    def save_data_to_csv(self, filename:str, data:DataFrame, subname="") -> str:
        if not filename:
            raise NameError
        filename = subname+"."+filename if subname else filename
        file_path = os.path.join(self.result_dir, f"{filename}.csv")
        try:
            data.to_csv(file_path)
        except Exception as e:
            self.logger.log(f"Unknown Error: {e}")
            raise Exception
        
        return file_path
    
    def save_all(self, result:ResultDataFrames) -> None:
        for item in result.data:
            save = self.save_data_to_csv(item.name, item.data, item.subname)
            self.logger.log(save)