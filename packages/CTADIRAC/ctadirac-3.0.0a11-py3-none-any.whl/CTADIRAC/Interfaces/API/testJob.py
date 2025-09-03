import DIRAC
#from DIRAC.Interfaces.API.Dirac import Dirac
from cwl_job import CWLJob

DIRAC.initialize()  # Initialize configuration

job = CWLJob()

job.set_cwl("hello_world.cwl")
job.set_cwl_inputs("input.yml")
job.setTag("production")
res = job.submit()

#res = dirac.submitJob(job)

#print (res)
print(res["Value"])
