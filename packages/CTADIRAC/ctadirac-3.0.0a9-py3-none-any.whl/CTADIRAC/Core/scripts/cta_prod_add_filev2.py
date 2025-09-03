#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os
from multiprocessing import Pool

# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.Core.Security.ProxyInfo import getProxyInfo
from DIRAC.DataManagementSystem.Client.DataManager import DataManager

from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

Script.setUsageMessage(
    """
Bulk upload of a list of local files or a single file from the current directory to a Storage Element

lfns must contain local file names, i.e.:
lfn = /ctao/<subdirs>/<local_file>

Usage:
   cta-prod-add-file <lfn> <SE>
   cta-prod-add-file <ascii file with a list of lfns> <SE>
"""
)

Script.parseCommandLine(ignoreErrors=True)

args = Script.getPositionalArgs()
if len(args) > 1:
    infile = args[0]
    SE = args[1]
else:
    Script.showHelp()

DIRAC.initialize()

gLogger.setLevel("NOTICE")

res = getProxyInfo()

if not res["OK"]:
    gLogger.error("Error getting proxy info")
    DIRAC.exit(2)

voName = res["Value"]["VOMS"][0].split("/")[1]

@Script()
def main():
    if os.path.isfile(infile):
        infileList = read_inputs_from_file(infile)
    else:
        infileList = [infile]

    p = Pool(10)
    p.map(addfile, infileList)

def addfile(lfn):
    start_path = lfn.split("/")[1]
    if start_path != voName:
        gLogger.error(f"Wrong lfn: path must start with vo name {voName}:\n {lfn}")
        return
    dm = DataManager(vo=voName)
    res = dm.putAndRegister(lfn, os.path.basename(lfn), SE)
    if not res["OK"]:
        message = res["Message"]
        gLogger.error(f"Error uploading file {lfn}:\n{message}")
        return
    gLogger.info(f"Successfully uploaded file {lfn}")

if __name__ == "__main__":
    main()
