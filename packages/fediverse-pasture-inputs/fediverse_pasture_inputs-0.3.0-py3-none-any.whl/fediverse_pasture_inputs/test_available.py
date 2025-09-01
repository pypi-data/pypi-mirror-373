import pytest
from typing import Callable, List
from fediverse_pasture.runner.entry import Entry

from .tool.transformer import ExampleTransformer
from . import available
from .types import value_from_dict_for_app, InputData


def test_available():
    assert len(available) > 0


@pytest.mark.parametrize("title, input_data", available.items())
def test_entries(title, input_data):
    assert len(input_data.examples) > 0


@pytest.mark.parametrize("title, input_data", available.items())
async def test_entries_support_result(title, input_data):
    example_transformer = ExampleTransformer()
    if input_data.support:
        func = value_from_dict_for_app(input_data.support.result, "activity")

        for ex in input_data.examples:
            activity = await example_transformer.create_activity(ex)

            assert isinstance(func, Callable)

            result = func(activity)

            assert isinstance(result, str)


@pytest.mark.parametrize("value", [None, {}])
@pytest.mark.parametrize("title, input_data", available.items())
async def test_entries_support_result_on_None(value, title, input_data):
    if input_data.support:
        func = value_from_dict_for_app(input_data.support.result, "mastodon")
        assert isinstance(func, Callable)

        for ex in input_data.examples:
            result = func(value)

            assert result == "❌"


@pytest.mark.parametrize("title, input_data", available.items())
async def test_entries_detail_extractor(title, input_data):
    example_transformer = ExampleTransformer()
    if input_data.details:
        func = value_from_dict_for_app(input_data.details.extractor, "activity")
        assert isinstance(func, Callable)

        expected_count = None

        for ex in input_data.examples:
            activity = await example_transformer.create_activity(ex)

            result = func(activity)

            if expected_count is None:
                expected_count = len(result)

            assert isinstance(result, list)
            assert len(result) == expected_count


def app_names_for_input_data(input_data: InputData) -> List[str]:
    assert input_data.details
    return list(input_data.details.extractor.keys()) + ["sharkey"]


@pytest.mark.parametrize("value", [None, {}])
@pytest.mark.parametrize("title, input_data", available.items())
async def test_entries_detail_on_none_and_empty_dict(
    value, title, input_data: InputData
):
    if input_data.details:
        for app in app_names_for_input_data(input_data):
            entry = Entry(entry={app: value})

            result = input_data.detail_for_app(entry, app)
            assert isinstance(result, list)
