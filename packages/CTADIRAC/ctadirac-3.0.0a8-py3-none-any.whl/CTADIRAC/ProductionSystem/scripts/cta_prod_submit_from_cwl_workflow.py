#!/usr/bin/env python
"""
Launch a transformation from CWL workflow descriptions

Usage:
    cta-prod-submit-from-cwl-workflow <name of the Transformation> <path of the directory containing CWL files> <CWL file with workflow description> <YAML file with workflow inputs>

Examples:
    cta-prod-submit-from-cwl-workflow Transformation_test ../CWL ../CWL/simulation-run.cwl ../CWL/simulation-run.yml
"""

__RCSID__ = "$Id$"

import re
import DIRAC
from DIRAC.Core.Base.Script import Script
from CTADIRAC.Interfaces.API.MCPipeJob import MCPipeJob
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from CTADIRAC.ProductionSystem.CWL.CWLWorkflow import Workflow


def submit_transformation_from_workflow(transfo, transfo_name, cwl_file, yml_file):
    """Build MC Simulation Transformation"""

    # Build Transformation
    transfo.Name = "TransformationTest"
    transfo.setTransformationName(transfo_name)  # this must be unique
    transfo.setType("MCSimulation")
    transfo.setDescription("Prod6 MC Pipe TS")
    transfo.setLongDescription("Prod6 simulation pipeline")  # mandatory

    # Build Workflow
    wf = Workflow()
    wf.load(cwl_file, yml_file)
    cmd_list = wf.run_workflow(yml_file)

    # Build Job
    MCJob = MCPipeJob()
    MCJob.setType("MCSimulation")
    MCJob.setOutputSandbox(["*Log.txt"])

    # Build steps
    i_step = 1
    for cmd in cmd_list:
        if "dirac_prod_run" in cmd:
            # dirac_prod_run is not a command, add ./ for executable
            cmd = "./" + cmd
            # Replace static run number with dynamic run number to run with DIRAC
            cmd = re.sub("--run [0-9]+", f"--run {MCJob.run_number}", cmd)

        # Run workflow
        step = MCJob.setExecutable(
            str(cmd.split(" ", 1)[0]),
            arguments=str(cmd.split(" ", 1)[1]),
            logFile="Step%i_Log.txt" % i_step,
        )
        step["Value"]["name"] = "Step%i" % i_step
        step["Value"]["descr_short"] = str(cmd.split(" ", 1)[0])
        i_step += 1

    MCJob.setExecutionEnv({"NSHOW": "10"})

    # Submit Transformation
    transfo.setBody(MCJob.workflow.toXML())
    result = transfo.addTransformation()  # transformation is created here
    if not result["OK"]:
        return result
    transfo.setStatus("Active")
    transfo.setAgentType("Automatic")
    return result


@Script()
def main():
    Script.parseCommandLine()
    argss = Script.getPositionalArgs()
    if len(argss) != 4:
        Script.showHelp()
    transfo_name = argss[0]
    config_dir = argss[1]
    cwl_file = argss[2]
    yml_file = argss[3]
    if config_dir not in cwl_file:
        Script.showHelp()
    transfo = Transformation()
    result = submit_transformation_from_workflow(
        transfo, transfo_name, cwl_file, yml_file
    )
    try:
        if not result["OK"]:
            DIRAC.gLogger.error(result["Message"])
            DIRAC.exit(-1)
        else:
            DIRAC.gLogger.notice("Done")
    except Exception:
        DIRAC.gLogger.exception()
        DIRAC.exit(-1)


if __name__ == "__main__":
    main()
