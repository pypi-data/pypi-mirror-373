#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os
from multiprocessing import Pool

# DIRAC imports
import DIRAC
from DIRAC import gLogger
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Core.Base.Script import Script
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog

Script.setUsageMessage(
    """
Bulk get file size from a list of lfns
Usage:
   cta-prod-get-file-size [options] <ascii file with lfn list>
"""
)

Script.parseCommandLine(ignoreErrors=True)

fc = FileCatalog()


@Script()
def main():
    args = Script.getPositionalArgs()
    if len(args) > 0:
        infile = args[0]
    else:
        Script.showHelp()

    infileList = read_inputs_from_file(infile)
    p = Pool(1)
    p.map(getSize, infileList)


def getSize(lfn):
    res = fc.getFileSize(lfn)
    if not res["OK"]:
        gLogger.error("Failed to get size for lfn", lfn)
        return res["Message"]
    if lfn in res["Value"]["Successful"]:
        size_GB = res["Value"]["Successful"][lfn] / (1024 * 1024 * 1024)
        gLogger.notice(f"{os.path.basename(lfn)} {size_GB:.1f} GB")
    else:
        res = DIRAC.S_ERROR(f"Failed to get size for lfn {lfn}")
        gLogger.error(res["Message"])
        return res


if __name__ == "__main__":
    main()
