"""
    Almir J Gomes - 30/06/2025
    --------------------------
    Driver: ORACLEDB
    ----------------
    Oracle modo THIN não funciona com bancos < 12.1
    Oracle Thin Mode vs Thick Mode no oracledb
    O driver oracledb do Python pode operar em dois modos de conexão com o Oracle Database:
    🔹 Comparação Geral (modos: THIN e THIcK)
        Recurso	                        cx_Oracle	    oracledb modo THICK	    oracledb modo THIN
        Requer Oracle Client	        Sim	            Sim	                    Não
        Compatível com modo thin    	❌ Não	        ❌ Não	                ✅ Sim
        Suportado pela Oracle (futuro)	Obsoleto	    ✅ Sim	                ✅ Sim
        Suporta makedsn	                ✅ Sim	        ✅ Sim	                ✅ Sim


    Driver: CX_ORACLE
    -----------------
    Ultima versão 8.3 (lançada em 2021)
        .esta congelado suas atualizações - agora é oracledb
    Prós:
        Driver oficial da oracle, muito maduro.
        Suporte completo a features especificas da oracle, como LOBs, REFCURSOR, etc.
        Performance solida
        Integrado com SQLalchemy como oracle+cx_oracle
    Contras:
        THIN mode não é compativel com este driver
        Requer Oracle Client instalado (instant client ou full)
        Esta sendo substituido pelo ORACLEDB
        Suportado com restrições a bancos oracle anteriores a versão 11g (11.2) (inclusive)
        Versão python: Do 3.5 até 3.9, em versão posteriores a 3.9, usa-se o oracledb

    Driver: ORACLEDB
    ----------------
    Prós:
        Compativel com cx_oracle (inclusive o namespace e oracledb)
        Pode rodar em moto "thin": não requer Oracle Client
        Suporte total ao SQLAlchemy como oracle+oracledb
        Melhor integração com ambientes modernos (containers, cloud, etc.)
    Contras:
        Modo thin ainda não tem 100% dos recursos avançados (como OCI-specific features)
        É mais novo, então pode haver ajustes de compatibilidade em sistemas legados
        Suportado apenas com bancos oracle 11.2 ou posterior.
        Versão python: 3.7 À 3.13 ou posterior
        obs: Varias tentativas de conexao com python 3.9 e banco 11.4.0.2, sem sucesso!

    Driver: SQLAlchemy
    ------------------
    Prós:
        Abstrai o acesso ao banco via ORTM ou SQL "cru".
        Permite trocar o driver facilmente (cx_oracle, oracledb, etc.)
        Suporte nativo a Oracle com strings como:
            oracle+cx_oracle://usuario:senha@host:porta/sid
            oracle+oracledb://usuario:senha@host:porta/sid
    Contras:
        Não é um driver: depende de um driver real por baixo araledb, cx_oracle)
        A performance pode depender do driver usado

    Situação	                                    Melhor escolha
    .Quer evitar instalação do Oracle Client	    oracledb (modo thin)
    .Precisa de todos os recursos da Oracle
     (LOB, REF CURSOR etc.)	                        oracledb (modo thick) ou cx_Oracle
    .Usando SQLAlchemy ORM ou query builder	        sqlalchemy com oracledb
    .Projeto novo	                                oracledb (é o futuro do cx_Oracle)
    .Projeto legado com cx_Oracle	                Pode continuar, mas considere migrar

    Propriedades:
    -------------
       .self.DICT_CONEXAO: Dicionario recebido por parametro
       .self.DATABASE: Nome do banco de dados. Ex.: ORACLE
       .self.DB_VERSION: Versao do banco de dados
       .self.NOME_DATABASE: Nome (para uso interno) e de refencia do banco de dados. Ex.: MONTEREY
       .self.DRIVER_CONEXAO: Driver de conexao (Oracle=cx_oracle, oracledb ou SQLAlchemy.)
       .self.DRIVER_MODE: Oracle=Thin ou Thick
       .self.DRIVER_LIBRARY= cx_oracle ou oraclebd
       .self.PATH_LIBRARY=Localização do driver se o mesmo for externo
       .self.TYPE_CONNECTION: service_name ou sid
       .self.INSTANCE: Nome da instancia do banco de dados
       .self.HOST: Nome do host ou IP
       .self.PORT: porta utilizada
       .self.USERNAME: Nome do usuario
       .self.PASSWORD: Senha do usuario

"""
import os
import cx_Oracle as cx
import oracledb as db
import sqlalchemy as sqa
from sqlalchemy import create_engine, text
import json

from DE_Lib.Utils import Generic

gen = Generic.GENERIC()

class ORACLE:
    def __init__(self):
        ...

    #region metodos
    def Connect(self, str_cnn: dict):
        msg, result = None, None
        try:
            self.setProperty(str_cnn)
            if self.DRIVER_CONEXAO.upper() == "CX_ORACLE":
                self.getConnectCX_ORACLE()
            elif self.DRIVER_CONEXAO.upper() == "ORACLEDB":
                self.getConnectORACLEDB()
            elif self.DRIVER_CONEXAO.upper() == "SQLALCHEMY":
                self.getConnectSQLAlchemy()
            result = self.CONNECTION
        except Exception as error:
            self.CONNECTION = None
            self.CONNECTION_VALID = False
            self.DICT_CONEXAO["password"] = "<PASSWORD>"
            self.DATABASE_ERROR = f"""Erro ao tentar se conectar com o banco de dados:\n{json.dumps(self.DICT_CONEXAO, indent=4)}\nDNS: {self.CONNECTION_DNS}\n***Erro: {error}"""
            result = self.CONNECTION
        finally:
            return result

    def getConnectCX_ORACLE(self):
        msg, result = None, None
        try:
            # O driver cx_oracle é apenas compativel com modo THICK
            __conn = None
            self.setLibrary()
            self.DRIVER_MODE = gen.nvl(self.DRIVER_MODE, "THICK")
            __conn = cx.connect(self.USERNAME, self.PASSWORD, self.getDnsName(), threaded=True)
            self.CONNECTION = __conn
            if self.getTestConnect(__conn):
                self.CONNECTION_VALID = True
                self.DATABASE_ERROR = False
            else:
                raise Exception(self.ERROR)
        except Exception as error:
            self.CONNECTION = None
            self.CONNECTION_VALID = False
            self.DICT_CONEXAO["password"] = "<PASSWORD>"
            self.DATABASE_ERROR = f"""Erro ao tentar se conectar com o banco de dados:\n{json.dumps(self.DICT_CONEXAO, indent=4)}\nDNS: {self.CONNECTION_DNS}\n***Erro: {error}"""
            result = self.CONNECTION
        finally:
            return result

    def getConnectORACLEDB(self):
        msg, result = None, None
        try:
            # O driver ORACLEDB é apenas compativel com modo THICK
            self.setLibrary() # Tem que rever se realmente precisa desta library par ao ORACLEDB
            __conn = db.connect(user=self.USERNAME, password=self.PASSWORD, dsn=self.getDnsName())
            self.CONNECTION = __conn
            if self.getTestConnect(__conn):
                self.CONNECTION_VALID = True
                self.DATABASE_ERROR = False
            else:
                raise Exception(self.ERROR)
        except Exception as error:
            self.CONNECTION = None
            self.CONNECTION_VALID = False
            self.DICT_CONEXAO["password"] = "<PASSWORD>"
            self.DATABASE_ERROR = f"""Erro ao tentar se conectar com o banco de dados:\n{json.dumps(self.DICT_CONEXAO, indent=4)}\nDNS: {self.CONNECTION_DNS}\n***Erro: {error}"""
            result = self.CONNECTION
        finally:
            return result

    def getConnectSQLAlchemy(self):
        msg, result = None, None
        try:
            __libOra = None
            __conn = None
            if not self.DRIVER_LIBRARY:
                __libOrA = "cx_oracle"
            else:
                __libOra = self.DRIVER_LIBRARY.lower()
            __strcnn = f"""{self.DATABASE.lower()}+{__libOra}://{self.USERNAME}:{self.PASSWORD}@{self.getDnsName()}"""
            __conn = sqa.create_engine(__strcnn).connect().connection
            self.CONNECTION = __conn
            if self.getTestConnect(__conn):
                self.CONNECTION_VALID = True
                self.DATABASE_ERROR = False
            else:
                raise Exception(self.ERROR)
            result = self.CONNECTION
        except Exception as error:
            self.CONNECTION = None
            self.CONNECTION_VALID = False
            self.DICT_CONEXAO["password"] = "<PASSWORD>"
            self.DATABASE_ERROR = f"""Erro ao tentar se conectar com o banco de dados:\n{json.dumps(self.DICT_CONEXAO, indent=4)}\nDNS: {self.CONNECTION_DNS}\n***Erro: {error}"""
            result = self.CONNECTION_VALID
        finally:
            return result

    def getConnectionTypeSID(self):
        msg, result = None, None
        try:
            if gen.nvl(self.TYPE_CONNECTION.upper(), "SERVICE_NAME") == "SID":
                result = True
            else:
                result = False
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getDnsName(self):
        msg, result = None, None
        try:
            if self.DRIVER_CONEXAO.upper() == "CX_ORACLE":
                if self.getConnectionTypeSID():
                    self.CONNECTION_DNS = cx.makedsn(host=self.HOST, port=self.PORT, sid=self.INSTANCE)
                else:
                    self.CONNECTION_DNS = cx.makedsn(host=self.HOST, port=self.PORT, service_name=self.INSTANCE)
            else:
                if self.getConnectionTypeSID():
                    self.CONNECTION_DNS = cx.makedsn(host=self.HOST, port=self.PORT, sid=self.INSTANCE)
                else:
                    self.CONNECTION_DNS = cx.makedsn(host=self.HOST, port=self.PORT, service_name=self.INSTANCE)
            result = self.CONNECTION_DNS
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def setLibrary(self):
        msg, result = None, None
        try:
            if not os.getenv("ORACLE_LIB"):
                if os.path.isdir(self.PATH_LIBRARY):
                    os.environ["ORACLE_LIB"] = self.PATH_LIBRARY
            else:
                self.PATH_LIBRARY = os.getenv("ORACLE_LIB")

            cx.init_oracle_client(lib_dir=result)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getTestConnect(self, conn):
        msg, result = None, None
        try:
            self.ERROR = None
            qry = "Select sysdate from dual"
            cur = self.CONNECTION.cursor()
            row = cur.execute(qry).fetchall()
            result = True
        except Exception as error:
            msg = f"Não foi possivel executar uma query simples no banco de dados. {error}"
            self.ERROR = msg
            result = False
        finally:
            return result

    #endregion

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
            self.ERROR = None
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
        return self.__connection_dsn

    @CONNECTION_DNS.setter
    def CONNECTION_DNS(self, value):
        self.__connection_dsn = value

    @property
    def DB_VERSION(self):
        return self.__db_version

    @DB_VERSION.setter
    def DB_VERSION(self, value):
        self.__db_version = value

    @property
    def ERROR(self):
        return self.__error

    @ERROR.setter
    def ERROR(self, value):
        self.__error = value
    #endregion