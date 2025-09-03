#!/usr/bin/env python
"""
Create yml configuration files to submit R1->DL1 processing with EventDisplay

dl0_to_dl1_dark.yml
dl0_to_dl1_moon.yml

Then use:
cta-prod-submit <prodName> dl0_to_dl1_dark.yml
....

Usage example:
   cta-prod-create-workflow-evndisp-config <workflow_template.yml>

Example of workflow_template:

MCCampaign: PROD6
site: LaPalma
input_array_layout: Hyperarray
zenith: 60.0
analysis_prog_version: v5.13.2
compiler: gcc114_default
configuration_id: 16
pointing: North
"""

__RCSID__ = "$Id$"

from ruamel.yaml import YAML


from DIRAC.Core.Base.Script import Script

Script.parseCommandLine()

import DIRAC

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

arguments = Script.getPositionalArgs()
if len(arguments) != 1:
    Script.showHelp()

workflow_config_file = arguments[0]

with open(workflow_config_file) as stream:
    workflow_config = yaml.load(stream)

mandatory_keys = [
    "MCCampaign",
    "site",
    "input_array_layout",
    "zenith",
    "analysis_prog_version",
    "analysis_prog_compiler",
    "pointing",
]

for key in mandatory_keys:
    if key not in workflow_config:
        DIRAC.gLogger.notice(f"Missing mandatory key {key}")
        DIRAC.exit(-1)

MCCampaign = workflow_config["MCCampaign"]
site = workflow_config["site"]

if site not in ["LaPalma", "Paranal"]:
    DIRAC.gLogger.notice(f"Invalid value {site} for site")
    DIRAC.exit(-1)

input_array_layout = workflow_config["input_array_layout"]

pointing = workflow_config["pointing"]
if pointing not in ["North", "South"]:
    DIRAC.gLogger.notice(f"Invalid value {pointing} for pointing")
    DIRAC.exit(-1)

thetaP = workflow_config["zenith"]
zenith_str = str(int(thetaP)) + "deg"

version = workflow_config["analysis_prog_version"]
compiler = workflow_config["analysis_prog_compiler"]
configuration_id = workflow_config["configuration_id"]

common_dict = {}
common_dict["MCCampaign"] = MCCampaign
common_dict["configuration_id"] = configuration_id
common_dict["base_path"] = "/vo.cta.in2p3.fr/MC"


def create_dl0_dl1_config(moon):
    prod_dict = {}
    prod_step_list = []

    if moon == "dark":
        nsb = "NSB1x"
    elif moon == "half":
        nsb = "NSB5x"
    elif moon == "full":
        nsb = "NSB19x"

    id = 0
    for particle in [
        "gamma",
        "electron",
        "gamma-diffuse",
        "proton",
    ]:
        dataset = (
            MCCampaign.capitalize()
            + "_"
            + site
            + "_"
            + input_array_layout
            + "_"
            + nsb
            + "_"
            + particle
            + "_"
            + pointing
            + "_"
            + zenith_str
            + "_R1"
        )
        id += 1
        prod_step_dict = {}
        prod_step_dict["ID"] = id
        input_meta_query = {}
        input_meta_query["parentID"] = None
        input_meta_query["dataset"] = dataset
        prod_step_dict["input_meta_query"] = input_meta_query
        job_config = {}
        job_config["type"] = "EvndispProcessing"
        job_config["version"] = version
        job_config["compiler"] = compiler
        job_config["group_size"] = 5
        job_config["data_level"] = 1
        job_config["options"] = zenith_str + " " + moon
        job_config["tag"] = "production"
        job_config["catalogs"] = "DIRACFileCatalog"
        prod_step_dict["job_config"] = job_config
        prod_step_list.append(prod_step_dict)

    prod_dict["ProdSteps"] = prod_step_list
    prod_dict["Common"] = common_dict

    file_name = f"dl0_to_dl1_{moon}.yml"
    with open(file_name, "w") as file:
        yaml.dump(prod_dict, file)


@Script()
def main():
    create_dl0_dl1_config("dark")
    create_dl0_dl1_config("half")
    create_dl0_dl1_config("full")


########################################################
if __name__ == "__main__":
    main()
