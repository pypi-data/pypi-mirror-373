import io
import json
import pandas as pd
from finter.api.quanda_db_api import QuandaDbApi
from finter.settings import logger


class DB:
    """
    read only db
    """

    def __init__(self, db_name):
        try:
            self.table_list = QuandaDbApi().quanda_db_table_name_list_retrieve(db=db_name)
        except Exception as e:
            logger.error(f"API call failed: {e}")
            logger.error(f"not supported db: {db_name}")
            raise ValueError(f"not supported db: {db_name}")
        self.table_list = self.table_list['data']
        self.db_name = db_name
        self.column_dict = {}
        self.cache = {}

    def tables(self):
        return self.table_list

    def columns(self, table_name):
        if not self.column_dict.get(table_name):
            data = QuandaDbApi().quanda_db_column_list_retrieve(db=self.db_name, table=table_name)
            self.column_dict[table_name] = data['data']
        return self.column_dict[table_name]

    def query(self, query):
        result = self.cache.get(query)
        if result is None or result.empty:
            # TODO. quanda_db to pyicevberg
            # from finter.data.pyiceberg_db.s3_iceberg import S3Iceberg
            # table_name, row_filter, selected_fields, limit_num = S3Iceberg._sql_query_to_iceberg_params(query)
            # result = S3Iceberg.get_data(
            #     self.db_name,
            #     table_name,
            #     row_filter,
            #     selected_fields,
            #     limit_num
            # ).to_pandas()

            response = QuandaDbApi().quanda_db_query_retrieve(db=self.db_name, query=query)

            # Read the content and decode it
            content = response.read()
            content = content.decode('utf-8')  # Decode bytes to string

            try:
                # Split metadata and CSV data
                metadata_json, csv_data = content.split('\n', 1)

                # Parse metadata
                metadata = json.loads(metadata_json)

                # Read CSV data
                df = pd.read_csv(io.StringIO(csv_data), names=metadata['column_names'])

                # Set dtypes
                for col, dtype_str in metadata['dtypes'].items():
                    try:
                        if dtype_str == 'object':
                            # Keep object columns as is
                            continue
                        elif dtype_str.startswith('datetime'):
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                        elif dtype_str == 'bool':
                            df[col] = df[col].astype('bool')
                        elif 'int' in dtype_str:
                            df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype_str)
                        elif 'float' in dtype_str:
                            df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype_str)
                        else:
                            df[col] = df[col].astype(dtype_str)
                    except ValueError as e:
                        logger.error(f"Warning: Could not convert column '{col}' to {dtype_str}. Error: {str(e)}")
                        # Keep the column as is if conversion fails

                self.cache[query] = df
                result = df
            except Exception as e:
                logger.error(f"Error processing response: {str(e)}")
                # You might want to re-raise the exception or handle it differently
                raise

        return result
