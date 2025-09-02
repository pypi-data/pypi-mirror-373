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
            qry = f"""
                    SELECT LEVEL - 1 "level"
                          ,LPAD(' ', (LEVEL - 1) * 2) || DISPLAY AS HIERARQUIA
                          ,HASH
                          ,HASHPARENT
                          ,NUM_ORDEM
                          ,NOM_PARAMETRO
                          ,TAGS
                          ,NOM_VARIAVEL
                          ,DISPLAY
                          ,TIPO_PARAMETRO
                          ,DES_DATATYPE
                          ,VAL_PARAMETRO
                          ,DES_PARAMETRO
                          ,FLG_ENCRYPT
                          ,FLG_NULLABLE
                          ,FLG_UPDATEABLE
                          ,FLG_TEMPLATE
                          ,FLG_ATIVO
                          ,DAT_INI_VIGENCIA
                          ,DAT_FIM_VIGENCIA
                      FROM bi_dax.dax_param
                     WHERE DAT_FIM_VIGENCIA IS NULL
                     START WITH HASHPARENT {__hash}
                    CONNECT BY PRIOR HASH = HASHPARENT
                      ORDER SIBLINGS BY NUM_ORDEM
                  """
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

