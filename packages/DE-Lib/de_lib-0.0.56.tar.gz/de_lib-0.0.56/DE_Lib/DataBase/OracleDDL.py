from logging import exception

import pandas as pd

class OracleDDL:
    def __init__(self):
        msg = result = None, None
        try:
            ...
        except Exception as error:
            msg = error
            result = msg
        finally:
            print(result)


    def map_dtype_to_oracle(self, dtype):
        msg = result = None, None
        try:
            if pd.api.types.is_integer_dtype(dtype):
                result =  "NUMBER"
            elif pd.api.types.is_float_dtype(dtype):
                result =  "FLOAT"
            elif pd.api.types.is_bool_dtype(dtype):
                result =  "CHAR(1)"  # True = 'Y', False = 'N'
            elif pd.api.types.is_string_dtype(dtype):
                result =  "VARCHAR2(255)"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                result =  "DATE"
            else:
                result =  "VARCHAR2(4000)"
            result = "VARCHAR2(4000)"
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
        
    def generate_create_table_sql(self, table_name, df):
        msg = result = None, None
        try:
            columns = []
            for col in df.columns:
                colname = col.lower()
                oracle_type = self.map_dtype_to_oracle(df[col].dtype)
                columns.append(f"{colname} {oracle_type}")
            columns_sql = ",\n  ".join(columns)
            result = f"CREATE TABLE {table_name} (\n  {columns_sql}\n)"
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result  

    def truncate_table(self, table_name):
        msg = result = None, None
        try:
            result = f"TRUNCATE TABLE {table_name}"
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def prepare_data_for_insert(self, df):
        msg = result = None, None
        try:
            def convert_row(row):
                return tuple(
                    'Y' if isinstance(val, bool) and val else 'N' if isinstance(val, bool) else val for val in row)
            result = [convert_row(row) for row in df.itertuples(index=False, name=None)]
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def create_table_and_insert_data(self, df, table_name, conn, truncate: True):
        msg = result = None, None
        try:
            cur = conn.cursor()
            try:
                if truncate:
                    truncate_sql = self.truncate_table(table_name)
                    cur.execute(truncate_sql)
                    self.Table_was_truncated = truncate

                create_sql = self.generate_create_table_sql(table_name, df)
                cur.execute(create_sql)
            except:
                pass #cur.execute(f"DROP TABLE {table_name}")

            placeholders = ', '.join([f":{i+1}" for i in range(len(df.columns))])
            insert_sql = f"INSERT INTO {table_name} VALUES({placeholders})"
            data = self.prepare_data_for_insert(df)
            cur.executemany(insert_sql, data)
            conn.commit()
            cur.close()
            conn.close()

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @property
    def Table_was_truncated(self):
        return self.__Table_was_truncated

    @Table_was_truncated.setter
    def Table_was_truncated(self, value):
        self.__Table_was_truncated = value
