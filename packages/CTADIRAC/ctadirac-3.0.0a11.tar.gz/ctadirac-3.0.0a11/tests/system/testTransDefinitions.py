""" Utility for building transformation tests
"""

__RCSID__ = "$Id$"

# from DIRAC
from DIRAC.TransformationSystem.Client.Transformation import Transformation
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from testJobDefinitions import create_workflow_body_step

transClient = TransformationClient()


def get_trans(trans_name):
    res = transClient.getTransformation(trans_name)
    return res


def clean_trans(trans_name):
    res = transClient.stopTransformation(trans_name)
    if not res["OK"]:
        print(f"Failed to stop transformation {trans_name}")
    else:
        print(f"Stop transformation {trans_name}")
    res = transClient.deleteTransformation(trans_name)
    if not res["OK"]:
        print(f"Failed to delete transformation {trans_name}")
    else:
        print(f"Deleted existing transformation {trans_name}")
    return res


def create_mc_transformation(trans_name):
    # Standard parameters
    transformation = Transformation()
    transformation.setTransformationName(trans_name)
    transformation.setType("MCSimulation")
    transformation.setDescription("MC Test")
    transformation.setLongDescription("MC Simulation Test Transformation")
    outputquery = {
        "application": "mandelbrot",
        "image_format": "ascii",
        "image_width": 7680,
        "image_height": 200,
    }
    transformation.setoutputMetaQuery(outputquery)
    workflow_body = create_workflow_body_step()
    transformation.setBody(workflow_body)
    res = transformation.addTransformation()
    transformation.setStatus("Active")
    transformation.setAgentType("Automatic")
    return res, transformation


def extend_trans(trans_id, n_tasks):
    res = transClient.extendTransformation(trans_id, n_tasks)
    if not res["OK"]:
        print(f"Failed to extend transformation {trans_id}")
    else:
        print(f"Extended transformation {trans_id} with {n_tasks} tasks")
    return res


def check_trans_status(trans_name):
    res = transClient.getTransformationParameters(trans_name, "Status")
    if not res["OK"]:
        print(f"Failed to get the status of transformation {trans_name}")
    else:
        status = res["Value"]
        print(f"Status of transformation {trans_name}: {status}")
    return res
