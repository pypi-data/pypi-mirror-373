import unittest
import tempfile
import os
import json
import pandas as pd
from unknown_data import (
    Category, Encoder, DataLoader, DataSaver, 
    BrowserDataEncoder, DeletedDataEncoder
)

class TestIntegrationScenarios(unittest.TestCase):
    """실제 사용 시나리오를 시뮬레이션하는 통합 테스트"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, "data")
        self.result_dir = os.path.join(self.temp_dir, "results")
        os.makedirs(self.data_dir)
        os.makedirs(self.result_dir)
        
        # 테스트용 브라우저 데이터 파일 생성
        browser_data = self.get_sample_browser_data()
        browser_file = os.path.join(self.data_dir, "browser_results.json")
        with open(browser_file, 'w', encoding='utf-8') as f:
            json.dump(browser_data, f, ensure_ascii=False, indent=2)
            
        # 테스트용 삭제된 파일 데이터 생성
        deleted_data = self.get_sample_deleted_data()
        deleted_file = os.path.join(self.data_dir, "deleted_results.json") 
        with open(deleted_file, 'w', encoding='utf-8') as f:
            json.dump(deleted_data, f, ensure_ascii=False, indent=2)

    def get_sample_browser_data(self):
        return {
            "collected_files": [
                {
                    "file_name": "History",
                    "file_path": "/Users/user/Library/Application Support/Google/Chrome/Default/History",
                    "file_type": "sqlite",
                    "success": True,
                    "browser_type": "chrome"
                },
                {
                    "file_name": "Cookies",
                    "file_path": "/Users/user/Library/Application Support/Google/Chrome/Default/Cookies",
                    "file_type": "sqlite",
                    "success": True,
                    "browser_type": "chrome"
                }
            ],
            "collection_time": "2023-01-01T10:00:00",
            "detailed_files": [
                {
                    "file_name": "History",
                    "file_path": "/Users/user/Library/Application Support/Google/Chrome/Default/History",
                    "file_type": "sqlite",
                    "success": True,
                    "browser_type": "chrome",
                    "table_names": ["urls", "visits", "downloads"],
                    "sqlite_data": {
                        "urls": [
                            {"id": 1, "url": "https://example.com", "title": "Example", "visit_count": 5},
                            {"id": 2, "url": "https://google.com", "title": "Google", "visit_count": 10}
                        ],
                        "visits": [
                            {"id": 1, "url": 1, "visit_time": 13320000000000000, "from_visit": 0},
                            {"id": 2, "url": 2, "visit_time": 13320000000000001, "from_visit": 1}
                        ],
                        "downloads": [
                            {"id": 1, "current_path": "/Users/test/file.pdf", "url": "https://example.com/file.pdf"}
                        ]
                    }
                },
                {
                    "file_name": "Cookies",
                    "file_path": "/Users/user/Library/Application Support/Google/Chrome/Default/Cookies",
                    "file_type": "sqlite",
                    "success": True,
                    "browser_type": "chrome",
                    "table_names": ["cookies"],
                    "sqlite_data": {
                        "cookies": [
                            {"name": "session_id", "value": "abc123", "host_key": ".example.com", "path": "/"},
                            {"name": "user_pref", "value": "dark_mode", "host_key": ".google.com", "path": "/"}
                        ]
                    }
                }
            ],
            "discovered_profiles": [
                {
                    "profile_name": "Default",
                    "profile_path": "/Users/user/Library/Application Support/Google/Chrome/Default",
                    "browser": "Chrome"
                }
            ],
            "statistics": {
                "total_files": 2,
                "successful_files": 2,
                "failed_files": 0,
                "total_size": 1024000
            },
            "temp_directory": "/tmp/browser_extraction"
        }

    def get_sample_deleted_data(self):
        return {
            "collection_info": {
                "scan_time": "2025-09-01 10:00:00",
                "scan_type": "full_system",
                "tools_used": ["MFT Parser", "Recycle Bin Analyzer"]
            },
            "data_sources": {
                "mft_analysis": True,
                "recycle_bin_analysis": True,
                "free_space_carving": False
            },
            "mft_deleted_files": [
                {
                    "file_name": "confidential_report.docx",
                    "original_path": "C:\\Users\\john\\Documents\\confidential_report.docx",
                    "deleted_time": "2025-08-30 15:30:00",
                    "file_size": 245760,
                    "file_signature": "PK",
                    "recoverable": True
                },
                {
                    "file_name": "personal_photos.zip",
                    "original_path": "C:\\Users\\john\\Pictures\\personal_photos.zip",
                    "deleted_time": "2025-08-29 09:15:00",
                    "file_size": 15728640,
                    "file_signature": "PK",
                    "recoverable": False
                }
            ],
            "recycle_bin_files": [
                {
                    "original_name": "old_project.zip",
                    "deleted_path": "$RECYCLE.BIN\\S-1-5-21\\$R123ABC.zip",
                    "deleted_time": "2025-08-31 11:20:00",
                    "file_size": 5242880,
                    "delete_user": "john"
                }
            ],
            "statistics": {
                "total_deleted_files": 2,
                "total_recycle_bin_files": 1,
                "total_size_deleted": 21217280,
                "recoverable_files": 1
            }
        }

    def test_complete_browser_workflow(self):
        """완전한 브라우저 데이터 처리 워크플로우 테스트"""
        # 1. 데이터 로딩
        loader = DataLoader()
        data = loader.local_data_load(Category.BROWSER, self.data_dir)
        
        # 2. 데이터 인코딩
        encoder = Encoder()
        browser_encoder = encoder.convert_data(data, Category.BROWSER)
        
        # 3. 결과 검증
        self.assertIsInstance(browser_encoder, BrowserDataEncoder)
        result_dfs = browser_encoder.get_result_dfs()
        
        # 4. 결과가 비어있지 않은지 확인
        self.assertGreater(len(result_dfs.data), 0)
        
        # 5. 특정 데이터프레임 검증 - 브라우저 데이터의 경우 다양한 결과가 나올 수 있음
        found_statistics = False
        found_profiles = False
        
        for result_df in result_dfs.data:
            if result_df.name == "statistics":
                found_statistics = True
                self.assertFalse(result_df.data.empty)
            elif result_df.name == "profile":
                found_profiles = True
                self.assertFalse(result_df.data.empty)
        
        self.assertTrue(found_statistics, "Statistics 데이터프레임이 생성되지 않았습니다")
        self.assertTrue(found_profiles, "Profile 데이터프레임이 생성되지 않았습니다")
        
        # 6. 데이터 저장
        saver = DataSaver(self.result_dir)
        saver.save_all(result_dfs)
        
        # 7. 저장된 파일 확인
        saved_files = os.listdir(self.result_dir)
        self.assertGreater(len(saved_files), 0)

    def test_complete_deleted_files_workflow(self):
        """완전한 삭제된 파일 데이터 처리 워크플로우 테스트"""
        # 1. 데이터 로딩
        loader = DataLoader()
        data = loader.local_data_load(Category.DELETED, self.data_dir)
        
        # 2. 데이터 인코딩
        encoder = Encoder()
        deleted_encoder = encoder.convert_data(data, Category.DELETED)
        
        # 3. 결과 검증
        self.assertIsInstance(deleted_encoder, DeletedDataEncoder)
        result_dfs = deleted_encoder.get_result_dfs()
        
        # 4. 결과가 비어있지 않은지 확인
        self.assertGreater(len(result_dfs.data), 0)
        
        # 5. 특정 데이터프레임 검증
        found_mft = False
        found_recycle = False
        found_statistics = False
        
        for result_df in result_dfs.data:
            if result_df.name == "mft_deleted_files":
                found_mft = True
                self.assertFalse(result_df.data.empty)
                # MFT 데이터 확인
                self.assertIn("file_name", result_df.data.columns)
                self.assertEqual(len(result_df.data), 2)
            elif result_df.name == "recycle_bin_files":
                found_recycle = True
                self.assertFalse(result_df.data.empty)
                # Recycle Bin 데이터 확인
                self.assertIn("original_name", result_df.data.columns)
                self.assertEqual(len(result_df.data), 1)
            elif result_df.name == "statistics":
                found_statistics = True
                self.assertFalse(result_df.data.empty)
        
        self.assertTrue(found_mft, "MFT 삭제 파일 데이터프레임이 생성되지 않았습니다")
        self.assertTrue(found_recycle, "휴지통 파일 데이터프레임이 생성되지 않았습니다")
        self.assertTrue(found_statistics, "Statistics 데이터프레임이 생성되지 않았습니다")

    def test_cross_category_processing(self):
        """여러 카테고리 데이터 동시 처리 테스트"""
        loader = DataLoader()
        encoder = Encoder()
        saver = DataSaver(self.result_dir)
        
        # 브라우저 데이터 처리
        browser_data = loader.local_data_load(Category.BROWSER, self.data_dir)
        browser_encoder = encoder.convert_data(browser_data, Category.BROWSER)
        browser_results = browser_encoder.get_result_dfs()
        
        # 삭제된 파일 데이터 처리
        deleted_data = loader.local_data_load(Category.DELETED, self.data_dir)
        deleted_encoder = encoder.convert_data(deleted_data, Category.DELETED)
        deleted_results = deleted_encoder.get_result_dfs()
        
        # 모든 결과 저장
        saver.save_all(browser_results)
        saver.save_all(deleted_results)
        
        # 저장된 파일 확인
        saved_files = os.listdir(self.result_dir)
        self.assertGreater(len(saved_files), 2)  # 최소 2개 이상의 파일이 저장되어야 함

    def tearDown(self):
        """테스트 후 임시 파일 정리"""
        import shutil
        shutil.rmtree(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
