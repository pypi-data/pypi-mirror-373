from unittest.mock import MagicMock

import pytest
from CTADIRAC.WorkloadManagementSystem.Client.CTAODownloadInputData import (
    CTAODownloadInputData,
)
from DIRAC import S_OK
from DIRAC.WorkloadManagementSystem.Client.test.Test_Client_DownloadInputData import *  # noqa: F403, F405


@pytest.fixture
def mockSE(mocker):
    mockObjectSE = MagicMock()
    mockObjectSE.getFileMetadata.return_value = S_OK(
        {"Successful": {"/a/lfn/1.txt": {"Cached": 1, "Accessible": 1}}, "Failed": {}}
    )
    mockObjectSE.getFile.return_value = S_OK(
        {"Successful": {"/a/lfn/1.txt": {}}, "Failed": {}}
    )
    mockObjectSE.getStatus.return_value = S_OK({"Read": True, "DiskSE": True})
    mockObjectSE.status.return_value = {"Read": True, "DiskSE": True}

    theMockSE = MagicMock()
    theMockSE.return_value = mockObjectSE
    mocker.patch(
        "DIRAC.WorkloadManagementSystem.Client.DownloadInputData.StorageElement",
        new=theMockSE,
    )
    mocker.patch(
        "CTADIRAC.WorkloadManagementSystem.Client.CTAODownloadInputData.StorageElement",
        new=theMockSE,
    )
    return theMockSE


@pytest.fixture
def dli():
    ctao_dli = CTAODownloadInputData(
        {
            "InputData": [],
            "Configuration": {"LocalSEList": ["SE_Local"]},
            "InputDataDirectory": "CWD",
            "FileCatalog": S_OK(
                {
                    "Successful": {
                        "/a/lfn/1.txt": {
                            "Size": 10,
                            "GUID": "aGUID",
                            "SE_Local": "",
                            "SE_Remote": "",
                            "SE_Bad": "",
                            "SE_Tape": "",
                        }
                    }
                }
            ),
        }
    )
    ctao_dli.availableSEs = ["SE_Local", "SE_Remote"]
    return ctao_dli
