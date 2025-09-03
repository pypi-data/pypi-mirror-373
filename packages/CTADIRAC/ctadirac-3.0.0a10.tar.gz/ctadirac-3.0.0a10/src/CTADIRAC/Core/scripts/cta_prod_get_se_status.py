#!/usr/bin/env python

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base.Script import Script

Script.setUsageMessage(
    "\n".join(
        [
            "Get storage elements usage of production SEs",
            "Usage:",
            "%s <file with output of lcg-infosites --vo vo.cta.in2p3.fr se>"
            % Script.scriptName,
            f"\ne.g: {Script.scriptName} ccsrm02.in2p3.fr (default is all SEs)",
        ]
    )
)


Script.parseCommandLine(ignoreErrors=True)

from DIRAC.Core.Utilities.PrettyPrint import printTable
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations


@Script()
def main():
    args = Script.getPositionalArgs()

    if len(args) > 2:
        Script.showHelp()

    # Default list
    if len(args) == 1:
        opsHelper = Operations()
        SEList = opsHelper.getValue("ProductionSEs/Hosts", [])
    else:
        SEList = args[:2]

    sedict = {}
    for SE in SEList:
        sedict[SE] = []

    fields = ["SE", "Available(TB)", "Used(TB)", "Total(TB)", "Used(%)"]
    records = []

    fp = open(args[0])

    for se in fp:
        if len(se.split()) == 4:
            spacedict = {}
            SE = se.split()[3]
            if SE in SEList and se.split()[0] != "n.a" and se.split()[1] != "n.a":
                # ## convert into TB
                available = float(se.split()[0]) / 1e9
                used = float(se.split()[1]) / 1e9
                spacedict["Available"] = available
                spacedict["Used"] = used
                spacedict["Total"] = available + used
                sedict[SE].append(spacedict)

    for SE in SEList:
        for spacedict in sedict[SE]:
            available = f"{spacedict['Available']:.1f}"
            used = f"{spacedict['Used']:.1f}"
            total = f"{spacedict['Total']:.1f}"
            fraction_used = spacedict["Used"] / spacedict["Total"] * 100
            fraction_used = f"{fraction_used:.1f}"
            records.append([SE, available, used, total, fraction_used])

    printTable(fields, records)
    DIRAC.exit()


if __name__ == "__main__":
    main()
