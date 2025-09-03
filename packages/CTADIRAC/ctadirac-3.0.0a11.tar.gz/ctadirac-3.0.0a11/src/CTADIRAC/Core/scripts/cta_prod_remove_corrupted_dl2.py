#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os
import subprocess

# DIRAC imports
from DIRAC.Core.Base.Script import Script
import DIRAC
from DIRAC import gLogger
from DIRAC.Interfaces.API.Dirac import Dirac
from CTADIRAC.Core.Utilities.tool_box import run_number_from_filename
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from DIRAC.Resources.Catalog.TSCatalogClient import TSCatalogClient

Script.parseCommandLine(ignoreErrors=True)

dirac = Dirac()
fcc = FileCatalogClient()
tcc = TSCatalogClient()


def get_osb(job_id):
    res = dirac.getOutputSandbox(job_id)
    if not res["OK"]:
        gLogger.error(res["Message"])


def get_jdl(job_id):
    res = dirac.getJobJDL(job_id)
    if not res["OK"]:
        gLogger.error(res["Message"])
        DIRAC.exit(1)
    input_lfn_list = res["Value"]["InputData"]
    return input_lfn_list


def parse_log(job_id, lfn_list):
    awk_cmd = "awk -F '/' '{print $7}'"
    file = subprocess.check_output(
        f"grep CannotMerge {job_id}/ctapipe_merge_Log.txt | {awk_cmd}", shell=True
    )
    file = file.decode("utf-8").strip()
    gLogger.notice(f"corrupted file {file}")
    for lfn in lfn_list:
        if file in lfn:
            return lfn


def get_metadata(lfn):
    res = fcc.getFileUserMetadata(lfn)
    if not res["OK"]:
        gLogger.error(res["Message"])
        DIRAC.exit(1)
    job_id = res["Value"]["jobID"]
    return job_id


def get_corrupted_simtel_lfn(lfn_list, corrupted_lfn):
    file = os.path.basename(corrupted_lfn)
    run_number = f"run{run_number_from_filename(file, 'ctapipe')}"
    for lfn in lfn_list:
        if run_number in lfn:
            return lfn


def remove(lfn):
    gLogger.notice(f"remove {lfn}")
    res = fcc.removeFile(lfn)
    if not res["OK"]:
        gLogger.error(res["Message"])
    res = tcc.removeFile(lfn)
    if not res["OK"]:
        gLogger.error(res["Message"])


@Script()
def main():
    argss = Script.getPositionalArgs()
    job_ids = argss
    for job_id in job_ids:
        get_osb(job_id)
        input_dl2_lfn_list = get_jdl(job_id)
        input_corrupted_dl2_lfn = parse_log(job_id, input_dl2_lfn_list)
        dl2_job_id = get_metadata(input_corrupted_dl2_lfn)
        input_simtel_lfn_list = get_jdl(dl2_job_id)
        input_corrupted_simtel_lfn = get_corrupted_simtel_lfn(
            input_simtel_lfn_list, input_corrupted_dl2_lfn
        )
        remove(input_corrupted_simtel_lfn)
        remove(input_corrupted_dl2_lfn)


if __name__ == "__main__":
    main()
