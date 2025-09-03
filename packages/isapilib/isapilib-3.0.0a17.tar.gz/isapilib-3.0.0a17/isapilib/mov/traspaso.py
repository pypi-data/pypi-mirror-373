from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from django.db import transaction

from isapilib.core.exceptions import TraspasoException
from isapilib.external.utilities import execute_sp

if TYPE_CHECKING:
    from isapilib.models import Venta, VentaD, VentaTraspasarArticulos


class TraspasoItems:
    def __init__(self, order: Venta, estacion: int):
        self.order = order
        self.estacion = estacion
        self.items: List[VentaTraspasarArticulos] = []

        self.clean()

    def clean(self):
        from isapilib.models import VentaTraspasarArticulos
        VentaTraspasarArticulos.objects.filter(venta=self.order.pk, estacion=self.estacion).delete()

    def add_item(self, detail: VentaD):
        from isapilib.models import VentaTraspasarArticulos
        traspaso = VentaTraspasarArticulos.objects.create(
            venta=self.order.pk,
            estacion=self.estacion,
            articulo=detail.articulo,
            cantidad=detail.cantidad,
            precio=detail.precio or 0,
            accion='Agregar',
            descuento_linea=detail.descuento_linea,
            descuento_importe=detail.descuento_importe,
            paquete=detail.paquete,
            aplica_mov=detail.venta.mov,
            aplica_mov_id=detail.venta.mov_id,
            renglon=detail.renglon,
            origen='API',
        )
        self.items.append(traspaso)
        return traspaso

    def execute(self):
        from isapilib.models import VentaTraspasarArticulos
        try:
            with transaction.atomic():
                response = execute_sp('xpVentaTraspasarArticulosProcesar', {
                    'ID': self.order.pk,
                    'Estacion': self.estacion,
                    'Usuario': 'SOPDESA',
                    'FechaTrabajo': datetime.now(),
                    'Conexion': 1,
                    'CA_EnSilencio': 0,
                }, only_output=False, with_transaction=True)[0][0]
                if VentaTraspasarArticulos.objects.filter(venta=self.order.pk, estacion=self.estacion).exists():
                    raise TraspasoException(self.order.pk, self.estacion, response[0])
                return response
        except Exception as e:
            raise e
