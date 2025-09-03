from unittest.mock import patch
import pytest
import typer
from CTADIRAC.Core.scripts.cta_job_get_parameter import (
    extract_parameter,
    finalize,
    get_job_list_from_job,
    get_job_list_from_transformation,
    get_jobs_parameters,
    job,
    transformation,
)


@patch("CTADIRAC.Core.scripts.cta_job_get_parameter.TransformationClient")
def test_get_job_list_from_transformation(mock_transformation_client) -> None:
    mock_transformation_client.return_value.getTransformations.return_value = {
        "OK": True,
        "Value": [{"TransformationID": 1}],
    }
    mock_transformation_client.return_value.getTransformationTasks.return_value = {
        "OK": True,
        "Value": [{"ExternalID": "1"}],
    }
    job_list = get_job_list_from_transformation(condition={"Status": ["Active"]})
    assert job_list == [1]


@patch("CTADIRAC.Core.scripts.cta_job_get_parameter.JobMonitoringClient")
def test_get_job_list_from_job(mock_job_monitoring_client) -> None:
    mock_job_monitoring_client.return_value.getJobs.return_value = {
        "OK": True,
        "Value": [1],
    }

    job_list = get_job_list_from_job(condition={"Status": ["Done"]})
    assert job_list == [1]

    mock_job_monitoring_client.return_value.getJobs.return_value = {
        "OK": False,
        "Value": [None],
    }
    job_list = get_job_list_from_job(condition={"Status": ["Done"]})
    assert job_list == []


total_cpu = "TotalCPUTime(s)"


@patch("CTADIRAC.Core.scripts.cta_job_get_parameter.JobMonitoringClient")
def test_get_jobs_parameters(mock_job_monitoring_client) -> None:
    mock_job_monitoring_client.return_value.getJobParameters.return_value = {
        "OK": True,
        "Value": {1: {total_cpu: "152"}},
    }
    jobs_parameters = get_jobs_parameters([1])
    assert jobs_parameters == {1: {total_cpu: "152"}}

    mock_job_monitoring_client.return_value.getJobParameters.return_value = {
        "OK": False,
        "Value": None,
    }
    with pytest.raises(typer.Exit) as exec_info:
        get_jobs_parameters([1])
    assert str(exec_info.value) == "{'OK': False, 'Value': None}"


@patch("CTADIRAC.Core.scripts.cta_job_get_parameter.get_jobs_parameters")
def test_extract_parameter(mock_get_job_param) -> None:
    mock_get_job_param.return_value = {1: {total_cpu: "152"}}
    param_list = extract_parameter([1])
    assert param_list == [152]

    mock_get_job_param.return_value = {
        1: {"AgentLocalSE": "CSCS-Disk", total_cpu: "152"}
    }
    param_list = extract_parameter([1], "AgentLocalSE")
    assert param_list == ["CSCS-Disk"]

    mock_get_job_param.return_value = {1: {total_cpu: "152"}}
    with pytest.raises(typer.Exit) as exec_info:
        extract_parameter([1], "AgentLocalSE")
    assert str(exec_info.value) == "Empty parameter list"


@patch("CTADIRAC.Core.scripts.cta_job_get_parameter.extract_parameter")
def test_finalize(mock_extract_param) -> None:
    mock_extract_param.return_value = []
    finalize([], "Test", "", "", False)


@patch("CTADIRAC.Core.scripts.cta_job_get_parameter.get_job_list_from_transformation")
def test_transformation_cmd(mock_get_lft) -> None:
    mock_get_lft.return_value = []
    with pytest.raises(typer.Exit) as exec_info:
        transformation(fields=["TransformationID", 152])
    assert str(exec_info.value) == "No jobs selected"


@patch("CTADIRAC.Core.scripts.cta_job_get_parameter.get_job_list_from_job")
def test_job_cmd(mock_get_lfj) -> None:
    mock_get_lfj.return_value = []
    with pytest.raises(typer.Exit) as exec_info:
        job(fields=["JobGroup", 152])
    assert str(exec_info.value) == "No jobs selected"
