import pandas as pd
import pandavro as pda


class AVRO:
    def __init__(self):
        ...

    def ExportDataFrame(self,
             df: pd.DataFrame,
             file_name: str,
             file_sufix: str = "",
             file_path: str = ""
             ):
        msg, result = None, True
        try:
            pda.to_avro(file_path_or_buffer=file_name, df=df)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

