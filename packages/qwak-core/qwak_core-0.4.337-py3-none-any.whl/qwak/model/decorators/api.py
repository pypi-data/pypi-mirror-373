from typing import Callable

from dependency_injector.wiring import Provide, inject

from qwak.exceptions import QwakException
from qwak.inner.runtime_di.containers import QwakRuntimeContainer
from qwak.model.adapters.input_adapters.base_input_adapter import BaseInputAdapter
from qwak.model.adapters.input_adapters.dataframe_input_adapter import (
    DataFrameInputAdapter,
)
from qwak.model.adapters.output_adapters.base_output_adapter import BaseOutputAdapter
from qwak.model.adapters.output_adapters.dataframe_output_adapter import (
    DataFrameOutputAdapter,
)

API_NOT_CONFIGURED_ERROR_MESSAGE = (
    "There has been an error configuring the Qwak model. When testing locally, "
    "please use 'run_local' as described in our docs: "
    "https://docs.qwak.com/docs/testing-locally#/running-models-locally"
)


@inject
def api_decorator(
    analytics: bool = True,
    analytics_sample_ratio: float = 1.0,
    analytics_exclude_columns: list = [],
    feature_extraction: bool = False,
    input_adapter: BaseInputAdapter = DataFrameInputAdapter(),
    output_adapter: BaseOutputAdapter = DataFrameOutputAdapter(),
    api_decorator_function_creator=Provide[
        QwakRuntimeContainer.api_decorator_function_creator
    ],
) -> Callable:
    if callable(analytics):
        raise TypeError(
            """
        You forgot to call the `@api` decorator.

        Correct way -
        @api()
        def function():
            pass

        Wrong way -
        @api
        def function():
            pass
        """
        )
    try:
        return api_decorator_function_creator(
            analytics,
            feature_extraction,
            input_adapter,
            output_adapter,
            analytics_sample_ratio,
            analytics_exclude_columns,
        )
    except TypeError as e:
        if "__call__() takes 1" in str(e):
            raise QwakException(API_NOT_CONFIGURED_ERROR_MESSAGE)
