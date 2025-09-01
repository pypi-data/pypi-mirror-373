#region Imports
import inspect
import os
import json
import datetime as dt

from DE_Lib.Log import Level
from DE_Lib.DataBase import SQLite as SLT
from DE_Lib.Utils import DateUtils, Generic, System, Colors
#endregion

#region Instancias
lvl = Level.LEVEL() # biblioteca LOG - Trata os niveis do log
slt = SLT.SQLITE() # biblioteca DataBase - Driver SQLite
dtu = DateUtils.DATEUTILS() # bibliotaca Utils.DateUtils - Tratamento de dadas
gen = Generic.GENERIC() # biblioteda Utils.Generic - diversas funcionalidades
sop = System.SO() # biblioteca Utils.SO - Diversar funcoes do sistema operacional
cor = Colors.COLORS() # biblioteca Utils.Colors - represantação de cores (utilizada na LOG)
#endregion


class LOG:
    def __init__(self):
        self.__processo = None
        self.__list_log_detail = []
        self.__log_header = None

    #region Inicializacao, Registro de Evento e Finalizacao do LOG
    def setInit(self, processo: dict):
        msg, result = None, True
        try:
            self.TABLE_LOG = processo["table"]
            self.TABLE_EVENT = processo["event"]
            self.__processo = processo
            self.__call_origin = self.__getCALLFUNCTION()
            self.__log_header = self.__setLogHeader()
            print(self.__setPrintInicializacao())
        except Exception as error:
            msg = error
            result = result + msg
        finally:
            return result

    # ----------------------------------
    def setLogEvent(self, content: str, level=lvl.NOTSET, color: str = "", lf: bool = True, onscreen: bool = True):
        msg, result = None, True
        try:
            self.__setLogDetail(content=content, level=level)
            self.__setPrintScreen(level=level)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ----------------------------------
    def setEnd(self):
        msg, result = None, True
        try:

            __log = self.LOG_HEADER
            __log["event_content"]= self.LOG_DETAIL
            self.__log_header = __log

            fh = open(self.FILELOG, "w")
            buf = fh.write(json.dumps(self.LOG_HEADER, indent=4))
            fh.close()
            print(self.__setPrintFinalizacao())

            rst = self.setInsertLOG()
            #print(rst)
            rst = self.setInsertEVENT()
            #print(rst)

            #print(json.dumps(__log, indent=4))
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
    #endregion

    #region Estrutura do Header e Evento do LOG
    # ----------------------------------
    def __setLogHeader(self):
        msg, result = None, True
        try:
            __header = {"hash": gen.build_key(),
                        "nom_rotina": self.PROCESSO["processo"],
                        "nom_subrotina": self.CALL_FUNCTION,
                        "descricao": self.PROCESSO["descricao"],
                        "filename": self.FILELOG,
                        "os_user": sop.OSINFO["os_user"],
                        "user_db": "",
                        "local_ip": sop.OSINFO["local_ip"],
                        "local_name": sop.OSINFO["local_name"],
                        "processor": sop.OSINFO["processor"],
                        "so_platform": sop.OSINFO["so_platform"],
                        "so_system": sop.OSINFO["so_system"],
                        "so_version": sop.OSINFO["so_version"],
                        "datahoralog": dt.datetime.now().strftime(dtu.MILLISECONDS_FORMAT_PYTHON),
                        "versao": sop.OSINFO["so_version"]
                        }
            result = __header
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def __setLogDetail(self, level, content):
        msg, result = None, True
        try:
            __detail = {"hash": gen.build_key(),
                       "hash_parent": self.LOG_HEADER["hash"],
                       "datahoralog": dt.datetime.now().strftime(dtu.MILLISECONDS_FORMAT_PYTHON),
                       "level_code": level["code"],
                       "level_name": level["name"],
                       "function_name": self.CALL_FUNCTION,
                       "func_line": self.CALL_LINE,
                       "func_index": self.CALL_INDEX,
                       "code_context": self.CALL_CONTEXT,
                       "code_file": self.CALL_FILE,
                       "event_content": content
                       }
            self.__list_log_detail.append(__detail)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
    #endregion

    #region Set PRINT
    # ----------------------------------
    def __setPrintInicializacao(self):
        msg, result = None, True
        try:
            size = len(max(self.LOG_HEADER.values(), key=len)) + 21
            sep = cor.green_fore + "#" + "-" * size + "#" + cor.reset + "\n"
            data = []
            for key in self.LOG_HEADER:
                h = cor.green_fore + "# " + cor.reset + cor.red_fore + key + cor.reset + " " + "." * (15-len(str(key))) + " : " + cor.yellow_fore + self.LOG_HEADER[key] + cor.reset + " " * (size-21-len(self.LOG_HEADER[key])) + cor.green_fore + " #" + cor.reset
                data.append(h)

            result = sep
            for n in data:
                result = result + n + "\n"
            result = result + sep

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ----------------------------------
    def __setPrintFinalizacao(self):
        msg, result = None, True
        try:
            size = len(max(self.LOG_HEADER.values(), key=len)) + 21
            sep = cor.green_fore + "#" + "-" * size + "#" + cor.reset + "\n"
            result = sep
            result = result + f"Log Finalizado - {dt.datetime.now().strftime(dtu.MILLISECONDS_FORMAT_PYTHON)}\n"
            result = result + f"Tamanho em memoria do LOG: {gen.DictSizeBytes(self.LOG_HEADER)} bytes\n"
            result = result + sep

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
    #endregion

    # region Print LOG
    def __setPrintScreen(self, level, lf: bool = True, onscreen: bool = True):
        if onscreen:
            __log = self.LOG_DETAIL[-1]
            __text = f"""{cor.reset}{__log["datahoralog"]}-{level["color"]}{__log["level_name"].ljust(10)}{cor.reset}: {level["color"]}{__log["event_content"]}{cor.reset}"""
            if lf:
                print(__text)
            else:
                print(__text, end="")

    def __setPrintFile(self, logger, msg):
        logger.write(msg)
    # endregion

    #region SET´s Metodos
    def __setDeviceFile(self):
        msg, result = None, True
        try:
            # Foi passado um nome de arquivo de log
            if self.PROCESSO["filename"] is None:
                if not os.path.isdir(os.path.dirname(self.FILELOG)):
                    # se o diretorio informado não existir sera utilizado o diretorio local
                    if os.path.basename(self.FILELOG) is None:
                        self.__setFileName(os.path.join(os.getcwd(), self.PROCESSO), ".json")
                else:
                    self.__setFileName(os.path.join(os.getcwd(), self.PROCESSO["processo"], ".json"))
                # Criando um File Handle para o arquivo informado
                result = open(self.FILELOG, "w", encoding='utf-8')
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def __getCALLFUNCTION(self, value = inspect.stack()):
        msg, result = None, True
        try:
            result = {"filename":value[1].filename,
                      "line": value[1].lineno,
                      "function": value[1].function,
                      "code_context": value[1].code_context[0].strip(),
                      "index": value[1].index
                      }
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def __setFileName(self, value):
        msg, result = None, True
        try:
            self.__processo["filename"] = value
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
    #endregion

    #region Property LOG
    @property
    def LOG_DETAIL(self):
        return self.__list_log_detail

    @ property
    def LOG_HEADER(self):
        return self.__log_header
    #endregion

    #region Property´s CALL
    @property
    def CALL_FUNCTION(self):
        return self.__call_origin["function"]

    @property
    def CALL_LINE(self):
        return self.__call_origin["line"]

    @property
    def CALL_FILE(self):
        return self.__call_origin["filename"]

    @property
    def CALL_CONTEXT(self):
        return self.__call_origin["code_context"]

    @property
    def CALL_INDEX(self):
        return self.__call_origin["index"]
    #endregion

    #region Property´s diversas
    @property
    def PROCESSO(self):
        return self.__processo

    @property
    def CONN(self):
        return self.__processo["conexao"]

    @property
    def FILELOG(self):
        return self.PROCESSO["file"]
    # endregion

    #region DML LOG
    # ----------------------------------
    def setInsertLOG(self):
        msg, result = None, True
        try:
            owner = ""
            stmt = f"""
                    Insert into {self.TABLE_LOG}
                                 (HASH
                                 ,NOM_ROTINA
                                 ,NOM_SUBROTINA
                                 ,DESCRICAO
                                 ,"FILE"
                                 ,"OS_USER"
                                 ,"USER_DB"
                                 ,LOCAL_IP
                                 ,LOCAL_NAME
                                 ,PROCESSOR
                                 ,SO_PLATFORM
                                 ,SO_SYSTEM
                                 ,SO_VERSION
                                 ,"TIMESTAMP"
                                 ,VERSAO
                                 )
                           VALUES(:hash
                                 ,:nom_rotina
                                 ,:nom_subrotina
                                 ,:descricao
                                 ,:filename
                                 ,:os_user
                                 ,:user_db                                 
                                 ,:local_ip
                                 ,:local_name
                                 ,:processor
                                 ,:so_platform
                                 ,:so_system
                                 ,:so_version
                                 ,to_timestamp(:datahoralog, '{dtu.MILLISECONDS_FORMAT_SQL}')
                                 ,:versao
                                 )                                 
                    """
            if self.CONN is not None:
                __head = self.LOG_HEADER
                del(__head["event_content"])
                cur = self.CONN.cursor()
                cur.execute(stmt, __head)
                self.CONN.commit()
                cur.close()
                #self.CONN.close()
                result = "Log HEADER criado!"
            else:
                ...
                #raise Exception("Não foi fornecido uma conexao com banco de dados!")
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ----------------------------------
    def setInsertEVENT(self):
        msg, result = None, True
        try:
            owner = ""
            stmt = f"""
                    Insert into {self.TABLE_EVENT}
                                 (HASH
                                 ,HASH_PARENT
                                 ,"TIMESTAMP"
                                 ,LEVEL_CODE
                                 ,LEVEL_NAME
                                 ,FUNCTION_NAME
                                 ,FUNC_LINE
                                 ,FUNC_INDEX
                                 ,CODE_COTEXT
                                 ,CODE_FILE
                                 ,EVENT_CONTENT
                                 )
                           VALUES(:hash
                                 ,:hash_parent
                                 ,to_timestamp(:datahoralog, '{dtu.MILLISECONDS_FORMAT_SQL}')
                                 ,:level_code
                                 ,:level_name
                                 ,:function_name
                                 ,:func_line
                                 ,:func_index
                                 ,:code_context
                                 ,:code_file
                                 ,:event_content
                                 )                                 
                    """
            if self.CONN is not None:
                __detail = self.LOG_DETAIL
                cur = self.CONN.cursor()
                cur.executemany(stmt, (__detail))
                self.CONN.commit()
                cur.close()
                #self.CONN.close()
                result = "Log DETAIL criado!"
            else:
                ...
                #raise Exception("Não foi fornecido uma conexao com banco de dados!")
        except Exception as error:
            msg = error
            result = msg
        finally:
                return result

    #endregion

    #region DDL LOG
    # ----------------------------------
    def DDL_LOG(self, base: str = "SQLite"):
        msg, result = None, True
        try:
            if base == "SQLite":
                log = f"""
                        CREATE TABLE IF NOT EXISTS LOG_TESTE (
                            HASH TEXT(32) NOT NULL,
                            NOM_ROTINA TEXT(50) NOT NULL,
                            NOM_SUBROTINA TEXT(128),
                            DESCRICAO TEXT(256),
                            FILE TEXT(256),
                            OS_USER TEXT(128),
                            USER_DB TEXT(128),
                            LOCAL_IP TEXT(32),
                            LOCAL_NAME TEXT(64),
                            PROCESSOR TEXT(32),
                            SO_PLATFORM TEXT(32),
                            SO_SYSTEM TEXT(32),
                            SO_VERSION TEXT(32),
                            "TIMESTAMP" TIMESTAMP DEFAULT (datetime('now')) NOT NULL,
                            VERSAO TEXT(32),
                            CONSTRAINT LOG_PK PRIMARY KEY (HASH)
                        );
                        """
                event = f"""                    
                        CREATE TABLE IF NOT EXISTS LOG_EVENT_TESTE (
                            HASH TEXT(32) NOT NULL,
                            HASH_PARENT TEXT(32) NOT NULL,
                            "TIMESTAMP" TIMESTAMP DEFAULT (datetime('now')) NOT NULL,
                            LEVEL_CODE TEXT(16) ,
                            LEVEL_NAME TEXT(16) ,
                            FUNCTION_NAME TEXT(128) ,
                            FUNC_LINE INT,
                            FUNC_INDEX INT,
                            CODE_COTEXT TEXT(256),
                            CODE_FILE TEXT(256),
                            EVENT_CONTENT TEXT(512),
                            CONSTRAINT LOG_EVENT_PK PRIMARY KEY (HASH)
                        );
                        """
            elif base == "ORACLE":
                log = f"""CREATE TABLE IF NOT EXISTS LOG_TESTE (
                            HASH VARCHAR2(32) NOT NULL,
                            NOM_ROTINA VARCHAR2(50) NOT NULL,
                            NOM_SUBROTINA VARCHAR2(128),
                            DESCRICAO VARCHAR2(256),
                            FILE VARCHAR2(256),
                            OS_USER VARCHAR2(128),
                            USER_DB VARCHAR2(128),
                            LOCAL_IP VARCHAR2(32),
                            LOCAL_NAME VARCHAR2(64),
                            PROCESSOR VARCHAR2(32),
                            SO_PLATFORM VARCHAR2(32),
                            SO_SYSTEM VARCHAR2(32),
                            SO_VERSION VARCHAR2(32),
                            "TIMESTAMP" TIMESTAMP DEFAULT (datetime('now')) NOT NULL,
                            VERSAO VARCHAR2(32),
                            CONSTRAINT LOG_PK PRIMARY KEY (HASH)
                        );
                        """
                event = f"""                    
                        CREATE TABLE IF NOT EXISTS LOG_EVENT_TESTE (
                            HASH VARCHAR2(32) NOT NULL,
                            HASH_PARENT VARCHAR2(32) NOT NULL,
                            "TIMESTAMP" TIMESTAMP DEFAULT (datetime('now')) NOT NULL,
                            LEVEL_CODE VARCHAR2(16) ,
                            LEVEL_NAME VARCHAR2(16) ,
                            FUNCTION_NAME VARCHAR2(128) ,
                            FUNC_LINE INT,
                            FUNC_INDEX INT,
                            CODE_COVARCHAR2 VARCHAR2(256),
                            CODE_FILE VARCHAR2(256),
                            EVENT_CONTENT VARCHAR2(512),
                            CONSTRAINT LOG_EVENT_PK PRIMARY KEY (HASH)
                        );
                        """

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
    #endregion

    @property
    def TABLE_LOG(self):
        return self.__TABLE_LOG

    @TABLE_LOG.setter
    def TABLE_LOG(self, value):
        self.__TABLE_LOG = value

    @property
    def TABLE_EVENT(self):
        return self.__TABLE_EVENT

    @TABLE_EVENT.setter
    def TABLE_EVENT(self, value):
        self.__TABLE_EVENT = value
