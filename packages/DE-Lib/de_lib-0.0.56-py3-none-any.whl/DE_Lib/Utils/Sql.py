import re

class SQL:
    def __init__(self):
        ...

    @staticmethod
    def colunas_cursor(cursor) -> list:
        header = [head[0] for head in cursor.description]
        return header

    @staticmethod
    def Crud(sql: str = None, values: dict = None, conexao=None, commit: bool = True):
        msg, result, linhas_afetadas = None, [], 0
        try:
            if not isinstance(sql, str) or sql is None:
                raise Exception(f"""Comando sql não foi definido {sql}""")
            if conexao is None:
                raise Exception(f"""Conexão não foi informada {conexao}""")
            if not isinstance(values, dict):
                raise Exception(f"""Lista de valores não foi informada {values}""")
            cursor = conexao.cursor()
            cursor.execute(sql, values)
            linhas_afetadas = cursor.rowcount
            cursor.close()
            if commit:
                conexao.commit()
            msg = f"""Comando SQL executado com sucesso!"""
        except Exception as error:
            msg = f"""Falha ao tentar executar o comando SQL! Erro: {error}"""
            result = msg
        finally:
            result = {"linhas_afetadas": linhas_afetadas, "mensagem": msg, "sql": sql}
            return result

    @staticmethod
    def fromListDictToList(listDict, keyValue) -> list:
        result = None
        try:
            __list = []
            for n in range(len(listDict)):
                __list.append(listDict[n][keyValue])
            result = __list
        except Exception as error:
            result = error.args[0]
        finally:
            return result

    @staticmethod
    def ListToDict(colsname:list,  lst:list):
        msg, result = None, None
        try:
            result = []
            for n in range(len(lst)):
                result.append(dict(zip(colsname, lst[n])))
        except Exception as error:
            msg = error.args[0]
            result = msg
        finally:
            return result

    @staticmethod
    def CursorToDict(cursor) -> list:
        msg, result = None, None
        try:
            columnsName = [col[0] for col in cursor.description]
            result = []
            rows = cursor.fetchall()
            if len(rows) > 0:
                for row in rows:
                    result.append(dict(zip(columnsName, row)))
            else:
                result.append(dict.fromkeys(columnsName))
        except Exception as error:
            msg = error.args[0]
            result = msg
        finally:
            return result

    @staticmethod
    def setQueryWhere( qry, new_where:str=None):
        msg, result = None, None
        try:
            match = re.search(r"\bWHERE\b(.*?)(\bGROUP\b|\bORDER\b|\bFETCH\b|$)", qry, re.IGNORECASE | re.DOTALL)
            if not new_where:
                __and = ""
            else:
                __and = "\n\t\t\t\t\tand"
            if match:
                # Substitui a cláusula WHERE inteira pela nova
                parte_antes = qry[:match.start(1)]
                parte_where = match.group(1).strip()
                parte_depois = qry[match.end(1):]
                result = f"{parte_antes} {parte_where} {__and} {new_where} {parte_depois}"
            else:
                # Não havia WHERE — adiciona antes do ORDER/GROUP/FETCH ou no fim
                insert_pos = re.search(r"\bGROUP\b|\bORDER\b|\bFETCH\b", qry, re.IGNORECASE)
                if insert_pos:
                    result = qry[:insert_pos.start()] + f" WHERE {new_where} " + qry[insert_pos.start():]
                else:
                    result = qry.strip() + f" WHERE {new_where}"
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def setPlaceHolders(self, stmt: str, database:str="SQLALCHEMY") -> dict:
        msg, result = None, {}
        try:
            if database.upper()  in ("ORACLE", "SQLALCHEMY"):
                #__text = f""":{key}"""
                __text = re.findall(r":([a-zA-Z_][a-zA-Z0-9_]*)", stmt)
            elif database.upper() == "MYSQL":
                #__text = f"""%({key})s"""
                __text = re.findall(r":%\(([a-zA-Z_][a-zA-Z0-9_]*)\)s", stmt)
            __size = len(__text) + 1
            __dummy = stmt.find(__text)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result