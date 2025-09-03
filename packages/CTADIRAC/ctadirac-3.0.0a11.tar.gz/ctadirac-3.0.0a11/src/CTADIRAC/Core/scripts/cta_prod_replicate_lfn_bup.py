#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
from multiprocessing import Pool

# DIRAC imports
from DIRAC import gLogger
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Core.Base.Script import Script

Script.setUsageMessage(
    """
Extension of dirac-dms-replicate-lfn in multi-thread mode
Allows for bulk replication of a list of LFNs to a destination Storage Element
Usage:
   cta-prod-replicate-lfn <ascii file with lfn list> <SE>
"""
)

Script.parseCommandLine(ignoreErrors=True)

args = Script.getPositionalArgs()
if len(args) > 1:
    infile = args[0]
    SE = args[1]
else:
    Script.showHelp()

# Import of Dirac must comes after parseCommandLine
from DIRAC.Interfaces.API.Dirac import Dirac


@Script()
def main():
    infileList = read_inputs_from_file(infile)
    p = Pool(10)
    p.map(replicateFile, infileList)


def replicateFile(lfn):
    dirac = Dirac()
    res = dirac.replicateFile(lfn, SE)
    if not res["OK"]:
        gLogger.error("Error replicating file", lfn)
        return res["Message"]


if __name__ == "__main__":
    main()
