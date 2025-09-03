import pytest
from pathlib import Path
from deepdiff import DeepDiff
from pydantic_yaml import parse_yaml_raw_as

from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)


def test_validation_configuration_generation_default_values():
    validation_configuration = ValidationConfiguration()
    model_dict = validation_configuration.model_dump()
    expected_model_dict = {
        "exclude_metrics": False,
        "custom_templates_path": None,
        "max_failed_rows_number": 100,
        "metrics_validation": False,
        "row_validation": False,
        "schema_validation": False,
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_validation_configuration_generation_custom_values():
    validation_configuration = ValidationConfiguration(
        exclude_metrics=False,
        schema_validation=True,
        metrics_validation=True,
        row_validation=True,
        custom_templates_path=Path("/path/to/custom-templates"),
        max_failed_rows_number=10,
    )

    model_dict = validation_configuration.model_dump()
    expected_model_dict = {
        "exclude_metrics": False,
        "custom_templates_path": Path("/path/to/custom-templates"),
        "max_failed_rows_number": 10,
        "metrics_validation": True,
        "row_validation": True,
        "schema_validation": True,
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_validation_configuration_generation_pydantic_default_values():
    file_content = r"""validation_configuration:
"""

    validation_configuration = parse_yaml_raw_as(ValidationConfiguration, file_content)

    assert validation_configuration is not None

    model_dict = validation_configuration.model_dump()
    expected_model_dict = {
        "exclude_metrics": False,
        "custom_templates_path": None,
        "max_failed_rows_number": 100,
        "metrics_validation": False,
        "row_validation": False,
        "schema_validation": False,
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_validation_configuration_generation_pydantic_custom_values():
    file_content = r"""validation_configuration:
schema_validation: true
metrics_validation: true
row_validation: false
custom_templates_path: /Users/Test/Workspace/DataValidation/Templates
max_failed_rows_number: 5
exclude_metrics: true
"""

    validation_configuration = parse_yaml_raw_as(ValidationConfiguration, file_content)

    assert validation_configuration is not None

    model_dict = validation_configuration.model_dump()
    expected_model_dict = {
        "exclude_metrics": True,
        "custom_templates_path": Path("/Users/Test/Workspace/DataValidation/Templates"),
        "max_failed_rows_number": 5,
        "metrics_validation": True,
        "row_validation": False,
        "schema_validation": True,
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_validation_configuration_invalid_max_failed_rows_number_value_exception():
    with (pytest.raises(ValueError) as ex_info):
        ValidationConfiguration(
            schema_validation=True,
            metrics_validation=True,
            row_validation=True,
            custom_templates_path=Path("/path/to/custom-templates"),
            max_failed_rows_number=-2,
        )

    assert r"""1 validation error for ValidationConfiguration
  Value error, Invalid value for max failed rows number in validation configuration. Value must be greater than or equal to 1. [type=value_error, input_value={'schema_validation': Tru...failed_rows_number': -2}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/value_error""" == str(
        ex_info.value
    )
