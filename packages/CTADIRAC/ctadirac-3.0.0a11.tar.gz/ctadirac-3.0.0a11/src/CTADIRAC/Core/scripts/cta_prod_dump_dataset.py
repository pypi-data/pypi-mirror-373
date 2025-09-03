#!/usr/bin/env python
"""
Dump in a file the list of files for a given dataset

Usage:
   cta-prod-dump-dataset <datasetName or ascii file with a list of datasets>
"""

__RCSID__ = "$Id$"

import os
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient


@Script()
def main():
    Script.parseCommandLine(ignoreErrors=True)
    argss = Script.getPositionalArgs()
    fc = FileCatalogClient()

    datasetList = []
    if len(argss) == 1:
        if os.path.isfile(argss[0]):
            gLogger.notice(f"Reading datasets from input file: {argss[0]}")
            datasetList = read_inputs_from_file(argss[0])
        else:
            datasetList.append(argss[0])
    else:
        Script.showHelp()

    for dataset in datasetList:
        res = fc.getDatasetFiles(dataset)
        if not res["OK"]:
            gLogger.error("Failed to get files for dataset:", res["Message"])
            DIRAC.exit(-1)
        else:
            lfnList = res["Value"]["Successful"][dataset]
            f = open(dataset + ".list", "w")
            for lfn in lfnList:
                f.write(lfn + "\n")
            f.close()
            gLogger.notice(f"{len(lfnList)} files have been put in {dataset}.list")
    DIRAC.exit()


####################################################
if __name__ == "__main__":
    main()
