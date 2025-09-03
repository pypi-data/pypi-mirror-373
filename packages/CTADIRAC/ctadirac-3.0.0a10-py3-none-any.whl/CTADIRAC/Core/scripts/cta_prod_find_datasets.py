#!/usr/bin/env python
"""
Find datasets related to DL2 processing with ctapipe

Usage example:
   cta-prod-find-datasets --MCCampaign=PROD5b --site=LaPalma --array_layout=Alpha --az=180 --zen=20.0 --ctapipe_ver=v0.19.0 --nsb=1
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    Script.registerSwitch("", "MCCampaign=", "MCCampaign")
    Script.registerSwitch("", "site=", "site")
    Script.registerSwitch("", "array_layout=", "array_layout")
    Script.registerSwitch("", "az=", "azimuth angle")
    Script.registerSwitch("", "zen=", "zenith angle")
    Script.registerSwitch("", "div_ang=", "divergent angle")
    Script.registerSwitch("", "nsb=", "nsb")
    Script.registerSwitch("", "max_merged=", "max_merged")
    Script.registerSwitch("", "ctapipe_ver=", "ctapipe_version")
    switches, argss = Script.parseCommandLine(ignoreErrors=True)

    if not switches:
        Script.showHelp()

    # defaults
    MCCampaign = "PROD5b"
    site = "LaPalma"
    array_layout = "Alpha"
    phiP = 180.0
    thetaP = 20
    div_ang = None
    nsb = 1
    max_merged = 3
    analysis_prog_version = "v0.19.0"

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
        elif switch[0] == "div_ang":
            div_ang = switch[1]
        elif switch[0] == "nsb":
            nsb = int(switch[1])
        elif switch[0] == "max_merged":
            max_merged = int(switch[1])
        elif switch[0] == "ctapipe_ver":
            analysis_prog_version = switch[1]

    file_ext_list = [
        ".DL1ImgParDL2Geo",
        ".DL1ParDL2Geo",
        ".DL2GeoEneGam",
    ]
    file_name_list = []

    for file_ext in file_ext_list:
        if file_ext == ".DL1ImgParDL2Geo":
            analysis_prog = "ctapipe-merge"
            merged = 1
        if file_ext == ".DL1ParDL2Geo":
            analysis_prog = "ctapipe-merge"
            merged = max_merged
        if file_ext == ".DL2GeoEneGam":
            analysis_prog = "ctapipe-apply-models"
            merged = 0

        MDdict_common = {
            "analysis_prog": analysis_prog,
            "data_level": {"=": 2},
            "merged": {"=": merged},
            "sct": "False",
            "outputType": "Data",
        }

        for particle in ["gamma-diffuse", "proton", "gamma", "electron"]:
            MDdict = {
                "MCCampaign": MCCampaign,
                "site": site,
                "array_layout": array_layout,
                "particle": particle,
                "thetaP": {"=": int(thetaP)},
                "phiP": {"=": phiP},
                "nsb": {"=": nsb},
            }

            if div_ang:
                MDdict.update({"div_ang": {"=": div_ang}})

            MDdict.update({"analysis_prog_version": analysis_prog_version})

            if particle == "gamma-diffuse":
                if file_ext == ".DL2GeoEneGam":
                    split_list = ["test"]
                else:
                    split_list = ["train_en", "train_cl", "test"]
            elif particle == "proton":
                if file_ext == ".DL2GeoEneGam":
                    split_list = ["test"]
                else:
                    split_list = ["train_cl", "test"]
            elif particle in ["gamma", "electron"]:
                split_list = ["test"]

            for split in split_list:
                fields = []
                MDdict["split"] = split

                for key, value in MDdict.items():
                    if key == "thetaP":
                        fields.append("zen0" + str(value["="]))
                    elif key == "phiP":
                        if value["="] == 180:
                            az = "000"
                        elif value["="] == 0:
                            az = "180"
                        fields.append("az" + az)
                    elif key == "split":
                        fields.append(str(value) + "_merged")
                    elif key == "nsb":
                        fields.append("nsb0" + str(value["="]) + "x")
                    elif key == "div_ang":
                        fields.append("div" + str(value["="]))
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

                if particle in ["gamma", "electron"]:
                    MDdict.pop("split")

                MDdict.update(MDdict_common)

                if div_ang:
                    file_name = (
                        "_".join(fields[0:4])
                        + "_"
                        + "".join(fields[4:8])
                        + "_"
                        + "_".join(fields[8:10])
                    )
                else:
                    file_name = (
                        "_".join(fields[0:4])
                        + "_"
                        + "".join(fields[4:7])
                        + "_"
                        + fields[7]
                        + "_"
                        + "_".join(fields[8:10])
                    )

                file_list = (
                    "_".join(fields[0:3])
                    + "_"
                    + "".join(fields[4:7])
                    + "_"
                    + fields[7]
                    + "_dataset.list"
                )
                file_name_list.append(file_name.capitalize() + file_ext)

    # Add another dataset for all final DL2 files
    MDdict.pop("particle")
    MDdict["split"] = "test"

    if div_ang:
        file_name = (
            "_".join(fields[0:3])
            + "_"
            + "".join(fields[4:8])
            + "_"
            + "_".join(fields[8:10])
        )
    else:
        file_name = (
            "_".join(fields[0:3])
            + "_"
            + "".join(fields[4:7])
            + "_"
            + fields[7]
            + "_"
            + "_".join(fields[8:10])
        )

    file_name_list.append(file_name.capitalize() + file_ext)

    # Add a dataset with all processing final and intermediate products (Data, Models)
    file_ext = ".Data"
    MDdict.pop("split")
    MDdict.pop("merged")
    MDdict["outputType"] = {"in": ["Data", "Model"]}
    MDdict["analysis_prog"] = {
        "in": [
            "ctapipe-merge",
            "ctapipe-process",
            "ctapipe-apply-models",
            "ctapipe-train-particle-classifier",
            "ctapipe-train-energy-regressor",
        ]
    }

    file_name = "_".join(fields[0:3]) + "_" + "".join(fields[4:7]) + "_" + fields[7]
    file_name_list.append(file_name.capitalize() + file_ext)

    # Add a datasets with Logs for all processing final and intermediate products
    file_ext = ".Log"
    MDdict.pop("nsb")
    MDdict["outputType"] = "Log"
    MDdict["analysis_prog"] = {
        "in": [
            "ctapipe-merge",
            "ctapipe-process",
            "ctapipe-apply-models",
            "ctapipe-train-particle-classifier",
            "ctapipe-train-energy-regressor",
        ]
    }

    file_name = "_".join(fields[0:3]) + "_" + "".join(fields[4:7]) + "_" + fields[7]
    file_name_list.append(file_name.capitalize() + file_ext)

    # Add dataset names to _dataset.list
    f = open(file_list.capitalize(), "w")
    for file_name in file_name_list:
        f.write(file_name + "\n")
    f.close()

    DIRAC.gLogger.notice("list of dataset dumped into:", file_list.capitalize())


####################################################
if __name__ == "__main__":
    main()
