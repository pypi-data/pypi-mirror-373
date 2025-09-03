from typing import Literal, TypedDict
from DIRAC import S_OK


class DReportReturnType(TypedDict):
    """used for typing the DIRAC return structure"""

    OK: Literal[True]
    Value: dict[bool, str]


def s_report(report: bool = False, message: str = "") -> DReportReturnType:
    """Return a S_OK but with a report bool"""
    return S_OK({"Report": report, "Message": message})
