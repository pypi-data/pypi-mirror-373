import os
import json
import tempfile
from ..core import Category
import boto3
from botocore.exceptions import NoCredentialsError, ClientError


class DataLoader:
    def __init__(self):
        self.data_dir = "./data/agent_result"
        self.file_path:str

    def local_data_load(self, category: Category, directory=None) -> dict:
        if directory:
            self._set_data_dir(directory)
        self._get_file_path(category)
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def _set_data_dir(self, directory:str) -> None:
        if not os.path.exists(directory):
            raise NotADirectoryError(f"디렉토리가 존재하지 않습니다: {directory}")
        self.data_dir = directory
    
    def _get_file_path(self, category: Category) -> None:
        file_list = os.listdir(self.data_dir)
        matching_files = [filename for filename in file_list if filename.lower().startswith(category.value)]
        
        if not matching_files:
            raise FileNotFoundError(f"No file starts with '{category.value}' in {self.data_dir}")
        
        file_path = os.path.join(self.data_dir, matching_files[0])
        self.file_path = file_path
        
    def s3_data_load(self, category: Category, s3_config: dict) -> dict:
        """
        S3에서 데이터를 로드합니다.
        
        Args:
            category: 데이터 카테고리
            s3_config: S3 설정 딕셔너리
                - bucket (str): S3 버킷 이름
                - task_id (str): 작업 ID (UUID)
                - region (str, optional): AWS 리전
                - profile (str, optional): AWS 프로파일
        
        Returns:
            dict: 로드된 데이터
            
        Example:
            s3_config = {
                'bucket': 'my-forensics-bucket',
                'task_id': '550e8400-e29b-41d4-a716-446655440000',
                'region': 'us-east-1'
            }
            data = loader.s3_data_load(Category.BROWSER, s3_config)
        """
        required_keys = ['bucket', 'task_id']
        for key in required_keys:
            if key not in s3_config:
                raise ValueError(f"s3_config에 '{key}' 파라미터가 필요합니다.")
        
        # task_id와 category를 이용해 S3 키 생성
        s3_key = f"{s3_config['task_id']}/{category.value}_data.json"
        
        self._init_s3_client(s3_config)

        with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            self._s3_client.download_file(
                s3_config['bucket'], 
                s3_key, 
                temp_path
            )
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {e}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise FileNotFoundError(f"S3 파일을 찾을 수 없습니다: s3://{s3_config['bucket']}/{s3_key}")
            elif error_code == 'NoSuchBucket':
                raise FileNotFoundError(f"S3 버킷을 찾을 수 없습니다: {s3_config['bucket']}")
            else:
                raise Exception(f"S3 다운로드 오류: {e}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _init_s3_client(self, s3_config: dict) -> None:
        try:
            client_kwargs = {}
            
            if 'region' in s3_config:
                client_kwargs['region_name'] = s3_config['region']
                
            if 'profile' in s3_config:
                session = boto3.Session(profile_name=s3_config['profile'])
                self._s3_client = session.client('s3', **client_kwargs)
            else:
                self._s3_client = boto3.client('s3', **client_kwargs)
                
        except NoCredentialsError:
            raise NoCredentialsError()