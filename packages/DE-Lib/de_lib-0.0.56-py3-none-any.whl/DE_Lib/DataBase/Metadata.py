import pandas as pd

class METADATA:
    def __init__(self):
        ...

    def getMetadados(self, table, owner: str = '', con=None, database: str = 'ORACLE', driver: str = "SQLALCHEMY"):
        msg, result = None, None
        try:
            self._owner = owner
            self._table = table
            self._qry = self.QUERYS_METADADOS[database.upper()]
            #cur = con.connection.cursor()
            if driver.upper() == "SQLALCHEMY":
                result = pd.read_sql(con=con.connection, sql=self.QUERY)
            else:
                result = pd.read_sql(con=con, sql=self.QUERY)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @property
    def QUERYS_METADADOS(self):
        value = {
            "ORACLE": f"""Select * from all_tab_columns where owner = '{self._owner}' and table_name = '{self._table}' order by column_id"""
            ,
            "POSTGRES": f"""Select * from information_schema.columns where table_schema = '{self._owner}' and table_name = '{self._table}' order by ordinal_position"""
            , "SQLITE": f"""Select * from pragma_table_info('{self._table}') order by cid"""
            ,
            "MYSQL": f"""Select * from information_schema.columns where table_name = '{self._table}' order by ordinal_position"""
            ,
            "REDSHIFT": f"""Select column_name from information_schema.columns where table_schema ='{self._owner}' and table_name = '{self._table}' order by ordinal_position"""
            ,
            "CACHE": f"""SELECT * FROM INFORMATION_SCHEMA.COLUMNS where table_schema = '{self._owner}' and table_name = '{self._table}' order by ordinal_position"""
            , "MSSQL": f"""select t.name Tabela
                                                ,ac.name Coluna
                                                ,ac.column_id
                                                ,sep.value Comment
                                                ,t2.name Data_Type
                                            from sys.schemas s
                                            join sys.tables t
                                              on t.schema_id = s.schema_id
                                            join sys.all_columns ac
                                              on ac.object_id = t.object_id
                                            join sys.types t2
                                              on t2.system_type_id = ac.system_type_id
                                            left join sys.extended_properties sep
                                              on sep.major_id = t.object_id
                                                 and sep.minor_id = ac.column_id
                                                 and sep.name = 'MS_Description'
                                           where s.name = ISNULL('{self._owner}', 'dbo')
                                             and t.name = '{self._table}'
                                           order by t.name, ac.column_id
                                """
        }
        return value

    @property
    def QUERY(self):
        return self._qry