""" Utility for building production tests
"""

__RCSID__ = "$Id$"

import json

from DIRAC.Core.Base.Script import Script


# from DIRAC
from DIRAC import gLogger
from DIRAC import S_OK
from DIRAC.ProductionSystem.Client.ProductionClient import ProductionClient
from DIRAC.ProductionSystem.Client.ProductionStep import ProductionStep
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.Interfaces.API.Dirac import Dirac
from testJobDefinitions import create_workflow_body_step
from testJobDefinitions import create_workflow_body_step1
from testJobDefinitions import create_workflow_body_step2

Script.parseCommandLine()

dm = DataManager()
prod_client = ProductionClient()
prod_desc = prod_client.prodDescription
dirac = Dirac()

testDir = "/ctao/tests/prodsys"


def create_production_step(name, type, input_query=None, output_query=None):
    prod_step = ProductionStep()
    prod_step.Name = name
    prod_step.Type = type
    prod_step.Inputquery = input_query
    prod_step.Outputquery = output_query
    return prod_step


def set_md_in_dfc():
    md_field_dict = {
        "application": "VARCHAR(128)",
        "image_format": "VARCHAR(128)",
        "image_width": "int",
        "image_height": "int",
    }
    fc = FileCatalog()
    for md_field in md_field_dict.keys():
        md_field_type = md_field_dict[md_field]
        res = fc.addMetadataField(md_field, md_field_type)
        yield res


def clean_prod_sys_dir():
    gLogger.notice("Cleaning directory", testDir)
    res = dm.cleanLogicalDirectory(testDir)
    return res


# Create the first production step and add it to the Production
def create_prod_step1(output_se=None):
    outputquery = {
        "application": "mandelbrot",
        "image_format": "ascii",
        "image_width": 7680,
        "image_height": 200,
    }
    prod_step1 = create_production_step(
        "ImageProd", "MCSimulation", output_query=outputquery
    )
    if output_se:
        body = create_workflow_body_step1(output_se=output_se)
    else:
        body = create_workflow_body_step()
    prod_step1.Body = body
    res = prod_client.addProductionStep(prod_step1)
    return res, prod_step1


# Create the second production step and add it to the Production
def create_prod_step2(prod_step1, output_se):
    input_query = {
        "application": "mandelbrot",
        "image_format": "ascii",
        "image_width": 7680,
        "image_height": 200,
    }
    output_query = {
        "application": "mandelbrot",
        "image_format": "ascii",
        "image_width": 7680,
        "image_height": 1400,
    }
    prod_step2 = create_production_step(
        "MergeImage",
        "DataReprocessing",
        input_query=input_query,
        output_query=output_query,
    )

    body = create_workflow_body_step2(output_se)
    prod_step2.Body = body
    prod_step2.GroupSize = 7
    prod_step2.ParentStep = prod_step1
    res = prod_client.addProductionStep(prod_step2)
    return res, prod_step2


# Check if there is already an existing production SeqProd and delete it
def get_prod(prod_name):
    res = prod_client.getProduction(prod_name)
    return res


def set_prod_status(prod_name, prod_client=prod_client, status="Stopped"):
    res = prod_client.setProductionStatus(prod_name, status)
    return res


def delete_prod(prod_name, prod_client=prod_client):
    res = prod_client.deleteProduction(prod_name)
    return res


def clean_prod(prod_name):
    res = prod_client.getProduction(prod_name)
    if res["OK"]:
        if res["Value"]["ProductionName"] == prod_name:
            print(f"Clean existing production {prod_name}")
            res = set_prod_status(prod_name=prod_name)
            if not res["OK"]:
                print(f"Failed to stop production {prod_name}")
            else:
                print(f"Stop production {prod_name}")
            res = delete_prod(prod_name=prod_name)
            if not res["OK"]:
                print(f"Failed to delete production {prod_name}")
            else:
                print(f"Deleted existing production {prod_name}")
    else:
        print(f"Failed to get production {prod_name}: {res['Message']}")
        return S_OK(res)
    return res


# Create the production SeqProd
def create_prod(prod_name, prod_desc=prod_desc):
    res = prod_client.addProduction(prod_name, json.dumps(prod_desc))
    return res


# Start the production, i.e. instantiate the transformation steps
def start_prod(prod_name):
    res = prod_client.startProduction(prod_name)
    return res


def get_prod_transformations(prod_name):
    res = prod_client.getProductionTransformations(prod_name)
    trans_list = res["Value"]
    return trans_list


def extend_transformation(transfo, n_tasks=21):
    res = transfo.extend_transformation(n_tasks, printOutput=False)
    return res


def get_transformation_jobs_id(trans_id):
    job_group = str(str(trans_id).zfill(8))
    # Choose jobs no more than 30 days old
    # jobDate = toString(datetime.datetime.utcnow().date() - 30 * day)
    res = dirac.selectJobs(jobGroup=job_group)
    return res
