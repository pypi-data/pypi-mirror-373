#!/usr/bin/env python
"""
Show the progress of DataProcessing transformations

Usage:
   cta-transformation-show-progress <transID or ascii file with a list of transID comma separated>

Example:
   cta-transformation-show-progress 2010
"""

__RCSID__ = "$Id$"

import os

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient


def get_transformation_info(transID):
    transClient = TransformationClient()

    paramShowNames = [
        "TransformationID",
        "TransformationName",
        "Type",
        "Status",
        "Files_Total",
        "Files_PercentProcessed",
        "Files_Processed",
        "Files_Unused",
        "Jobs_TotalCreated",
        "Jobs_Waiting",
        "Jobs_Running",
        "Jobs_Done",
        "Jobs_Failed",
        "Jobs_Stalled",
    ]

    res = transClient.getTransformationSummaryWeb(
        {"TransformationID": transID}, [], 0, 1
    )

    if not res["OK"]:
        DIRAC.gLogger.error(res["Message"])
        DIRAC.exit(-1)

    if res["Value"]["TotalRecords"] > 0:
        paramNames = res["Value"]["ParameterNames"]
        for paramValues in res["Value"]["Records"]:
            paramShowValues = map(
                lambda pname: paramValues[paramNames.index(pname)], paramShowNames
            )
            showDict = dict(zip(paramShowNames, paramShowValues))
            files_PercentProcessed = showDict["Files_PercentProcessed"]
            transName = showDict["TransformationName"]

    return (transName, files_PercentProcessed)


#########################################################
@Script()
def main():
    Script.parseCommandLine()
    args = Script.getPositionalArgs()
    if len(args) != 1:
        Script.showHelp()

    # get arguments
    transIDs = []
    for arg in args[0].split(","):
        if os.path.exists(arg):
            lines = open(arg).readlines()
            for line in lines:
                for transID in line.split(","):
                    transIDs += [int(transID.strip())]
        else:
            transIDs.append(int(arg))

    values = []

    for transID in transIDs:
        transName, files_PercentProcessed = get_transformation_info(transID)
        values.append((transName, files_PercentProcessed))

    # print table
    gLogger.notice("\n|_. Transformation Name |_. Files Processed (%)| ")
    for value in values:
        gLogger.notice(f"|{'|'.join(map(str, value))}|")

    DIRAC.exit()


if __name__ == "__main__":
    main()
