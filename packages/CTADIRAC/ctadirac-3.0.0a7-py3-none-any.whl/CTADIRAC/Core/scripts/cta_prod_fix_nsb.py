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
        gLogger.notice(f"Checking input Log file:\n {lfn} ")
        file_name = os.path.basename(lfn)

        # List the content of the tar file
        res = list(os.popen("tar -tf " + file_name + " '*log.gz'"))
        tardir = res[0].split("/")[0]
        # Extract the tar file
        code = os.system("tar -xvf " + file_name)
        if code != 0:
            gLogger.error(f"Unable to untar Log file:\n {file_name}")
            DIRAC.exit(-1)
        os.system("gunzip -r " + tardir)
        res = list(
            os.popen("grep camera_CTA-LST -r " + tardir + " | grep file | wc -l")
        )
        if res[0].strip() != "4":
            data_lfn = lfn.replace("Log", "Data").replace("log_hist.tar", "simtel.zst")
            gLogger.error(f"Buggy Data file:\n {data_lfn}")
            gLogger.notice("Setting nsb=-1")
            res = fcc.setMetadata(data_lfn, {"nsb": -1})
            if not res["OK"]:
                return res

        code = os.system("rm -Rf " + tardir)
        if code != 0:
            gLogger.error("Unable to remove tar directory")
            DIRAC.exit(-1)
        code = os.system("rm " + file_name)
        if code != 0:
            gLogger.error(f"Unable to remove Log file:\n {file_name}")
            DIRAC.exit(-1)

    DIRAC.exit()


if __name__ == "__main__":
    main()
