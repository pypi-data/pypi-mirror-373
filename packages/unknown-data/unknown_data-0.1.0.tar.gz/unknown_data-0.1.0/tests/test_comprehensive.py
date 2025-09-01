import unittest
import pandas as pd
import tempfile
import os
import json
from unknown_data import (
    Category, DataKeys, ResultDataFrame, ResultDataFrames, 
    Logger, BaseDataEncoder, DataSaver, Encoder,
    BrowserDataEncoder, DeletedDataEncoder, LnkDataEncoder,
    MessengerEncoder, PrefetchEncoder, UsbDataEncoder,
    DataLoader
)

class TestArtifactCore(unittest.TestCase):
    """Core 모듈의 기본 기능 테스트"""

    def setUp(self):
        self.data_keys = DataKeys()
        self.logger = Logger("TestLogger")
        self.encoder = BaseDataEncoder()
        # 임시 디렉토리 사용으로 테스트 격리
        self.temp_dir = tempfile.mkdtemp()
        self.saver = DataSaver(self.temp_dir)

    def tearDown(self):
        # 테스트 후 임시 파일 정리
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_category_enum_all_values(self):
        """모든 Category 값 테스트"""
        self.assertEqual(Category.BROWSER.value, 'browser')
        self.assertEqual(Category.DELETED.value, 'deleted')
        self.assertEqual(Category.LNK.value, 'lnk')
        self.assertEqual(Category.MESSENGER.value, 'messenger')
        self.assertEqual(Category.PREFETCH.value, 'prefetch')
        self.assertEqual(Category.USB.value, 'usb')

    def test_data_keys_all_categories(self):
        """모든 카테고리의 데이터 키 검증"""
        # BROWSER 키 검증
        browser_keys = self.data_keys.get_data_keys(Category.BROWSER)
        expected_browser_keys = {'collected_files', 'collection_time', 'detailed_files', 
                               'discovered_profiles', 'statistics', 'temp_directory'}
        self.assertEqual(browser_keys, expected_browser_keys)
        
        # DELETED 키 검증
        deleted_keys = self.data_keys.get_data_keys(Category.DELETED)
        expected_deleted_keys = {'collection_info', 'data_sources', 'mft_deleted_files', 
                               'recycle_bin_files', 'statistics'}
        self.assertEqual(deleted_keys, expected_deleted_keys)
        
        # LNK 키 검증
        lnk_keys = self.data_keys.get_data_keys(Category.LNK)
        expected_lnk_keys = {'collection_info', 'lnk_files', 'search_directories'}
        self.assertEqual(lnk_keys, expected_lnk_keys)
        
        # MESSENGER 키 검증
        messenger_keys = self.data_keys.get_data_keys(Category.MESSENGER)
        expected_messenger_keys = {'collection_info', 'collection_options', 
                                 'messenger_data', 'statistics'}
        self.assertEqual(messenger_keys, expected_messenger_keys)
        
        # PREFETCH 키 검증
        prefetch_keys = self.data_keys.get_data_keys(Category.PREFETCH)
        expected_prefetch_keys = {'collection_info', 'prefetch_files'}
        self.assertEqual(prefetch_keys, expected_prefetch_keys)
        
        # USB 키 검증
        usb_keys = self.data_keys.get_data_keys(Category.USB)
        expected_usb_keys = {'collection_info', 'usb_devices'}
        self.assertEqual(usb_keys, expected_usb_keys)

    def test_data_keys_invalid_category(self):
        """잘못된 카테고리에 대한 예외 처리 테스트"""
        with self.assertRaises(TypeError):
            self.data_keys.get_data_keys("invalid_category")

    def test_result_data_frame_functionality(self):
        """ResultDataFrame의 모든 기능 테스트"""
        df = pd.DataFrame({'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']})
        
        # 기본 생성
        result_df = ResultDataFrame(name="test_data", data=df)
        self.assertEqual(result_df.name, "test_data")
        self.assertEqual(result_df.subname, "")
        self.assertTrue(result_df.data.equals(df))
        
        # subname과 함께 생성
        result_df_with_sub = ResultDataFrame(name="test_data", data=df, subname="chrome")
        self.assertEqual(result_df_with_sub.subname, "chrome")

    def test_result_data_frames_operations(self):
        """ResultDataFrames의 add 메서드 테스트"""
        df1 = pd.DataFrame({'data1': [1, 2]})
        df2 = pd.DataFrame({'data2': [3, 4]})
        df3 = pd.DataFrame({'data3': [5, 6]})
        
        result_dfs = ResultDataFrames()
        
        # 기본 추가
        result_dfs.add(name="first", data=df1)
        self.assertEqual(len(result_dfs.data), 1)
        self.assertEqual(result_dfs.data[0].name, "first")
        
        # subname과 함께 추가
        result_dfs.add(name="second", data=df2, subname="chrome")
        self.assertEqual(len(result_dfs.data), 2)
        self.assertEqual(result_dfs.data[1].subname, "chrome")
        
        # 빈 이름으로 추가 시 예외 발생 확인
        with self.assertRaises(NameError):
            result_dfs.add(name="", data=df3)

    def test_logger_functionality(self):
        """Logger의 출력 기능 테스트"""
        import io
        import sys
        from contextlib import redirect_stdout
        
        # stdout 캡처
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.logger.log("Test message")
        
        output = captured_output.getvalue()
        self.assertIn("TestLogger", output)
        self.assertIn("Test message", output)
        self.assertIn("2025", output)  # 현재 년도 포함 확인

    def test_data_saver_operations(self):
        """DataSaver의 파일 저장 기능 테스트"""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35]
        })
        
        # 기본 파일 저장
        file_path = self.saver.save_data_to_csv("test_data", df)
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.endswith("test_data.csv"))
        
        # subname과 함께 저장
        file_path_with_sub = self.saver.save_data_to_csv("test_data", df, "chrome")
        self.assertTrue(os.path.exists(file_path_with_sub))
        self.assertTrue(file_path_with_sub.endswith("chrome.test_data.csv"))
        
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


class TestEncoders(unittest.TestCase):
    """각 Encoder의 실제 동작 테스트"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_browser_encoder_basic_functionality(self):
        """BrowserDataEncoder의 기본 기능 테스트"""
        encoder = BrowserDataEncoder()
        
        # 카테고리 확인
        self.assertEqual(encoder.category, Category.BROWSER)
        
        # 샘플 데이터
        sample_data = {
            'collected_files': [
                {'file_name': 'History', 'success': True, 'file_type': 'database'},
                {'file_name': 'Cookies', 'success': True, 'file_type': 'database'}
            ],
            'collection_time': '2025-09-01 10:00:00',
            'detailed_files': [
                {
                    'file_name': 'History',
                    'success': True,
                    'browser_type': 'chrome',
                    'profile_name': 'Default',
                    'data': {
                        'urls': [
                            {'url': 'https://example.com', 'title': 'Example', 'visit_count': 5}
                        ]
                    }
                }
            ],
            'discovered_profiles': [
                {'browser': 'chrome', 'profile': 'Default', 'path': '/path/to/profile'}
            ],
            'statistics': {
                'total_files': 2,
                'success_files': 2,
                'failed_files': 0
            },
            'temp_directory': '/tmp/browser_analysis'
        }
        
        # 데이터 변환 실행
        result = encoder.convert_data(sample_data)
        self.assertTrue(result)
        
        # 결과 데이터프레임 확인
        result_dfs = encoder.get_result_dfs()
        self.assertIsInstance(result_dfs, ResultDataFrames)
        self.assertGreater(len(result_dfs.data), 0)
        
        # 성공 파일 리스트 확인
        self.assertEqual(len(encoder.success_file_list), 2)
        self.assertIn('History', encoder.success_file_list)
        self.assertIn('Cookies', encoder.success_file_list)

    def test_deleted_encoder_functionality(self):
        """DeletedDataEncoder의 기능 테스트"""
        encoder = DeletedDataEncoder()
        
        self.assertEqual(encoder.category, Category.DELETED)
        
        sample_data = {
            'collection_info': {
                'scan_time': '2025-09-01 10:00:00',
                'scan_type': 'full'
            },
            'data_sources': {
                'mft_analysis': True,
                'recycle_bin_analysis': True
            },
            'mft_deleted_files': [
                {
                    'file_name': 'deleted_file1.txt',
                    'original_path': 'C:\\Users\\test\\deleted_file1.txt',
                    'deleted_time': '2025-08-30 15:30:00',
                    'file_size': 1024
                },
                {
                    'file_name': 'deleted_file2.pdf',
                    'original_path': 'C:\\Users\\test\\Documents\\deleted_file2.pdf',
                    'deleted_time': '2025-08-29 09:15:00',
                    'file_size': 2048
                }
            ],
            'recycle_bin_files': [
                {
                    'original_name': 'recycled_file.docx',
                    'deleted_path': '$RECYCLE.BIN\\file1',
                    'deleted_time': '2025-08-31 11:20:00'
                }
            ],
            'statistics': {
                'total_deleted_files': 3,
                'mft_files': 2,
                'recycle_bin_files': 1
            }
        }
        
        result = encoder.convert_data(sample_data)
        self.assertTrue(result)
        
        # 결과 확인
        result_dfs = encoder.get_result_dfs()
        self.assertGreater(len(result_dfs.data), 0)
        
        # MFT 삭제 파일 확인
        self.assertFalse(encoder.mft_deleted_files.empty)
        self.assertEqual(len(encoder.mft_deleted_files), 2)

    def test_messenger_encoder_functionality(self):
        """MessengerEncoder의 기능 테스트"""
        encoder = MessengerEncoder()
        
        self.assertEqual(encoder.category, Category.MESSENGER)
        
        sample_data = {
            'collection_info': {
                'collection_time': '2025-09-01 10:00:00',
                'target_applications': ['KakaoTalk', 'Line', 'Telegram']
            },
            'collection_options': {
                'include_media': True,
                'include_deleted': False
            },
            'messenger_data': [
                {
                    'app_name': 'KakaoTalk',
                    'chat_room': 'Friend Chat',
                    'message_count': 150,
                    'media_count': 25,
                    'date_range': '2025-08-01 to 2025-09-01'
                },
                {
                    'app_name': 'Line',
                    'chat_room': 'Family Group',
                    'message_count': 89,
                    'media_count': 12,
                    'date_range': '2025-08-15 to 2025-09-01'
                }
            ],
            'statistics': {
                'total_applications': 2,
                'total_messages': 239,
                'total_media': 37
            }
        }
        
        result = encoder.convert_data(sample_data)
        self.assertTrue(result)
        
        result_dfs = encoder.get_result_dfs()
        self.assertGreater(len(result_dfs.data), 0)
        
        # 메신저 데이터 확인
        self.assertFalse(encoder.messenger_data.empty)
        self.assertEqual(len(encoder.messenger_data), 2)

    def test_encoder_base_class_functionality(self):
        """Encoder 기본 클래스의 통합 기능 테스트"""
        encoder = Encoder()
        
        # 각 카테고리별 encoder 객체 확인
        self.assertIsInstance(encoder.browser, BrowserDataEncoder)
        self.assertIsInstance(encoder.deleted, DeletedDataEncoder)
        self.assertIsInstance(encoder.lnk, LnkDataEncoder)
        self.assertIsInstance(encoder.messenger, MessengerEncoder)
        self.assertIsInstance(encoder.prefetch, PrefetchEncoder)
        self.assertIsInstance(encoder.usb, UsbDataEncoder)
        
        # 브라우저 데이터로 테스트
        browser_data = {
            'collected_files': [],
            'collection_time': '2025-09-01',
            'detailed_files': [],
            'discovered_profiles': [],
            'statistics': {},
            'temp_directory': '/tmp'
        }
        
        result_encoder = encoder.convert_data(browser_data, Category.BROWSER)
        self.assertIsInstance(result_encoder, BrowserDataEncoder)
        
        # 잘못된 카테고리 테스트
        with self.assertRaises(TypeError):
            encoder.convert_data(browser_data, "invalid_category")

    def test_data_validation_errors(self):
        """데이터 검증 오류 케이스 테스트"""
        encoder = BrowserDataEncoder()
        
        # 빈 데이터
        with self.assertRaises(NotImplementedError):
            encoder.convert_data({})
        
        # 잘못된 키를 가진 데이터
        invalid_data = {
            'wrong_key1': 'value1',
            'wrong_key2': 'value2'
        }
        
        with self.assertRaises(NotImplementedError):
            encoder.convert_data(invalid_data)


class TestDataLoader(unittest.TestCase):
    """DataLoader 클래스 테스트"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.loader = DataLoader()
        
        # 테스트용 JSON 파일 생성
        self.test_data = {
            "collection_info": {"time": "2025-09-01"},
            "test_data": [{"id": 1, "name": "test"}]
        }
        
        self.test_file_path = os.path.join(self.temp_dir, "browser_test_data.json")
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, ensure_ascii=False)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_local_data_load(self):
        """로컬 데이터 로드 기능 테스트"""
        # 디렉토리 설정
        self.loader._set_data_dir(self.temp_dir)
        
        # 데이터 로드
        loaded_data = self.loader.local_data_load(Category.BROWSER)
        
        self.assertEqual(loaded_data, self.test_data)
    
    def test_data_loader_error_cases(self):
        """DataLoader 오류 케이스 테스트"""
        # 존재하지 않는 디렉토리
        with self.assertRaises(NotADirectoryError):
            self.loader._set_data_dir("/non/existent/directory")
        
        # 해당 카테고리 파일이 없는 경우
        empty_dir = tempfile.mkdtemp()
        try:
            with self.assertRaises(FileNotFoundError):
                self.loader.local_data_load(Category.MESSENGER, empty_dir)
        finally:
            import shutil
            shutil.rmtree(empty_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
