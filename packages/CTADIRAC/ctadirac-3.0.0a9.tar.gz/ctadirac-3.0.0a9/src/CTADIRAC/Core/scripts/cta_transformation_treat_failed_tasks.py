#!/usr/bin/env python

"""
  Expects an input file with a list of lfns with the corresponding transID
  Set transformation files to Processed

  Usage:
    cta-transformation-treat-failed-tasks <ascii file with a list of (transID, lfn)>
"""

__RCSID__ = "$Id$"

# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

Script.parseCommandLine(ignoreErrors=True)


def read_inputs(file_path):
    content = open(file_path).readlines()
    resList = []
    for line in content:
        transID = line.strip().split(" ")[0]
        lfn = line.strip().split(" ")[1]
        if line != "\n":
            resList.append((transID, lfn))
    return resList


@Script()
def main():
    _, argss = Script.parseCommandLine(ignoreErrors=True)
    if len(argss) != 1:
        Script.showHelp()

    infile = argss[0]
    resList = read_inputs(infile)

    # Initialize the transDict with all transID keys
    transDict = {}
    for transID, lfn in resList:
        transDict.update({transID: []})

    # Update the transDict with values
    for transID, lfn in resList:
        transDict[transID].append(lfn)

    tc = TransformationClient()

    for transID in transDict:
        res = tc.setFileStatusForTransformation(
            transID, newLFNsStatus="Unused", lfns=transDict[transID], force=True
        )
        if not res["OK"]:
            gLogger.error(res["Message"])
            DIRAC.exit(-1)


if __name__ == "__main__":
    main()
