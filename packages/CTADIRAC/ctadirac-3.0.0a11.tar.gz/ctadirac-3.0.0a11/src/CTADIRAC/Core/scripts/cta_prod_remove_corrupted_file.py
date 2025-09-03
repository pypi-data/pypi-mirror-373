#!/usr/bin/env python

"""
Remove files downloaded as job InputData having a Bad checksum
"""

__RCSID__ = "$Id$"

# Generic imports
import os

# DIRAC imports
import DIRAC
from DIRAC.Core.Base.Script import Script

Script.parseCommandLine()

# Specific DIRAC imports
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.Interfaces.API.Dirac import Dirac


@Script()
def main():
    if "JOBID" in os.environ:
        jobID = os.environ["JOBID"]
        dirac = Dirac()
        res = dirac.getJobJDL(jobID)
        if "InputData" in res["Value"]:
            lfn = res["Value"]["InputData"]

    dm = DataManager(["DIRACFileCatalog"])
    DIRAC.gLogger.notice(f"Check file: {lfn}")

    res = dm.getFile(lfn)

    if lfn in res["Value"]["Failed"]:
        if "Bad checksum" in res["Value"]["Failed"][lfn]:
            DIRAC.gLogger.notice(f"Bad checksum. Removing: {lfn}")
            res = dm.removeFile(lfn)
            if res["OK"]:
                DIRAC.gLogger.notice(f"Successfully removed: {lfn}")
            else:
                DIRAC.gLogger.error(res["Message"])
                DIRAC.exit(-1)
    else:
        DIRAC.gLogger.notice(f"Good checksum for: {lfn}")
        DIRAC.exit()


####################################################
if __name__ == "__main__":
    main()
