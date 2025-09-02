from datetime import datetime

class Table:
    """
    read only pyiceberg format db table
    """
    
    def __init__(self, db_name):
        from finter.data.pyiceberg_db.s3_iceberg import S3Iceberg
        self.S3Iceberg = S3Iceberg
        
        self.db_name = db_name
        self.field_dict = {}
        self.cache = {}
    
    def query(self, query, snapshot_time:datetime=None):
        table_name, row_filter, selected_fields, limit_num = self.S3Iceberg._sql_query_to_iceberg_params(query)
        
        try:
            result = self.S3Iceberg.get_data(
                self.db_name,
                table_name,
                row_filter,
                selected_fields,
                limit_num,
                snapshot_time
            ).to_pandas()
            
            self.cache[query] = result.copy()
            return result
        except TypeError as e:
            assert str(e) != "Cannot convert LongLiteral into string", f"The type in the WHERE clause of your query does not match the database column type. \nPlease check Table.fields('{table_name}')"
            raise e  # 다른 TypeError는 그대로 다시 발생
        
    def fields(self, table_name):
        if not self.field_dict.get(table_name):
            self.field_dict[table_name] = self.S3Iceberg.get_spec(self.db_name, table_name)['Table_spec']
        return self.field_dict[table_name]