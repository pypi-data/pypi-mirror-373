from django.core.management import BaseCommand

from isapilib.api.models import ConnectionAPI


class Command(BaseCommand):
    help = 'Check connection to external database'

    def add_arguments(self, parser):
        parser.add_argument(
            "connection",
            nargs="?",
            help="id connection",
        )

    def handle(self, *args, **options):
        try:
            connectionapi = ConnectionAPI.objects.get(pk=options["connection"])
            name = connectionapi.get_name()

            result, description = connectionapi.verify_connection()
            if result:
                self.stdout.write(self.style.SUCCESS(f'Connection to database {name} was successful.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Failed to connect to database {name}: {description}'))

        except ConnectionAPI.DoesNotExist:
            self.stdout.write(self.style.SUCCESS(f"Branch doesn't exist."))
