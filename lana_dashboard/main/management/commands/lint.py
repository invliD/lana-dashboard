import os

from django.conf import settings
from django.core.management.base import BaseCommand
from flake8.main.application import Application as Flake8


class Command(BaseCommand):
	help = 'Run flake8.'

	def handle(self, *args, **options):
		os.chdir(os.path.join(os.path.join(settings.BASE_DIR, '..')))
		flake8 = Flake8()
		flake8.run(['flake8', 'lana_dashboard'])
		flake8.exit()
