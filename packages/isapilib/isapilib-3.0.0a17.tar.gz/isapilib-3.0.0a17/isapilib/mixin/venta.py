from __future__ import annotations

import random
from typing import Union, TYPE_CHECKING

from django.db import transaction
from django.db.models import QuerySet

from isapilib.core import exceptions
from isapilib.external.utilities import execute_sp
from isapilib.mov.traspaso import TraspasoItems

if TYPE_CHECKING:
    from isapilib.models import Venta, Art, VentaD


class VentaMixin:
    class ACTIONS:
        AFECTAR = 'AFECTAR'
        CONSECUTIVO = 'CONSECUTIVO'
        GENERAR = 'GENERAR'
        CANCELAR = 'CANCELAR'

    def get_origen(self: Venta) -> Union[Venta, None]:
        from isapilib.models import Venta
        if self.origen is None or self.origen_id is None: return None
        return Venta.objects.filter(mov=self.origen, mov_id=self.origen_id).order_by('-fecha_emision').first()

    def get_destinations(self: Venta) -> Union[Venta, None]:
        from isapilib.models import Venta
        if self.mov is None or self.mov_id is None: return None
        return Venta.objects.filter(origen=self.mov, origen_id=self.mov_id).order_by('-fecha_emision').all()

    def create_parts_order_from_service(self: Venta) -> Venta:
        from isapilib.models import Venta

        try:
            with transaction.atomic():
                if self.mov != 'Servicio': raise ValueError('La instancia de venta no es un servicio')

                if self.estatus != 'PENDIENTE':
                    msg = 'El servicio no esta afectado' if self.estatus == 'SINAFECTAR' else 'El servicio ya esta concluido'
                    raise exceptions.ValidationException(msg)

                estimated_pk = execute_sp('xpCA_xpMovCopiarSoloEncabezado', {
                    'Sucursal': self.sucursal.pk,
                    'Modulo': 'VTAS',
                    'ID': self.id,
                    'Empresa': self.empresa.pk,
                    'Mov': 'Pedido Servicio',
                    'MovID': self.mov_id,
                    'Usuario': self.usuario,
                    'TipoCambio': self.tipo_cambio,
                    'Moneda': self.moneda,
                    'Almacen': self.almacen.pk,
                    'AlmacenDestino': self.almacen.pk,
                })[0]

                estimated = Venta.objects.get(id=estimated_pk)
                estimated.origen = self.mov
                estimated.origen_id = self.mov_id
                estimated.save()
                return estimated
        except Exception as e:
            raise e

    def create_service_from_appointment(self: Venta, action=None) -> Venta:
        from isapilib.models import Venta

        try:
            with transaction.atomic():
                if self.mov != 'Cita Servicio': raise ValueError('La instancia de venta no es una cita servicio')
                order = Venta.objects.filter(origen=self.mov, origen_id=self.mov_id, mov='Servicio').order_by(
                    '-fecha_emision').first()

                if self.estatus == 'CONCLUIDO' or getattr(order, 'estatus', 'SINAFECTAR') in ['PENDIENTE', 'CONCLUIDO']:
                    raise exceptions.ValidationException('La cita ya esta concluida')

                if not self.details.exists():
                    raise exceptions.ValidationException('La cita no tiene detalles')

                if self.estatus == 'SINAFECTAR':
                    self.afectar()

                code, description = self.afectar(accion=self.ACTIONS.GENERAR, generar='Servicio')
                if code != 80030:
                    raise exceptions.CoreException(code, description, self)

                order = Venta.objects.filter(origen=self.mov, origen_id=self.mov_id).order_by('-fecha_emision').first()
                if action: order.afectar(accion=action)
                return order
        except Exception as e:
            raise e

    def traspasar_items(self, details: QuerySet[VentaD]):
        try:
            with transaction.atomic():
                if details.count() == 0: return

                order = self.get_origen()
                estacion = random.randint(10000, 99999)

                traspaso = TraspasoItems(order, estacion)

                for detail in details:
                    traspaso.add_item(detail)

                traspaso.execute()
        except Exception as e:
            raise e

    def accept_parts_order(self: Venta, items: tuple[str, bool]) -> bool:
        from isapilib.models import VentaD

        try:
            with transaction.atomic():
                if self.mov != 'Pedido Servicio': raise ValueError('La instancia de venta no es una pedido servicio')
                items_pk = []
                errors = []

                for art_pk, is_accept in items:
                    try:
                        self.details.get(articulo=art_pk)
                        if is_accept: items_pk.append(art_pk)
                    except VentaD.DoesNotExist:
                        errors.append((art_pk, 'El articulo no existe en el pedido servicio'))

                if 0 < len(errors):
                    raise Exception(errors)

                self.traspasar_items(self.details.filter(articulo__in=items_pk))
        except Exception as e:
            raise e

    def add_item(self: Venta, art: Art, cantidad=1, save=True) -> VentaD:
        from isapilib.models import VentaD
        count = VentaD.objects.filter(venta=self).count() + 1
        detail = VentaD(venta=self, renglon_sub=0, renglon_tipo='N', almacen=self.almacen, uen=self.uen,
                        sucursal=self.sucursal, sucursal_origen=self.sucursal, agente=self.agente,
                        hora_requerida=self.hora_requerida, renglon=2048 * count, renglon_id=count,
                        articulo=art, impuesto1=art.impuesto1, descripcion_extra=art.descripcion1,
                        comentarios=art.descripcion1, precio=art.precio_lista or 0, ut=1, cc_tiempo_tab=1,
                        cantidad=cantidad)
        if save: detail.save()
        return detail

    def afectar(self: Venta, *, accion=None, generar=None, usuario=None, s=0, modulo=None, estacion=None, base=None):
        accion = accion or self.ACTIONS.AFECTAR
        code, description = execute_sp('spAfectar', {
            'Modulo': modulo or 'VTAS',
            'ID': self.id,
            'Accion': accion,
            'Base': base or 'Todo',
            'Usuario': usuario or 'SOPDESA',
            'GenerarMov': generar,
            'EnSilencio': s,
            'Estacion': estacion or 1000,
        })

        self.refresh_from_db()

        if (
                (accion == self.ACTIONS.AFECTAR and self.estatus == 'SINAFECTAR') or
                (accion == self.ACTIONS.CONSECUTIVO and self.mov_id is None)
        ):
            raise exceptions.CoreException(code, description, self)

        return code, description

    def cancelar(self):
        self.afectar(accion=self.ACTIONS.CANCELAR)
