#!/usr/bin/env python
from typing import NoReturn
import numpy as np
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
import matplotlib.pyplot as plt
from DIRAC.Core.Base.Script import Script
from DIRAC.WorkloadManagementSystem.Client.JobMonitoringClient import (
    JobMonitoringClient,
)
from DIRAC.TransformationSystem.Client.TransformationClient import (
    TransformationClient,
)
from DIRAC import gLogger

from CTADIRAC.Core.Utilities.typer_callbacks import (
    ALLOWED_PARAMETERS,
    PARAMETER_DICT,
    job_fields_arg_callback,
    job_parameters_callback,
    transformation_fields_arg_callback,
)

script = Script()
# Disabling DIRAC script argument parsing
script.localCfg.isParsed = True
script.parseCommandLine(ignoreErrors=True)

app = typer.Typer()

fields_arg_help = (
    "Fields to select jobs. VALUE can be a single value or a coma separated list"
)

default_job_parameter = "TotalCPUTime"
jobs_parameter: str = typer.Option(
    default_job_parameter,
    "--param",
    "-p",
    callback=job_parameters_callback,
    help="Job parameter to be selected. See 'show-parameter' command.",
    show_default=True,
)

do_save_plot: str = typer.Option(
    None, "--plot", help="Plot the data in file specified by filename"
)
do_save_data: str = typer.Option(
    None, "--data", help="Save the data in file specified by filename"
)
with_stat: str = typer.Option(None, "--stat", help="Add mean and std dev in plot")

trans_fields_arg = typer.Argument(
    ...,
    metavar="FIELD VALUE ...",
    callback=transformation_fields_arg_callback,
    help=fields_arg_help,
)
job_fields_arg = typer.Argument(
    ...,
    metavar="FIELD VALUE ...",
    callback=job_fields_arg_callback,
    help=fields_arg_help,
)

progress_description = "[progress.description]{task.description}"
progress_final_desc = "Getting jobs list [green]\N{check mark}"
progress_jobs_failed_desc = "Getting jobs list [red]\N{cross mark}"


def get_job_list_from_transformation(condition: dict) -> list:
    """Get the jobs ID list for given transformations status and type"""
    with Progress(
        SpinnerColumn(),
        TextColumn(progress_description),
        transient=False,
    ) as progress:
        prog_task = progress.add_task(description="Getting jobs list...", total=None)
        trans_client = TransformationClient()

        res = trans_client.getTransformations(condition)
        job_list = []
        if res["OK"]:
            for trans_info in res["Value"]:
                trans_id = trans_info["TransformationID"]
                tasks_info = trans_client.getTransformationTasks(
                    {"TransformationID": trans_id}
                )
                for task in tasks_info["Value"]:
                    job_list.append(int(task["ExternalID"]))
        else:
            gLogger.error(res)
        if job_list:
            progress.update(prog_task, description=progress_final_desc)
        else:
            progress.update(prog_task, description=progress_jobs_failed_desc)
    return job_list


def get_job_list_from_job(condition: dict) -> list:
    with Progress(
        SpinnerColumn(),
        TextColumn(progress_description),
        transient=False,
    ) as progress:
        task = progress.add_task(description="Getting jobs list...", total=None)
        jm_client = JobMonitoringClient()
        res_jobs = jm_client.getJobs(condition)
        if res_jobs["OK"]:
            if res_jobs["Value"]:
                progress.update(task, description=progress_final_desc)
                return res_jobs["Value"]
            else:
                progress.update(task, description=progress_jobs_failed_desc)
                return []
        else:
            progress.update(task, description=progress_jobs_failed_desc)
            gLogger.error(res_jobs)
            return []


def get_jobs_parameters(jobs_list: list):
    """Get the job parameters for given list"""
    with Progress(
        SpinnerColumn(),
        TextColumn(progress_description),
        transient=False,
    ) as progress:
        task = progress.add_task(description="Getting jobs parameters...", total=None)
        jm_client = JobMonitoringClient()
        result = jm_client.getJobParameters(jobs_list)
        if result["OK"]:
            progress.update(
                task, description="Getting jobs parameters [green]\N{check mark}"
            )
            return result["Value"]
        else:
            progress.update(
                task, description="Getting jobs parameters [red]\N{cross mark}"
            )
            raise typer.Exit(result)


def extract_parameter(
    jobs_list: list, parameter: str = PARAMETER_DICT[default_job_parameter]
) -> list:
    """Extract the parameter from the jobs parameters"""
    jobs_parameters = get_jobs_parameters(jobs_list)
    param_list = []
    for parameters in jobs_parameters.values():
        try:
            param_list.append(float(parameters.get(parameter)))
        except ValueError:
            param_list.append(parameters.get(parameter))
        except TypeError:
            continue
    if not param_list:
        raise typer.Exit("Empty parameter list")
    else:
        typer.echo(f"{len(param_list)} entries selected.")
    return param_list


def plot_data(
    param_list: list, file_name: str, jobs_parameter: str, with_stat: bool = False
) -> None:
    """Plot data"""
    with Progress(
        SpinnerColumn(),
        TextColumn(progress_description),
        transient=False,
    ) as progress:
        task = progress.add_task(description="Creating plot...", total=None)
        figure_name: str = f"{file_name}.png"
        plt.figure(figsize=(12, 8))
        plt.xlabel(jobs_parameter)
        plt.ylabel("Number of jobs")
        if isinstance(param_list[0], (int, float)):
            # Plot histogram for numerical data
            plt.hist(param_list, bins=10, color="steelblue", edgecolor="black")
            if with_stat:
                # Adding mean and std dev:
                mean = np.mean(param_list)
                std_dev = np.std(param_list)
                plt.legend(
                    [
                        f"Total jobs: {len(param_list)}, Mean: {mean:.2f}, Std Dev: {std_dev:.2f}"
                    ]
                )
        else:
            # Count the frequency of each unique string
            string_counts = {}
            for string in param_list:
                string_counts[string] = string_counts.get(string, 0) + 1

            # Plot bar chart for string data
            plt.bar(string_counts.keys(), string_counts.values(), color="steelblue")
            plt.xticks(rotation=45, ha="right")
            if with_stat:
                plt.legend([f"Total jobs: {len(param_list)}"])
        plt.tight_layout()
        plt.savefig(figure_name)
        progress.update(
            task, description=f"{figure_name} created [green]\N{check mark}"
        )


def save_data(param_list: list, file_name: str) -> None:
    """Print data list"""
    with Progress(
        SpinnerColumn(),
        TextColumn(progress_description),
        transient=False,
    ) as progress:
        task = progress.add_task(description="Saving data...", total=None)
        dat_file: str = f"{file_name}.dat"
        str_param_list: list[str] = [str(param) for param in param_list]
        with open(dat_file, "w") as f:
            f.write("\n".join(str_param_list))
        progress.update(task, description=f"{dat_file} created [green]\N{check mark}")


def finalize(
    jobs_list: list, jobs_parameter: str, plot: str, data: str, with_stat: bool
) -> None:
    typer.echo(f"{len(jobs_list)} jobs selected")
    param_list = extract_parameter(jobs_list, jobs_parameter)
    if plot:
        plot_data(param_list, plot, jobs_parameter, with_stat)
    if data:
        save_data(param_list, data)


# Command defintion:
@app.command("show-parameter")
def show_parameter() -> NoReturn:
    """Display the job parameters list"""
    typer.echo(ALLOWED_PARAMETERS)
    raise typer.Exit()


@app.command("transformation")
def transformation(
    plot: str = do_save_plot,
    with_stat: bool = with_stat,
    jobs_parameter: str = jobs_parameter,
    data: str = do_save_data,
    fields: list[str] = trans_fields_arg,
) -> None:
    """Select jobs parameters using transformation fields"""
    fields = fields[0]
    jobs_list = get_job_list_from_transformation(fields)
    if not jobs_list:
        raise typer.Exit("No jobs selected")
    finalize(jobs_list, jobs_parameter, plot, data, with_stat)


@app.command("job")
def job(
    plot: str = do_save_plot,
    with_stat: bool = with_stat,
    jobs_parameter: str = jobs_parameter,
    data: str = do_save_data,
    fields: list[str] = job_fields_arg,
) -> None:
    """Select jobs parameters using job fields"""
    fields = fields[0]
    jobs_list = get_job_list_from_job(fields)
    if not jobs_list:
        raise typer.Exit("No jobs selected")
    finalize(jobs_list, jobs_parameter, plot, data, with_stat)


if __name__ == "__main__":
    app()
