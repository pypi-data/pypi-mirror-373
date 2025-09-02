import os
import signal
import socket as skt
import platform as so
import datetime as dt

class SO:
    def __init__(self):
        self.__msg = {} # mensagems para funcionalidades


    def ping(self, hostname) -> bool:
        msg, result = None, False
        # hostname = "google.com"  # example
        response = os.system("ping -n 1 " + hostname + " >> trash_ping.log")
        # and then check the response...
        if response == 0:
            self.__msg["ping"] = f"""{hostname} Sucesso!"""
            result = True
        else:
            self.__msg["ping"] = f"""{hostname} Não encontrado!"""
        return result

    def killPID(self, pid):
        msg, result = None, True
        try:
            os.kill(pid, signal.SIGKILL)
            self.__msg["pid"] = "PID eliminado!"
        except Exception as error:
            self.__msg["pid"] = f"""Erro ao tentar eliminar o PID!\n{error}"""
            result = False
        finally:
            return result

    @property
    def PID(self):
        return os.getpid()

    @property
    def OSINFO(self):
        result = {"user_db": None,
                  "local_ip": skt.gethostbyname(skt.gethostname()),
                  "local_name": skt.gethostname(),
                  "processor": so.machine(),
                  "os_user": os.getlogin(),
                  "so_platform": so.platform(),
                  "so_system": so.system(),
                  "so_version": so.version()
                  }
        return result

    @staticmethod
    def convert_sql_type(self, sql_type: str):
        msg, result = None, None
        try:
            # Mapeamento genérico de tipos SQL para Python
            SQL_TO_PYTHON_TYPE = {
                "INTEGER": int,
                "SMALLINT": int,
                "BIGINT": int,
                "DECIMAL": float,
                "NUMERIC": float,
                "REAL": float,
                "FLOAT": float,
                "DOUBLE": float,
                "BOOLEAN": bool,
                "CHAR": str,
                "VARCHAR": str,
                "TEXT": str,
                "CLOB": str,
                "BLOB": bytes,
                "DATE": "datetime.date",
                "DATETIME": "datetime.datetime",
                "TIMESTAMP": "datetime.datetime",
                "TIME": "datetime.time",
            }
            result = SQL_TO_PYTHON_TYPE.get(sql_type.upper(), str)  # Default: str se não encontrado
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def convert_sql_value(self, sql_type, value):
        """
        Converte um valor SQL para seu equivalente em Python.
        :param sql_type: Datatype da coluna expressa em "value"
        :param value: Valor a ser convertido
        :return: Valor convertido no datatype apropriado para o python
        """
        msg, result = None, None
        try:
            python_type = self.convert_sql_type(sql_type)
            if python_type in [dt.date, dt.time, dt.datetime]:
                result = python_type.fromisoformat(value)
            else:
                ...
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
