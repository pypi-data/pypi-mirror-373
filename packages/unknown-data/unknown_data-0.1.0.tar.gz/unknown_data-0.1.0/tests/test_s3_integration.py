"""
S3 데이터 로더 테스트
"""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import NoCredentialsError, ClientError

from src.unknown_data.loader.loader import DataLoader
from src.unknown_data.core import Category


class TestS3DataLoader:
    """S3 데이터 로더 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.loader = DataLoader()
        self.sample_s3_config = {
            'bucket': 'test-bucket',
            'task_id': 'test-task-123',
            'region': 'us-east-1'
        }
        self.sample_data = {
            "browser_data": [
                {"url": "https://example.com", "visit_count": 10},
                {"url": "https://google.com", "visit_count": 5}
            ]
        }
    
    @patch('src.unknown_data.loader.loader.boto3.client')
    def test_s3_data_load_success(self, mock_boto_client):
        """S3에서 성공적으로 데이터를 로드하는 테스트"""
        # Mock S3 클라이언트 설정
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        
        # 임시 파일 생성 및 데이터 작성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            json.dump(self.sample_data, temp_file)
            temp_path = temp_file.name
        
        # download_file 모킹 - 실제로는 temp_path에 파일이 이미 있음
        def mock_download(bucket, key, local_path):
            # 임시 파일을 local_path로 복사
            with open(temp_path, 'r') as src, open(local_path, 'w') as dst:
                dst.write(src.read())
        
        mock_s3.download_file.side_effect = mock_download
        
        try:
            # 테스트 실행
            result = self.loader.s3_data_load(Category.BROWSER, self.sample_s3_config)
            
            # 검증
            assert result == self.sample_data
            mock_s3.download_file.assert_called_once()
            # 호출 인자를 개별적으로 확인
            call_args = mock_s3.download_file.call_args
            assert call_args[0][0] == 'test-bucket'  # bucket
            assert call_args[0][1] == 'test-task-123/browser_data.json'  # key (task_id/category_data.json)
            assert call_args[0][2].endswith('.json')  # temp file path
        finally:
            # 정리
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_s3_config_validation(self):
        """S3 설정 검증 테스트"""
        invalid_configs = [
            {},  # 빈 설정
            {'bucket': 'test-bucket'},  # task_id 누락
            {'task_id': 'test-task-123'},  # bucket 누락
        ]
        
        for config in invalid_configs:
            with pytest.raises(ValueError):
                self.loader.s3_data_load(Category.BROWSER, config)
    
    @patch('src.unknown_data.loader.loader.boto3.client')
    def test_s3_no_credentials_error(self, mock_boto_client):
        """AWS 자격 증명이 없을 때의 에러 테스트"""
        mock_boto_client.side_effect = NoCredentialsError()
        
        with pytest.raises(NoCredentialsError):
            self.loader.s3_data_load(Category.BROWSER, self.sample_s3_config)
    
    @patch('src.unknown_data.loader.loader.boto3.client')
    def test_s3_file_not_found(self, mock_boto_client):
        """S3 파일이 없을 때의 에러 테스트"""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        
        # NoSuchKey 에러 모킹
        error_response = {'Error': {'Code': 'NoSuchKey'}}
        mock_s3.download_file.side_effect = ClientError(error_response, 'GetObject')
        
        with pytest.raises(FileNotFoundError, match="S3 파일을 찾을 수 없습니다"):
            self.loader.s3_data_load(Category.BROWSER, self.sample_s3_config)
    
    @patch('src.unknown_data.loader.loader.boto3.client')
    def test_s3_bucket_not_found(self, mock_boto_client):
        """S3 버킷이 없을 때의 에러 테스트"""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        
        # NoSuchBucket 에러 모킹
        error_response = {'Error': {'Code': 'NoSuchBucket'}}
        mock_s3.download_file.side_effect = ClientError(error_response, 'GetObject')
        
        with pytest.raises(FileNotFoundError, match="S3 버킷을 찾을 수 없습니다"):
            self.loader.s3_data_load(Category.BROWSER, self.sample_s3_config)
    
    @patch('src.unknown_data.loader.loader.boto3.client')
    def test_s3_invalid_json(self, mock_boto_client):
        """잘못된 JSON 파일 테스트"""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        
        # 잘못된 JSON이 담긴 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_file.write("invalid json content")
            temp_path = temp_file.name
        
        def mock_download(bucket, key, local_path):
            with open(temp_path, 'r') as src, open(local_path, 'w') as dst:
                dst.write(src.read())
        
        mock_s3.download_file.side_effect = mock_download
        
        try:
            with pytest.raises(ValueError, match="JSON 파싱 오류"):
                self.loader.s3_data_load(Category.BROWSER, self.sample_s3_config)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('src.unknown_data.loader.loader.boto3.Session')
    @patch('src.unknown_data.loader.loader.boto3.client')
    def test_s3_with_profile(self, mock_boto_client, mock_session):
        """AWS 프로파일을 사용한 S3 접근 테스트"""
        config_with_profile = {
            'bucket': 'test-bucket',
            'task_id': 'test-task-123',
            'profile': 'test-profile'
        }
        
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        mock_s3 = Mock()
        mock_session_instance.client.return_value = mock_s3
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            json.dump(self.sample_data, temp_file)
            temp_path = temp_file.name
        
        def mock_download(bucket, key, local_path):
            with open(temp_path, 'r') as src, open(local_path, 'w') as dst:
                dst.write(src.read())
        
        mock_s3.download_file.side_effect = mock_download
        
        try:
            result = self.loader.s3_data_load(Category.BROWSER, config_with_profile)
            
            # 검증
            assert result == self.sample_data
            mock_session.assert_called_once_with(profile_name='test-profile')
            mock_session_instance.client.assert_called_once_with('s3')
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestS3UsageExample:
    """S3 사용 예제 테스트"""
    
    @patch('src.unknown_data.loader.loader.boto3.client')
    def test_usage_example(self, mock_boto_client):
        """실제 사용 예제 테스트"""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        
        sample_data = {
            "browser_data": [
                {"url": "https://example.com", "visit_count": 10}
            ]
        }
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            json.dump(sample_data, temp_file)
            temp_path = temp_file.name
        
        def mock_download(bucket, key, local_path):
            with open(temp_path, 'r') as src, open(local_path, 'w') as dst:
                dst.write(src.read())
        
        mock_s3.download_file.side_effect = mock_download
        
        try:
            # 사용 예제
            loader = DataLoader()
            s3_config = {
                'bucket': 'my-forensic-data',
                'task_id': 'test-task-456',
                'region': 'us-west-2'
            }
            
            data = loader.s3_data_load(Category.BROWSER, s3_config)
            
            # 검증
            assert 'browser_data' in data
            assert len(data['browser_data']) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
