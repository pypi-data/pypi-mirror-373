import json
from unittest.mock import MagicMock

import pytest
from CTADIRAC.Core.Workflow.Modules.ProdDataManager import ProdDataManager

prod_dm = ProdDataManager()


def test_getRunPath():
    filemetadata = {"runNumber": "00000044"}
    res = prod_dm._getRunPath(filemetadata)
    assert res == "000xxx"


@pytest.fixture
def manager():
    mgr = ProdDataManager(catalogs=[])
    # replace the real fc/fcc with mocks
    mgr.fc = MagicMock()
    mgr.fcc = MagicMock()
    return mgr


def test_createMDTopDirectory(manager):
    manager.fc.createDirectory.return_value = {"OK": True}
    manager.fcc.setMetadata.return_value = {"OK": True}
    output_metadata = {
        "MCCampaign": "PROD6",
        "site": "Paranal",
        "particle": "gamma",
        "tel_sim_prog": "sim_telarray",
    }
    metadata_json = json.dumps(output_metadata)
    base_path = "/ctao/test/MC"
    program_category = "tel_sim"
    res = manager.createMDTopDirectory(metadata_json, base_path, program_category)
    path = "/ctao/test/MC/PROD6/Paranal/gamma/sim_telarray"
    assert res["OK"]
    assert res["Value"] == path


def test_createMDSubDirectory(manager):
    manager.fc.createDirectory.return_value = {"OK": True}
    manager.fcc.setMetadata.return_value = {"OK": True}
    output_metadata = {
        "MCCampaign": "PROD6",
        "site": "Paranal",
        "particle": "gamma",
        "tel_sim_prog": "sim_telarray",
        "data_level": -1,
        "configuration_id": 10,
    }
    metadata_json = json.dumps(output_metadata)
    base_path = "/ctao/test/MC/PROD6/Paranal/gamma/sim_telarray"
    program_category = "tel_sim"
    output_type_list = ["Data", "Log"]
    trans_id = 2
    res = manager.createMDSubDirectory(
        metadata_json, base_path, program_category, output_type_list, trans_id
    )
    path = "/ctao/test/MC/PROD6/Paranal/gamma/sim_telarray/2"
    assert res["OK"]
    assert res["Value"] == path, f"Expected: {path}, Got: {res['Value']}"
