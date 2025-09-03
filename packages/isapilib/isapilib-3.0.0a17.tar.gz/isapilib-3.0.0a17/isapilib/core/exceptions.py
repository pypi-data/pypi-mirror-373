class SepaException(Exception):

    def __init__(self, description, user=None, branch=None):
        self.user = user
        self.branch = branch
        super().__init__(description)


class ValidationException(Exception):
    pass


class CoreException(Exception):
    def __init__(self, code, message, instance=None):
        self.code = code
        self.message = message
        self.instance = instance
        super().__init__(str(self))

    def _get_instance(self):
        try:
            return f' ({self.instance.pk})'
        except Exception:
            return ''

    def __str__(self):
        from isapilib.models import MensajeLista
        message = MensajeLista.objects.filter(mensaje=self.code).first()
        message = f'{message.descripcion}, {self.message}' if message else self.message
        return str(f'{self.code}: {message}' + self._get_instance()).capitalize()


class TraspasoException(Exception):
    def __init__(self, order, estacion, message):
        self.order = order
        self.estacion = estacion
        self.message = message
        super().__init__(str(self))

    def __str__(self):
        return f'{self.message} ({self.order}, {self.estacion})'


class AbortCreationException(Exception):
    pass
