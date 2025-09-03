#!/usr/bin/env python

__RCSID__ = "$Id$"


# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script

Script.setUsageMessage(
    """
Check replica location against the a given SE
Usage:
   cta-check-get-replicas <ascii file with lfn list> <destSE>
"""
)

Script.parseCommandLine(ignoreErrors=True)

from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

fc = FileCatalog()

args = Script.getPositionalArgs()
if len(args) > 0:
    infile = args[0]
    destSE = args[1]
else:
    Script.showHelp()

f0 = open(f"{infile}_NoReplicas.lfns", "w")
f1 = open(f"{infile}_SingleReplica_{destSE}.lfns", "w")
f2 = open(f"{infile}_MultipleReplicas_{destSE}.lfns", "w")
f3 = open(f"{infile}_MissingReplica_{destSE}.lfns", "w")


#@Script()
def main():
    resList = read_inputs_from_file(infile)
    for lfn in resList:
        checkReplicas(lfn)
    gLogger.notice(f"Files dumped: check {infile}_*.lfns")


def checkReplicas(lfn):
    res = fc.getReplicas(lfn)
    if not res["OK"]:
        gLogger.notice("Failed to get replicas for lfn", lfn)
        return res["Message"]
    if lfn in res["Value"]["Successful"]:
        resDict = res["Value"]["Successful"][lfn]
        nReplicas = len(resDict)
        if destSE in resDict:
            if nReplicas == 1:
                f1.write(f"{lfn}\n")
            else:
                f2.write(f"{lfn}\n")
        else:
            if nReplicas == 0:
                f0.write(f"{lfn}\n")
            else:
                f3.write(f"{lfn}\n")
    else:
        res = DIRAC.S_ERROR(f"Failed to get replicas for lfn {lfn}")
        gLogger.notice(res["Message"])
        return res


if __name__ == "__main__":
    main()
