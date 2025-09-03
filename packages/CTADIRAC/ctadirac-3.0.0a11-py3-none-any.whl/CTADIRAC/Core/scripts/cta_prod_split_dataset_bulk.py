#!/usr/bin/env python
"""
Wrapper of the cta-prod-split-dataset command to set metadata by chuncks of 1000
It avoids timeouts for large datasets

Usage:
   cta-prod-split-dataset-bulk <datasetName or ascii file with a list of datasets> <percentage of train_en files> <percentage of train_cl files> <percentage of test files>
   cta-prod-split-dataset-bulk <datasetName or ascii file with a list of datasets> <percentage of train_cl files> <percentage of test files>
If 3 percentages are given, it splits the dataset into 3 datasets (train_en, train_cl, test).
If 2 percentages are given, it splits the dataset into 2 datasets (train_cl, test).

Example:
  cta-prod-split-dataset-bulk Prod5b_LaPalma_AdvancedBaseline_NSB1x_gamma-diffuse_North_20deg_DL0 0.25 0.25 0.5
Produces:
Prod5b_LaPalma_AdvancedBaseline_NSB1x_gamma-diffuse_North_20deg_DL0_train_en
Prod5b_LaPalma_AdvancedBaseline_NSB1x_gamma-diffuse_North_20deg_DL0_train_cl
Prod5b_LaPalma_AdvancedBaseline_NSB1x_gamma-diffuse_North_20deg_DL0_test

  cta-prod-split-dataset-bulk Prod5b_LaPalma_AdvancedBaseline_NSB1x_proton_North_20deg_DL0 0.25 0.75
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


@Script()
def main():
    switches, argss = Script.parseCommandLine(ignoreErrors=True)
    if len(argss) not in [3, 4]:
        Script.showHelp()
    dataset = argss[0]
    fc = FileCatalogClient()
    result = fc.getDatasetFiles(dataset)
    if not result["OK"]:
        gLogger.error("Failed to get files for dataset:", result["Message"])
        DIRAC.exit(-1)
    else:
        lfn_list = result["Value"]["Successful"][dataset]

    max_run = len(lfn_list)
    a = divmod(max_run, 1000)[0]
    if max_run > 1000:
        for i in range(0, a):
            min = i * 1000
            max = i * 1000 + 1000
            cmd = "cta-prod-split-dataset {} --min={} --max={}".format(
                " ".join(argss),
                str(min),
                str(max),
            )
            print(cmd)
            os.system(cmd)
    min = str(a * 1000)
    max = str(max_run)
    cmd = f"cta-prod-split-dataset {' '.join(argss)} --min={str(min)} --max={str(max)}"
    gLogger.notice(cmd)
    os.system(cmd)
    DIRAC.exit()


####################################################
if __name__ == "__main__":
    main()
