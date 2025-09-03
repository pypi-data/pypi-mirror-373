from typing import Union
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationStatus
from DIRAC.WorkloadManagementSystem.Client import JobStatus
from DIRAC.ConfigurationSystem.Client.Helpers.Resources import getSites
import typer


def transformation_type_callback(value: str) -> Union[list[str], None]:
    trans_types: list[str] = value.split(",")
    allowed_types: list[str] = ["MCSimulation", "Processing", "Merging", "All"]
    for t_type in trans_types:
        if t_type not in allowed_types:
            raise typer.BadParameter(
                f"Bad transformation type '{t_type}'. Allowed types: {allowed_types}"
            )
        if t_type == "All":
            return None
    return trans_types


def transformation_status_callback(value: str) -> Union[list[str], None]:
    allowed_status: list[str] = TransformationStatus.TRANSFORMATION_STATES + ["All"]
    status_list: list[str] = value.split(",")
    for status in status_list:
        if status not in allowed_status:
            raise typer.BadParameter(
                f"Bad transformation status '{status}'. Allowed status: {allowed_status}"
            )
        if status == "All":
            return None
    return status_list


ALLOWED_PARAMETERS: list[str] = [
    "AgentLocalSE",
    "CEQueue",
    "CPUNormalizationFactor",
    "DiskSpace",
    "GridCE",
    "HostName",
    "JobType",
    "JobWrapperPID",
    "LastUpdateCPU",
    "LoadAverage",
    "LocalAccount",
    "MatcherServiceTime",
    "Memory",
    "MemoryUsed",
    "ModelName",
    "NormCPUTime",
    "OutputSandboxMissingFiles",
    "PayloadPID",
    "PilotAgent",
    "Pilot_Reference",
    "ScaledCPUTime",
    "TotalCPUTime",
    "WallClockTime",
]

TRUE_PARAMETERS: list[str] = [
    "AgentLocalSE",
    "CEQueue",
    "CPUNormalizationFactor",
    "DiskSpace(MB)",
    "GridCE",
    "HostName",
    "JobType",
    "JobWrapperPID",
    "LastUpdateCPU(s)",
    "LoadAverage",
    "LocalAccount",
    "MatcherServiceTime",
    "Memory(MB)",
    "MemoryUsed(MB)",
    "ModelName",
    "NormCPUTime(s)",
    "OutputSandboxMissingFiles",
    "PayloadPID",
    "PilotAgent",
    "Pilot_Reference",
    "ScaledCPUTime(s)",
    "TotalCPUTime(s)",
    "WallClockTime(s)",
]
PARAMETER_DICT = dict(zip(ALLOWED_PARAMETERS, TRUE_PARAMETERS))


def transformation_or_job_id_callback(value: str):
    value = value.split(",")
    try:
        for val in value:
            int(val)
    except (TypeError, AttributeError, ValueError):
        raise typer.BadParameter(f"Bad parameters type '{val}' should be an integer")
    return value


def job_parameters_callback(value: str) -> str:
    if value not in ALLOWED_PARAMETERS:
        raise typer.BadParameter(f"Bad parameters '{value}'")
    return PARAMETER_DICT[value]


def job_site_callback(value: str):
    res_sites = getSites()
    sites = []
    if res_sites["OK"]:
        sites = res_sites["Value"]
    values = value.split(",")
    for val in values:
        if val not in sites:
            raise typer.BadParameter(f"Bad sites '{value}'. Allowed sites: {sites}")
    return values


def job_status_callback(value: str) -> Union[list[str], None]:
    allowed_status: list[str] = JobStatus.JOB_FINAL_STATES + ["All"]
    status_list: list[str] = value.split(",")
    for status in status_list:
        if status not in allowed_status:
            raise typer.BadParameter(
                f"Bad job status '{status}'. Allowed status: {allowed_status}"
            )
        if status == "All":
            return None
    return status_list


ALLOWED_JOB_FIELDS = {
    "JobGroup": transformation_or_job_id_callback,
    "Site": job_site_callback,
    "Status": job_status_callback,
}

ALLOWED_TRANSFROMATION_FIELDS = {
    "TransformationID": transformation_or_job_id_callback,
    "Status": transformation_status_callback,
    "Type": transformation_type_callback,
}


def transformation_fields_arg_callback(values: list) -> list[dict]:
    argument_dict = {}
    for i in range(0, len(values), 2):
        arg = values[i]
        value = values[i + 1]
        if arg in ALLOWED_TRANSFROMATION_FIELDS:
            trans_value = ALLOWED_TRANSFROMATION_FIELDS[arg](value)
            argument_dict[arg] = trans_value
        else:
            raise typer.BadParameter(
                f"Argument '{arg}' not in allowed transformation fields: {list(ALLOWED_TRANSFROMATION_FIELDS.keys())}"
            )
    return [argument_dict]


def job_fields_arg_callback(values: list) -> list[dict]:
    argument_dict = {}
    for i in range(0, len(values), 2):
        arg = values[i]
        value = values[i + 1]
        if arg in ALLOWED_JOB_FIELDS:
            trans_value = ALLOWED_JOB_FIELDS
            argument_dict[arg] = trans_value[arg](value)
        else:
            raise typer.BadParameter(
                f"Argument '{arg}' not in allowed job fields: {list(ALLOWED_JOB_FIELDS.keys())}"
            )
    return [argument_dict]


PRODUCTION_FIELDS: list[str] = [
    "ProductionID",
    "ProductionName",
    "Status",
    "CreationDate",
    "LastUpdate",
    "AuthorDN",
    "AuthorGroup",
]


def cond_dict_callback(value: str | None):
    if value is None:
        return None
    cond_dict = eval(value)
    if not isinstance(cond_dict, dict):
        example = "{'ProductionID': [1,2,3]}"
        raise typer.BadParameter(f"'{value}' should be a dict type: '{example}'")
    else:
        for key in cond_dict.keys():
            if key not in PRODUCTION_FIELDS:
                raise typer.BadParameter(
                    f"'{key}' is a bad key.\nAvailable keys: {PRODUCTION_FIELDS}"
                )
    return cond_dict
