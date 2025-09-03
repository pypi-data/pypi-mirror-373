#!/usr/bin/env python
import sys
import logging
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import cast
import json
import tempfile
import yaml
import random
from rich.text import Text

from cwl_utils.parser import (
    load_document_by_uri,
    save,
)

from cwl_utils.parser.cwl_v1_2 import (
    CommandLineTool,
    File,
    Saveable,
    Workflow,
)

from ruamel.yaml import YAML


from CTADIRAC.ctadiracx.cli.submission_models import (
    JobParameterModel,
    JobSubmissionModel,
)

from CTADIRAC.ctadiracx.cli.utils import _get_metadata

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# -----------------------------------------------------------------------------
# Job Execution Coordinator
# -----------------------------------------------------------------------------


class JobExecutionCoordinator:
    """Reproduction of the JobExecutionCoordinator.

    In Dirac, you would inherit from it to define your pre/post-processing strategy.
    In this context, we assume that these stages depend on the JobType.
    """

    def __init__(self, job: JobSubmissionModel):
        # Get a metadata instance
        self.metadata = _get_metadata(job)

    def pre_process(self, job_path: Path, command: list[str]) -> list[str]:
        """Pre process a job according to its type."""
        if self.metadata:
            return self.metadata.pre_process(job_path, command)

        return command

    def post_process(self, job_path: Path) -> bool:
        """Post process a job according to its type."""
        if self.metadata:
            return self.metadata.post_process(job_path)

        return True


# -----------------------------------------------------------------------------
# JobWrapper
# -----------------------------------------------------------------------------


def _pre_process(
    executable: CommandLineTool | Workflow,
    arguments: JobParameterModel | None,
    job_exec_coordinator: JobExecutionCoordinator,
    job_path: Path,
) -> list[str]:
    """
    Pre-process the job before execution.

    :return: True if the job is pre-processed successfully, False otherwise
    """
    logger = logging.getLogger("JobWrapper - Pre-process")

    # Prepare the task for cwltool
    logger.info("Preparing the task for cwltool...")
    command = ["cwltool"]

    task_dict = save(executable)
    task_path = job_path / "task.cwl"
    with open(task_path, "w") as task_file:
        YAML().dump(task_dict, task_file)
    command.append(str(task_path.name))

    if arguments:
        if arguments.sandbox:
            # Download the files from the sandbox store
            logger.info("Downloading the files from the sandbox store...")
            for sandbox in arguments.sandbox:
                sandbox_path = Path("sandboxstore") / f"{sandbox}.tar.gz"
                with tarfile.open(sandbox_path, "r:gz") as tar:
                    tar.extractall(job_path)
            logger.info("Files downloaded successfully!")

        # Download input data from the file catalog
        logger.info("Downloading input data from the file catalog...")
        input_data = []
        for _, input_value in arguments.cwl.items():
            input = input_value
            if not isinstance(input_value, list):
                input = [input_value]

            for item in input:
                if not isinstance(item, File):
                    continue

                # TODO: path is not the only attribute to consider, but so far it is the only one used
                if not item.path:
                    raise NotImplementedError("File path is not defined.")

                input_path = Path(item.path)
                if "filecatalog" in input_path.parts:
                    input_data.append(item)

        for file in input_data:
            # TODO: path is not the only attribute to consider, but so far it is the only one used
            if not file.path:
                raise NotImplementedError("File path is not defined.")

            input_path = Path(file.path)
            shutil.copy(input_path, job_path / input_path.name)
            file.path = file.path.split("/")[-1]
        logger.info("Input data downloaded successfully!")

        # Prepare the parameters for cwltool
        logger.info("Preparing the parameters for cwltool...")
        parameter_dict = save(cast(Saveable, arguments.cwl))
        parameter_path = job_path / "parameter.cwl"
        with open(parameter_path, "w") as parameter_file:
            YAML().dump(parameter_dict, parameter_file)
        command.append(str(parameter_path.name))
    return job_exec_coordinator.pre_process(job_path, command)


def _post_process(
    status: int,
    stdout: str,
    stderr: str,
    job_path: Path,
    job_exec_coordinator: JobExecutionCoordinator,
):
    """
    Post-process the job after execution.

    :return: True if the job is post-processed successfully, False otherwise
    """
    logger = logging.getLogger("JobWrapper - Post-process")
    if status != 0:
        raise RuntimeError(f"Error {status} during the task execution.")

    logger.info(stdout)
    logger.info(stderr)

    job_exec_coordinator.post_process(job_path)


def run_job(job: JobSubmissionModel) -> bool:
    """
    Executes a given CWL workflow using cwltool.
    This is the equivalent of the DIRAC JobWrapper.

    :return: True if the job is executed successfully, False otherwise
    """
    logger = logging.getLogger("JobWrapper")
    job_exec_coordinator = JobExecutionCoordinator(job)

    # Isolate the job in a specific directory
    job_path = Path(".") / "workernode" / f"{random.randint(1000, 9999)}"
    job_path.mkdir(parents=True, exist_ok=True)

    try:
        # Pre-process the job
        logger.info("Pre-processing Task...")
        command = _pre_process(
            job.task,
            job.parameters[0] if job.parameters else None,
            job_exec_coordinator,
            job_path,
        )
        logger.info("Task pre-processed successfully!")

        # Execute the task
        logger.info(f"Executing Task: {command}")
        result = subprocess.run(command, capture_output=True, text=True, cwd=job_path)

        if result.returncode != 0:
            logger.error(
                f"Error in executing workflow:\n{Text.from_ansi(result.stderr)}"
            )
            return False
        logger.info("Task executed successfully!")

        # Post-process the job
        logger.info("Post-processing Task...")
        _post_process(
            result.returncode,
            result.stdout,
            result.stderr,
            job_path,
            job_exec_coordinator,
        )
        logger.info("Task post-processed successfully!")
        return True

    except Exception:
        logger.exception("JobWrapper: Failed to execute workflow")
        return False
    # finally:
    # Clean up
    # if job_path.exists():
    #    shutil.rmtree(job_path)


def main():
    logger = logging.getLogger("JobWrapper")

    json_str = sys.argv[1]

    job_model_dict = json.loads(json_str)

    task_dict = job_model_dict["task"]

    with tempfile.NamedTemporaryFile("w+", suffix=".cwl", delete=False) as f:
        yaml.dump(task_dict, f)
        f.flush()
        task_obj = load_document_by_uri(f.name)

    job_model_dict["task"] = task_obj

    job = JobSubmissionModel.model_validate(job_model_dict)

    res = run_job(job)
    if res:
        logger.info("Job done.")
    else:
        logger.info("Job failed.")


if __name__ == "__main__":
    main()
