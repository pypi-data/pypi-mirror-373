import blosc
import boto3
from botocore.exceptions import ClientError
from enum import Enum

import finter
from finter.rest import ApiException
from finter.settings import get_api_client
from finter.settings import logger


class ErrorType(str, Enum):
    NO_DATA = "No data"

    def __str__(self):
        return str(self.name)


def get_aws_credentials(object_type, object_value, bucket, personal):
    api_instance = finter.AWSCredentialsApi(get_api_client())

    try:
        if bucket:
            api_response = api_instance.aws_credentials_quanda_retrieve(
                object_type=object_type,
                object_value=object_value,
                bucket=bucket,
                personal=personal
            )
        else:
            api_response = api_instance.aws_credentials_quanda_retrieve(
                object_type=object_type,
                object_value=object_value,
                personal=personal
            )
        return api_response
    except ApiException as e:
        logger.error("Exception when calling AWSCredentialsApi->aws_credentials_quanda_retrieve: %s\n" % e)
        return None


def get_user_info():
    api_instance = finter.UserApi(get_api_client())
    user = api_instance.user_info_retrieve(item='id')
    return user


class QuandaLoader:
    bucket = 'quanda-data-production'

    @staticmethod
    def get_object_full_path(object_value, personal=False):
        if personal:
            user = get_user_info()
            return f"personal/{user.data}/{object_value}"
        return object_value

    @staticmethod
    def _get_s3_client(object_type, object_value, bucket, personal):
        credentials = get_aws_credentials(object_type, object_value, bucket, personal)
        if credentials is None:
            raise Exception(f"Access to unauthorized data({object_value}). Please check the data permission.")
        else:
            return boto3.client(
                's3',
                aws_access_key_id=credentials.aws_access_key_id,
                aws_secret_access_key=credentials.aws_secret_access_key,
                aws_session_token=credentials.aws_session_token
            )

    @classmethod
    def get_object_list(cls, object_type, object_value, bucket=None, personal=False):
        if bucket is None:
            bucket = cls.bucket
        try:
            object_value = cls.get_object_full_path(object_value, personal)
            s3_client = cls._get_s3_client(object_type, object_value, bucket, personal)
            paginator = s3_client.get_paginator('list_objects_v2')

            response_iterator = paginator.paginate(
                Bucket=bucket if bucket else cls.bucket,
                Prefix=object_value
            )
            result = []
            for page in response_iterator:
                for content in page.get('Contents', []):
                    result.append(content['Key'])

            return result
        except Exception as e:
            raise Exception(f"QuandaLoader.get_object_list failed: {e}")

    @classmethod
    def get_dir_list(cls, object_type, object_value, bucket=None, personal=False):
        if bucket is None:
            bucket = cls.bucket
        try:
            # object_value가 '/'로 끝나지 않으면 추가
            if not object_value.endswith("/"):
                object_value += "/"

            object_value = cls.get_object_full_path(object_value, personal)
            s3_client = cls._get_s3_client(object_type, object_value, bucket, personal)
            paginator = s3_client.get_paginator('list_objects_v2')

            response_iterator = paginator.paginate(
                Bucket=bucket,
                Prefix=object_value,
                Delimiter="/"  # 디렉토리 단위로 가져오기
            )

            result = []
            for page in response_iterator:
                for prefix in page.get('CommonPrefixes', []):  # 디렉토리 목록 추출
                    # 전체 경로에서 object_value 부분을 제외하고 디렉토리명만 추출
                    dir_name = prefix['Prefix'].replace(object_value, "").rstrip("/")
                    result.append(dir_name)

            return result
        except Exception as e:
            raise Exception(f"QuandaLoader.get_dir_list failed: {e}")

    @classmethod
    def get_data(cls, object_name, bucket=None, personal=False):
        if bucket is None:
            bucket = cls.bucket
        object_type = "name"

        try:
            object_value = cls.get_object_full_path(object_name, personal)
            s3_client = cls._get_s3_client(object_type, object_value, bucket, personal)

            response = s3_client.get_object(Bucket=bucket, Key=object_value)
            data = response['Body'].read()

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code in ('NoSuchKey', 'AccessDenied'):
                raise Exception(str(ErrorType.NO_DATA))

            raise Exception(f"QuandaLoader.get_data failed: {e}")

        except Exception as e:
            raise Exception(f"QuandaLoader.get_data failed: {e}")

        try:
            return blosc.decompress(data)
        except Exception:
            pass

        return data
