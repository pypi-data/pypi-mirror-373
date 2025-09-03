#############################################################################
# $HeadURL$
#############################################################################

""" The StorageMonitorAgent checks the storage space usage
    for SEs defined in the Agent section
"""

__RCSID__ = "$Id$"

from DIRAC import S_OK, S_ERROR
from DIRAC.ConfigurationSystem.Client.CSAPI import CSAPI
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.Utilities.Subprocess import systemCall
from DIRAC.Core.Utilities.PrettyPrint import printTable
from DIRAC.FrameworkSystem.Client.NotificationClient import NotificationClient


class StorageMonitorAgent(AgentModule):
    addressTo = ""
    addressFrom = ""
    voName = ""
    bdii = "lcg-bdii.cern.ch:2170"
    productionSEs = []
    subject = "StorageMonitorAgent"

    def initialize(self):
        self.addressTo = self.am_getOption("MailTo", self.addressTo)
        self.addressFrom = self.am_getOption("MailFrom", self.addressFrom)

        if self.addressTo and self.addressFrom:
            self.log.info("MailTo", self.addressTo)
            self.log.info("MailFrom", self.addressFrom)

        self.productionSEs = self.am_getOption("ProductionSEs", self.productionSEs)
        if self.productionSEs:
            self.log.info("ProductionSEs", self.productionSEs)
        else:
            self.log.fatal("ProductionSEs option not defined for agent")
            return S_ERROR()

        self.voName = self.am_getOption("VirtualOrganization", self.voName)
        if self.voName:
            self.log.info("Agent will manage VO", self.voName)
        else:
            self.log.fatal("VirtualOrganization option not defined for agent")
            return S_ERROR()

        self.bdii = self.am_getOption("Bdii", self.bdii)
        if self.bdii:
            self.log.info("Bdii", self.bdii)

        self.csAPI = CSAPI()
        return self.csAPI.initialize()

    def execute(self):
        """General agent execution method"""
        # Get a "fresh" copy of the CS data
        result = self.csAPI.downloadCSData()
        if not result["OK"]:
            self.log.warn(
                "Could not download a fresh copy of the CS data", result["Message"]
            )

        # Execute command to retrieve storage usage information
        cmdTuple = ["lcg-infosites", "--vo", self.voName, "se"]
        self.log.info(f"Executing {cmdTuple}")
        ret = systemCall(0, cmdTuple, env={"LCG_GFAL_INFOSYS": self.bdii})

        if not ret["OK"]:
            return ret
        elif not ret["Value"][1] != "":
            self.log.error(f"Error while executing {cmdTuple}")
            return S_ERROR()

        # initialize sedict
        sedict = {}
        for SE in self.productionSEs:
            sedict[SE] = []

        fields = ["SE", "Available(TB)", "Used(TB)", "Total(TB)", "Used(%)"]
        records = []
        fullSEList = []

        for se in ret["Value"][1].split("\n"):
            if len(se.split()) == 4:
                spacedict = {}
                SE = se.split()[3]
                if (
                    SE in self.productionSEs
                    and se.split()[0] != "n.a"
                    and se.split()[1] != "n.a"
                ):
                    # ## convert into TB
                    available = float(se.split()[0]) / 1e9
                    used = float(se.split()[1]) / 1e9
                    spacedict["Available"] = available
                    spacedict["Used"] = used
                    spacedict["Total"] = available + used
                    sedict[SE].append(spacedict)

        for SE in self.productionSEs:
            for spacedict in sedict[SE]:
                available = f"{spacedict['Available']:.1f}"
                used = f"{spacedict['Used']:.1f}"
                total = f"{spacedict['Total']:.1f}"
                fraction_used = spacedict["Used"] / spacedict["Total"] * 100
                if fraction_used > 90.0:
                    fullSEList.append(SE)
                    self.log.warn(f"{SE} full at {fraction_used:.1f}%")
                fraction_used = f"{fraction_used:.1f}"
                records.append([SE, available, used, total, fraction_used])

        body = printTable(fields, records, printOut=False)

        if len(fullSEList) > 0:
            self.subject = f"CRITICAL storage usage beyond 90%: {', '.join(fullSEList)}"

        if self.addressTo and self.addressFrom:
            notification = NotificationClient()
            result = notification.sendMail(
                self.addressTo, self.subject, body, self.addressFrom, localAttempt=False
            )
            if not result["OK"]:
                self.log.error("Can not send  notification mail", result["Message"])

        return S_OK()
