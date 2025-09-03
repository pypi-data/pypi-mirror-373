#!/usr/bin/env python
"""
Create yml configuration files to submit dl0->dl2 processing workflow with ctapipe

dl0_to_dl2.yml
merge.yml
train_energy.yml
train_classifier.yml
apply_moodels.yml

Then use:
cta-prod-submit <prodName> dl0_to_dl2.yml
cta-prod-submit <prodName> merge.yml
....

Usage example:
   cta-prod-create-workflow-config <workflow_template.yml>

Example of workflow_template:

MCCampaign: PROD6
site: LaPalma
input_array_layout: Prod6-Hyperarray
processing_array_layout: Alpha
zenith: 60.0
analysis_prog_version: v0.23.0
analysis_config_version: v1
configuration_id: 16
moon: dark
pointing: North
"""

__RCSID__ = "$Id$"

from copy import deepcopy
from ruamel.yaml import YAML

import DIRAC
from DIRAC.Core.Base.Script import Script

Script.parseCommandLine()


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
    "processing_array_layout",
    "zenith",
    "analysis_prog_version",
    "analysis_config_version",
    "moon",
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
processing_array_layout = workflow_config["processing_array_layout"]
moon = workflow_config["moon"]
config_version = workflow_config["analysis_config_version"]

if moon == "dark":
    nsb = "NSB1x"
elif moon == "half":
    nsb = "NSB5x"
elif moon == "full":
    nsb = "NSB19x"
else:
    DIRAC.gLogger.notice(f"Invalid value {moon} for moon")
    DIRAC.exit(-1)
pointing = workflow_config["pointing"]
if pointing == "North":
    phiP = 180.0
elif pointing == "South":
    phiP = 0.0
else:
    DIRAC.gLogger.notice(f"Invalid value {pointing} for pointing")
    DIRAC.exit(-1)

thetaP = workflow_config["zenith"]
zenith_str = str(int(thetaP)) + "deg"

version = workflow_config["analysis_prog_version"]
configuration_id = workflow_config["configuration_id"]

common_dict = {}
common_dict["MCCampaign"] = MCCampaign
common_dict["configuration_id"] = configuration_id
common_dict["base_path"] = "/vo.cta.in2p3.fr/MC"


def create_ctapipe_process_config(dl_level):
    prod_dict = {}
    prod_step_list = []

    id = 0
    for particle in [
        "gamma__",
        "electron__",
        "gamma-diffuse__train_en",
        "gamma-diffuse__train_cl",
        "gamma-diffuse__test",
        "proton__train_cl",
        "proton__test",
    ]:
        split = particle.split("__")[1]
        if split:
            dataset = (
                MCCampaign.capitalize()
                + "_"
                + site
                + "_"
                + input_array_layout
                + "_"
                + nsb
                + "_"
                + particle.split("__")[0]
                + "_"
                + pointing
                + "_"
                + zenith_str
                + "_R1_"
                + split
            )
        else:
            dataset = (
                MCCampaign.capitalize()
                + "_"
                + site
                + "_"
                + input_array_layout
                + "_"
                + nsb
                + "_"
                + particle.split("__")[0]
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
        if dl_level == 1:
            input_meta_query["dataset"] = dataset
        else:
            input_meta_query["parentID"] = None
            input_meta_query["MCCampaign"] = MCCampaign
            input_meta_query["array_layout"] = processing_array_layout
            input_meta_query["site"] = site
            input_meta_query["particle"] = particle.split("_")[0]
            input_meta_query["thetaP"] = thetaP
            input_meta_query["phiP"] = phiP
            input_meta_query["analysis_prog"] = "ctapipe-process"
            input_meta_query["analysis_prog_version"] = version
            input_meta_query["data_level"] = 1
            input_meta_query["outputType"] = "Data"
            input_meta_query["configuration_id"] = configuration_id
            input_meta_query["moon"] = moon
            if split:
                input_meta_query["split"] = split
            else:
                input_meta_query["split"] = "test"
        prod_step_dict["input_meta_query"] = input_meta_query
        job_config = {}
        job_config["type"] = "CtapipeProcessing"
        job_config["version"] = version
        job_config["array_layout"] = processing_array_layout
        job_config["group_size"] = 5
        job_config["output_extension"] = f"DL{dl_level}.h5"
        job_config["data_level"] = dl_level
        if site == "LaPalma":
            subarray_cfg = "subarray_north_" + processing_array_layout.lower() + ".yml"
        elif site == "Paranal":
            subarray_cfg = "subarray_south_" + processing_array_layout.lower() + ".yml"
        if dl_level == 1:
            options = f"-c {config_version}/dl0_to_dl1.yml"
            if not split:
                job_config["split"] = "test"
        else:
            options = f"-c {config_version}/dl1_to_dl2.yml -c {config_version}/{MCCampaign.lower()}/{subarray_cfg}"
        job_config["options"] = options
        prod_step_dict["job_config"] = job_config
        prod_step_list.append(prod_step_dict)

    prod_dict["ProdSteps"] = prod_step_list
    prod_dict["Common"] = common_dict

    if dl_level == 1:
        file_name = "dl0_to_dl1.yml"
    else:
        file_name = "dl1_to_dl2.yml"

    with open(file_name, "w") as file:
        yaml.dump(prod_dict, file)


def create_merge_config():
    prod_dict = {}
    prod_step_list = []

    id = 0
    for particle in [
        "gamma_test",
        "electron_test",
        "gamma-diffuse_train_en",
        "gamma-diffuse_train_cl",
        "gamma-diffuse_test",
        "proton_train_cl",
        "proton_test",
    ]:
        for i in range(0, 3):
            id += 1
            prod_step_dict = {}
            prod_step_dict["ID"] = id
            input_meta_query = {}

            job_config = {}
            job_config["type"] = "Merging"
            job_config["version"] = version

            if id in [3, 6, 9, 12, 15, 18, 21]:
                job_config["group_size"] = 10000
            else:
                job_config["group_size"] = 25

            if id in [2, 5, 8, 11, 14, 17, 20]:
                input_meta_query["parentID"] = id - 1
                job_config["output_extension"] = "01_merged.DL2.h5"
            elif id in [3, 6, 9, 12, 15, 18, 21]:
                input_meta_query["parentID"] = id - 1
                if particle in [
                    "gamma_test",
                    "electron_test",
                    "gamma-diffuse_test",
                    "proton_test",
                ]:
                    job_config["output_extension"] = (
                        processing_array_layout.lower() + "_" + "test_merged.DL2.h5"
                    )
                elif particle in [
                    "gamma-diffuse_train_en",
                    "gamma-diffuse_train_cl",
                    "proton_train_cl",
                ]:
                    job_config["output_extension"] = (
                        processing_array_layout.lower()
                        + "_train_"
                        + particle.split("_")[2]
                        + "_merged.DL2.h5"
                    )
            else:
                job_config["output_extension"] = "merged.DL2.h5"
                input_meta_query["parentID"] = None
                input_meta_query["MCCampaign"] = MCCampaign
                input_meta_query["array_layout"] = processing_array_layout
                input_meta_query["site"] = site
                input_meta_query["particle"] = particle.split("_")[0]
                input_meta_query["thetaP"] = thetaP
                input_meta_query["phiP"] = phiP
                input_meta_query["analysis_prog"] = "ctapipe-process"
                input_meta_query["analysis_prog_version"] = version
                input_meta_query["data_level"] = 2
                input_meta_query["outputType"] = "Data"
                input_meta_query["configuration_id"] = configuration_id
                input_meta_query["merged"] = 0
                input_meta_query["moon"] = moon
                for split in ["train_en", "train_cl", "test"]:
                    if split in particle:
                        input_meta_query["split"] = split

            prod_step_dict["input_meta_query"] = input_meta_query
            prod_step_dict["job_config"] = job_config
            prod_step_list.append(deepcopy(prod_step_dict))

    prod_dict["ProdSteps"] = prod_step_list
    prod_dict["Common"] = common_dict

    with open("merge.yml", "w") as file:
        yaml.dump(prod_dict, file)


def create_train_energy_config():
    prod_dict = {}
    prod_step_list = []
    prod_step_dict = {}
    input_meta_query = {}

    prod_step_dict["ID"] = 1
    input_meta_query["parentID"] = None
    input_meta_query["MCCampaign"] = MCCampaign
    input_meta_query["array_layout"] = processing_array_layout
    input_meta_query["site"] = site
    input_meta_query["particle"] = "gamma-diffuse"
    input_meta_query["split"] = "train_en"
    input_meta_query["thetaP"] = thetaP
    input_meta_query["phiP"] = phiP
    input_meta_query["analysis_prog"] = "ctapipe-merge"
    input_meta_query["analysis_prog_version"] = version
    input_meta_query["data_level"] = 2
    input_meta_query["outputType"] = "Data"
    input_meta_query["configuration_id"] = configuration_id
    input_meta_query["merged"] = 3
    input_meta_query["moon"] = moon
    prod_step_dict["input_meta_query"] = input_meta_query
    job_config = {}
    job_config["type"] = "CtapipeTrainEnergy"
    job_config["version"] = version
    job_config["tag"] = "training"
    options = f"-c {config_version}/train_energy_regressor.yml"
    job_config["options"] = options
    prod_step_dict["job_config"] = job_config
    prod_step_list.append(prod_step_dict)

    prod_dict["ProdSteps"] = prod_step_list
    prod_dict["Common"] = common_dict

    with open("train_energy.yml", "w") as file:
        yaml.dump(prod_dict, file)


def create_train_classifier_config():
    prod_dict = {}
    prod_step_list = []

    id = 0
    for particle in ["gamma-diffuse", "proton"]:
        id += 1

        prod_step_dict = {}
        input_meta_query = {}

        prod_step_dict["ID"] = id
        input_meta_query["parentID"] = None
        input_meta_query["MCCampaign"] = MCCampaign
        input_meta_query["array_layout"] = processing_array_layout
        input_meta_query["site"] = site
        input_meta_query["particle"] = particle
        input_meta_query["split"] = "train_cl"
        input_meta_query["thetaP"] = thetaP
        input_meta_query["phiP"] = phiP
        input_meta_query["analysis_prog"] = "ctapipe-merge"
        input_meta_query["analysis_prog_version"] = version
        input_meta_query["data_level"] = 2
        input_meta_query["outputType"] = "Data"
        input_meta_query["configuration_id"] = configuration_id
        input_meta_query["merged"] = 3
        input_meta_query["moon"] = moon
        prod_step_dict["input_meta_query"] = input_meta_query
        job_config = {}
        job_config["type"] = "CtapipeApplyModels"
        job_config["version"] = version
        job_config["options"] = "--reconstructor energy_model.pkl"
        prod_step_dict["job_config"] = job_config
        prod_step_list.append(prod_step_dict)

    id += 1

    prod_step_dict = {}
    input_meta_query = {}

    prod_step_dict["ID"] = id
    input_meta_query["parentID"] = None
    input_meta_query["MCCampaign"] = MCCampaign
    input_meta_query["array_layout"] = processing_array_layout
    input_meta_query["site"] = site
    input_meta_query["split"] = "train_cl"
    input_meta_query["thetaP"] = thetaP
    input_meta_query["phiP"] = phiP
    input_meta_query["analysis_prog"] = "ctapipe-apply-models"
    input_meta_query["analysis_prog_version"] = version
    input_meta_query["data_level"] = 2
    input_meta_query["outputType"] = "Data"
    input_meta_query["configuration_id"] = configuration_id
    input_meta_query["moon"] = moon
    prod_step_dict["input_meta_query"] = input_meta_query
    job_config = {}
    job_config["type"] = "CtapipeTrainClassifier"
    job_config["version"] = version
    options = f"-c {config_version}/train_particle_classifier.yml"
    job_config["options"] = options
    job_config["tag"] = "training"
    job_config["group_size"] = 2
    prod_step_dict["job_config"] = job_config
    prod_step_list.append(prod_step_dict)

    prod_dict["ProdSteps"] = prod_step_list
    prod_dict["Common"] = common_dict

    with open("train_classifier.yml", "w") as file:
        yaml.dump(prod_dict, file)


def create_apply_models_config():
    prod_dict = {}
    prod_step_list = []

    id = 0
    for particle in ["gamma", "electron", "gamma-diffuse", "proton"]:
        id += 1

        prod_step_dict = {}
        input_meta_query = {}

        prod_step_dict["ID"] = id
        input_meta_query["parentID"] = None
        input_meta_query["MCCampaign"] = MCCampaign
        input_meta_query["array_layout"] = processing_array_layout
        input_meta_query["site"] = site
        input_meta_query["particle"] = particle
        input_meta_query["split"] = "test"
        input_meta_query["thetaP"] = thetaP
        input_meta_query["phiP"] = phiP
        input_meta_query["analysis_prog"] = "ctapipe-merge"
        input_meta_query["analysis_prog_version"] = version
        input_meta_query["data_level"] = 2
        input_meta_query["outputType"] = "Data"
        input_meta_query["configuration_id"] = configuration_id
        input_meta_query["merged"] = 3
        input_meta_query["moon"] = moon
        prod_step_dict["input_meta_query"] = input_meta_query
        job_config = {}
        job_config["type"] = "CtapipeApplyModels"
        job_config["version"] = version
        job_config[
            "options"
        ] = "--reconstructor energy_model.pkl --reconstructor classifier_model.pkl"
        prod_step_dict["job_config"] = job_config
        prod_step_list.append(prod_step_dict)

    prod_dict["ProdSteps"] = prod_step_list
    prod_dict["Common"] = common_dict

    with open("apply_models.yml", "w") as file:
        yaml.dump(prod_dict, file)


def main():
    create_ctapipe_process_config(1)
    create_ctapipe_process_config(2)
    create_merge_config()
    create_train_energy_config()
    create_train_classifier_config()
    create_apply_models_config()


########################################################
if __name__ == "__main__":
    main()
