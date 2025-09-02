import sqlite3 as sq3
import sqlalchemy as sqa
import os
import json

from DE_Lib.Utils import Generic

gen = Generic.GENERIC()

class SQLITE:
    def __init__(self):
        ...

    def Connect(self, str_cnn: dict, **kwargs):
        msg, result = None, True
        try:
            self.setProperty(str_cnn)
            __file = os.path.join(self.HOST, self.INSTANCE)
            if os.path.isfile(__file):
                if "check_same_thread" in kwargs.keys():
                    __check_same_thread = kwargs.get("check_same_thread")
                else:
                    __check_same_thread = True
                __conn = None
                if not self.DRIVER_CONEXAO:
                    __conn = sq3.connect(__file, check_same_thread=__check_same_thread)
                elif self.DRIVER_CONEXAO.upper() == "SQLALCHEMY":
                    engine = sqa.create_engine(f"""sqlite:///{__file}""")
                    __conn = engine.connect().connection
            self.CONNECTION = __conn
            self.CONNECTION_VALID = True
            self.DATABASE_ERROR = False
            result = self.CONNECTION
        except Exception as error:
            self.CONNECTION = None
            self.CONNECTION_VALID = False
            self.DICT_CONEXAO["password"] = "<PASSWORD>"
            self.DATABASE_ERROR = f"""Erro ao tentar se conectar com o banco de dados:\n{json.dumps(self.DICT_CONEXAO, indent=4)}\nDNS: {self.CONNECTION_DNS}\n***Erro: {error}"""
            result = self.CONNECTION_VALID
        finally:
            return result

    def setProperty(self, value:dict):
        msg, result = None, None
        try:
            self.DICT_CONEXAO = value
            self.DATABASE = value["database"]
            self.DB_VERSION = value["db_version"]
            self.NOME_DATABASE = value["name"]
            self.DRIVER_CONEXAO = value["driver_conexao"]
            self.DRIVER_MODE = value["driver_mode"]
            self.DRIVER_LIBRARY = value["driver_library"]
            self.PATH_LIBRARY = value["path_library"]
            self.TYPE_CONNECTION = value["type_conection"]
            self.INSTANCE = value["instance"]
            self.HOST = value["host"]
            self.PORT = value["port"]
            self.USERNAME = value["username"]
            self.PASSWORD = value["password"]
            self.CONNECTION_VALID = None
            self.DATABASE_ERROR = None
            self.CONNECTION = None
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    #region propertys
    @property
    def DATABASE(self):
        return self.__database

    @DATABASE.setter
    def DATABASE(self, value):
        self.__database = value

    @property
    def NOME_DATABASE(self):
        return self.__name

    @NOME_DATABASE.setter
    def NOME_DATABASE(self, value):
        self.__name = value

    @property
    def DRIVER_CONEXAO(self):
        return self.__driver_conexao

    @DRIVER_CONEXAO.setter
    def DRIVER_CONEXAO(self, value):
        self.__driver_conexao = value

    @property
    def DRIVER_MODE(self):
        return self.__driver_mode

    @DRIVER_MODE.setter
    def DRIVER_MODE(self, value):
        self.__driver_mode = value

    @property
    def DRIVER_LIBRARY(self):
        return self.__driver_library

    @DRIVER_LIBRARY.setter
    def DRIVER_LIBRARY(self, value):
        self.__driver_library = value

    @property
    def PATH_LIBRARY(self):
        return self.__path_library

    @PATH_LIBRARY.setter
    def PATH_LIBRARY(self, value):
        self.__path_library = value

    @property
    def TYPE_CONNECTION(self):
        return self.__type_connection

    @TYPE_CONNECTION.setter
    def TYPE_CONNECTION(self, value):
        self.__type_connection = value

    @property
    def INSTANCE(self):
        return self.__instance

    @INSTANCE.setter
    def INSTANCE(self, value):
        self.__instance = value

    @property
    def HOST(self):
        return self.__host

    @HOST.setter
    def HOST(self, value):
        self.__host = value

    @property
    def PORT(self):
        return self.__port

    @PORT.setter
    def PORT(self, value):
        self.__port = value

    @property
    def USERNAME(self):
        return self.__username

    @USERNAME.setter
    def USERNAME(self, value):
        self.__username = value

    @property
    def PASSWORD(self):
        return self.__password

    @PASSWORD.setter
    def PASSWORD(self, value):
        self.__password = value

    @property
    def CONNECTION_VALID(self):
        return self.__connection_valid

    @CONNECTION_VALID.setter
    def CONNECTION_VALID(self, value):
        self.__connection_valid = value

    @property
    def DATABASE_ERROR(self):
        return self.__database_error

    @DATABASE_ERROR.setter
    def DATABASE_ERROR(self, value):
        self.__database_error = value

    @property
    def CONNECTION(self):
        return self.__connection

    @CONNECTION.setter
    def CONNECTION(self, value):
        self.__connection = value

    @property
    def DICT_CONEXAO(self):
        return self.__dict_conexao

    @DICT_CONEXAO.setter
    def DICT_CONEXAO(self, value):
        self.__dict_conexao = value

    @property
    def CONNECTION_DNS(self):
        return self.__connection_dns

    @CONNECTION_DNS.setter
    def CONNECTION_DNS(self, value):
        self.__connection_dns = value

    @property
    def DB_VERSION(self):
        return self.__db_version

    @DB_VERSION.setter
    def DB_VERSION(self, value):
        self.__db_version = value

    #endregion