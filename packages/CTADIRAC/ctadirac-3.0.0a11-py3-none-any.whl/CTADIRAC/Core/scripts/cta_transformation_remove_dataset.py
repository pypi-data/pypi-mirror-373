#!/usr/bin/env python
"""
Create a transformation to remove the files of a dataset (all replicas)

Usage:
   cta-transformation-remove-dataset <dataset_name> <group_size>
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient


def get_dataset_files(dataset_name):
    fc = FileCatalogClient()
    res = fc.getDatasetFiles(dataset_name)
    if not res["OK"]:
        gLogger.error("Failed to get files for dataset:", res["Message"])
        DIRAC.exit(-1)
    else:
        lfn_list = res["Value"]["Successful"][dataset_name]
        gLogger.notice(f"Found {len(lfn_list)} files for removal")
    return lfn_list


@Script()
def main():
    Script.parseCommandLine(ignoreErrors=True)
    argss = Script.getPositionalArgs()
    if len(argss) != 2:
        Script.showHelp()

    dataset_name = argss[0]
    lfn_list = get_dataset_files(dataset_name)

    group_size = int(argss[1])

    t = Transformation()
    tc = TransformationClient()
    trans_name = f"Removing_{dataset_name}"
    t.setTransformationName(trans_name)
    t.setType("Removal")
    t.setDescription("Removing file")
    t.setLongDescription("Removing file")
    t.setGroupSize(group_size)
    t.setPlugin("Standard")
    transBody = "Removal;RemoveFile"
    t.setBody(transBody)

    res = t.addTransformation()
    if not res["OK"]:
        gLogger.error(res["Message"])
        DIRAC.exit(-1)

    transID = t.getTransformationID()
    res = tc.addFilesToTransformation(transID["Value"], lfn_list)
    if not res["OK"]:
        gLogger.error(res["Message"])
        DIRAC.exit(-1)

    t.setAgentType("Automatic")
    t.setStatus("Active")

    DIRAC.exit()


#########################################################
if __name__ == "__main__":
    main()
