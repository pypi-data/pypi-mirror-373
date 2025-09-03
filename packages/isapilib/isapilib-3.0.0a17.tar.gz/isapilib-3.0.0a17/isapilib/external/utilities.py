from datetime import datetime
from typing import List

from django.db import router, connections
from django.db.models import Q


class ExecutionQuery:
    def __init__(self, name, params, using):
        self.name = name
        self.params = params or []
        self.using = using or router.db_for_write(None)

    @property
    def cursor(self):
        if not hasattr(self, '_cursor'):
            self._cursor = connections[self.using].cursor()
        return self._cursor

    def get_query(self):
        return self.name

    def get_params(self):
        return self.params

    def _execute(self, query, params, using):
        self.cursor.execute(query, params)
        results = []
        try:
            while True:
                rows = self.cursor.fetchall()
                if rows:
                    results.append(rows)
                if not self.cursor.nextset():
                    break
        except Exception as e:
            pass

        return results

    def execute(self):
        return self._execute(self.get_query(), self.get_params(), self.using)


class ExecutionFN(ExecutionQuery):
    def get_query(self):
        fn_params = self.get_params()
        return f'''SELECT dbo.{self.name}({', '.join(['%s' for _ in fn_params])})'''

    def execute(self):
        results = super().execute()
        while isinstance(results, (list, tuple)):
            results = results[0]
        return results


class ExecutionSP(ExecutionQuery):
    def __init__(self, name, params, with_transaction=False, using=None, ):
        super().__init__(name, params, using)
        self.with_transaction = with_transaction

    @property
    def output_variables(self) -> List[str]:
        if not hasattr(self, '_output_variables'):
            query = "SELECT PARAMETER_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM information_schema.parameters WHERE SPECIFIC_NAME = %s AND PARAMETER_MODE = 'INOUT'"
            response = self._execute(query, [self.name], self.using)
            self._output_variables = response[0] if 0 < len(response) else []
        return self._output_variables or []

    def get_execution_settings(self):
        execution_settings = ['SET NOCOUNT ON;']
        if self.with_transaction: execution_settings.append('BEGIN TRANSACTION;')
        return '\n'.join(execution_settings)

    def declare_variable(self, name, type, length):
        declaration = f'{name} '

        if type in ('varchar', 'char'):
            declaration += f"{type}({'MAX' if length == -1 else length})"
        else:
            declaration += f'{type}'

        return declaration

    def get_declaration_output_variables(self):
        if len(self.output_variables) == 0: return ''
        variables = [self.declare_variable(name, type, length) for name, type, length in self.output_variables]
        return f"DECLARE {', '.join(variables)};"

    def get_sp_parameters(self):
        if isinstance(self.params, dict):
            parameters = ', '.join([f'@{i}=%s' for i in self.params.keys()])
        else:
            parameters = ', '.join(['%s' for _ in self.params])

        output_variables = ', '.join([f'{data[0]}={data[0]} OUTPUT' for data in self.output_variables])
        if output_variables != '': output_variables = ', ' + output_variables
        return f'{parameters}{output_variables}'

    def get_sp_exec(self):
        parameters = self.get_sp_parameters()
        if parameters == '': return f'EXEC {self.name};'
        return f'EXEC {self.name} {parameters};'

    def get_select_for_results(self):
        if len(self.output_variables) == 0: return ''
        variables = ', '.join([data[0] for data in self.output_variables])
        return f"SELECT 'OUTPUT', {variables};"

    def get_extra(self):
        extra = []
        if self.with_transaction: extra.append('COMMIT;')
        return '\n'.join(extra)

    def get_query(self):
        execution_settings = self.get_execution_settings()
        declaration_output_variables = self.get_declaration_output_variables()
        exec_sp = self.get_sp_exec()
        results = self.get_select_for_results()
        extra = self.get_extra()
        return '\n'.join([
            execution_settings,
            declaration_output_variables,
            exec_sp,
            results,
            extra
        ]).strip()

    def to_internal_value(self, value):
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%dT%H:%M:%S')
        return value

    def to_internal_values(self, values):
        return [self.to_internal_value(value) for value in values]

    def get_params(self):
        values = super().get_params()
        if isinstance(values, dict):
            values = values.values()
        return self.to_internal_values(values)

    def execute(self, only_output=True):
        results = super().execute()
        if only_output:
            last_line = results[-1][0]
            if last_line[0] == 'OUTPUT':
                return last_line[1:]
        return results


def execute_query(query, params=None, using=None):
    return ExecutionQuery(query, params, using).execute()


def execute_fn(fn_name, fn_params=None, using=None):
    return ExecutionFN(fn_name, fn_params, using).execute()


def execute_sp(sp_name, sp_params=None, only_output=True, with_transaction=False, using=None):
    return ExecutionSP(sp_name, sp_params, with_transaction, using).execute(only_output)


def get_sucursal(mov='Servicio', sucursal=0):
    from isapilib.models import Sucursal
    if issubclass(type(sucursal), Sucursal): sucursal = sucursal.pk

    if (mov in ['Venta Perdida', 'Dias', 'Reservar'] or 'Nota' in mov) and sucursal % 2 == 1:
        sucursal -= 1

    if mov in ['Cita Servicio'] and int(sucursal) % 2 == 0:
        sucursal += 1

    return Sucursal.objects.get(pk=sucursal).pk


def get_almacen(mov='Servicio', sucursal=0):
    from isapilib.models import Sucursal, Almacen
    if issubclass(type(sucursal), Sucursal): sucursal = sucursal.pk

    if (mov in ['Venta Perdida', 'Hist Refacc', 'Reservar'] or 'Nota' in mov) and sucursal % 2 == 1:
        sucursal -= 1
        return Almacen.objects.get(Q(sucursal=sucursal), Q(almacen='R') | Q(almacen__istartswith='RS')).pk
    else:
        return Almacen.objects.get(sucursal=sucursal, almacen__istartswith='S').pk


def get_uen(modulo='VTAS', mov='Servicio', sucursal=0, concepto='Publico', using=None):
    from isapilib.models import Sucursal
    if issubclass(type(sucursal), Sucursal): sucursal = sucursal.pk
    return execute_fn("fnCA_GeneraUENValida", [modulo, mov, sucursal, concepto], using=using)


def get_param_empresa(interfaz, clave, default=None, using=None):
    from isapilib.models import InterfacesPredefinidasDEmpresa as Data
    using = using or router.db_for_write(None)
    valor = Data.objects.using(using).filter(clave=clave, interfaces__interfaz=interfaz).first()
    return getattr(valor, 'valor_default', default)


def get_param_sucursal(sucursal, clave, default=None, using=None):
    from isapilib.models import Sucursal, ParametrosSucursal as Data
    using = using or router.db_for_write(None)
    if issubclass(type(sucursal), Sucursal): sucursal = sucursal.pk
    valor = Data.objects.using(using).filter(sucursal=sucursal, clave=clave).first()
    return getattr(valor, 'valor', default)


def verify_col(table, column, using=None) -> bool:
    try:
        query = f"SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' AND COLUMN_NAME = '{column}'"
        result = execute_query(query, using)
        exists = result[0][0][0]
        return bool(exists)
    except IndexError:
        return False


def get_utc_offset(using=None) -> int:
    result = execute_query('SELECT DATEPART(TZOFFSET, SYSDATETIMEOFFSET())', [], using=using)[0][0][0]
    return int(result)
