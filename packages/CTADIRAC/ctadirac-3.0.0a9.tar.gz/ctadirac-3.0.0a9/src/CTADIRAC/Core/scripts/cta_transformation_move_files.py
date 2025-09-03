#!/usr/bin/env python
"""
Move files from a source SE to a target SE

Usage:
cta-transformation-move-files <lfn or ascii file with a list of lfns> <source SE> <target SE> <group size> <extra_tag>

Arguments:
<lfn or ascii file with a list of lfns>: files to be moved
<source SE>: source SE
<target SE>: target SE
<group size>: size of the transformation (default=1)
<extra_tag>: extra tag appended to the name of the transformation

Example:
cta-transformation-move-files lfns.list CEA-Disk GRIF-Disk 100 prod5b_data
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
    if len(argss) != 5:
        Script.showHelp()

    if os.path.isfile(argss[0]):
        gLogger.notice("Reading lfns from input file:", argss[0])
        lfn_list = read_inputs_from_file(argss[0])
    else:
        lfn_list.append(argss[0])

    source_se = argss[1]
    target_se = argss[2]
    group_size = int(argss[3])
    extra_tag = argss[4]

    t = Transformation()
    tc = TransformationClient()
    trans_name = f"Moving_{extra_tag}_from_{source_se}_to_{target_se}"
    t.setTransformationName(trans_name)
    t.setType("Replication")
    t.setSourceSE(source_se)
    t.setTargetSE(target_se)
    t.setDescription("Moving data")
    t.setLongDescription("Moving data")
    t.setGroupSize(group_size)
    tBody = None
    t.setPlugin("Broadcast")
    transBody = (
        {
            "Moving": [
                (
                    "ReplicateAndRegister",
                    {"SourceSE": source_se, "TargetSE": target_se},
                ),
                ("RemoveReplica", {"TargetSE": source_se}),
            ],
            "Replication": "",
        }["Moving"]
        if tBody is None
        else tBody
    )

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
