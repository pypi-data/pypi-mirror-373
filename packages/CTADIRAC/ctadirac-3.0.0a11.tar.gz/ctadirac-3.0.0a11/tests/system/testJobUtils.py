"""Some useful definitions"""

import os
import time

from DIRAC.Interfaces.API.Job import Job
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC import gLogger


def get_job(job_class=None):
    if not job_class:
        job_class = Job
    job_obj = job_class()
    return job_obj


def get_dirac(dirac_class=None):
    if not dirac_class:
        dirac_class = Dirac
    dirac_obj = dirac_class()
    return dirac_obj


def base_to_all_jobs(j_name, job_class=None):
    print("----------------------------------------------------------------------\n")
    print(f"Submitting job {j_name}")

    J = get_job(job_class)
    J.setName(j_name)
    J.setCPUTime(17800)
    return J


def check_job_status(jobid, exp_status):
    infos = Dirac().getJobStatus(jobid)
    status = infos["Value"][jobid]["Status"]
    n = 0
    secs = float(0.0)
    while status != exp_status:
        n += 1
        if n >= 20:
            gLogger.notice("Too many iterations...")
            print(f"{jobid} waiting too long")
            return [jobid, False]
        elif status in ["Failed", "Deleted", "Killed"]:
            print(f"\n{jobid} {status}")
            gLogger.notice(f"{jobid}: {status} != {exp_status} (waiting 30s)")
            return [jobid, False]
        elif status == "Running":
            print(f"\n{jobid} {status}")
        for _ in range(30):
            time.sleep(1)
            secs += 1.0
            print(f"Waiting [{secs:.1f}s]", end="\r", flush=True)
        print("", end="\r")
        infos = Dirac().getJobStatus(jobid)
        status = infos["Value"][jobid]["Status"]

        if status == exp_status:
            print(f"\n{jobid} {status}")

    return [jobid, True]


def wait_loop_display(string, sleep_time):
    time_loop = sleep_time * 5
    secs = float(0.0)
    for _ in range(time_loop):
        time.sleep(0.2)
        secs += 0.2
        print(f"{string} [{secs:.2f}s]", end="\r", flush=True)
    print("", end="\r")


def check_file(jobid, exp_output, filepath):
    res = False
    with open(filepath) as output:
        if exp_output in output.read():
            print(f"{jobid} produced expected output")
            res = True
        else:
            print(f"{jobid} did not produce expected output")
    return res


def check_job_output(jobid, exp_output, output_file):
    Dirac().getOutputSandbox(jobid)
    dirpath = os.path.join(os.getcwd(), str(jobid))
    Dirac().getJobOutputData(jobid, destinationDir=dirpath)
    filepath = os.path.join(dirpath, output_file)
    if os.path.exists(filepath):
        res = check_file(jobid, exp_output, filepath)
    else:
        print(f"{output_file} not found")
        res = False
    return [jobid, res]


def end_of_all_jobs(job):
    result = get_dirac().submitJob(job)
    # gLogger.notice(f"Job submission result: {result}")
    if result["OK"]:
        print(f"Submitted with job ID: {result['Value']}")

    return result
