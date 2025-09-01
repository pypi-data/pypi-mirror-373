import datetime as dt
import json
import os
import platform as so
import socket as skt

class LOG:
    def __init__(self, **kwargs):
        try:
            self._PROCESSO = kwargs
            self._CR = True # Carriage_Return
            #
            if (self._PROCESSO["device_out"] is None) or (len(self._PROCESSO["device_out"]) == 0):
                self._PROCESSO["device_out"] = ["screen"]
            if "database" in self._PROCESSO["device_out"] and "memory" in self._PROCESSO["device_out"]:
                del(self._PROCESSO["device_out"][self._PROCESSO["device_out"].index("memory")])
            #
            if self._PROCESSO["nome_tabela_log"] is None:
                self._PROCESSO["nome_tabela_log"] = "LOG"
            if self._PROCESSO["nome_tabela_log_evento"] is None:
                self._PROCESSO["nome_tabela_log_evento"] = "LOG_EVENTO"
            #
            self._CONEXAO = self._PROCESSO["conexao_log"]
            self._TABLE_LOG = self._PROCESSO["nome_tabela_log"]
            self._TABLE_EVENT = self._PROCESSO["nome_tabela_log_evento"]
            self._DEVICE_OUT = self._PROCESSO["device_out"]

            self._filename_absolute = os.path.splitext(self._PROCESSO["file"])[0]+".json"
            self._CORES = self._cores_ansi()
            self._HASH_LOG = self._hash()
            self._FILE_LOG_EVENT = []
        except Exception as error:
            print(error)
            raise Exception("Classe LOGGING não foi instanciada")

    def Inicializa(self) -> object:
        file_handler, body_json, cor, msg, result = None, None, None, None, []
        try:
            cor = self.Preto_Fore + self.Cyan_Claro_Back
            if "screen" in self._DEVICE_OUT:
                msg = f"""LOG Inicializado!"""
            if "file" in self._DEVICE_OUT:
                msg = f"""LOG Inicializado ({self._filename_absolute})"""
                file_handler = open(self._filename_absolute, "w", encoding='utf-8')
                text = """{"body": \n\t{ "content": \n\t\t{ """ + f""" "File": "{self._filename_absolute}",""" + f""" \n\t\t"datalog": "{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}",""" + f"""\n\t\t "payload":[ \n\t\t\t"""
                self._print_file(file_handler, text)
            if "database" in self._DEVICE_OUT:
                msg = f"""LOG Inicializado"""
                self._print_db_new(payload=self._PROCESSO, nome_tabela=self._TABLE_LOG)
            if "memory" in self._DEVICE_OUT:
                msg = f"""LOG Inicializado"""
                self._print_memory(nome_tabela=self._TABLE_LOG, payload=self._PROCESSO)
        except Exception as error:
            msg = f"""Falha do tentar inicializar o LOG ({self._filename_absolute})"""
            cor = self.Branco_Fore + self.Verde_Claro_Back
        finally:
            msg = f"""{cor} {msg} [{",".join(self._DEVICE_OUT)}] {self.Reset}"""
            self._print_screen(msg)
            return file_handler

    def Popula(self, logger, level, content, function_name: str = "", cor: str = "", lf: bool = True, onscreen: bool = True) -> None:
        payload = None
        try:
            # Construindo o Payload para insert na tabela
            payload = self._payload_event(content=content, function=function_name)
            self._LOG_LEVEL_COLOR = self._LOG_LEVEL_COLOR + cor

            if self._CR:
                msg = f"""{self._LOG_LEVEL_COLOR}{dt.datetime.now()} - {self._LOG_LEVEL_CODE}-{self._LOG_LEVEL_NAME} - {function_name} - {content}"""
                if not lf:
                    self._Carriage_Return()
            else:
                msg = f""": {self._LOG_LEVEL_COLOR}{content}"""
                if lf:
                    self._Carriage_Return()
            # if not lf:
            #     msg = f""": {content}"""
            # ----------------------------------------------
            if "screen" in self._DEVICE_OUT:
                self._print_screen(msg, lf, onscreen)
            if "file" in self._DEVICE_OUT:
                texto = json.dumps(payload, indent=15) + ","
                self._print_file(logger, texto)
            if "database" in self._DEVICE_OUT:
                self._print_db_new(payload=payload, nome_tabela=self._TABLE_EVENT)
            if "memory" in self._DEVICE_OUT:
                self._print_memory(nome_tabela=self._TABLE_EVENT, payload=payload)
            self._LOG_LEVEL_COLOR = self.Reset
        except Exception as error:
            print(self.Vermelho_Claro_Fore + error + self.Reset)
        finally:
            return payload

    def Finaliza(self, logger: object) -> None:
        cor, msg, result, result = None, None, None, None
        try:
            cor = self.Reset + self.Preto_Fore + self.Cyan_Claro_Back
            msg = f"""LOG Finalizado!"""
            if "screen" in self._DEVICE_OUT:
                pass
            if "file" in self._DEVICE_OUT:
                text = "]}}}"
                self._print_file(logger, text)
                logger.close()
            if "database" in self._DEVICE_OUT:
                self._CONEXAO.close()
            if "memory" in self._DEVICE_OUT:
                result = [self._FILE_LOG, self._FILE_LOG_EVENT]
        except Exception as error:
            msg = f"""Erro ao tentar fechar o arquivo de LOG. Erro {error}"""
            cor = self.Branco_Fore + self.Vermelho_Claro_Back
            #result = msg
        finally:
            msg = f"""{cor} {msg} [{",".join(self._DEVICE_OUT)}] {self.Reset}"""
            self._print_screen(msg)
            return result

    def _payload_header(self, processo: dict) -> None:
        result = None
        try:
            now = dt.datetime.now()
            binds = {}
            binds.update(processo)
            binds.update(self.OS_INFO)
            # Consistindo se colunas existem no dicionario
            if "timestamp" not in binds.keys(): binds["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S.%f")
            if "hash" not in binds.keys(): binds["hash"] = self._HASH_LOG
            if "versao" not in binds.keys(): binds["versao"] = None
            del binds["conexao_log"]
            del binds["nome_tabela_log"]
            del binds["nome_tabela_log_evento"]
            del binds["device_out"]
            result = binds
        except Exception as error:
            print(error)
        finally:
            return result

    def _payload_event(self, content: str, function: str):
        try:
            now = dt.datetime.now()
            payload = {"hash": self._hash(str(self._HASH_LOG)),
                       "hash_log": self._HASH_LOG,
                       "timestamp": now.strftime("%Y-%m-%d %H:%M:%S.%f"),
                       "level_code": self._LOG_LEVEL_CODE,
                       "level_name": self._LOG_LEVEL_NAME,
                       "function_name": function,
                       "content": content
                       }
        except Exception as error:
            print(error)
        finally:
            return payload

    def _hash(self, complemento: str = ""):
        hora = dt.datetime.now().strftime("%Y%m%d%H%M%S%f")
        return abs(hash(hora+complemento))

    def _print_screen(self, msg, lf: bool = True, onscreen: bool = True):
        if onscreen:
            if lf:
                print(msg)
            else:
                print(msg, end="")

    def _print_file(self, logger, msg):
        logger.write(msg)

    def _print_db_new(self, payload: dict, nome_tabela: str):
        msg = False
        try:
            cur = self._CONEXAO.cursor()
            if nome_tabela == self._PROCESSO["nome_tabela_log_evento"]:
                sql =   f"""
                        Insert into {self._PROCESSO["nome_tabela_log_evento"]}
                                     (hash,
                                      hash_log,
                                      timestamp,
                                      level_code,
                                      level_name,
                                      function_name,
                                      content)
                               VALUES(:hash,
                                      :hash_log,
                                      :timestamp,
                                      :level_code,
                                      :level_name,
                                      :function_name,
                                      :content)
                        """
            else:
                payload = self._payload_header(payload)
                sql =   f"""
                        Insert into {self._PROCESSO["nome_tabela_log"]}
                                    (nom_rotina,
                                     nom_subrotina,
                                     descricao,
                                     file,
                                     user_os,
                                     user_db,
                                     local_ip,
                                     local_name,
                                     processor,
                                     so_platafor,
                                     so_system,
                                     so_version,
                                     timestamp,
                                     hash,
                                     versao)
                              VALUES(:nom_rotina,
                                     :nom_subrotina,
                                     :descricao,
                                     :file,
                                     :user_os,
                                     :user_db,
                                     :local_ip,
                                     :local_name,
                                     :processor,
                                     :so_platafor,
                                     :so_system,
                                     :so_version,
                                     :timestamp,
                                     :hash,
                                     :versao)      
                        """
            cur.execute(sql, payload)
            self._CONEXAO.commit()
            msg = "Registro de LOG criado!"
        except Exception as error:
            msg = f"""Falha ao tentar inserir um registro na tabela LOG. Erro: {error}"""
        finally:
            return msg

    def _print_memory(self, nome_tabela: str, payload: dict):
        msg = False
        try:
            if nome_tabela == self._PROCESSO["nome_tabela_log_evento"]:
                self._FILE_LOG_EVENT.append(payload)
            else:
                payload = self._payload_header(payload)
                self._FILE_LOG = payload

            msg = "Registro de LOG criado!"
        except Exception as error:
            msg = f"""Falha ao tentar inserir um registro na tabela LOG. Erro: {error}"""
        finally:
            return msg

    def Foreground(self, nome_cor):
        cores = self.CORES
        nome_cor = nome_cor.title()
        return cores[nome_cor][0]

    def Background(self, nome_cor):
        cores = self.CORES
        nome_cor = nome_cor.title()
        return cores[nome_cor][1]

    def _Carriage_Return(self):
        self._CR = not self._CR
        return self._CR

    @property
    def OS_INFO(self) -> dict:
        return self._os_info()

    @property
    def CORES(self):
        return self._CORES

    @property
    def NOTSET(self):
        self._LOG_LEVEL_CODE = 0
        self._LOG_LEVEL_NAME = "NOTSET"
        self._LOG_LEVEL_COLOR = self.Branco_Fore
        return self._LOG_LEVEL_CODE

    @property
    def WARNING(self):
        self._LOG_LEVEL_CODE = 10
        self._LOG_LEVEL_NAME = "WARNING"
        self._LOG_LEVEL_COLOR = self.Amarelo_Claro_Fore
        return self._LOG_LEVEL_CODE

    @property
    def DEBUG(self):
        self._LOG_LEVEL_CODE = 20
        self._LOG_LEVEL_NAME = "DEBUG"
        self._LOG_LEVEL_COLOR = self.Verde_Claro_Fore
        return self._LOG_LEVEL_CODE

    @property
    def ERROR(self):
        self._LOG_LEVEL_CODE = 30
        self._LOG_LEVEL_NAME = "ERROR"
        self._LOG_LEVEL_COLOR = self.Vermelho_Claro_Fore
        return self._LOG_LEVEL_CODE

    @property
    def INFO(self):
        self._LOG_LEVEL_CODE = 40
        self._LOG_LEVEL_NAME = "INFO"
        self._LOG_LEVEL_COLOR = self.Cinza_Claro_Fore
        return self._LOG_LEVEL_CODE

    @property
    def CRITICAL(self):
        self._LOG_LEVEL_CODE = 50
        self._LOG_LEVEL_NAME = "CRITICAL"
        self._LOG_LEVEL_COLOR = self.Vermelho_Fore + self.Preto_Back
        return self._LOG_LEVEL_CODE

    @property
    def DESTAQUE(self):
        self._LOG_LEVEL_CODE = 50
        self._LOG_LEVEL_NAME = "DESTAQUE"
        self._LOG_LEVEL_COLOR = self.Cyan_Fore
        return self._LOG_LEVEL_CODE

    @property
    def ENFASE(self):
        self._LOG_LEVEL_CODE = 50
        self._LOG_LEVEL_NAME = "ENFASE"
        self._LOG_LEVEL_COLOR = self.Branco_Fore + self.Negrito + self.Sublinhado
        return self._LOG_LEVEL_CODE

    @property
    def Preto_Fore(self):
        return self.Foreground("Preto")

    @property
    def Vermelho_Fore(self):
        return self.Foreground("Vermelho")

    @property
    def Verde_Fore(self):
        return self.Foreground("Verde")

    @property
    def Amarelo_Fore(self):
        return self.Foreground("Amarelo")

    @property
    def Azul_Fore(self):
        return self.Foreground("Azul")

    @property
    def Magenta_Fore(self):
        return self.Foreground("Magenta")

    @property
    def Cyan_Fore(self):
        return self.Foreground("Cyan")

    @property
    def Cinza_Claro_Fore(self):
        return self.Foreground("Cinza Claro")

    @property
    def Cinza_Escuro_Fore(self):
        return self.Foreground("Cinza Escuro")

    @property
    def Vermelho_Claro_Fore(self):
        return self.Foreground("Vermelho Claro")

    @property
    def Verde_Claro_Fore(self):
        return self.Foreground("Verde Claro")

    @property
    def Amarelo_Claro_Fore(self):
        return self.Foreground("Amarelo Claro")

    @property
    def Azul_Claro_Fore(self):
        return self.Foreground("Azul Claro")

    @property
    def Magenta_Claro_Fore(self):
        return self.Foreground("Magenta Claro")

    @property
    def Cyan_Claro_Fore(self):
        return self.Foreground("Cyan Claro")

    @property
    def Branco_Fore(self):
        return self.Foreground("Branco")

    @property
    def Preto_Back(self):
        return self.Background("Preto")

    @property
    def Vermelho_Back(self):
        return self.Background("Vermelho")

    @property
    def Verde_Back(self):
        return self.Background("Verde")

    @property
    def Amarelo_Back(self):
        return self.Background("Amarelo")

    @property
    def Azul_Back(self):
        return self.Background("Azul")

    @property
    def Magenta_Back(self):
        return self.Background("Magenta")

    @property
    def Cyan_Back(self):
        return self.Background("Cyan")

    @property
    def Cinza_Claro_Back(self):
        return self.Background("Cinza Claro")

    @property
    def Cinza_Escuro_Back(self):
        return self.Background("Cinza Escuro")

    @property
    def Vermelho_Claro_Back(self):
        return self.Background("Vermelho Claro")

    @property
    def Verde_Claro_Back(self):
        return self.Background("Verde Claro")

    @property
    def Amarelo_Claro_Back(self):
        return self.Background("Amarelo Claro")

    @property
    def Azul_Claro_Back(self):
        return self.Background("Azul Claro")

    @property
    def Magenta_Claro_Back(self):
        return self.Background("Magenta Claro")

    @property
    def Cyan_Claro_Back(self):
        return self.Background("Cyan Claro")

    @property
    def Branco_Back(self):
        return self.Background("Branco")

    @property
    def Negrito(self):
        return self.Foreground("Negrito")

    @property
    def Italico(self):
        return self.Foreground("Italico")

    @property
    def Sublinhado(self):
        return self.Foreground("Sublinhado")

    @property
    def Riscado(self):
        return self.Foreground("Riscado")

    @property
    def Inverte(self):
        return self.Foreground("Inverte")

    @property
    def Reverse(self):
        return self.Foreground("Reverse")

    @property
    def Reset(self):
        return self.Foreground("Reset")

    @staticmethod
    def _cores_ansi() -> dict:
        file_json, cores = None, None
        try:
            #cor = foreground , background
            #Exemplo: Fore = Vermelho, back = amarelo --> cores["Vermelho"][0]+cores["Amarelo"][1]
            # 0 = Cor da fonte, 1 = Cor do fundo
            # json_file = open("cores_ansi.json")
            # cores = json.load(json_file)
            cores = {"Preto": ["\033[1;30m", "\033[1;40m"],
                     "Vermelho": ["\033[1;31m", "\033[1;41m"],
                     "Verde": ["\033[1;32m", "\033[1;42m"],
                     "Amarelo": ["\033[1;33m", "\033[1;43m"],
                     "Azul": ["\033[1;34m", "\033[1;44m"],
                     "Magenta": ["\033[1;35m", "\033[1;45m"],
                     "Cyan": ["\033[1;36m", "\033[1;46m"],
                     "Cinza Claro": ["\033[1;37m", "\033[1;47m"],
                     "Cinza Escuro": ["\033[1;90m", "\033[1;100m"],
                     "Vermelho Claro": ["\033[1;91m", "\033[1;101m"],
                     "Verde Claro": ["\033[1;92m", "\033[1;102m"],
                     "Amarelo Claro": ["\033[1;93m", "\033[1;103m"],
                     "Azul Claro": ["\033[1;94m", "\033[1;104m"],
                     "Magenta Claro": ["\033[1;95m", "\033[1;105m"],
                     "Cyan Claro": ["\033[1;96m", "\033[1;106m"],
                     "Branco": ["\033[1;97m", "\033[1;107m"],
                     "Negrito": ["\033[;1m", None],
                     "Italico": ["\033[;3m", None],
                     "Sublinhado": ["\033[;4m", None],
                     "Riscado": ["\033[;9m", None],
                     "Inverte": ["\033[;7m", None],
                     "Reverse": ["\033[;17m", None],
                     "Reset": ["\033[0;0m", None]
                     }
        except Exception as error:
            print(error)
        finally:
            #son_file.close()
            return cores

    @staticmethod
    def _os_info() -> dict:
        os_info = {"user_os": os.getlogin(),
                   "user_db": None,
                   "local_ip": skt.gethostbyname(skt.gethostname()),
                   "local_name": skt.gethostname(),
                   "processor": so.machine(),
                   "so_platafor": so.platform(),
                   "so_system": so.system(),
                   "so_version": so.version()
                   }
        return os_info
