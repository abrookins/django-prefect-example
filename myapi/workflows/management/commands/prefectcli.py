from django.core.management.base import BaseCommand
from prefect.cli import app


class Command(BaseCommand):
    help = 'Run Prefect commands'

    def run_from_argv(self, argv):
        app(argv[2:])
