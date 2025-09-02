import pandas as pd


class XLSX:
    def __init__(self):
        ...

    def ExportDataFrame(self
                       ,df: pd.DataFrame
                       ,file_name: str
                       ,file_path: str = ""
                       ,file_sufix: str = ""
                       ,sheet_name: str = 'Dados'
                       ,na_rep: str = ""
                       ,float_format: str = None
                       ,columns: list = None
                       ,header: bool = True
                       ,index: bool = True
                       ,index_label=None
                       ,startrow: int = 0
                       ,startcol: int = 0
                       ,engine: str = "xlsxwriter"
                       ,merge_cells=True
                       ,encoding: str = None
                       ,inf_rep: str = "inf"
                       ,verbose: bool = True
                       ,freeze_panes=None
                       ,storage_options=None
                       ):
        msg, result = None, None
        try:
            df.to_excel(file_or_path=file_name
                        ,sheet_name=sheet_name
                        ,na_rep=na_rep
                        ,float_format=float_format
                        ,columns=columns
                        ,header=header
                        ,index=index
                        ,index_label=index_label
                        ,startrow=startrow
                        ,startcol=startcol
                        ,engine=engine
                        ,merge_cells=merge_cells
                        ,encoding=encoding
                        ,inf_rep=inf_rep
                        ,verbose=verbose
                        ,freeze_panes=freeze_panes
                        ,storage_options=storage_options
                        )
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

