#!/usr/bin/env python
"""
Check problematic files

To be tested for merged step 1

Usage:
   cta-prod-check-problematic <trans_id> <output data level>
   <output data level> must be : DL1, DL2, merged
"""

__RCSID__ = "$Id$"

import os
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from DIRAC.TransformationSystem.Client import TransformationFilesStatus
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient


def main():
    Script.parseCommandLine(ignoreErrors=True)
    argss = Script.getPositionalArgs()
    fcc = FileCatalogClient()

    trans_client = TransformationClient()
    lfn_list = []
    if len(argss) == 2:
        trans_id = argss[0]
        if argss[1] in ["DL1", "DL2", "merged"]:
            out_data_level = argss[1]
        else:
            DIRAC.gLogger.error(f"Second argument must be in : DL1, DL2, merged")
    else:
        Script.showHelp()



    cond_dict = {"TransformationID": trans_id, "Status" : "Problematic"}

    res = trans_client.getTransformationFiles(cond_dict)
    for lfn_dict in res["Value"]:
        lfn_list.append(lfn_dict["LFN"])

    lfn_0 = lfn_list[0]
    if out_data_level == "DL1":
        out_path = os.path.dirname(lfn_0).split("sim_telarray")[0]
    elif out_data_level == "DL2":
        out_path = os.path.dirname(lfn_0).split("ctapipe-process")[0]
    elif out_data_level == "merged":
        out_path = os.path.dirname(lfn_0).split("ctapipe-process")[0]
    if out_data_level in ["DL1", "DL2"]:
        out_path = os.path.join(out_path, "ctapipe-process", trans_id)
    elif out_data_level == "merged":
        out_path = os.path.join(out_path, "ctapipe-merge", trans_id)

    DIRAC.gLogger.notice(f"Output path : {out_path}")
    DIRAC.gLogger.notice(f"First input file : {lfn_0}")
    res = fcc.getFileUserMetadata(lfn_0)
    if not res["OK"]:
        DIRAC.gLogger.warn(f"Failed to get user metadata for {lfn_0}")
        DIRAC.exit(1)

    nsb_value = res["Value"]["nsb"]
    metadata_dict = {"nsb" : int(nsb_value)}
    if "split" in res["Value"]:
        split_value = res["Value"]["split"]
        metadata_dict.update({"split": split_value})

    if out_data_level == "merged":
        in_file_name = os.path.basename(lfn_0)
        data_dir = os.path.dirname(lfn_0).split("/")[-2:]
        data_path = os.path.join(data_dir[0], data_dir[1])
        out_file_name = in_file_name.replace("DL2.h5","merged.DL2.h5")
        out_lfn = os.path.join(out_path, data_path, out_file_name)
        res = fcc.exists(out_lfn)
        if res["Value"]["Successful"][out_lfn]:
            DIRAC.gLogger.notice(f"{out_lfn} found. Set metadata")
            res = fcc.setMetadata(out_lfn, metadata_dict)
            if not res["OK"]:
                DIRAC.gLogger.warn(f"Failed to set metadata")
            for lfn in lfn_list:
                res = trans_client.setFileStatusForTransformation(
                    trans_id, TransformationFilesStatus.PROCESSED, lfn
                )
                if not res["OK"]:
                    DIRAC.gLogger.warn(f"Failed to set file status to PROCESSED {lfn}")
        else:
            DIRAC.gLogger.notice(f"{out_lfn} not found")
    else:
        for lfn in lfn_list:
            in_file_name = os.path.basename(lfn)
            data_dir = os.path.dirname(lfn).split("/")[-2:]
            data_path = os.path.join(data_dir[0], data_dir[1])
            if out_data_level == "DL1":
                out_file_name = in_file_name.replace("simtel.zst","DL1.h5")
            elif out_data_level == "DL2":
                out_file_name = in_file_name.replace("DL1.h5","DL2.h5")
            out_lfn = os.path.join(out_path, data_path, out_file_name)
            res = fcc.exists(out_lfn)
            if res["Value"]["Successful"][out_lfn]:
                DIRAC.gLogger.notice(f"{out_lfn} found, set metadata")
                res = fcc.setMetadata(out_lfn, metadata_dict)
                if not res["OK"]:
                    DIRAC.gLogger.warn(f"Failed to set metadata")
                res = trans_client.setFileStatusForTransformation(
                    trans_id, TransformationFilesStatus.PROCESSED, lfn
                )
                if not res["OK"]:
                    DIRAC.gLogger.warn(f"Failed to set file status to PROCESSED {lfn}")
            else:
                DIRAC.gLogger.notice(f"{out_lfn} not found")

    DIRAC.exit()


####################################################
if __name__ == "__main__":
    main()
