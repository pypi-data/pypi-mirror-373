#!/usr/bin/env python
"""
Get summary informations of all productions
"""
import DIRAC
from DIRAC.Core.Base.Script import Script
import typer
from rich.table import Table
from rich.console import Console

from CTADIRAC.Core.Utilities.typer_callbacks import (
    PRODUCTION_FIELDS,
    cond_dict_callback,
)

script = Script()
script.localCfg.isParsed = True
script.parseCommandLine(ignoreErrors=True)


app = typer.Typer()
long: bool = typer.Option(False, "--long", help="Long output.")

cond_dict = typer.Option(
    None,
    "--cond",
    callback=cond_dict_callback,
    help="Condition dictionnary to select fields.",
)


def extract_user_name_from_dn(author_dn):
    return author_dn.split("CN=")[-1]


def fill_columns(prod, fields, long):
    columns = []
    for f in fields:
        if f == "AuthorDN" and not long:
            columns += [str(extract_user_name_from_dn(prod[f]))]
        else:
            columns += [str(prod[f])]
    return columns


@app.command()
def main(long: bool = long, cond_dict: str = cond_dict):
    from DIRAC.ProductionSystem.Client.ProductionClient import ProductionClient

    prod_client = ProductionClient()
    res = prod_client.getProductions(condDict=cond_dict)
    fields = PRODUCTION_FIELDS
    if not long:
        fields.remove("CreationDate")
    table = Table(*fields)
    console = Console()
    if res["OK"]:
        prod_list = res["Value"]
        if not isinstance(res["Value"], list):
            prod_list = [res["Value"]]
        for prod in prod_list:
            columns = fill_columns(prod, fields, long)
            table.add_row(*columns)
    else:
        DIRAC.gLogger.error(res["Message"])
        DIRAC.exit(-1)

    console.print(table)


if __name__ == "__main__":
    app()
