from datetime import datetime, timedelta, UTC

from isapilib.external.utilities import get_utc_offset
from isapilib.models import Venta


class DateAfterTodayValidator:
    requires_context = False

    def __call__(self, value):
        hora_string = value['hora_requerida']
        hora_requerida = datetime.strptime(hora_string, '%H:%M').time()
        fecha_requerida = value['fecha_requerida']
        fecha_requerida = fecha_requerida.combine(fecha_requerida, hora_requerida)
        fecha_requerida = fecha_requerida.replace(tzinfo=UTC)
        current_date = datetime.now(UTC) + timedelta(minutes=get_utc_offset())
        try:
            if fecha_requerida < current_date:
                raise Exception('The date must be after the current date')
        except TypeError as e:
            raise Exception(f'[{fecha_requerida.tzinfo}, {current_date.tzinfo}] - {e}')

        return value


class NoDuplicateAppointmentsValidator:
    requires_context = False

    def __call__(self, value):
        filters = {
            'mov': 'Cita Servicio',
            'agente': value['agente'],
            'fecha_requerida__date': value['fecha_requerida'].date(),
            'hora_recepcion': value['hora_recepcion'],
            'estatus': 'CONFIRMAR'
        }
        if Venta.objects.filter(**filters).exists():
            raise Exception('This appointment has already been scheduled')
