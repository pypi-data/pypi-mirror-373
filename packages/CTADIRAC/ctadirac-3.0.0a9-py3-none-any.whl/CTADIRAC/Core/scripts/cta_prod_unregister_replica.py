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
Bulk removal of a list of replicas at a given SE from the catalog
Usage:
   cta-prod-unregister-replica <ascii file with lfn list> <SE>
"""
)

Script.parseCommandLine(ignoreErrors=True)
# Must comes after parseCommandLine
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog

fc = FileCatalog()

args = Script.getPositionalArgs()
if len(args) > 1:
    infile = args[0]
    SE = args[1]
else:
    Script.showHelp()


def unregisterReplicas(lfn):
    res = fc.getReplicas(lfn)
    if res["OK"]:
        if lfn in res["Value"]["Failed"]:
            gLogger.error(res["Value"]["Failed"][lfn])
        else:
            pfn = res["Value"]["Successful"][lfn][SE]
            replicaDict = {lfn: {"PFN": pfn, "SE": SE}}
            res = fc.removeReplica(replicaDict)
            if not res["OK"]:
                gLogger.error(res["Message"])
    else:
        gLogger.error(res["Message"])


@Script()
def main():
    infileList = read_inputs_from_file(infile)
    p = Pool(10)
    p.map(unregisterReplicas, infileList)


if __name__ == "__main__":
    main()
