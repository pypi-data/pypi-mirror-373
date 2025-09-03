""" Manage data and meta-data
"""

__RCSID__ = "$Id$"

# generic imports
import collections
import glob
import json
import os

# DIRAC imports
import DIRAC
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.Core.Utilities import List
from DIRAC.Core.Utilities.SiteSEMapping import getSEsForSite
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from DIRAC.TransformationSystem.Client import TransformationFilesStatus
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient


class ProdDataManager:
    """Manage data and meta-data"""

    def __init__(self, catalogs=["DIRACFileCatalog"]):
        """Constructor"""
        self.catalogs = catalogs
        self.setupCatalogClient(catalogs)
        self.printCatalogConfig(catalogs)
        self.transClient = TransformationClient()
        # ## Get the TransformationID
        self.TransformationID = "0000"  # used for local execution or submission to wms
        self.InputData = []
        if "JOBID" in os.environ:
            jobID = os.environ["JOBID"]
            dirac = Dirac()
            res = dirac.getJobJDL(jobID)
            if "TransformationID" in res["Value"]:
                self.TransformationID = res["Value"]["TransformationID"]
            if "InputData" in res["Value"]:
                self.InputData = res["Value"]["InputData"]

    def setupCatalogClient(self, catalogs):
        """Init FileCatalog client
        Ideally we would like to use only FileCatalog but it doesn't work for setMetadata
        because the returned value has a wrong format. So use of FileCatalogClient instead
        """
        self.fc = FileCatalog(catalogs)
        self.fcc = FileCatalogClient()

    def printCatalogConfig(self, catalogs):
        """Dumps catalog configuration"""
        for catalog in catalogs:
            res = self.fc._getCatalogConfigDetails(catalog)
            DIRAC.gLogger.debug("CatalogConfigDetails:", res)

    def _getSEList(self, SEType="ProductionOutputs", DataType="SimtelProd"):
        """get from CS the list of available SE for data upload"""
        opsHelper = Operations()
        optionName = os.path.join(SEType, DataType)
        SEList = opsHelper.getValue(optionName, [])
        SEList = List.randomize(SEList)
        DIRAC.gLogger.notice(f"List of {SEType} SE: {SEList} ")

        # # Check if the local SE is in the list. If yes try it first by reversing list order
        localSEList = []
        res = getSEsForSite(DIRAC.siteName())
        if res["OK"]:
            localSEList = res["Value"]

        retainedlocalSEList = []
        for localSE in localSEList:
            if localSE in SEList:
                DIRAC.gLogger.notice(
                    "The local Storage Element is an available SE: ", localSE
                )
                retainedlocalSEList.append(localSE)
                SEList.remove(localSE)

        SEList = retainedlocalSEList + SEList
        if len(SEList) == 0:
            return DIRAC.S_ERROR("Error in building SEList")

        return DIRAC.S_OK(SEList)

    def _checkemptydir(self, path):
        """check that the directory is not empty"""
        if len(glob.glob(path)) == 0:
            error = f"Empty directory: {path}"
            return DIRAC.S_ERROR(error)
        else:
            return DIRAC.S_OK()

    def _getRunPath(self, filemetadata):
        """format path to string with 1 digit precision
        run_number is taken from filemetadata
        filemetadata can be a dict or the run_number itself
        """
        if isinstance(filemetadata, dict):
            run_number = int(filemetadata["runNumber"])
        else:
            run_number = int(filemetadata)
        run_numberMod = run_number % 1000
        runpath = "%03dxxx" % ((run_number - run_numberMod) / 1000)
        return runpath

    def _formatPath(self, path):
        """format path to string with 1 digit precision"""
        if isinstance(path, float) or isinstance(path, int):
            path = f"{path:.1f}"
        return str(path)

    def createMDTopDirectory(self, metadata, basepath, program_category):
        """create meta data structure"""

        ### Create the directory structure
        md = json.loads(metadata, object_pairs_hook=collections.OrderedDict)

        path = basepath
        process_program = program_category + "_prog"
        for key, value in collections.OrderedDict(
            (k, md[k])
            for k in ("MCCampaign", "site", "particle", process_program)
            if k in md
        ).items():
            path = os.path.join(path, self._formatPath(value))
            res = self.fc.createDirectory(path)
            if not res["OK"]:
                return res

            # Set directory metadata for each subdir: 'site', 'particle', 'process_program'
            res = self.fcc.setMetadata(path, {key: value})
            if not res["OK"]:
                return res

        return DIRAC.S_OK(path)

    def createMDSubDirectory(
        self, metadata, base_path, program_category, output_type_list, trans_id
    ):
        """create meta data structure"""

        ### Create the directory structure
        md = json.loads(metadata, object_pairs_hook=collections.OrderedDict)
        process_program = program_category + "_prog"

        # Create the TransformationID subdir and set MD
        path = os.path.join(base_path, str(trans_id))
        res = self.fc.createDirectory(path)
        if not res["OK"]:
            return res

        process_program_version = process_program + "_version"
        res = self.fcc.setMetadata(
            path,
            {
                k: md[k]
                for k in (
                    "phiP",
                    "thetaP",
                    "array_layout",
                    process_program_version,
                    "sct",
                    "systematics",
                )
                if k in md
            },
        )
        if not res["OK"]:
            return res

        # Create subdir according to the output_type (Data, Log, Model) and set MD
        transformation_path = path
        for output_type in output_type_list:
            path = os.path.join(transformation_path, output_type)
            res = self.fc.createDirectory(path)
            if not res["OK"]:
                return res

            res = self.fcc.setMetadata(path, {"outputType": output_type})
            if not res["OK"]:
                return res

            # Set additional metadata at subdir level if not already defined
            for metadataKey in [
                "data_level",
                "configuration_id",
            ]:
                res = self.fcc.setMetadata(path, {metadataKey: md[metadataKey]})
                if not res["OK"]:
                    return res

            if output_type in ["Data", "Log"]:
                res = self.fcc.setMetadata(path, {"merged": md.get("merged", 0)})
                if not res["OK"]:
                    return res

        return DIRAC.S_OK(transformation_path)

    def getTransformationPath(self, metadata, basepath, program_category):
        """get the transformation path"""

        ### Create the directory structure
        md = json.loads(metadata, object_pairs_hook=collections.OrderedDict)

        path = basepath
        process_program = program_category + "_prog"
        for value in collections.OrderedDict(
            (k, md[k])
            for k in ("MCCampaign", "site", "particle", process_program)
            if k in md
        ).values():
            path = os.path.join(path, self._formatPath(value))

        # get the TransformationID subdir
        transformation_path = os.path.join(path, self.TransformationID)

        return DIRAC.S_OK(transformation_path)

    def putAndRegister(self, lfn, localfile, filemetadata, DataType):
        """put and register one file and set metadata"""
        # ## Get the list of Production SE
        res = self._getSEList("ProductionOutputs", DataType)
        if res["OK"]:
            ProductionSEList = res["Value"]
        else:
            return res

        # ## Get the list of Failover SE
        res = self._getSEList("ProductionOutputsFailover", DataType)
        if res["OK"]:
            FailoverSEList = res["Value"]
        else:
            return res

        # ## Upload file to a Production SE
        res = self._putAndRegisterToSEList(lfn, localfile, ProductionSEList)
        if not res["OK"]:
            DIRAC.gLogger.error(
                f"Failed to upload file to any Production SE: {ProductionSEList}"
            )
            # ## Upload file to a Failover SE
            res = self._putAndRegisterToSEList(lfn, localfile, FailoverSEList)
            if not res["OK"]:
                return DIRAC.S_ERROR(
                    f"Failed to upload file to any Failover SE: {FailoverSEList}"
                )

        ### Set file metadata also adding jobID metadata
        if res["OK"]:
            fmd = json.loads(filemetadata)
            if "JOBID" in os.environ:
                fmd.update({"jobID": os.environ["JOBID"]})
            res = self.fc.setMetadata(lfn, fmd)
            if not res["OK"]:
                return res

            return DIRAC.S_OK()

    def _putAndRegisterToSEList(self, lfn, localfile, SEList):
        """put and register one file to one SE in the SEList"""
        # Try to upload file to a SE in the list
        voName = lfn.split("/")[1]
        if voName not in ["ctao", "vo.cta.in2p3.fr"]:
            DIRAC.gLogger.error(f"Invalid lfn: path must start with vo name\n {lfn}")
            return DIRAC.S_ERROR()
        dm = DataManager(self.catalogs, vo=voName)

        for SE in SEList:
            msg = f"Try to upload local file: {localfile} \nwith LFN: {lfn} \nto {SE}"
            DIRAC.gLogger.notice(msg)
            res = dm.putAndRegister(lfn, localfile, SE)
            # Check if failed
            if not res["OK"]:
                DIRAC.gLogger.error(
                    f"Failed to putAndRegister {lfn}:\n {res['Message']}"
                )
            else:
                DIRAC.gLogger.notice(f"Successfully uploaded {lfn} to {SE}")
                return DIRAC.S_OK()
        return DIRAC.S_ERROR()

    def setTransformationFileStatus(self, lfn, status):
        if status == "PROCESSED":
            res = self.transClient.setFileStatusForTransformation(
                self.TransformationID, TransformationFilesStatus.PROCESSED, lfn
            )
        elif status == "PROBLEMATIC":
            res = self.transClient.setFileStatusForTransformation(
                self.TransformationID, TransformationFilesStatus.PROBLEMATIC, lfn
            )
        elif status == "UNUSED":
            res = self.transClient.setFileStatusForTransformation(
                self.TransformationID, TransformationFilesStatus.UNUSED, lfn
            )
        else:
            DIRAC.gLogger.error(f"Not allowed File Status {status}")
            return DIRAC.S_ERROR()

        return res

    def cleanLocalFiles(self, datadir, pattern="*"):
        """remove files matching pattern in datadir"""

        for localfile in glob.glob(os.path.join(datadir, pattern)):
            DIRAC.gLogger.notice("Removing local file: ", localfile)
            os.remove(localfile)

        return DIRAC.S_OK()
