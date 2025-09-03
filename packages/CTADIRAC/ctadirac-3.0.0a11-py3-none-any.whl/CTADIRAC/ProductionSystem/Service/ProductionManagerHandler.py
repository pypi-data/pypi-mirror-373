from DIRAC.ProductionSystem.Service.ProductionManagerHandler import (
    ProductionManagerHandler as DIRACProductionManagerHandler,
)


class ProductionManagerHandlerMixin:
    types_get_parent_transformation = [int]

    def export_get_parent_transformation(self, trans_id):
        res = self.productionDB.get_parent_transformation(trans_id)
        return res


class ProductionManagerHandler(
    ProductionManagerHandlerMixin, DIRACProductionManagerHandler
):
    pass
