import pandas as pd
from dataclasses import dataclass, field
from pandas import DataFrame
from ..core import BaseDataEncoder, ResultDataFrames, Category


@dataclass
class BrowserDataFrame:
    binary_data_list: list = field(default_factory=list)
    
    # History
    annotations: DataFrame = field(default_factory=pd.DataFrame)
    binary_data: DataFrame = field(default_factory=pd.DataFrame)
    downloads: DataFrame = field(default_factory=pd.DataFrame)
    download_url_chains: DataFrame = field(default_factory=pd.DataFrame)
    keyword_search_terms: DataFrame = field(default_factory=pd.DataFrame)
    segment: DataFrame = field(default_factory=pd.DataFrame)
    segment_usage: DataFrame = field(default_factory=pd.DataFrame)
    urls: DataFrame = field(default_factory=pd.DataFrame)
    visited_links: DataFrame = field(default_factory=pd.DataFrame)
    visits: DataFrame = field(default_factory=pd.DataFrame)

    # Login

    # cookie
    cookies: DataFrame = field(default_factory=pd.DataFrame)

        # Web data


class BrowserDataEncoder(BaseDataEncoder):
    def __init__(self) -> None:
        super().__init__()
        self.category=Category.BROWSER
        self.success_file_list=[]

        # 결과물 데이터프레임
        self.collected_data_outline: DataFrame = DataFrame()
        self.profile: DataFrame = DataFrame()
        self.statistics: DataFrame = DataFrame()
        self.chrome_data=BrowserDataFrame()
        self.edge_data=BrowserDataFrame()

    # 결과물 데이터프레임 참조 리스트 -> 일괄 csv 변환을 위해서.
    def get_result_dfs(self) -> ResultDataFrames:
        result = super().get_result_dfs()
        if not self.collected_data_outline.empty:
            result.add("collected_data_outline", self.collected_data_outline)
        if not self.profile.empty:
            result.add("profile", self.profile)
        if not self.statistics.empty:
            result.add("statistics", self.statistics)
        
        if not self.chrome_data.annotations.empty:
            result.add("annotations", self.chrome_data.annotations, "chrome")
        if not self.chrome_data.binary_data.empty:
            result.add("binary_data", self.chrome_data.binary_data, "chrome")
        if not self.chrome_data.downloads.empty:
            result.add("downloads", self.chrome_data.downloads, "chrome")
        if not self.chrome_data.download_url_chains.empty:
            result.add("download_url_chains", self.chrome_data.download_url_chains, "chrome")
        if not self.chrome_data.keyword_search_terms.empty:
            result.add("keyword_search_terms", self.chrome_data.keyword_search_terms, "chrome")
        if not self.chrome_data.segment.empty:
            result.add("segment", self.chrome_data.segment, "chrome")
        if not self.chrome_data.segment_usage.empty:
            result.add("segment_usage", self.chrome_data.segment_usage, "chrome")
        if not self.chrome_data.urls.empty:
            result.add("urls", self.chrome_data.urls, "chrome")
        if not self.chrome_data.visited_links.empty:
            result.add("visited_links", self.chrome_data.visited_links, "chrome")
        if not self.chrome_data.visits.empty:
            result.add("visits", self.chrome_data.visits, "chrome")
        if not self.chrome_data.cookies.empty:
            result.add("cookies", self.chrome_data.cookies, "chrome")

        if not self.edge_data.annotations.empty:
            result.add("annotations", self.edge_data.annotations, "edge")
        if not self.edge_data.binary_data.empty:
            result.add("binary_data", self.edge_data.binary_data, "edge")
        if not self.edge_data.downloads.empty:
            result.add("downloads", self.edge_data.downloads, "edge")
        if not self.edge_data.download_url_chains.empty:
            result.add("download_url_chains", self.edge_data.download_url_chains, "edge")
        if not self.edge_data.keyword_search_terms.empty:
            result.add("keyword_search_terms", self.edge_data.keyword_search_terms, "edge")
        if not self.edge_data.segment.empty:
            result.add("segment", self.edge_data.segment, "edge")
        if not self.edge_data.segment_usage.empty:
            result.add("segment_usage", self.edge_data.segment_usage, "edge")
        if not self.edge_data.urls.empty:
            result.add("urls", self.edge_data.urls, "edge")
        if not self.edge_data.visited_links.empty:
            result.add("visited_links", self.edge_data.visited_links, "edge")
        if not self.edge_data.visits.empty:
            result.add("visits", self.edge_data.visits, "edge")
        if not self.edge_data.cookies.empty:
            result.add("cookies", self.edge_data.cookies, "edge")

        return result


    # 데이터처리를 총괄하며 외부에서 호출하는 함수
    def convert_data(self, data: dict) -> bool:
        super().convert_data(data)
        for first_depth in self.data.keys():
            match first_depth:
                case "collected_files":
                    # 수집한 데이터 명세 -> binary file은 제외
                    self._collected_files(first_depth)
                case "collection_time":
                    self.collected_time = pd.DataFrame([data.get(first_depth)])
                case "detailed_files":
                    files_data = self.data[first_depth]
                    self._detailed_files(files_data)
                case "discovered_profiles":
                    self._discovered_profiles(first_depth)
                case "statistics":
                    self._statistics_data(first_depth)
                case "temp_directory":
                    self.temp_directory = pd.DataFrame([data.get(first_depth)])
                case _:
                    print(first_depth)

        return True
    
    def _collected_files(self, first_depth):
        list_data = self.data[first_depth]
        self.success_file_list.extend([i["file_name"] for i in list_data if i["success"] and not i["file_type"] == "binary"])
        df = pd.DataFrame([i for i in list_data if i["success"] and not i["file_type"] == "binary"])
        self.collected_data_outline = df

    def _discovered_profiles(self, first_depth):
        list_data = self.data.get(first_depth)
        df = pd.DataFrame(list_data)
        self.profile = df
    
    def _statistics_data(self, first_depth):
        stat_data = self.data[first_depth]
        self.statistics = pd.DataFrame([stat_data])
        self.logger.log("[browser_data_result]")
        for key in stat_data.keys():
            self.logger.log(f"{key} : {stat_data.get(key)}")
    
    def _detailed_files(self, files_data):
        for file in files_data:
            if not file.get("success"):
                self.logger.log(f"{file.get('file_name')} failed")
                continue

            file_path = file.get("file_path", "")
            browser_type = file.get("browser_type", "").lower()
            
            # file_path나 browser_type으로 브라우저 결정
            if file_path and ("Chrome" in file_path.split("/") or "chrome" in file_path.lower()):
                self._process_browser_data(self.chrome_data, file)
                self.chrome_data.binary_data = pd.DataFrame(self.chrome_data.binary_data_list)
            elif file_path and ("Edge" in file_path.split("/") or "edge" in file_path.lower()):
                self._process_browser_data(self.edge_data, file)
                self.edge_data.binary_data = pd.DataFrame(self.edge_data.binary_data_list)
            elif browser_type == "chrome":
                self._process_browser_data(self.chrome_data, file)
                self.chrome_data.binary_data = pd.DataFrame(self.chrome_data.binary_data_list)
            elif browser_type == "edge":
                self._process_browser_data(self.edge_data, file)
                self.edge_data.binary_data = pd.DataFrame(self.edge_data.binary_data_list)
            else:
                # 기본적으로 chrome으로 처리
                self._process_browser_data(self.chrome_data, file)
                self.chrome_data.binary_data = pd.DataFrame(self.chrome_data.binary_data_list)

    
    def _process_browser_data(self, data_store:BrowserDataFrame, file:dict) -> None:
        if file.get("file_type") == "binary":
            data_store.binary_data_list.append(file)
            return
        
        table_names = file.get("table_names")
        if not table_names:
            self.logger.log(f"{file.get("file_name")} no data to process")
            return
        
        file_name = file.get("file_name")
        sqlite_data = file.get("sqlite_data",[])

        match file_name:
            case "History":
                self._process_history_sqlite_data(data_store, sqlite_data, table_names)
            case "Login Data":
                self._process_login_sqlite_data(data_store, sqlite_data, table_names)
            case "Cookies":
                self._process_cookies_sqlite_data(data_store, sqlite_data, table_names)
            case "Web Data":
                self._process_web_sqlite_data(data_store, sqlite_data, table_names)
            case _:
                self.logger.log("Incorrect file_name")
                raise NotImplementedError

    def _process_login_sqlite_data(self, data_store:BrowserDataFrame, sqlite_data:dict, table_names):
        for table_name in table_names:
            table = sqlite_data[table_name]

            match table_name:
                case "insecure_credentials":
                    pass
                case "logins":
                    pass
                case "password_notes":
                    pass
                case "stats":
                    pass
                case _:
                    pass

    def _process_cookies_sqlite_data(self, data_store:BrowserDataFrame, sqlite_data:dict, table_names):
        for table_name in table_names:
            table = sqlite_data[table_name]

            match table_name:
                case "cookies":
                    df = pd.DataFrame(table)
                    data_store.cookies = df
                case "meta":
                    pass
                case _:
                    pass

    def _process_web_sqlite_data(self, data_store:BrowserDataFrame, sqlite_data:dict, table_names):
        for table_name in table_names:
            table = sqlite_data[table_name]

            match table_name:
                case "address_type_tokens":
                    pass
                case _:
                    pass


    def _process_history_sqlite_data(self, data_store:BrowserDataFrame, sqlite_data:dict, table_names):
        for table_name in table_names:
            table = sqlite_data[table_name]

            match table_name:
                case "content_annotations":
                    df = pd.DataFrame(table)
                    if data_store.annotations.empty:
                        data_store.annotations = df
                    else:
                        data_store.annotations = pd.merge(data_store.annotations, df, how='outer', on='visit_id')
                case "context_annotations":
                    df = pd.DataFrame(table)
                    if data_store.annotations.empty:
                        data_store.annotations = df
                    else:
                        data_store.annotations = pd.merge(data_store.annotations, df, how='outer', on='visit_id')
                case "downloads":
                    df = pd.DataFrame(table)
                    data_store.downloads = df
                case "downloads_url_chains":
                    df = pd.DataFrame(table)
                    data_store.download_url_chains = df
                case "keyword_search_terms":
                    df = pd.DataFrame(table)
                    data_store.keyword_search_terms = df
                case "segment_usage":
                    df = pd.DataFrame(table)
                    data_store.segment_usage = df
                case "segments":
                    df = pd.DataFrame(table)
                    data_store.segment = df
                case "urls":
                    df = pd.DataFrame(table)
                    data_store.urls = df
                case "visited_links":
                    df = pd.DataFrame(table)
                    data_store.visited_links = df
                case "visits":
                    df = pd.DataFrame(table)
                    data_store.visits = df
                case _:
                    continue
