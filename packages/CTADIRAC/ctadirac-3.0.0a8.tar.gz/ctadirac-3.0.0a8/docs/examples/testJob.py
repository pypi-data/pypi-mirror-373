"""
    Launcher script for a simple job example
"""

__RCSID__ = "$Id$"

from DIRAC.Core.Base import Script

Script.parseCommandLine()
from DIRAC.Interfaces.API.Job import Job
from DIRAC import gLogger
from DIRAC.Interfaces.API.Dirac import Dirac

dirac = Dirac()
job = Job()
job.setExecutable("echo", arguments="Hello world")
job.setName("testjob")
res = dirac.submitJob(job)
gLogger.notice("Submission Result:", res["Value"])
