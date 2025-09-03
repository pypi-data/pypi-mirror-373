#!/usr/bin/env python
"""
  Check if files exist in the Catalog
  and dump the list of Found and Not Found files

  Usage:
  cta-dms-check-lfn [options] <ascii file with lfn list>
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base.Script import Script
from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file


@Script()
def main():
    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()
    if len(args) > 0:
        infile = args[0]
    else:
        Script.showHelp()

    lfns = read_inputs_from_file(infile)
    lfnsFound = []
    lfnsNotFound = []

    fc = FileCatalogClient()

    for lfn in lfns:
        res = fc.exists(lfn)
        if not res["OK"]:
            gLogger.error(res["Message"])

        if res["Value"]["Successful"][lfn]:
            gLogger.debug(f"{lfn} found in Catalog")
            lfnsFound.append(lfn)
        else:
            gLogger.debug(f"{lfn} not found in Catalog")
            lfnsNotFound.append(lfn)

    fname = infile + "_Found.list"
    f = open(fname, "w")
    for lfn in lfnsFound:
        f.write(lfn + "\n")
    f.close()
    gLogger.notice(f"{len(lfnsFound)} files have been dumped in {fname}")

    fname = infile + "_NotFound.list"
    f = open(fname, "w")
    for lfn in lfnsNotFound:
        f.write(lfn + "\n")
    f.close()
    gLogger.notice(f"{len(lfnsNotFound)} files have been dumped in {fname}")
    DIRAC.exit()


####################################################
if __name__ == "__main__":
    main()
