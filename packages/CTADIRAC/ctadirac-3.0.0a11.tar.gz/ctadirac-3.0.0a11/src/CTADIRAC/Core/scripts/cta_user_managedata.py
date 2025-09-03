#!/usr/bin/env python
""" Simple data management script for users
    put and register files in DFC or the specified catalog
"""

__RCSID__ = "$Id$"

# generic imports
import os
import glob
import json

# DIRAC imports
import DIRAC
from DIRAC.Core.Base.Script import Script

Script.parseCommandLine()

# Specific DIRAC imports
from DIRAC.Core.Utilities import List
from CTADIRAC.Core.Workflow.Modules.ProdDataManager import ProdDataManager

####################################################


@Script()
def main():
    """simple wrapper to put and register all analysis files

    Keyword arguments:
    args -- a list of arguments in order []
    """
    args = Script.getPositionalArgs()
    outputpattern = args[0]
    outputpath = args[1]
    SEListArg = json.loads(args[2])
    SEList = []
    for SE in SEListArg:
        SEList.append(str(SE))
    # Load catalogs
    catalogs = args[3]
    catalogs_json = json.loads(catalogs)

    # # Init DataManager
    prod_dm = ProdDataManager(catalogs_json)

    # # Upload data files
    res = prod_dm._checkemptydir(outputpattern)
    if not res["OK"]:
        return res

    for localfile in glob.glob(outputpattern):
        filename = os.path.basename(localfile)
        lfn = os.path.join(outputpath, filename)
        SEList = List.randomize(SEList)
        res = prod_dm._putAndRegisterToSEList(lfn, localfile, SEList)
        # ##  check if failed
        if not res["OK"]:
            return res

    DIRAC.exit()


####################################################
if __name__ == "__main__":
    main()
