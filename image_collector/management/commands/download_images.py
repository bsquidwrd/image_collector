# Project: image_collector
# File Name: download_images
# Created by: bsquidwrd
# Created on: 4/6/2016

import pkgutil
import importlib
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """
    Goes through and downloads images for websites that are in the database
    and uses their respective modules to process the desired images
    """

    def handle(self, *args, **options):
        sub_modules = []
        for importer, modname, ispkg in pkgutil.walk_packages('image_collector.modules'):
            if 'image_collector.modules.' not in str(modname):
                continue
            sub_modules.append(str(modname))

        for m in sub_modules:
            i = importlib.import_module(m)
            try:
                run_command = getattr(i, 'handle_command')
                run_command()
            except Exception as e:
                print(e)
                continue

