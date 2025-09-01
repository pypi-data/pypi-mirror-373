import unittest
import pandas as pd
import tempfile
import os
from unknown_data.core import Category, DataKeys, ResultDataFrame, ResultDataFrames, Logger, BaseDataEncoder, DataSaver

class TestArtifactCore(unittest.TestCase):

    def setUp(self):
        self.data_keys = DataKeys()
        self.logger = Logger("TestLogger")
        self.encoder = BaseDataEncoder()
        # 임시 디렉토리를 사용하여 테스트 격리
        self.temp_dir = tempfile.mkdtemp()
        self.saver = DataSaver(self.temp_dir)

    def tearDown(self):
        # 테스트 후 임시 파일 정리
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_category_enum(self):
        """Category Enum의 모든 값 테스트"""
        self.assertEqual(Category.BROWSER.value, 'browser')
        self.assertEqual(Category.DELETED.value, 'deleted')
        self.assertEqual(Category.LNK.value, 'lnk')
        self.assertEqual(Category.MESSENGER.value, 'messenger')
        self.assertEqual(Category.PREFETCH.value, 'prefetch')
        self.assertEqual(Category.USB.value, 'usb')

    def test_data_keys(self):
        """DataKeys 클래스의 모든 카테고리별 키 검증"""
        # BROWSER 키 검증
        self.assertEqual(self.data_keys.get_data_keys(Category.BROWSER), 
                         {'collected_files', 'collection_time', 'detailed_files', 'discovered_profiles', 'statistics', 'temp_directory'})
        
        # DELETED 키 검증
        self.assertEqual(self.data_keys.get_data_keys(Category.DELETED), 
                         {'collection_info', 'data_sources', 'mft_deleted_files', 'recycle_bin_files', 'statistics'})
        
        # LNK 키 검증
        self.assertEqual(self.data_keys.get_data_keys(Category.LNK),
                         {'collection_info', 'lnk_files', 'search_directories'})
        
        # MESSENGER 키 검증
        self.assertEqual(self.data_keys.get_data_keys(Category.MESSENGER),
                         {'collection_info', 'collection_options', 'messenger_data', 'statistics'})
        
        # PREFETCH 키 검증
        self.assertEqual(self.data_keys.get_data_keys(Category.PREFETCH),
                         {'collection_info', 'prefetch_files'})
        
        # USB 키 검증
        self.assertEqual(self.data_keys.get_data_keys(Category.USB),
                         {'collection_info', 'usb_devices'})

    def test_result_data_frame(self):
        """ResultDataFrame 클래스의 기능 테스트"""
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        result_df = ResultDataFrame(name="test", data=df, subname="sub")
        self.assertEqual(result_df.name, "test")
        self.assertEqual(result_df.subname, "sub")
        self.assertTrue(result_df.data.equals(df))

    def test_result_data_frames(self):
        """ResultDataFrames 클래스의 add 메서드 테스트"""
        df1 = pd.DataFrame({'a': [1, 2]})
        df2 = pd.DataFrame({'b': [3, 4]})
        result_dfs = ResultDataFrames()
        
        # 기본 추가
        result_dfs.add(name="test1", data=df1)
        self.assertEqual(len(result_dfs.data), 1)
        self.assertEqual(result_dfs.data[0].name, "test1")
        self.assertEqual(result_dfs.data[0].subname, "")
        
        # subname과 함께 추가
        result_dfs.add(name="test2", data=df2, subname="sub")
        self.assertEqual(len(result_dfs.data), 2)
        self.assertEqual(result_dfs.data[1].subname, "sub")
        
        # 빈 이름으로 추가 시 예외 발생 확인
        with self.assertRaises(NameError):
            result_dfs.add(name="", data=df1)

    def test_logger(self):
        """Logger 클래스의 로깅 기능 테스트"""
        import io
        import sys
        from contextlib import redirect_stdout
        
        # stdout 캡처하여 로그 출력 확인
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.logger.log("This is a test log.")
        
        output = captured_output.getvalue()
        self.assertIn("TestLogger", output)
        self.assertIn("This is a test log.", output)
        # 날짜 형식 확인 (YYYY-MM-DD HH:MM:SS)
        import re
        date_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        self.assertTrue(re.search(date_pattern, output))

    def test_data_encoder_validation(self):
        """BaseDataEncoder의 데이터 검증 기능 테스트"""
        self.encoder.category = Category.BROWSER
        
        # 유효한 데이터
        valid_data = {
            'collected_files': [],
            'collection_time': '2023-01-01',
            'detailed_files': [],
            'discovered_profiles': [],
            'statistics': {},
            'temp_directory': '/tmp'
        }
        self.assertTrue(self.encoder.convert_data(valid_data))
        
        # 빈 데이터로 예외 발생 확인
        with self.assertRaises(NotImplementedError):
            self.encoder.convert_data({})
        
        # 잘못된 키를 가진 데이터로 예외 발생 확인
        invalid_data = {
            'wrong_key1': 'value1',
            'wrong_key2': 'value2'
        }
        with self.assertRaises(NotImplementedError):
            self.encoder.convert_data(invalid_data)

    def test_data_saver(self):
        """DataSaver 클래스의 파일 저장 기능 테스트"""
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        
        # 기본 파일 저장
        file_path = self.saver.save_data_to_csv("test_file", df)
        self.assertTrue(file_path.endswith("test_file.csv"))
        self.assertTrue(os.path.exists(file_path))
        
        # subname과 함께 저장
        file_path_with_sub = self.saver.save_data_to_csv("test_file", df, "chrome")
        self.assertTrue(file_path_with_sub.endswith("chrome.test_file.csv"))
        self.assertTrue(os.path.exists(file_path_with_sub))
        
        # 저장된 파일 내용 검증
        loaded_df = pd.read_csv(file_path, index_col=0)
        pd.testing.assert_frame_equal(df, loaded_df)
        
        # 빈 파일명으로 저장 시 예외 발생 확인
        with self.assertRaises(NameError):
            self.saver.save_data_to_csv("", df)

    def test_data_saver_save_all(self):
        """DataSaver의 save_all 메서드 테스트"""
        df1 = pd.DataFrame({'data1': [1, 2]})
        df2 = pd.DataFrame({'data2': [3, 4]})
        
        result_dfs = ResultDataFrames()
        result_dfs.add("dataset1", df1)
        result_dfs.add("dataset2", df2, "chrome")
        
        # 모든 데이터 저장
        self.saver.save_all(result_dfs)
        
        # 파일 생성 확인
        file1_path = os.path.join(self.temp_dir, "dataset1.csv")
        file2_path = os.path.join(self.temp_dir, "chrome.dataset2.csv")
        
        self.assertTrue(os.path.exists(file1_path))
        self.assertTrue(os.path.exists(file2_path))

    def test_base_data_encoder_dict_methods(self):
        """BaseDataEncoder의 데이터 변환 메서드 테스트"""
        self.encoder.category = Category.BROWSER
        
        # 테스트 데이터 설정
        test_data = {
            'simple_dict': {'key1': 'value1', 'key2': 'value2'},
            'list_data': [
                {'id': 1, 'name': 'item1'},
                {'id': 2, 'name': 'item2'}
            ]
        }
        
        self.encoder.data = test_data
        
        # dict 데이터를 DataFrame으로 변환 테스트
        dict_df = self.encoder._dict_data_to_df('simple_dict')
        self.assertIsInstance(dict_df, pd.DataFrame)
        self.assertEqual(len(dict_df), 1)
        self.assertIn('key1', dict_df.columns)
        self.assertIn('key2', dict_df.columns)
        
        # list 데이터를 DataFrame으로 변환 테스트
        list_df = self.encoder._list_data_to_df('list_data')
        self.assertIsInstance(list_df, pd.DataFrame)
        self.assertEqual(len(list_df), 2)
        self.assertIn('id', list_df.columns)
        self.assertIn('name', list_df.columns)

    def test_flatten_dict_method(self):
        """_flatten_dict 메서드의 중첩 딕셔너리 평탄화 테스트"""
        self.encoder.category = Category.BROWSER
        
        # 중첩된 딕셔너리 테스트
        nested_dict = {
            'level1': {
                'level2': {
                    'value': 'nested_value'
                },
                'simple': 'simple_value'
            },
            'list_data': [1, 2, 3],
            'simple_key': 'simple_value'
        }
        
        flattened = self.encoder._flatten_dict(nested_dict)
        
        # 평탄화된 키 확인
        self.assertIn('level1__level2__value', flattened)
        self.assertIn('level1__simple', flattened)
        self.assertIn('simple_key', flattened)
        
        # 값 확인
        self.assertEqual(flattened['level1__level2__value'], 'nested_value')
        self.assertEqual(flattened['level1__simple'], 'simple_value')
        self.assertEqual(flattened['simple_key'], 'simple_value')
        
        # 리스트는 JSON으로 변환되는지 확인
        import json
        self.assertEqual(flattened['list_data'], json.dumps([1, 2, 3], ensure_ascii=False))

if __name__ == '__main__':
    unittest.main()