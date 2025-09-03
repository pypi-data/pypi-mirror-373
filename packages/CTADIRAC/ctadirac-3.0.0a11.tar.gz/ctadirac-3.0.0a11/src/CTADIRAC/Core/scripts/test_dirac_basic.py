"""Test job status."""

import pytest

from wms.tests.utils import wait_for_status

pytestmark = [
    pytest.mark.wms,
    pytest.mark.dirac_client,
]


# missing "Run a single-job workflow" UC ID
# @pytest.mark.verifies_usecase("DPPS-UC-110-????")
@pytest.mark.usefixtures("_init_dirac")
def test_simple_job(tmp_path):
    from DIRAC.Interfaces.API.Dirac import Dirac
    from DIRAC.Interfaces.API.Job import Job

    dirac = Dirac()

    job = Job()
    job.setExecutable("echo", arguments="Hello world")
    job.setName("testjob")
    job.setDestination("CTAO.CI.de")
    res = dirac.submitJob(job)
    assert res["OK"]
    job_id = res["Value"]

    # wait for job to succeed, will error in case of timeout or job failure
    result = wait_for_status(
        dirac,
        job_id=job_id,
        status="Done",
        error_on={"Failed"},
        timeout=300,
        job_output_dir=tmp_path,
    )
    print(result)


@pytest.mark.usefixtures("_init_dirac")
def test_cvmfs_available_on_ce(tmp_path):
    from DIRAC.Interfaces.API.Dirac import Dirac
    from DIRAC.Interfaces.API.Job import Job

    dirac = Dirac()

    job = Job()
    job.setExecutable("ls", "/cvmfs/ctao.dpps.test/")
    job.setExecutable("cat", "/cvmfs/ctao.dpps.test/new_repository")
    job.setName("cvmfs_job")
    job.setDestination("CTAO.CI.de")
    res = dirac.submitJob(job)
    assert res["OK"]
    job_id = res["Value"]

    # wait for job to succeed, will error in case of timeout or job failure
    result = wait_for_status(
        dirac,
        job_id=job_id,
        status="Done",
        error_on={"Failed"},
        timeout=300,
        job_output_dir=tmp_path,
    )
    print(result)


@pytest.mark.usefixtures("_init_dirac")
def test_cwl_job(tmp_path):
    from DIRAC.Interfaces.API.Dirac import Dirac
    from DIRAC.Interfaces.API.Job import Job

    dirac = Dirac()

    job = Job()
    cwl_workflow = "src/wms/tests/hello_world.cwl"
    cwl_input = "src/wms/tests/input.yml"
    arguments_str = f"{cwl_workflow} {cwl_input}"
    job.setExecutable("cwltool", arguments=arguments_str, logFile="Job_Log.txt")
    job.setInputSandbox([cwl_workflow, cwl_input])
    job.setOutputSandbox(["*Log.txt"])
    job.setName("test_cwl_job")
    job.setDestination("CTAO.CI.de")
    res = dirac.submitJob(job)
    assert res["OK"]
    job_id = res["Value"]

    # wait for job to succeed, will error in case of timeout or job failure
    result = wait_for_status(
        dirac,
        job_id=job_id,
        status="Done",
        error_on={"Failed"},
        timeout=300,
        job_output_dir=tmp_path,
    )
    print(result)
