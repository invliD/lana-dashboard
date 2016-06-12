import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from flake8.engine import get_style_guide


class Command(BaseCommand):
	help = 'Run flake8.'

	def handle(self, *args, **options):
		os.chdir(os.path.join(os.path.join(settings.BASE_DIR, '..')))
		style = get_style_guide(config_file='.flake8')
		report = style.check_files(['lana_dashboard'])
		if report.total_errors > 0:
			sys.exit(1)
