#!/usr/bin/env python
"""
Compute the group size for the second step of merging to end with 1 output file

Usage:
   cta-prod-compute-merge-size <datasetName or ascii file with a list of datasets> <merge_size>
"""

__RCSID__ = "$Id$"

import os

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file


def get_list_of_datasets(tag=""):
    fc = FileCatalogClient()
    dataset_tag = f"*{tag}*"
    res = fc.getDatasets(dataset_tag)
    if not res["OK"]:
        gLogger.error(res["Message"])
        DIRAC.exit(-1)
    dataset_dict = res["Value"]
    dataset_list = list()
    for dataset_name in dataset_dict["Successful"][dataset_tag]:
        dataset_list.append(dataset_name)
    return dataset_list


def get_dataset_info(dataset_name):
    fc = FileCatalogClient()
    res = fc.getDatasets(dataset_name)
    if not res["OK"]:
        gLogger.error("Failed to get datasets")
        DIRAC.exit(-1)
    dataset_dict = res["Value"]
    res = dataset_dict["Successful"][dataset_name][dataset_name]
    number_of_files = res["NumberOfFiles"]
    meta_query = res["MetaQuery"]
    total_size = res["TotalSize"]
    return (dataset_name, number_of_files, total_size, meta_query)


def main():
    switches, argss = Script.parseCommandLine(ignoreErrors=True)

    if len(argss) != 2:
        Script.showHelp()

    if os.path.isfile(argss[0]):
        gLogger.notice("Reading datasets from input file:", argss[0])
        dataset_list = read_inputs_from_file(argss[0])
    else:
        dataset_name = argss[0]
        dataset_list = list()
        if dataset_name.find("*") > 0:
            dataset_list = get_list_of_datasets(dataset_name)
        else:
            dataset_list.append(dataset_name)

    merge_size = argss[1]

    for dataset_name in dataset_list:
        name, n_files, size, mq = get_dataset_info(dataset_name)
        n_out_files = n_files / int(merge_size)
        if n_files % int(merge_size) != 0:
            n_out_files = int(n_out_files) + 1
        gLogger.notice("\n%s has %d files" % (dataset_name, n_files))
        gLogger.notice(
            "Nb of output files after merge with group_size %s: %d"
            % (merge_size, n_out_files)
        )

    DIRAC.exit()


if __name__ == "__main__":
    main()
