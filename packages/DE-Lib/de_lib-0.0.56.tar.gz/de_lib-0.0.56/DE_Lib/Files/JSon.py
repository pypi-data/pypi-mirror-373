import pandas as pd
import json


class JSON:
    def __init__(self):
        ...

    def ExportDataFrame(self,
             df: pd.DataFrame,
             file_name: str,
             file_sufix: str = None,
             file_path: str = "",
             orient: str = "records",
             date_format: str =None,
             double_precision: int = 10,
             force_ascii: bool = True,
             date_unit: str = 'ms',
             default_handler=None,
             lines: bool = False,
             compression: str = "infer",
             index: bool = True,
             indent: int = 2,
             storage_options=None,
             payload: dict = None
             ):
        msg, result = None, None
        try:
            if payload is not None:
                with open(file_name, "w", encoding='utf-8') as outfile:
                    json.dump(payload, outfile, indent=2)
            else:
                if orient not in ["split", "table"]:
                    df.to_json(path_or_buf=file_name,
                               orient=orient,
                               date_format=date_format,
                               double_precision=10,
                               force_ascii=force_ascii,
                               date_unit=date_unit,
                               default_handler=default_handler,
                               lines=lines,
                               compression=compression,
                               # index=index,
                               indent=indent,
                               storage_options=storage_options)
                else:
                    df.to_json(path_or_buf=file_name,
                               orient=orient,
                               date_format=date_format,
                               double_precision=10,
                               force_ascii=force_ascii,
                               date_unit=date_unit,
                               default_handler=default_handler,
                               lines=lines,
                               compression=compression,
                               index=index,
                               indent=indent,
                               storage_options=storage_options)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

