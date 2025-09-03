import inspect as inspect
from typing import Callable

from qwak.exceptions import QwakException
from qwak.feature_store.feature_sets.transformations.functions.schema import Schema
from qwak.tools.logger import get_qwak_logger

logger = get_qwak_logger()


def _get_schema_string(user_function: Callable, schema: Schema) -> str:
    import pandas as pd

    input_signature = inspect.signature(user_function)
    return_annotation = input_signature.return_annotation
    if return_annotation is inspect._empty:
        raise QwakException(
            f"return type annotation missing for {user_function.__name__}"
        )

    if return_annotation is pd.DataFrame:
        # return type is a Pandas DataFrame - all cols must be named
        if any([c for c in schema.columns if not c.name]):
            raise QwakException(
                f"pandas UDFs that return pd.DataFrame must have named columns."
                f" Please specify the name in the schema constructor"
                f" the Schema constructor? {user_function.__name__}"
            )
        return schema.to_ddl()

    if return_annotation is pd.Series:
        # return type is a series (meaning the UDF returns a single colum)
        if len(schema.columns) != 1:
            raise QwakException(
                f"Exactly 1 return type must be set for"
                f" a pandas udf returning pd.Series,"
                f" Function {user_function.__name__} returning pd.Series must return exactly 1 return type."
            )
        return_col = schema.columns[0]
        if return_col.name:
            logger.warning(
                f"return column name specified for {user_function.__name__},"
                f" however it will be disregarded as it returns pd.Series"
            )
        return return_col.type.to_ddl()

    raise QwakException(
        f"missing or unrecognized type annotation for {user_function.__name__}"
    )


def qwak_pandas_udf(output_schema: Schema) -> Callable:
    if not isinstance(output_schema, Schema):
        raise QwakException("Wrong schema type set for qwak_pandas_udf")

    def _qwak_pandas_udf(user_function: Callable) -> Callable:
        setattr(
            user_function,
            "_schema",
            _get_schema_string(user_function=user_function, schema=output_schema),
        )
        return user_function

    return _qwak_pandas_udf
