from unittest.mock import patch
import pytest
import typer
from CTADIRAC.Core.Utilities.typer_callbacks import (
    cond_dict_callback,
    job_fields_arg_callback,
    job_parameters_callback,
    job_site_callback,
    job_status_callback,
    transformation_fields_arg_callback,
    transformation_or_job_id_callback,
    transformation_status_callback,
    transformation_type_callback,
)


def test_transformation_type_callback() -> None:
    value = "MCSimulation,Processing"
    expected_result: list[str] = ["MCSimulation", "Processing"]
    result = transformation_type_callback(value)
    assert result == expected_result

    value = "InvalidType"
    with pytest.raises(typer.BadParameter):
        transformation_type_callback(value)

    value = "All"
    expected_result = None
    result: list[str] | None = transformation_type_callback(value)
    assert result == expected_result


def test_transformation_status_callback():
    value = "Active,Completed"
    expected_result: list[str] = ["Active", "Completed"]
    result = transformation_status_callback(value)
    assert result == expected_result

    value = "InvalidStatus"
    with pytest.raises(typer.BadParameter):
        transformation_status_callback(value)

    value = "All"
    expected_result = None
    result: list[str] | None = transformation_status_callback(value)
    assert result == expected_result


def test_transformation_or_job_id_callback() -> None:
    value = "123,456"
    expected_result = ["123", "456"]
    result = transformation_or_job_id_callback(value)
    assert result == expected_result

    value = "InvalidID"
    with pytest.raises(typer.BadParameter):
        transformation_or_job_id_callback(value)


def test_job_parameters_callback() -> None:
    value = "AgentLocalSE"
    result = job_parameters_callback(value)
    assert result == value

    value = "InvalidParam"
    with pytest.raises(typer.BadParameter):
        job_parameters_callback(value)


@patch("CTADIRAC.Core.Utilities.typer_callbacks.getSites")
def test_job_site_callback(mock_get_sites) -> None:
    site = "ARC.CSCS.ch"
    mock_get_sites.return_value = {"OK": True, "Value": [site]}
    value = site
    expected_result = [value]
    result = job_site_callback(value)
    assert result == expected_result

    value = "InvalidSite"
    with pytest.raises(typer.BadParameter):
        job_site_callback(value)


def test_job_status_callback() -> None:
    value = "Done,Failed"
    expected_result = ["Done", "Failed"]
    result = job_status_callback(value)
    assert result == expected_result

    value = "InvalidStatus"
    with pytest.raises(typer.BadParameter):
        job_status_callback(value)


def test_transformation_fields_arg_callback() -> None:
    value = ["TransformationID", "123,456", "Status", "Active"]
    expected_result = [{"Status": ["Active"], "TransformationID": ["123", "456"]}]
    result = transformation_fields_arg_callback(value)
    assert result == expected_result

    value = ["InvalidField", "value"]
    with pytest.raises(typer.BadParameter):
        transformation_fields_arg_callback(value)


def test_job_fields_arg_callback() -> None:
    value = ["JobGroup", "123,456", "Status", "Done,Failed"]
    expected_result = [{"Status": ["Done", "Failed"], "JobGroup": ["123", "456"]}]
    result = job_fields_arg_callback(value)
    assert result == expected_result

    value = ["InvalidField", "value"]
    with pytest.raises(typer.BadParameter):
        job_fields_arg_callback(value)


def test_cond_dict_callback():
    result = cond_dict_callback(None)
    assert result is None

    value = "{'ProductionID': [1,2,3]}"
    result = cond_dict_callback(value)
    assert isinstance(result, dict)

    value = "None"
    with pytest.raises(typer.BadParameter) as exc_info:
        cond_dict_callback(value)
    assert "should be a dict type" in exc_info.value.args[0]

    value = "{'UnknownField': [1,2,3]}"
    with pytest.raises(typer.BadParameter) as exc_info:
        cond_dict_callback(value)
    assert "is a bad key" in exc_info.value.args[0]
