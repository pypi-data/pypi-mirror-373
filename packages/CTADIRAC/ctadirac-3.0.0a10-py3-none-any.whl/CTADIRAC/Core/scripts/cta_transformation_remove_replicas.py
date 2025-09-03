#!/usr/bin/env python
"""
Remove replicas from a SE

Usage:
cta-transformation-remove-replicas <lfn or ascii file with a list of lfns> <SE> <group size> <extra_tag>

Arguments:
<lfn or ascii file with a list of lfns>: files to be moved
<SE>: SE
<group size>: size of the transformation (default=1)
<extra_tag>: extra tag appended to the name of the transformation

Example:
cta-transformation-remove-replica lfns.list CEA-Disk 100 prod5b_data
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
    if len(argss) != 4:
        Script.showHelp()

    if os.path.isfile(argss[0]):
        gLogger.notice("Reading lfns from input file:", argss[0])
        lfn_list = read_inputs_from_file(argss[0])
    else:
        lfn_list.append(argss[0])

    target_se = argss[1]
    group_size = int(argss[2])
    extra_tag = argss[3]

    t = Transformation()
    tc = TransformationClient()
    trans_name = f"Removing_{extra_tag}_from_{target_se}"
    t.setTransformationName(trans_name)
    t.setType("Removal")
    t.setTargetSE(target_se)
    t.setDescription("Removing replica")
    t.setLongDescription("Removing replica")
    t.setGroupSize(group_size)
    t.setPlugin("Broadcast")
    transBody = "Removal;RemoveReplica"
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
