#!/usr/bin/env python
"""
Split a dataset into train/test datasets.
Usage:
   cta-prod-split-dataset <datasetName or ascii file with a list of datasets> <percentage of train_en files> <percentage of train_cl files> <percentage of test files>
   cta-prod-split-dataset <datasetName or ascii file with a list of datasets> <percentage of train_cl files> <percentage of test files>
If 3 percentages are given, it splits the dataset into 3 datasets (train_en, train_cl, test).
If 2 percentages are given, it splits the dataset into 2 datasets (train_cl, test).

Example:
  cta-prod-split-dataset Prod5b_LaPalma_AdvancedBaseline_NSB1x_gamma-diffuse_North_20deg_DL0 0.25 0.25 0.5
Produces:
Prod5b_LaPalma_AdvancedBaseline_NSB1x_gamma-diffuse_North_20deg_DL0_train_en
Prod5b_LaPalma_AdvancedBaseline_NSB1x_gamma-diffuse_North_20deg_DL0_train_cl
Prod5b_LaPalma_AdvancedBaseline_NSB1x_gamma-diffuse_North_20deg_DL0_test

  cta-prod-split-dataset Prod5b_LaPalma_AdvancedBaseline_NSB1x_proton_North_20deg_DL0 0.25 0.75
Produces:
Prod5b_LaPalma_AdvancedBaseline_NSB1x_proton_North_20deg_DL0_train_cl
Prod5b_LaPalma_AdvancedBaseline_NSB1x_proton_North_20deg_DL0_test
"""

__RCSID__ = "$Id$"


import os

import DIRAC
from DIRAC.Core.Base.Script import Script
from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient


def set_split_meta_data(lfn_list, meta_value, timeout):
    pathMetaDict = {}
    metadata = {"split": meta_value}
    for lfn in lfn_list:
        pathMetaDict[lfn] = metadata
    fc = FileCatalogClient()
    result = fc.setMetadataBulk(pathMetaDict, timeout=timeout)
    if not result["OK"]:
        gLogger.error(result["Message"])
        DIRAC.exit(-1)
    return


def get_dataset_meta_query(dataset_name):
    fc = FileCatalogClient()
    res = fc.getDatasets(dataset_name)
    if not res["OK"]:
        gLogger.error("Failed to get datasets")
        DIRAC.exit(-1)
    dataset_dict = res["Value"]
    res = dataset_dict["Successful"][dataset_name][dataset_name]
    meta_query = res["MetaQuery"]
    return meta_query


def add_split_dataset(dataset_name, dataset_meta_query, split_value):
    fc = FileCatalogClient()
    dataset_meta_query["split"] = split_value
    dataset_split = f"{dataset_name}_{split_value}"
    datasetPath = os.path.join("/vo.cta.in2p3.fr/datasets/", dataset_split)
    res = fc.addDataset({datasetPath: dataset_meta_query})
    if not res["OK"]:
        gLogger.error(f"Failed to add dataset {dataset_split}: {res['Message']}")
        DIRAC.exit(-1)

    if dataset_split in res["Value"]["Failed"]:
        gLogger.error(
            "Failed to add dataset %s: %s"
            % (dataset_split, res["Value"]["Failed"][dataset_split])
        )
        DIRAC.exit(-1)
    return res


@Script()
def main():
    Script.registerSwitch("", "timeout=", "    timeout")
    Script.registerSwitch("", "min=", "    min of the full list")
    Script.registerSwitch("", "max=", "    max of the full list")
    switches, argss = Script.parseCommandLine(ignoreErrors=True)

    timeout = 600
    min = None
    max = None
    for switch in switches:
        if switch[0] == "timeout":
            timeout = int(switch[1])
        if switch[0] == "min":
            min = int(switch[1])
        if switch[0] == "max":
            max = int(switch[1])

    if len(argss) not in [3, 4]:
        Script.showHelp()

    dataset = argss[0]
    if len(argss) == 4:
        split_en = float(argss[1])
        split_cl = float(argss[2])
        split_test = float(argss[3])
        if split_en + split_cl + split_test != 1:
            gLogger.error("The sum of percentages must be equal to 1")
            DIRAC.exit(-1)
    elif len(argss) == 3:
        split_cl = float(argss[1])
        split_test = float(argss[2])
        if split_cl + split_test != 1:
            gLogger.error("The sum of percentages must be equal to 1")
            DIRAC.exit(-1)

    fc = FileCatalogClient()
    result = fc.getDatasetFiles(dataset)
    if not result["OK"]:
        gLogger.error("Failed to get files for dataset:", result["Message"])
        DIRAC.exit(-1)
    else:
        lfn_list = result["Value"]["Successful"][dataset]

    max_run = len(lfn_list)
    dataset_mq = get_dataset_meta_query(dataset)

    if len(argss) == 4:
        train_en_max_run = int(max_run * split_en)
        train_cl_max_run = int(max_run * split_cl)
        train_en_list = lfn_list[0:train_en_max_run]
        train_cl_list = lfn_list[
            train_en_max_run : (train_en_max_run + train_cl_max_run)
        ]
        test_list = lfn_list[(train_en_max_run + train_cl_max_run) :]

        if min is not None and max is not None:
            if min < train_en_max_run:
                set_split_meta_data(train_en_list[min:max], "train_en", timeout)
            if min < len(train_cl_list):
                set_split_meta_data(train_cl_list[min:max], "train_cl", timeout)
            if min < len(test_list):
                set_split_meta_data(test_list[min:max], "test", timeout)
        else:
            set_split_meta_data(train_en_list, "train_en", timeout)
            set_split_meta_data(train_cl_list, "train_cl", timeout)
            set_split_meta_data(test_list, "test", timeout)
        add_split_dataset(dataset, dataset_mq, "train_en")
        add_split_dataset(dataset, dataset_mq, "train_cl")
        add_split_dataset(dataset, dataset_mq, "test")
        gLogger.notice(
            f"Successfully split dataset {dataset} into 3 datasets : \n"
            f"{dataset}_train_en \n{dataset}_train_cl \n{dataset}_test"
        )
        DIRAC.exit()

    elif len(argss) == 3:
        train_cl_max_run = int(max_run * split_cl)
        train_cl_list = lfn_list[0:train_cl_max_run]
        test_list = lfn_list[train_cl_max_run:]
        if min is not None and max is not None:
            if min < train_cl_max_run:
                set_split_meta_data(train_cl_list[min:max], "train_cl", timeout)
            if min < len(test_list):
                set_split_meta_data(test_list[min:max], "test", timeout)
        else:
            set_split_meta_data(train_cl_list, "train_cl", timeout)
            set_split_meta_data(test_list, "test", timeout)
        add_split_dataset(dataset, dataset_mq, "train_cl")
        add_split_dataset(dataset, dataset_mq, "test")
        gLogger.notice(
            f"Successfully split dataset {dataset} into 2 datasets : \n{dataset}_train_cl \n{dataset}_test"
        )
        DIRAC.exit()


####################################################
if __name__ == "__main__":
    main()
