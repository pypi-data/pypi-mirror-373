#!/usr/bin/env python
"""
Submit a CWL workflow

Usage:
cta-submit-job job.cwl job.yml

"""

__RCSID__ = "$Id$"


import os
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.Interfaces.API.Job import Job
from CTADIRAC.ProductionSystem.CWL.CWLWorkflowStep import WorkflowStep
from DIRAC.Interfaces.API.Dirac import Dirac


def submit_job(run_cwl_file, run_cfg_file=None):

    # Build Job
    job = Job()
    job.setName("test_cwltool_job")

    input_sandbox = [run_cwl_file]
    if run_cfg_file:
        input_sandbox.append(run_cfg_file)
    #print(input_sandbox)
    job.setInputSandbox(input_sandbox)

    job.setOutputSandbox(["*Log.txt"])
    arguments_str = run_cwl_file + " " + run_cfg_file
    job.setExecutable("cwltool",
        arguments=arguments_str,
        logFile="Pipeline_Log.txt",
    )

    job.setTag("production")
    #print(job.workflow.toXML())
    # Submit job
    dirac = Dirac()

    res = dirac.submitJob(job)
    return res


def main():
    Script.parseCommandLine()
    argss = Script.getPositionalArgs()

    run_cwl_file = argss[0]
    run_cfg_file = None
    if len(argss)==2:
        run_cfg_file = argss[1]
    #print(run_cfg_file)

    res = submit_job(
        run_cwl_file,
        run_cfg_file,
    )

    try:
        if not res["OK"]:
            DIRAC.gLogger.error(res["Message"])
            DIRAC.exit(-1)
        else:
            gLogger.notice("Submission Result:", res["Value"])
    except Exception:
        DIRAC.gLogger.exception()
        DIRAC.exit(-1)


if __name__ == "__main__":
    main()
