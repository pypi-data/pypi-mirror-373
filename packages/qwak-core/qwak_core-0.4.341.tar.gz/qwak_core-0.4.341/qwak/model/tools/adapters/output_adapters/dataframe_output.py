import json

from qwak.exceptions import QwakHTTPException

from .json_output import JsonOutput


def df_to_json(result, output_orient: str):
    import pandas as pd

    if isinstance(result, pd.DataFrame):
        return result.to_json(orient=output_orient)

    if isinstance(result, pd.Series):
        return pd.DataFrame(result).to_json(orient=output_orient)
    return json.dumps(result)


class DataFrameOutput(JsonOutput):
    def __init__(self, output_orient: str = "records"):
        self.output_orient = output_orient

    def pack_user_func_return_value(
        self,
        return_result,
    ) -> str:
        try:
            return df_to_json(return_result, self.output_orient)
        except Exception as e:
            raise QwakHTTPException(message=str(e), status_code=500)
