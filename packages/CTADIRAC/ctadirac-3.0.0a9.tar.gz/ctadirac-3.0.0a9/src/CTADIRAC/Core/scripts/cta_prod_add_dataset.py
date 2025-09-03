#!/usr/bin/env python
"""
Add a dataset from a query specified in a json file, e.g.:

{"MCCampaign": "PROD5b",
"particle": "proton",
"site": "Paranal"}

The created dataset will get the name of the json file (without the extension)
Use the --dry-run option to display the list of files corresponding to the query in the json file without creating the dataset

Usage:
   cta-prod-add-dataset <json file with dataset query dict>
   cta-prod-add-dataset <json file with dataset query dict> --dry-run
Arguments:
   json file with dataset query dict
   The file should have the .json extension, e.g. my_dataset.json
"""

__RCSID__ = "$Id$"

import json
import ast
import os

import DIRAC
from DIRAC.Core.Base.Script import Script
from DIRAC import gLogger
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient


@Script()
def main():
    fc = FileCatalogClient()
    Script.registerSwitch(
        "", "dry-run", "shows the list of files corresponding to the dataset query"
    )
    switches, argss = Script.parseCommandLine(ignoreErrors=True)

    inputJsonList = []
    dry_run = False
    for switch in switches:
        if switch[0] == "dry-run":
            dry_run = True
    if len(argss) == 1:
        if not argss[0].endswith(".json"):
            gLogger.notice(
                "\nReading list of json files with dataset description from input file: %s\n"
                % argss[0]
            )
            inputJsonList = read_inputs_from_file(argss[0])
        else:
            inputJsonList.append(argss[0])
    else:
        Script.showHelp()

    f = open(argss[0] + ".datasets", "w")
    for inputJson in inputJsonList:
        if not inputJson.endswith(".json"):
            gLogger.error("Dataset description files must have .json extension")
            DIRAC.exit(-1)
        # read the meta data query from json file
        content = open(inputJson).readlines()
        for line in content:
            json_string = json.dumps(ast.literal_eval(line))

        MDdict = json.loads(json_string)

        # ensure the integer values are written in the right format
        for key, value in MDdict.items():
            if isinstance(value, float):
                MDdict[key] = {"=": value}

        datasetName = os.path.basename(inputJson).split(".json")[0]
        if dry_run:
            res = fc.findFilesByMetadata(MDdict, path="/")
            if not res["OK"]:
                gLogger.error("Can not access File Catalog:", res["Message"])
                DIRAC.exit(-1)
            lfnList = sorted(res["Value"])
            if len(lfnList) == 0:
                gLogger.notice("No files found for dataset:", datasetName)
            else:
                datasetLFN = datasetName + ".lfns"
                gLogger.notice("\ndry run:")
                gLogger.notice(f"{len(lfnList)} files found for dataset: {datasetName}")
                gLogger.notice("dumped in:", datasetLFN)
                f0 = open(datasetLFN, "w")
                for lfn in lfnList:
                    f0.write(f"{lfn}\n")
        else:
            datasetPath = os.path.join("/vo.cta.in2p3.fr/datasets/", datasetName)
            res = fc.addDataset({datasetPath: MDdict})

            if not res["OK"]:
                gLogger.error(f"Failed to add dataset {datasetName}: {res['Message']}")
                DIRAC.exit(-1)

            if datasetName in res["Value"]["Failed"]:
                gLogger.error(
                    "Failed to add dataset %s: %s"
                    % (datasetName, res["Value"]["Failed"][datasetName])
                )
                DIRAC.exit(-1)

            gLogger.notice("Successfully added dataset:", datasetName)
        f.write(datasetName + "\n")

    gLogger.notice("Datasets list dumped in ", argss[0] + ".datasets")
    DIRAC.exit()


####################################################
if __name__ == "__main__":
    main()
