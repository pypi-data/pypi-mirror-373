import hashlib
import string
from random import choice
import random as rd
import re
import datetime as dt
import sys
import pyautogui
import os
import json
import datetime as dt


class GENERIC:
    def __init__(self):
        self.__strCnn = None


    @staticmethod
    def convert_lob(value):
        msg, result = None, None
        try:
            if hasattr(value, 'read'):
                result = value.read()
            else:
                result = value
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def convert_date(value):
        msg, result = None, None
        try:
            if value:
                if not isinstance(value, str):
                    result = value.strftime("%d-%m-%Y")
                else:
                    result = value
            else:
                result = value
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # region Miscelanea
    @staticmethod
    def findchar(string: str, pattern: str, ocorrencia: int = None, inicio: int = 0, fim: int = 0, trim: bool = True):
        locate = None
        try:
            if trim:
                string = string.strip()
            if fim == 0:
                fim = len(string)
            if fim > inicio and (fim-inicio) > len(pattern):
                string = string[inicio:fim]
            if ocorrencia is not None:
                locate = re.findall(pattern, string)
                if ocorrencia is not None:
                    if ocorrencia > len(locate):
                        locate = locate[len(locate)-1]
        except Exception as error:
            locate = error
        finally:
            return locate

    @staticmethod
    def random_generator(size: int = 6, chars: str = string.ascii_uppercase + string.digits):
        value = ''.join(rd.choice(chars) for _ in range(size))
        return value

    @staticmethod
    def DictSizeBytes(dictName: dict) -> int:
        result = 0
        if isinstance(dictName, dict):
            result = sys.getsizeof(dictName)
            for key, valor in dictName.items():
                result += sys.getsizeof(key) + sys.getsizeof(valor)
        return result

    @staticmethod
    def calcular_formula(self, formula: str, variaveis):
        msg, result = None, None
        try:
            result = eval(formula, {}, variaveis)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
    # endregion

    # region Keys e Hash´s
    @staticmethod
    def build_key(size: int = 24,
                  sep: str = "-",
                  word_length: int = 4,
                  lower_case: bool = True,
                  upper_case: bool = True,
                  digits: bool = True,
                  hex_digits: bool = False,
                  oct_digits: bool = False,
                  special_chars: bool = False,
                  printable_chars: bool = False,
                  control_chars: bool = False
                  ) -> str:
        index = 1
        key = ""
        literal = ""
        if lower_case:
            literal = literal + string.ascii_lowercase
        if upper_case:
            literal = literal + string.ascii_uppercase
        if digits:
            literal = literal + string.digits
        if hex_digits:
            literal = literal + string.hexdigits
        if oct_digits:
            literal = literal + string.octdigits
        if special_chars:
            literal = literal + string.punctuation
        if printable_chars:
            literal = literal + string.printable
        if control_chars:
            literal = literal + string.whitespace
        try:
            for i in range(size):
                letra = choice(literal)
                if index == word_length and i < size - 1:
                    key += letra + sep
                    index = 1
                else:
                    key += letra
                    index += 1
        except Exception as error:
            key = f"Impossivel gerar uma chave. Erro: {error}"
        return key

    @staticmethod
    def build_keys(qtd: int = 1,
                   size: int = 24,
                   sep: str = "-",
                   word_length: int = 4,
                   lower_case: bool = True,
                   upper_case: bool = True,
                   digits: bool = True,
                   hex_digits: bool = False,
                   oct_digits: bool = False,
                   special_chars: bool = False,
                   printable_chars: bool = False,
                   control_chars: bool = False) -> list:
        keys = []
        for index in range(qtd):
            k = GENERIC.build_key(size=size,
                              sep=sep,
                              word_length=word_length,
                              lower_case=lower_case,
                              upper_case=upper_case,
                              digits=digits,
                              hex_digits=hex_digits,
                              oct_digits=oct_digits,
                              special_chars=special_chars,
                              printable_chars=printable_chars,
                              control_chars=control_chars
                              )
            keys.append(k)
        return keys

    @staticmethod
    def hash(word: str, pattern: str = "md5"):
        pattern_list = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
        h, msg, error = None, None, None
        try:
            #value /= b'{word}'/
            if pattern == pattern_list[0]:
                h = hashlib.md5()
            elif pattern == pattern_list[1]:
                h = hashlib.sha1()
            elif pattern == pattern_list[2]:
                h = hashlib.sha224()
            elif pattern == pattern_list[3]:
                h = hashlib.sha256()
            elif pattern == pattern_list[4]:
                h = hashlib.sha384()
            elif pattern == pattern_list[5]:
                h = hashlib.sha512()
            h.update(word.encode())
            msg = h.hexdigest()
        except Exception as error:
            msg = f"""Erro ao tentar montar o HASH. Erro: {error}"""
        finally:
            return msg
    # endregion

    # region Validações Lógicas
    @staticmethod
    def ifnull(var, val):
        if (var is None or var == 'None'):
            value = val
        else:
            value = var
        return value

    @staticmethod
    def iif(condicao: bool, value_true, value_false):
        if condicao:
            value = value_true
        else:
            value = value_false
        return value

    @staticmethod
    def nvl(value, default):
        msg, result = None, None
        try:
            if (value is not None):
                result = value
            else:
                result = default
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def is_valid_int(value):
        msg, result = None, True
        try:
            int(value)
        except Exception as error:
            msg = error
            result = False
        finally:
            return result

    @staticmethod
    def is_valid_float(value):
        msg, result = None, True
        try:
            float(value)
        except Exception as error:
            msg = error
            result = False
        finally:
            return result

    @staticmethod
    def is_valid_type(value, default_value, type="DATETIME",  mask="%Y-%m-%d %H:%M:%S.%f"):
        msg, result = None, None
        try:
            result = value
            if type.upper() == 'DATE':
                if not isinstance(value, dt.date):
                    if GENERIC.is_valid_date(value, mask):
                        result = dt.date(value, mask)
                    else:
                        if GENERIC.is_valid_date(default_value, mask):
                            result = dt.date(default_value, mask)
            elif type.upper() == 'DATETIME':
                if not isinstance(value, dt.datetime):
                    if GENERIC.is_valid_date(value, mask):
                        result = dt.datetime.strptime(value, mask)
                    else:
                        if GENERIC.is_valid_date(default_value, mask):
                            result = dt.datetime.strptime(default_value, mask)
            elif type.upper() == 'INT':
                if not isinstance(value, int):
                    if GENERIC.is_valid_int(value):
                        result = int(value)
                    else:
                        if GENERIC.is_valid_int(default_value):
                            result = int(default_value)
            elif type.upper() == "FLOAT":
                if not isinstance(value, float):
                    if GENERIC.is_valid_float(value):
                        result = float(value)
                    else:
                        if GENERIC.is_valid_float(default_value):
                            result = float(default_value)
            else:
                result = default_value
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def is_valid_date(date_str: str, mascara: str = "%Y-%m-%d %H:%M:%S"):
        msg, result = None, True
        try:
            dt.datetime.strptime(date_str, mascara)
        except Exception as error:
            msg = error
            result = False
        finally:
            return result
    # endregion

    @staticmethod
    def mouse_move(self):
        msg = result = None, None
        try:
            # print([w.title for w in gw.getAllWindows()])
            # janela = gw.getWindowsWithTitle('Teams')
            # janela[0].activate()  # traz para frente
            # #time.sleep(0.5)
            # janela[0].maximize()  # op
            # app = Application().connect(title_re=".*Teams.*")  # ou outro app
            # app.top_window().set_focus()
            now = dt.datetime.now()
            date_start = dt.datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=0)
            date_end = dt.datetime(year=now.year, month=now.month, day=now.day, hour=18, minute=0, second=0)
            print("Simulando atividade... Pressione Ctrl+C para parar.")
            #while True:
            while True:
                if dt.datetime.now() >= date_start and dt.datetime.now() <= date_end:
                    pyautogui.moveRel(xOffset=0, yOffset=1, duration=0.1)  # move o mouse 1 pixel pra baixo
                    pyautogui.moveRel(xOffset=0, yOffset=-1, duration=0.1)  # e volta
                    #pyautogui.click()
                else:
                    break
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def getDBVersion(nome_db, conn):
        """
        :param nome_db: Nome do banco de dados (sys_dba)
        :param conn:  conexao do banco de dados
        :return: string contendo a versao
        """
        msg, result = None, None
        try:
            if nome_db.upper() == "ORACLE":
                # tem que estar com privilegios SYS_DBA
                qry = "SELECT version FROM v$instance"
            if nome_db.upper() == "SQLITE":
                qry = "select sqlite_version()"
            cursor = conn.cursor()
            row = cursor.execute(qry)

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

        # ----------------------------------
    @staticmethod
    def getError(e):
        msg, result = None, None
        try:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            line = exc_tb.tb_lineno
            result = {"line": line, "error_type": exc_type.__name__, "error_msg": e}
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def getRootProject(marcadores=('pyproject.toml', 'setup.py', '.git')):
        msg, result = None, None
        try:
            caminho_atual = os.path.abspath(os.getcwd())
            while caminho_atual != os.path.dirname(caminho_atual):
                if any(os.path.exists(os.path.join(caminho_atual, marcador)) for marcador in marcadores):
                    result = caminho_atual
                    break
                else:
                    result = "Diretório raiz não encontrado com base nos marcadores especificados."
                caminho_atual = os.path.dirname(caminho_atual)
            #raise FileNotFoundError("Diretório raiz não encontrado com base nos marcadores especificados.")
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def camelCase(text):
        msg, result = None, None
        try:
            words = re.split(r'[_\-\s/.,;]+', text)
            result =  words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def snack_case(text):
        msg, result = None, None
        try:
            words = re.split(r'[_\-\s/.,;]+', text)
            result = "_".join(words).lower()
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def setProperty(cls, df, cols:dict):
        """
        Objetivo: Setar as propriedades de uma classe com base em um dataframe
                  Este metodo irá construir propriedades para cada nome de variavel (snack case)
                  e atribuir o valor da variavel para a propriedade, cada propriedade com o tipo especifico.
                  Exemplo: < gen.setProperty(cls=par, df=params, cols={"name":"NOM_VARIAVEL", "value": "VAL_PARAMETRO"})>
        :param cls: Nome da classe que recebera os propriedades
        :param df: DataFrame que contera o nome o valor e o datatype para cada propriedade
        :param cols: Dict --> Nome das colunas do dataframe que terao o conteudo desejado
                              Ex.: {"name": "<nome_coluna>", "value": "<nome_coluna", "datatype": "<nome_coluna>"}
                              representa os nomes da colunas do dataframe que trarão o nome da propriedade,
                              o valor da propriedade e do datatype da propriedade
        :return: Boolean True se sucesso, text se erro com o codigo do erro
        """
        msg, result = None, None
        try:
            __propName, __propValue, __propDType = None, None, None

            for index, row in df.iterrows():
                point = 1
                __propName = GENERIC.snack_case(row[cols["name"]])
                __propValue = GENERIC.nvl(row[cols["value"]], '')
                __propDType = GENERIC.nvl(row[cols["datatype"]], 'String')
                if __propDType.upper() in ("STRING"):
                    point = 2
                    __value = str(GENERIC.convert_lob(__propValue))
                elif __propDType.upper() in ("FLOAT"):
                    point = 3
                    __value = float(GENERIC.convert_lob(__propValue))
                elif __propDType.upper() in ("INTEGER"):
                    point = 4
                    __value = int(GENERIC.convert_lob(__propValue))
                elif __propDType.upper() in ("LIST"):
                    point = 5
                    __value = re.split(r'[_\-\s/.,;]+', GENERIC.convert_lob(__propValue))
                elif __propDType.upper() in ("RECORD"):
                    point = 6
                    __value = json.dumps(__propValue, indent=4, ensure_ascii=False)
                elif __propDType.upper() in ("LIST\RECORD"):
                    point = 7
                    __value = re.split(r'[_\-\s/.,;]+', GENERIC.convert_lob(__propValue))
                elif __propDType.upper() in ("DATE"):
                    point = 8
                    __value = dt.datetime.strptime(GENERIC.convert_lob(__propValue), "Y%-%m-%d")
                elif __propDType.upper() in ("DATETIME"):
                    point = 9
                    __value = dt.datetime.strptime(GENERIC.convert_lob(__propValue), "Y%-%m-%d %H:%M:%S")
                else:
                    point = 10
                    __value = str( __propValue)
                setter = setattr(cls, __propName, __value)
                point = 11
                getter = getattr(cls, __propName)
                point = 12
                result = True
        except Exception as error:
            msg = f"Point: {point} - {error}"
            result = msg
        finally:
            return result

    @staticmethod
    def getPropertysClasse(cls) -> dict:
        msg, result = None, {}
        try:
            x = dir(cls)  # listar_propriedades_instancia(par)
            for x in dir(cls):
                if x[0:1] != "_":
                    result[x] = getattr(cls, str(x))
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    def tab(qtd=1):
        msg, result = None, None
        try:
            result = f"""{chr(9) * qtd}"""
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result
