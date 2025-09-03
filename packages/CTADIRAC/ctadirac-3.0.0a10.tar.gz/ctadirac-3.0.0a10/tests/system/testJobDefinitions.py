""" Utility for building job tests
"""

import os
import json

from DIRAC import rootPath
from DIRAC.Interfaces.API.Job import Job
from DIRAC.Core.Workflow.Parameter import Parameter
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.DataManagementSystem.Client.DataManager import DataManager

from DIRAC.tests.Utilities.utils import find_all
from testJobUtils import base_to_all_jobs, end_of_all_jobs

dm = DataManager()
dirac = Dirac()
test_dir = "/ctao/tests/prodsys"
git_repo = "https://gitlab.cta-observatory.org/arrabito/mandel4ts.git"
workflow_path = "DIRAC/tests/Workflow"
exec_script = "exe-script.py"
mp_test = "mpTest.py"
mandelbrot_script = "./mandel4ts/mandelbrot.py"
mandelbrot_arg = "-P 0.0005 -M 1000 -L @{JOB_ID} -N 200"


def hello_world():
    """simple hello world job"""

    J = base_to_all_jobs("hello_world")
    try:
        J.setInputSandbox([find_all(exec_script, rootPath, workflow_path)[0]])
    except IndexError:
        J.setInputSandbox([find_all(exec_script, ".", workflow_path)[0]])
    J.setExecutable(exec_script, "", "hello_world.log")
    return end_of_all_jobs(J)


def hello_world_site_spec(site="CTAO.PIC.es"):
    """simple hello world job to specific site"""

    J = base_to_all_jobs(f"hello_world{site.split('.')[1]}")
    try:
        J.setInputSandbox([find_all(exec_script, rootPath, workflow_path)[0]])
    except IndexError:
        J.setInputSandbox([find_all(exec_script, ".", workflow_path)[0]])
    J.setExecutable(exec_script, "", "hello_world.log")
    J.setDestination(site)
    return end_of_all_jobs(J)


def mp_job(site="CTAO.PIC.es"):
    """simple hello world job with 6 CPUs"""

    J = base_to_all_jobs("mp_job")
    try:
        J.setInputSandbox([find_all(mp_test, rootPath, "DIRAC/tests/Utilities")[0]])
    except IndexError:
        J.setInputSandbox([find_all(mp_test, ".", "DIRAC/tests/Utilities")[0]])
    J.setExecutable(mp_test, "", "mp_job.log")
    J.setTag("multi-core")
    J.setNumberOfProcessors(minNumberOfProcessors=8)
    J.setDestination(site)
    return end_of_all_jobs(J)


def hello_world_input(input_lfn):
    """simple hello world job with input data"""
    J = base_to_all_jobs("hello_worldInput")
    J.setInputData(input_lfn)
    J.setExecutable("ls", "-ltrA", "hello_worldInput.log")
    return end_of_all_jobs(J)


def hello_world_output(output_file, exe_script, se):
    """Job with Output Data"""
    J = base_to_all_jobs("hello_worldOutput")
    with open(exe_script, "w") as script:
        script.write("#!/bin/bash\n")
        script.write(f"echo 'This is a test file' > {output_file}\n")
    J.setExecutable(exe_script)
    J.setExecutable("ls", arguments="-ltrA")
    J.setOutputData(output_file, output_se=se)
    return end_of_all_jobs(J)


def mandelbrot_simulation():
    J = base_to_all_jobs("mandelbrot_simulation")
    J.setExecutable(f"git clone {git_repo}")
    J.setExecutable(mandelbrot_script, arguments=mandelbrot_arg)
    return end_of_all_jobs(J)


def create_workflow_body_step():
    job = Job()
    job.setName("mandelbrot raw")
    job.setOutputSandbox(["*log"])
    # this is so that the JOB_ID within the transformation can be evaluated on the fly in the job application, see below
    job.workflow.addParameter(
        Parameter(
            "JOB_ID", "000000", "string", "", "", True, False, "Initialize JOB_ID"
        )
    )
    # define the job workflow in 3 steps
    # job step1: setup software
    job.setExecutable(f"git clone {git_repo}")
    # job step2: run mandelbrot application
    # note how the JOB_ID (within the transformation) is passed as an argument and will be evaluated on the fly
    job.setExecutable(mandelbrot_script, arguments=mandelbrot_arg)
    return job.workflow.toXML()


def create_workflow_body_step1(output_se):
    job = Job()
    job.setName("mandelbrot raw")
    job.setOutputSandbox(["*log"])
    # this is so that the JOB_ID within the transformation can be evaluated on the fly in the job application, see below
    job.workflow.addParameter(
        Parameter(
            "JOB_ID", "000000", "string", "", "", True, False, "Initialize JOB_ID"
        )
    )
    # define the job workflow in 3 steps
    # job step1: setup software
    job.setExecutable(f"git clone {git_repo}")
    # job step2: run mandelbrot application
    # note how the JOB_ID (within the transformation) is passed as an argument and will be evaluated on the fly
    job.setExecutable(mandelbrot_script, arguments=mandelbrot_arg)
    # job step3: upload data and set metadata
    output_path = os.path.join(test_dir, "mandelbrot/images/raw")
    output_pattern = "data_*txt"
    output_metadata = json.dumps(
        {
            "application": "mandelbrot",
            "image_format": "ascii",
            "image_width": 7680,
            "image_height": 200,
        }
    )
    job.setExecutable(
        "./mandel4ts/dirac-add-files.py",
        arguments=f"{output_path} '{output_pattern}' {output_se} '{output_metadata}'",
    )
    return job.workflow.toXML()


def create_workflow_body_step2(output_se):
    job = Job()
    job.setName("merge mandelbrot")
    job.setOutputSandbox(["*log"])
    # define the job workflow in 3 steps
    # job step1: setup software
    job.setExecutable(f"git clone {git_repo}")
    # job step2: run mandelbrot merge
    job.setExecutable("./mandel4ts/merge_data.py")
    # job step3: upload data and set metadata
    output_path = os.path.join(test_dir, "mandelbrot/images/merged")
    output_pattern = "data_merged*txt"
    nb_input_files = 7
    output_metadata = json.dumps(
        {
            "application": "mandelbrot",
            "image_format": "ascii",
            "image_width": 7680,
            "image_height": 200 * nb_input_files,
        }
    )
    job.setExecutable(
        "./mandel4ts/dirac-add-files.py",
        arguments=f"{output_path} '{output_pattern}' {output_se} '{output_metadata}'",
    )
    return job.workflow.toXML()


def clean_dir(dir):
    """Clean directory"""
    res = dm.cleanLogicalDirectory(dir)
    return res


def add_file(lfn, se):
    """Upload file to SE"""
    res = dirac.addFile(lfn, os.path.basename(lfn), se)
    return res
