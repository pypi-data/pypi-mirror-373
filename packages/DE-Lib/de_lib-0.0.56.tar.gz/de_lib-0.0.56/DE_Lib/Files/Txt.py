import pandas as pd
import csv


class TXT:
    def __init__(self):
        ...

    def ExportDataFrame(self,
                        df: pd.DataFrame,
                        file_name: str,
                        file_sufix: str = "",
                        file_path: str = "",
                        sep: str = "\t",
                        na_rep: str = "",
                        float_format: str = None,
                        columns: list = None,
                        header: bool = True,
                        index: bool = True,
                        index_label: str = None,
                        mode: str = 'w',
                        encoding: str = None,
                        compression: str = "infer",
                        quoting: int = csv.QUOTE_ALL,
                        quotechar: str = "\"",
                        line_terminator: str = None,
                        chunksize: object = None,
                        date_format: str = "%Y-%m-%d %H:%M:%S",
                        doublequote: bool = True,
                        escapechar: str = None,
                        decimal: str = ".",
                        errors: str = "strict",
                        storage_options: str = None
                        ):
        msg, result = None, None
        try:
            df.to_csv(path_or_buf=file_name,
                      sep=sep,
                      na_rep=na_rep,
                      float_format=float_format,
                      columns=columns,
                      header=header,
                      index=index,
                      index_label=index_label,
                      mode=mode,
                      encoding=encoding,
                      compression=compression,
                      quoting=quoting,
                      quotechar=quotechar,
                      #line_terminator=line_terminator,
                      chunksize=chunksize,
                      date_format=date_format,
                      doublequote=doublequote,
                      escapechar=escapechar,
                      decimal=decimal,
                      errors=errors,
                      storage_options=storage_options
                      )
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

