# generic imports
import os
import glob
import json

# DIRAC imports
import DIRAC
#from DIRAC.Core.Base.Script import Script

# CTADIRAC imports
from CTADIRAC.Core.Utilities.tool_box import run_number_from_filename
from CTADIRAC.Core.Workflow.Modules.ProdDataManager import ProdDataManager
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

#Script.parseCommandLine()
#argss = Script.getPositionalArgs()

DIRAC.initialize()  # Initialize configuration

def main():

    prod_dm = ProdDataManager()

    out_lfn = "/vo.cta.in2p3.fr/MC/PROD5b/LaPalma/gamma/ctapipe-merge/5883/Data/000xxx/gamma_20deg_0deg_run80___cta-prod5b-lapalma_desert-2158m-LaPalma-dark.merged.DL2.h5"
    in_lfn_list = [
    "/vo.cta.in2p3.fr/MC/PROD5b/LaPalma/gamma/ctapipe-process/5755/Data/000xxx/gamma_20deg_0deg_run912___cta-prod5b-lapalma_desert-2158m-LaPalma-dark.DL2.h5",
    "/vo.cta.in2p3.fr/MC/PROD5b/LaPalma/gamma/ctapipe-process/5755/Data/000xxx/gamma_20deg_0deg_run918___cta-prod5b-lapalma_desert-2158m-LaPalma-dark.DL2.h5"]

    map_lfn = {out_lfn : in_lfn_list}
    DIRAC.gLogger.notice("Mapping output/input")
    for key, value in map_lfn.items():
        DIRAC.gLogger.notice(
        f"{key} mapped to {value}"
        )
        DIRAC.gLogger.notice(f"Setting file status to PROCESSED {value}")
        res = prod_dm.setTransformationFileStatus(value, "PROCESSED")
        if not res["OK"]:
            DIRAC.gLogger.warn(f"Failed to set file status to PROCESSED {value}")
####################################################
if __name__ == "__main__":
    main()