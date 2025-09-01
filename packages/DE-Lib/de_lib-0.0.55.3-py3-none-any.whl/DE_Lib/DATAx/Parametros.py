from DE_Lib.Utils import Generic
import pandas as pd

gen = Generic.GENERIC()

class PARAMETROS:
    def __init__(self):
        msg, result = None, None
        try:
            ...
        except Exception as error:
            msg = error
            result = msg
        finally:
            ...

    def getParamIcon(self, df, expr):
        msg, result = None, None
        try:
            result = df.query(f"""NOM_PARAMETRO.str.contains('{expr}')""", engine='python')[['NOM_PARAMETRO', 'VAL_PARAMETRO']]

            # icons = df.query(f"""HASHPARENT=='{hash}'""")
            #result = df.to_dict("RECORDS")
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getParam(self, conn, hash=None):
        """
        Conectar a base de parametros e retornar um dataframe
        :param conn: Conexao com a base de parametros
        :param hash: Hash a ser procurado Default = None = Todos
        :return: Retorna um dataframe com os parametros
        """
        msg, result = None, None
        try:
            if not hash:
                __hash = f"""is null"""
            else:
                __hash = f"""= '{hash}'"""
            # A tabela vw_params_tree (views) tem que existir na base do mesmo owner
            qry = "select * from vw_params_tree"
            result = pd.read_sql(qry, conn)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @property
    def _parametros(self):
        return self.__parametros

    @_parametros.setter
    def _parametros(self, value):
        self.__parametros = value

