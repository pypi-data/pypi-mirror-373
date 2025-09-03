#!/usr/bin/env python
""" Data management script for production
    create DFC MetaData structure put and register files in DFC
    should work for corsika, simtel and EventDisplay output
"""

__RCSID__ = "$Id$"

# generic imports
import os
import glob
import json

# DIRAC imports
import DIRAC
from DIRAC.Core.Base.Script import Script

# CTADIRAC imports
from CTADIRAC.Core.Utilities.tool_box import run_number_from_filename
from CTADIRAC.Core.Workflow.Modules.ProdDataManager import ProdDataManager
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

Script.parseCommandLine()
DIRAC.initialize()  # Initialize configuration


def main():
    """simple wrapper to put and register all production files

    Keyword arguments:
    args -- a list of arguments in order []
    """
    args = Script.getPositionalArgs()
    metadata = args[0]
    file_metadata = args[1]
    base_path = args[2]
    output_pattern = args[3]
    package = args[4]
    program_category = args[5]
    catalogs = args[6]
    output_type = args[7]
    if len(args) == 9:
        update_ts = True
    else:
        update_ts = False

    exit_status = 0

    # Load catalogs
    catalogs_json = json.loads(catalogs)

    # Init ProdDataManager
    prod_dm = ProdDataManager(catalogs_json)

    # If wms execution don't update TS file status
    if prod_dm.TransformationID == "0000":
        update_ts = False

    # Define list for update TS File Status
    out_lfn_to_reassign_list = []
    to_reassign_lfn_list = []
    problematic_lfn_list = []
    in_lfn_list = prod_dm.InputData

    if not isinstance(in_lfn_list, list):
        in_lfn_list = in_lfn_list.split("LFN:")

    # Get the output directory
    result = prod_dm.getTransformationPath(metadata, base_path, program_category)
    if result["OK"]:
        path = result["Value"]

    # Check the content of the output directory
    res = prod_dm._checkemptydir(output_pattern)
    if not res["OK"]:
        DIRAC.gLogger.warn(res["Message"])
        to_reassign_lfn_list = in_lfn_list.copy()

    # Dump the list of output LFNs
    file = open("output_lfns.txt", "w")

    # Loop over each file and upload and register
    for localfile in glob.glob(output_pattern):
        file_name = os.path.basename(localfile)
        # Check run number, assign one as file metadata if needed
        fmd_dict = json.loads(file_metadata)
        try:
            run_number = run_number_from_filename(file_name, package)
        except BaseException:
            run_number = -9999
            DIRAC.gLogger.notice("Could not get a correct run number, assigning -9999")
        fmd_dict["runNumber"] = "%08d" % int(run_number)
        # get the output file path
        run_path = prod_dm._getRunPath(fmd_dict)
        lfn = os.path.join(path, output_type, run_path, file_name)
        fmd_json = json.dumps(fmd_dict)
        result = prod_dm.putAndRegister(lfn, localfile, fmd_json, package)
        if not result["OK"]:
            if "merged" in lfn or "model" in lfn:
                problematic_lfn_list = in_lfn_list.copy()
                exit_status = 1
            else:
                out_lfn_to_reassign_list.append(lfn)
                exit_status = 1
        else:
            file.write(lfn)
            file.write("\n")
    file.close()

    ### Add here the update of TS Status
    if update_ts:
        map_lfn = {}
        map_to_reassign_lfn = {}
        out_lfn_list = read_inputs_from_file("output_lfns.txt")
        problematic_file_list = []
        if os.path.exists("problematic_files.txt"):
            problematic_file_list = read_inputs_from_file("problematic_files.txt")
        # problematic_lfn_list = []

        for in_lfn in in_lfn_list:
            in_file_name = os.path.basename(in_lfn)
            if in_file_name in problematic_file_list:
                problematic_lfn_list.append(in_lfn)

        for out_lfn in out_lfn_list:
            if "merged" in out_lfn or "model" in out_lfn:
                map_lfn[out_lfn] = in_lfn_list
            else:
                out_file_name = os.path.basename(out_lfn)
                out_run_number = run_number_from_filename(out_file_name, package)
                # Temporary fix to take into account different format for simtelarray file names
                out_run_number_0d = "run%d" % int(out_run_number)
                out_run_number_6d = "run%06d" % int(out_run_number)
                for in_lfn in in_lfn_list:
                    in_file_name = os.path.basename(in_lfn)
                    # Temporary fix to take into account different format for simtelarray file names
                    if (
                        out_run_number_0d in in_file_name
                        or out_run_number_6d in in_file_name
                    ):
                        map_lfn[out_lfn] = in_lfn

        for out_lfn in out_lfn_to_reassign_list:
            out_file_name = os.path.basename(out_lfn)
            out_run_number = run_number_from_filename(out_file_name, package)
            # Temporary fix to take into account different format for simtelarray file names
            out_run_number_0d = "run%d" % int(out_run_number)
            out_run_number_6d = "run%06d" % int(out_run_number)
            for in_lfn in in_lfn_list:
                in_file_name = os.path.basename(in_lfn)
                # Temporary fix to take into account different format for simtelarray file names
                if (
                    out_run_number_0d in in_file_name
                    or out_run_number_6d in in_file_name
                ):
                    map_to_reassign_lfn[out_lfn] = in_lfn

        DIRAC.gLogger.notice("Mapping output/input")
        for key, value in map_lfn.items():
            DIRAC.gLogger.notice(f"{key} mapped to {value}")
            DIRAC.gLogger.notice(f"Setting file status to PROCESSED {value}")
            res = prod_dm.setTransformationFileStatus(value, "PROCESSED")
            if not res["OK"]:
                DIRAC.gLogger.warn(f"Failed to set file status to PROCESSED {value}")

        for lfn in problematic_lfn_list:
            DIRAC.gLogger.notice(f"Setting file status to PROBLEMATIC {lfn}")
            res = prod_dm.setTransformationFileStatus(lfn, "PROBLEMATIC")
            if not res["OK"]:
                DIRAC.gLogger.warn(f"Failed to set file status to PROBLEMATIC {lfn}")

        DIRAC.gLogger.notice("Mapping lfns to reassign")
        for key, value in map_to_reassign_lfn.items():
            DIRAC.gLogger.notice(
                f"{os.path.basename(key)} mapped to {os.path.basename(value)}"
            )
            DIRAC.gLogger.notice(f"List of problematic lfns {problematic_lfn_list}")
            if value not in problematic_lfn_list:
                # Temporary test : set to PROBLEMATIC instead of UNUSED
                DIRAC.gLogger.notice(f"Setting file status to PROBLEMATIC {value}")
                res = prod_dm.setTransformationFileStatus(value, "PROBLEMATIC")
                if not res["OK"]:
                    DIRAC.gLogger.warn(
                        f"Failed to set file status to PROBLEMATIC {value}"
                    )

        for lfn in to_reassign_lfn_list:
            if lfn not in problematic_lfn_list:
                DIRAC.gLogger.notice(f"Setting file status to UNUSED {lfn}")
                res = prod_dm.setTransformationFileStatus(lfn, "UNUSED")
                if not res["OK"]:
                    DIRAC.gLogger.warn(f"Failed to set file status to UNUSED {lfn}")

    DIRAC.exit(exit_status)


####################################################
if __name__ == "__main__":
    main()
