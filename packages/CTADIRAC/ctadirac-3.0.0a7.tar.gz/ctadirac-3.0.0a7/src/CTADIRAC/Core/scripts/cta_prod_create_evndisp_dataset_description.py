#!/usr/bin/env python
"""
Create datasets descriptions (in json format) for R1->DL1 processing with EventDisplay
The produced json files can be used as inputs to cta-prod-add-dataset

Usage example:
   cta-prod-create-evndisp-dataset-description --MCCampaign=PROD6 --site=LaPalma --array_layout=Prod6-Hyperarray --az=180 --zen=20.0 --evndisp_ver=v5.13.2 --nsb=1
"""

__RCSID__ = "$Id$"

import json

import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    Script.registerSwitch("", "MCCampaign=", "MCCampaign")
    Script.registerSwitch("", "site=", "site")
    Script.registerSwitch("", "array_layout=", "array_layout")
    Script.registerSwitch("", "az=", "azimuth angle")
    Script.registerSwitch("", "zen=", "zenith angle")
    Script.registerSwitch("", "nsb=", "nsb")
    Script.registerSwitch("", "evndisp_ver=", "evndisp version")
    switches, argss = Script.parseCommandLine(ignoreErrors=True)

    if not switches:
        Script.showHelp()

    # defaults
    MCCampaign = "PROD6"
    site = "LaPalma"
    array_layout = "Prod6-Hyperarray"
    phiP = 180.0
    thetaP = 20
    nsb = 1
    analysis_prog_version = "v5.13.2"

    for switch in switches:
        if switch[0] == "MCCampaign":
            MCCampaign = switch[1]
        elif switch[0] == "site":
            site = switch[1]
        elif switch[0] == "array_layout":
            array_layout = switch[1]
        elif switch[0] == "az":
            if switch[1] == "0":
                phiP = 180.0
            elif switch[1] == "180":
                phiP = 0.0
            else:
                DIRAC.gLogger.error("az allowed values are: 0, 180")
        elif switch[0] == "zen":
            thetaP = float(switch[1])
        elif switch[0] == "nsb":
            nsb = int(switch[1])
        elif switch[0] == "evndisp_ver":
            analysis_prog_version = switch[1]

    MDdict = {
        "MCCampaign": MCCampaign,
        "site": site,
        "array_layout": array_layout,
        "thetaP": {"=": int(thetaP)},
        "phiP": {"=": phiP},
        "nsb": {"=": nsb},
        "analysis_prog": "evndisp",
        "analysis_prog_version": analysis_prog_version,
        "data_level": {"=": 1},
        "sct": "False",
        "outputType": "Data",
    }

    file_name_list = []

    for particle in ["gamma-diffuse", "proton", "gamma", "electron"]:
        MDdict.update({"particle": particle})

        fields = []

        for key, value in MDdict.items():
            if key == "thetaP":
                fields.append("zen0" + str(value["="]))
            elif key == "phiP":
                if value["="] == 180:
                    az = "000"
                elif value["="] == 0:
                    az = "180"
                fields.append("az" + az)
            elif key == "nsb":
                fields.append("nsb0" + str(value["="]) + "x")
            elif key == "site":
                fields.append(value.lower())
            elif key in [
                "MCCampaign",
                "array_layout",
                "particle",
                "site",
                "analysis_prog_version",
            ]:
                fields.append(value.lower())

        json_string = json.dumps(MDdict)

        file_name = (
            "_".join(fields[0:3])
            + "_"
            + fields[7]
            + "_"
            + "".join(fields[3:6])
            + "_"
            + fields[6]
            + "_evndisp_DL1.json"
        )

        file_list = (
            "_".join(fields[0:3]) + "_" + "_".join(fields[3:6]) + "_dataset.list"
        )
        file_name_list.append(file_name.capitalize())
        # Write a json file with dataset query
        f = open(file_name.capitalize(), "w")
        f.write(json_string.replace('"', "'") + "\n")
        f.close()

    # Add dataset names to _dataset.list
    f = open(file_list.capitalize(), "w")
    for file_name in file_name_list:
        f.write(file_name + "\n")
    f.close()

    DIRAC.gLogger.notice(
        "list of dataset descriptions dumped into:", file_list.capitalize()
    )


####################################################
if __name__ == "__main__":
    main()
