#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os

# DIRAC imports
from DIRAC.Core.Base.Script import Script
import DIRAC

Script.parseCommandLine(ignoreErrors=True)

from DIRAC import gLogger
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient


@Script()
def main():
    fcc = FileCatalogClient()
    dirac = Dirac()
    resJDL = dirac.getJobJDL(os.environ["JOBID"])

    idata = resJDL["Value"]["InputData"]
    if isinstance(idata, str):
        idata = []
        if "LFN" in resJDL["Value"]["InputData"]:
            idata.append(resJDL["Value"]["InputData"].split("LFN:")[1])
        else:
            idata.append(resJDL["Value"]["InputData"])
    else:
        idata = resJDL["Value"]["InputData"]

    for lfn in idata:
        gLogger.notice(f"Checking input file:\n {lfn} ")
        file_name = os.path.basename(lfn)
        code = os.system("./dirac_simtel_check " + file_name)
        if code != 0:
            gLogger.error(f"Corrupted file:\n {lfn}")
            gLogger.notice("Setting nsb=-1")
            res = fcc.setMetadata(lfn, {"nsb": -1})
            if not res["OK"]:
                return res

    DIRAC.exit()


if __name__ == "__main__":
    main()
