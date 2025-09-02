import boto3
import pandas as pd
import time
import re
import logging
import functools
from typing import Optional, Union, List, Tuple, Callable
import finter
from finter.rest import ApiException
from finter.settings import get_api_client
from botocore.exceptions import ClientError


# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler if no handlers exist
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


PRIMARY_WORKGROUP = "primary"
ATHENA_DEFAULT_OUTPUT_LOCATION = "s3://aws-athena-query-results-quantit/"
MAX_ROW_LIMIT = 50000


def sts_session(func: Callable):
    """
    Decorator to handle AWS STS token expiration by refreshing credentials and retrying the operation.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        from pyiceberg.catalog.glue import GlueCatalog
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                return func(self, *args, **kwargs)
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if error_code in ['ExpiredTokenException', 'InvalidTokenException'] and retry_count < max_retries:
                    logger.info("AWS STS token expired. Refreshing credentials...")
                    # Refresh credentials
                    self.credentials = get_aws_credentials()
                    
                    # Reinitialize clients with new credentials
                    self.athena_client = boto3.client(
                        "athena",
                        aws_access_key_id=self.credentials.aws_access_key_id,
                        aws_secret_access_key=self.credentials.aws_secret_access_key,
                        aws_session_token=self.credentials.aws_session_token,
                        region_name="ap-northeast-2"
                    )
                    self.s3_client = boto3.client(
                        "s3",
                        aws_access_key_id=self.credentials.aws_access_key_id,
                        aws_secret_access_key=self.credentials.aws_secret_access_key,
                        aws_session_token=self.credentials.aws_session_token,
                        region_name="ap-northeast-2"
                    )
                    
                    # Reinitialize catalog with new credentials
                    self.catalog = GlueCatalog(
                        "glue",
                        **{
                            "s3.access-key-id": self.credentials.aws_access_key_id,
                            "s3.secret-access-key": self.credentials.aws_secret_access_key,
                            "s3.session-token": self.credentials.aws_session_token,
                            "s3.region": "ap-northeast-2",
                            "glue.access-key-id": self.credentials.aws_access_key_id,
                            "glue.secret-access-key": self.credentials.aws_secret_access_key,
                            "glue.session-token": self.credentials.aws_session_token,
                            "glue.region": "ap-northeast-2",
                            "uri": "https://glue.ap-northeast-2.amazonaws.com",
                        }
                    )
                    
                    logger.info("Credentials refreshed. Retrying operation...")
                    retry_count += 1
                    continue
                raise
            except Exception as e:
                raise
    return wrapper


def get_aws_credentials():
    api_instance = finter.AWSCredentialsApi(get_api_client())

    try:
        response_body, response_status_code, response_header = api_instance.aws_credentials_quanda_iceberg_retrieve_with_http_info()
        return response_body
    except ApiException as e:
        logger.error("Exception when calling AWSCredentialsApi->aws_credentials_quanda_iceberg_retrieve: %s", str(e))
        return None


class QuandaIceberg:

    def __init__(self):
        from pyiceberg.catalog.glue import GlueCatalog
        self.credentials = get_aws_credentials()
        self.athena_client = boto3.client(
            "athena",
            aws_access_key_id=self.credentials.aws_access_key_id,
            aws_secret_access_key=self.credentials.aws_secret_access_key,
            aws_session_token=self.credentials.aws_session_token,
            region_name="ap-northeast-2"
        )
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.credentials.aws_access_key_id,
            aws_secret_access_key=self.credentials.aws_secret_access_key,
            aws_session_token=self.credentials.aws_session_token,
            region_name="ap-northeast-2"
        )
        self.workgroup = PRIMARY_WORKGROUP
        self.output_location = ATHENA_DEFAULT_OUTPUT_LOCATION
        self.catalog = GlueCatalog(
            "glue",
            **{
                "s3.access-key-id": self.credentials.aws_access_key_id,
                "s3.secret-access-key": self.credentials.aws_secret_access_key,
                "s3.session-token": self.credentials.aws_session_token,
                "s3.region": "ap-northeast-2",
                "glue.access-key-id": self.credentials.aws_access_key_id,
                "glue.secret-access-key": self.credentials.aws_secret_access_key,
                "glue.session-token": self.credentials.aws_session_token,
                "glue.region": "ap-northeast-2",
                "uri": "https://glue.ap-northeast-2.amazonaws.com",
            }
        )

    @sts_session
    def databases(self) -> List[str]:
        """
        List all databases in the Glue catalog.
        """
        namespace_tuples: List[Tuple[str,...]] = self.catalog.list_namespaces()
        return [namespace_tuple[-1] for namespace_tuple in namespace_tuples if len(namespace_tuple)>=1]

    @sts_session
    def tables(self, db_name: str) -> List[str]:
        """
        List all tables in the Glue catalog.
        """
        table_tuples: List[Tuple[str, str]] = self.catalog.list_tables(namespace=db_name)
        return [".".join(table_tuple) for table_tuple in table_tuples if len(table_tuple)>=2]

    @sts_session
    def columns(self, db_name: str, table_name: str):
        """
        Get the table specification from the Glue catalog.
        """
        table = self.catalog.load_table(f"{db_name}.{table_name}")
        return table.specs

    def _validate_and_modify_limit(self, query: str) -> str:
        """
        Validate and modify the LIMIT clause in the query to ensure it doesn't exceed MAX_ROW_LIMIT
        
        Args:
            query (str): Original SQL query
            
        Returns:
            str: Modified query with validated LIMIT clause
        """
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # Check if query already has a LIMIT clause
        limit_match = re.search(r"\blimit\s+(\d+)\b", query_lower)
        
        if limit_match:
            # Extract the current limit value
            current_limit = int(limit_match.group(1))
            
            # If limit exceeds MAX_ROW_LIMIT, modify it
            if current_limit > MAX_ROW_LIMIT:
                logger.warning("Query limit %d exceeds maximum allowed limit %d. Adjusting to %d.", 
                             current_limit, MAX_ROW_LIMIT, MAX_ROW_LIMIT)
                return re.sub(r"\blimit\s+\d+\b", f"LIMIT {MAX_ROW_LIMIT}", query, flags=re.IGNORECASE)
            return query
        else:
            # Add default limit if no limit is specified
            return f"{query} LIMIT {MAX_ROW_LIMIT}"

    @sts_session
    def query(self, query: str, db_name: Optional[str] = None) -> pd.DataFrame:
        """
        Execute Athena query and return results as pandas DataFrame.
        Results are limited to a maximum of 50,000 rows.
        
        Args:
            query (str): SQL query to execute. Can include database name in the query (e.g., SELECT * FROM "db"."table")
            db_name (str, optional): Default database to use if not specified in the query
            
        Returns:
            pd.DataFrame: Query results as pandas DataFrame
        """
        try:
            # Validate and modify query limit
            modified_query = self._validate_and_modify_limit(query)
            
            # Prepare query execution parameters
            query_params = {
                "QueryString": modified_query,
                "WorkGroup": PRIMARY_WORKGROUP,
                "ResultConfiguration": {
                    "OutputLocation": ATHENA_DEFAULT_OUTPUT_LOCATION
                }
            }
            
            # Add database context if provided
            if db_name:
                query_params["QueryExecutionContext"] = {"Database": db_name}
            
            # Start query execution
            response = self.athena_client.start_query_execution(**query_params)
            
            query_execution_id = response["QueryExecutionId"]
            logger.info("Started query execution with ID: %s", query_execution_id)
            
            # Wait for query to complete
            while True:
                query_status = self.athena_client.get_query_execution(
                    QueryExecutionId=query_execution_id
                )["QueryExecution"]["Status"]["State"]
                
                if query_status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
                    break
                    
                time.sleep(1)
            
            if query_status == "FAILED":
                error_message = self.athena_client.get_query_execution(
                    QueryExecutionId=query_execution_id
                )["QueryExecution"]["Status"]["StateChangeReason"]
                logger.error("Query failed: %s", error_message)
                raise Exception(f"Query failed: {error_message}")
            
            logger.info("Query execution completed successfully")
            
            # Get query results
            results = []
            paginator = self.athena_client.get_paginator("get_query_results")
            
            for page in paginator.paginate(QueryExecutionId=query_execution_id):
                for row in page["ResultSet"]["Rows"]:
                    results.append([field.get("VarCharValue", "") for field in row["Data"]])
            
            # Convert to DataFrame
            if not results:
                logger.info("Query returned no results")
                return pd.DataFrame()
            
            # First row contains column names
            columns = results[0]
            data = results[1:]
            
            df = pd.DataFrame(data, columns=columns)
            logger.info("Retrieved %d rows of data", len(df))
            return df
            
        except Exception as e:
            logger.error("Error executing query: %s", str(e))
            raise