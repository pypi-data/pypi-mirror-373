#!/usr/bin/env python
""" Set meta data in bulk for a list of files.
Usage:
   cta-prod-set-metadata <ascii file with lfn list> <metadata name> <metadata value>
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient


@Script()
def main():
    Script.parseCommandLine()
    argss = Script.getPositionalArgs()

    if len(argss) == 3:
        infile = argss[0]
        meta_key = argss[1]
        meta_value = argss[2]
    else:
        Script.showHelp()

    lfns = read_inputs_from_file(infile)
    metadata = {meta_key: meta_value}
    pathMetaDict = {}

    for lfn in lfns:
        pathMetaDict[lfn] = metadata

    fc = FileCatalogClient()
    result = fc.setMetadataBulk(pathMetaDict)

    if not result["OK"]:
        gLogger.error(result["Message"])
        DIRAC.exit(-1)
    else:
        DIRAC.gLogger.notice(
            f"Successfully set meta data {meta_key} for {len(lfns)} files"
        )
        DIRAC.exit(0)


####################################################
if __name__ == "__main__":
    main()
