#!/usr/bin/env python
"""
Create a transformation to remove files (all replicas)

Usage:
cta-transformation-remove-files <lfn or ascii file with a list of lfns> <group size> <extra_tag>

Arguments:
<lfn or ascii file with a list of lfns>: files to be removed
<group size>: size of the transformation (default=1)
<extra_tag>: extra tag appended to the name of the transformation

Example:
cta-transformation-remove-files lfns.list 100 prod5b_data
"""

__RCSID__ = "$Id$"

import os

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file


@Script()
def main():
    lfn_list = []
    Script.parseCommandLine(ignoreErrors=True)
    argss = Script.getPositionalArgs()
    if len(argss) != 3:
        Script.showHelp()

    if os.path.isfile(argss[0]):
        gLogger.notice("Reading lfns from input file:", argss[0])
        lfn_list = read_inputs_from_file(argss[0])
    else:
        lfn_list.append(argss[0])

    group_size = int(argss[1])
    extra_tag = argss[2]

    t = Transformation()
    tc = TransformationClient()
    trans_name = f"Removing_{extra_tag}"
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
