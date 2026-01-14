import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('astept baza de date')
        db_conn = None
        db_up = False

        while not db_up:
            try:
                db_conn = connections['default']
                db_conn.cursor()
                db_up = True 
            except Exception as e:
                self.stdout.write('baza de date indisponibilă')
                time.sleep(1)
        
        self.stdout.write(self.style.SUCCESS('Baza de date este disponibilă!'))