from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models.aggregates import Sum

if TYPE_CHECKING:
    from isapilib.models import Vin, Compra


class VinMixin:
    def get_costo(self: Vin) -> int:
        from isapilib.models import Compra
        if isinstance(self.compra, Compra):
            return (self.compra.importe or 0) - (self.compra.impuestos or 0)
        return 0

    def get_precio(self: Vin) -> int:
        accessories = self.accessories.filter(tipo__afecta_precio=1)
        return accessories.aggregate(total=Sum('precio_contado'))['total'] or 0
