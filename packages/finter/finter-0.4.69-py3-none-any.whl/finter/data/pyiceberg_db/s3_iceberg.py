import re
from datetime import datetime
import finter
from finter.rest import ApiException
from finter.settings import get_api_client


def get_aws_credentials(database_name, table_name=None):
    api_instance = finter.AWSCredentialsApi(get_api_client())

    try:
        api_response = api_instance.aws_credentials_s3_iceberg_retrieve(
            database_name=database_name,
            table_name=table_name,
        )
        return api_response
    except ApiException as e:
        print("Exception when calling AWSCredentialsApi->aws_credentials_s3_iceberg_retrieve: %s\n" % e)
        return None


class S3Iceberg:
    from pyiceberg.catalog.glue import GlueCatalog
    from pyiceberg.expressions import AlwaysTrue

    @staticmethod
    def _sql_query_to_iceberg_params(query):
        match = re.search(r"select\s+(.*?)\s+from\s+(\w+)(?:\s+where\s+(.*?))?(?=\s+limit|\s*$)(?:\s+limit\s+(\d+))?", query, re.IGNORECASE)
        
        if match:
            selected_fields = tuple(match.group(1).split(","))
            table_name = match.group(2)
            where_clause = match.group(3) if match.group(3) else S3Iceberg.AlwaysTrue()
            limit_num = int(match.group(4)) if match.group(4) else 10000
        else:
            print(f"Query convert Fail. \nPlease check query : {query}")
        return table_name, where_clause, selected_fields, limit_num
    
    @staticmethod
    def get_data(
        db_name,
        table_name,
        row_filter=AlwaysTrue(),
        selected_fields=("*",),
        limit_num=None,
        snapshot_time=None
        ):
        credentials = get_aws_credentials(database_name=db_name, table_name=table_name)
        catalog = S3Iceberg.GlueCatalog(
            "get_process",
            **{
                "s3.access-key-id": credentials.aws_access_key_id,
                "s3.secret-access-key": credentials.aws_secret_access_key,
                "s3.session-token": credentials.aws_session_token,
                "s3.region": "ap-northeast-2",
                "glue.access-key-id": credentials.aws_access_key_id,
                "glue.secret-access-key": credentials.aws_secret_access_key,
                "glue.session-token": credentials.aws_session_token,
                "glue.region": "ap-northeast-2",
                "uri": "https://glue.ap-northeast-2.amazonaws.com",
            }
        )
        full_name = f"{db_name}.{table_name}"
        table = catalog.load_table(full_name)
        scan_param = {
            "row_filter": row_filter,
            "selected_fields": selected_fields,
            "limit": limit_num
        }
        
        if snapshot_time:
            snapshot = table.snapshot_as_of_time(snapshot_time)
            if snapshot:
                snapshot_id = snapshot.snapshot_id
                scan_param['snapshot_id'] = snapshot_id
            else:
                print(f"There is no data when {snapshot_time}\n Return current data")
                
        return table.scan(**scan_param)

    @staticmethod
    def get_snapshot_list(db_name, table_name):
        credentials = get_aws_credentials(database_name=db_name, table_name=table_name)
        catalog = S3Iceberg.GlueCatalog(
            "get_process",
            **{
                "s3.access-key-id": credentials.aws_access_key_id,
                "s3.secret-access-key": credentials.aws_secret_access_key,
                "s3.session-token": credentials.aws_session_token,
                "s3.region": "ap-northeast-2",
                "glue.access-key-id": credentials.aws_access_key_id,
                "glue.secret-access-key": credentials.aws_secret_access_key,
                "glue.session-token": credentials.aws_session_token,
                "glue.region": "ap-northeast-2",
                "uri": "https://glue.ap-northeast-2.amazonaws.com",
            }
        )
        table_name = f"{db_name}.{table_name}"
        table = catalog.load_table(table_name)

        snapshot_list = []
        for snapshot in table.snapshots():
            timestamp = datetime.fromtimestamp(snapshot.timestamp_ms / 1000)
            snapshot_list.append((snapshot.snapshot_id, timestamp))

        return snapshot_list
    
    @staticmethod
    def get_spec(db_name, table_name):
        credentials = get_aws_credentials(database_name=db_name, table_name=table_name)
        catalog = S3Iceberg.GlueCatalog(
            "get_process",
            **{
                "s3.access-key-id": credentials.aws_access_key_id,
                "s3.secret-access-key": credentials.aws_secret_access_key,
                "s3.session-token": credentials.aws_session_token,
                "s3.region": "ap-northeast-2",
                "glue.access-key-id": credentials.aws_access_key_id,
                "glue.secret-access-key": credentials.aws_secret_access_key,
                "glue.session-token": credentials.aws_session_token,
                "glue.region": "ap-northeast-2",
                "uri": "https://glue.ap-northeast-2.amazonaws.com",
            }
        )
        table_name = f"{db_name}.{table_name}"
        table = catalog.load_table(table_name)
        return {"Table_spec": table, "Partition_spec": table.spec(), "Sort_spec": table.sort_order()}

    @staticmethod
    def table_exists(db_name, table_name):        
        from pyiceberg.exceptions import NoSuchTableError
        credentials = get_aws_credentials(database_name=db_name, table_name=table_name)
        catalog = S3Iceberg.GlueCatalog(
            "get_process",
            **{
                "s3.access-key-id": credentials.aws_access_key_id,
                "s3.secret-access-key": credentials.aws_secret_access_key,
                "s3.session-token": credentials.aws_session_token,
                "s3.region": "ap-northeast-2",
                "glue.access-key-id": credentials.aws_access_key_id,
                "glue.secret-access-key": credentials.aws_secret_access_key,
                "glue.session-token": credentials.aws_session_token,
                "glue.region": "ap-northeast-2",
                "uri": "https://glue.ap-northeast-2.amazonaws.com",
            }
        )
        
        try:
            catalog.load_table(table_name)
            return True
        except NoSuchTableError:
            return False
