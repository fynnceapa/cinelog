from sys import stdout
import pika
import json
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Review, Movie, User
from django.shortcuts import get_object_or_404
import os

class Command(BaseCommand):
    def handle(self, *args, **options):
        stdout.write(self.style.SUCCESS('astept'))
        rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        connection = None
        while not connection:
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=rabbitmq_host)
                )
            except pika.exceptions.AMQPConnectionError:
                self.stdout.write('indisponibil')
                time.sleep(5)

        channel = connection.channel()

        channel.queue_declare(queue='reviews_queue', durable=True)

        stdout.write(self.style.SUCCESS('wait'))

        def callback(ch, method, properties, body):
            try:
                data = json.loads(body)
                self.stdout.write(f"Mesaj primit: {data}")

                user_id = data.get('user_id')
                movie_id = data.get('movie_id')
                rating = data.get('rating')
                content = data.get('content')

                user = User.objects.get(id=user_id)
                movie = Movie.objects.get(id=movie_id)

                Review.objects.create(
                    user=user,
                    movie=movie,
                    rating=rating,
                    content=content
                )
                
                stdout.write(self.style.SUCCESS(f"Recenzie salvata pentru filmul ID {movie_id}"))

                ch.basic_ack(delivery_tag=method.delivery_tag)

            except Exception as e:
                stdout.write(self.style.ERROR(f"Eroare procesare: {e}"))
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='reviews_queue', on_message_callback=callback)

        channel.start_consuming()