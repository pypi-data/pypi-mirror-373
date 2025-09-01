import redshift_connector as reds
import os
import json

from DE_Lib.Utils import Generic

gen = Generic.GENERIC()

class REDSHIFT:
    def __init__(self):
        self._connection_is_valid = None
        self._nome_database = None
        self._cnn = None
        self.__database_error = None

    def Connect(self, string_connect: dict):
        conn, result = None, None
        try:
            conn = reds.connect(host=string_connect["host"],
                                database=string_connect["instance"],
                                user=string_connect["username"],
                                password=string_connect["password"]
                            )
            self._connection_is_valid = True
            self._cnn = result
            self.__database_error = f"""{json.dumps(string_connect, indent=4).replace(string_connect["password"], "******")}\nConexao bem sucedida!"""
            self._nome_database = gen.nvl(string_connect["database"], "")
        except Exception as error:
            msg = f"""{json.dumps(string_connect, indent=4).replace(string_connect["password"], "******")}\nFalha ao tentar se conectar com o banco de dados RedShift\nException Error: {error} """
            result = msg
            self._connection_is_valid = False
            self.__database_error = msg
        finally:
            return result

    @property
    def CONNECTION(self):
        return self._cnn

    @property
    def CONNECTION_VALID(self):
        return self._connection_is_valid

    @property
    def NOME_DATABASE(self):
        return self._nome_database.upper()

    @property
    def DATABASE_ERROR(self):
        return self._DATABASE_ERROR