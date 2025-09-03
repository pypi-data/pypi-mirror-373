from isapilib.external.utilities import execute_sp


class CteMixin:
    def new_cte(self):
        self.cliente = execute_sp('spConsecutivo', ['CTE', 0])[0]
        self.colonia = 'NA'
        self.rfc = 'XAXX010101000'
        self.direccion = 'NA'
        self.direccion_numero = '1'
        self.tipo = 'Cliente'
        self.estado = 'NA'
        self.pais = 'NA'
        self.estatus = 'ALTA'
