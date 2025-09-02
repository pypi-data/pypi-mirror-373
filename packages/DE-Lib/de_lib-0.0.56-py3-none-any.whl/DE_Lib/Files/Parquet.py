import pandas as pd


class PARQUET:
    def __init__(self):
        ...

    def ExportDataFrame(self,
                df: pd.DataFrame,
                file_name: str,
                file_sufix: str = None,
                file_path: str = "",
                engine: str = "pyarrow",
                compression: str = "snappy",
                index: bool = False,
                partition_cols=None
                ):
        msg, result = None, None
        try:
            df.to_parquet(path=file_name
                         ,engine=engine
                         ,compression=compression
                         ,index=index
                         ,partition_cols=partition_cols
                         )
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

