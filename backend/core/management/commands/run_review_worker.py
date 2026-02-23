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
        print("astept rabbit")
        rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        connection = None
        while not connection:
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=rabbitmq_host)
                )
            except pika.exceptions.AMQPConnectionError:
                print('indisponibil')
                time.sleep(5)

        channel = connection.channel()

        channel.queue_declare(queue='reviews_queue', durable=True)

        print("wait")

        def callback(ch, method, properties, body):
            try:
                data = json.loads(body)
                print(f"Mesaj primit: {data}")
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
                    
                print(f"review creat pentru user {user_id} si film {movie_id}, folosind rabbitmq.")

                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Eroare la procesarea mesajului: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='reviews_queue', on_message_callback=callback)
        channel.start_consuming()