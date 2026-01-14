import pika, json, time
from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('asteptare rabbitmq'))
        
        connection = None
        while not connection:
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='rabbitmq')
                )
            except pika.exceptions.AMQPConnectionError:
                self.stdout.write('indisponibil')
                time.sleep(5)

        channel = connection.channel()
        channel.queue_declare(queue='notifications_queue', durable=True)

        self.stdout.write(self.style.SUCCESS('worker notif pornit'))

        def callback(ch, method, properties, body):
            try:
                data = json.loads(body)
                if data.get('type') == 'follow_notification':
                    context = {
                        'target_username': data['target_username'],
                        'follower_username': data['follower_username']
                    }
                    
                    html_content = render_to_string('emails/follow_notification.html', context)
                    text_content = strip_tags(html_content)

                    msg = EmailMultiAlternatives(
                        subject=f"CineLog: @{data['follower_username']} te urmărește!",
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[data['target_email']]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    
                    self.stdout.write(self.style.SUCCESS(f"Email trimis către {data['target_email']}"))
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Eroare: {e}"))
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_consume(queue='notifications_queue', on_message_callback=callback)
        channel.start_consuming()