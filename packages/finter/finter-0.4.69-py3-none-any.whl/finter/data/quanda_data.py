import pandas as pd
import requests
from finter.api.quanda_data_api import QuandaDataApi
from finter.framework_model import QuandaLoader
from finter.settings import logger


class QuandaData:

    @staticmethod
    def help():
        help_str = \
"""
# get file type data
# in case of loading excel file, maybe you need install openpyxl package
# ex) pip install openpyxl
import pandas as pd
from io import BytesIO
data = QuandaData.get('object_name', is_file_type=True)
df = pd.read_excel(BytesIO(data))

# get json data
import pandas as pd
data = QuandaData.get('object_name')
df = pd.read_json(data)
"""
        logger.info(help_str)

    @staticmethod
    def object_list(prefix='', bucket=None, personal=False):
        try:
            data = QuandaLoader.get_object_list(
                object_type='path', object_value=prefix, bucket=bucket, personal=personal,
            )
            return data
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return []

    @staticmethod
    def dir_list(prefix='', bucket=None, personal=False):
        try:
            data = QuandaLoader.get_dir_list(
                object_type='path', object_value=prefix, bucket=bucket, personal=personal,
            )
            return data
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return []

    @staticmethod
    def object_list_v2():
        try:
            data = requests.get(
                "https://api-quanda-drive.quantit.io/drive/file/all"
            )
            return data
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return []

    @staticmethod
    def get(object_name, is_file_type=False, bucket=None, personal=False):
        s3_uri_prefix = "s3://"
        if isinstance(object_name, str) and s3_uri_prefix in object_name:
            s3_uri_prefix = object_name.replace("s3://", "")
            bucket = s3_uri_prefix.split('/')[0]
            object_name = '/'.join(s3_uri_prefix.split('/')[1:])

        if is_file_type:
            return QuandaLoader.get_data(object_name=object_name, bucket=bucket, personal=personal)
        else:
            assert bucket is None, "bucket is not supported for non-file type data"
            data = QuandaDataApi().quanda_data_get_retrieve(object_name=object_name, personal=personal)
            data = data['data']
        return data

    @staticmethod
    def put(data, key, personal=False):
        try:
            if not personal:
                raise Exception("Personal is required")

            if not isinstance(data, pd.DataFrame):
                raise Exception("Data should be pandas DataFrame")

            QuandaDataApi().quanda_data_create(
                data=data.to_json(), object_name=key, personal=personal
            )
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    def upload_file(file, personal=False):
        try:
            if not personal:
                raise Exception("Personal is required")

            QuandaDataApi().quanda_data_upload_file_create(
                file_path=file,
                personal=personal
            )
        except Exception as e:
            logger.error(e)
            return None
