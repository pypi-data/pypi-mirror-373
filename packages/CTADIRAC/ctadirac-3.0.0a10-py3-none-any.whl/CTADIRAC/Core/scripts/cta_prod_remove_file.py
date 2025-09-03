#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os
from multiprocessing import Pool

# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog

from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

Script.setUsageMessage(
    """
Bulk removal of a list of files or a single file
Usage:
   cta-prod-remove-file [options] <lfn>
   cta-prod-remove-file [options] <ascii file with lfn list>
"""
)

Script.parseCommandLine(ignoreErrors=True)

DIRAC.initialize()

fc = FileCatalog()


def removeFile(lfn):
    res = fc.removeFile(lfn)
    if not res["OK"]:
        message = res["Message"]
        gLogger.error(f"Error removing file {lfn}:\n{message}")
        return


@Script()
def main():
    args = Script.getPositionalArgs()
    if len(args) > 0:
        infile = args[0]
    else:
        Script.showHelp()

    if os.path.isfile(infile):
        infileList = read_inputs_from_file(infile)
    else:
        infileList = [infile]
    p = Pool(10)
    p.map(removeFile, infileList)


if __name__ == "__main__":
    main()
