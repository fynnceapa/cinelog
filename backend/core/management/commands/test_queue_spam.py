import json
import pika
import random
import os
from django.core.management.base import BaseCommand
from core.models import Movie, User

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            user = User.objects.first()
            movie = Movie.objects.first()
            if not user or not movie:
                self.stdout.write(self.style.ERROR('baza de date goala'))
                return
        except Exception:
            self.stdout.write(self.style.ERROR('nu merge accesata'))
            return

        rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        
        self.stdout.write(f"conectare rabbit")
        
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host)
        )
        channel = connection.channel()
        channel.queue_declare(queue='reviews_queue', durable=True)

        self.stdout.write(self.style.SUCCESS('trimitere mesaje...'))

        for i in range(50):
            payload = {
                'user_id': user.id,
                'movie_id': movie.id,
                'rating': random.randint(4, 10),
                'content': f"Recenzie automată de test #{i} generată de script."
            }

            channel.basic_publish(
                exchange='',
                routing_key='reviews_queue',
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            self.stdout.write(f"Trimis mesaj #{i}")

        connection.close()
        self.stdout.write(self.style.SUCCESS('Terminat!'))