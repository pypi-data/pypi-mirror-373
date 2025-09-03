import importlib.util
from inspect import signature
from typing import Any, Callable, Dict, Optional

from qwak.exceptions import QwakException
from qwak.feature_store._common.value import (
    UPDATE_QWAK_SDK_WITH_FEATURE_STORE_EXTRA_MSG,
)


def validate_qwargs(qwargs: Dict[Any, Any]):
    for k, v in qwargs.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise QwakException("Only strings are supported in qwargs entries!")


def validate_function(
    function: Optional[Callable], dataframe_type: type, caller_class: type
):
    """
    Validates a transformation function for a given caller class.

    Parameters
    ----------
    function : Optional[Callable]
        The transformation function to be validated. It should have specific type annotations for its parameters and return type.
    dataframe_type : type
        The dataframe type that the dictionary should accept as value
    caller_class : type
        The class that is calling this validation function. Used for generating error messages.

    Raises
    ------
    QwakException
        If the 'pyspark' dependency is missing.
        If the function is empty.
        If the first argument of the function does not have `Dict[str, pyspark.sql.DataFrame]` type annotation.
        If the second argument of the function is present but not named `qwargs` or does not have `Dict[str, str]` type annotation.
        If the function's return type annotation is not `pyspark.sql.DataFrame`.
    """
    if importlib.util.find_spec("pyspark") is None:
        raise QwakException(
            f"Missing 'pyspark' dependency required for {caller_class.__name__} transformation. "
            f"{UPDATE_QWAK_SDK_WITH_FEATURE_STORE_EXTRA_MSG}"
        )
    if not function:
        raise QwakException(
            f"Please provide a valid function for the {caller_class.__name__} transformation"
        )

    function_signature = signature(function)
    function_parameters = function_signature.parameters

    if (
        len(function_parameters) == 0
        or list(function_parameters.values())[0].annotation != Dict[str, dataframe_type]
    ):
        raise QwakException(
            f"The first argument of a {caller_class.__name__} transformation function must have Dict[str, ${dataframe_type}] type annotation"
        )
    elif len(function_parameters) == 2:
        second_argument = list(function_parameters.values())[1]
        if (
            second_argument.name != "qwargs"
            or second_argument.annotation != Dict[str, Any]
        ):
            raise QwakException(
                f"The second argument of a {caller_class.__name__} transformation function must be named qwargs and have "
                "`Dict[str, Any]` type annotation."
            )
    elif len(function_parameters) > 2:
        raise QwakException(
            f"{caller_class.__name__} transformation function must have at most 2 arguments."
        )
    if function_signature.return_annotation != dataframe_type:
        raise QwakException(
            f"{caller_class.__name__} transformation function must ${dataframe_type} return type annotation."
        )
