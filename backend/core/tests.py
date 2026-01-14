import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Movie, Review

class ReviewQueueTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.movie = Movie.objects.create(
            title='Test Movie', 
            description='Descriere test', 
            release_date='2024-01-01'
        )
        self.client = Client()
        self.url = reverse('movie_detail', args=[self.movie.id])

    @patch('core.views.pika.BlockingConnection')
    def test_review_publish_success(self, mock_connection):
        """
        Scenario 1: RabbitMQ funcționează.
        Testăm dacă view-ul trimite mesajul în coadă și NU salvează în DB (worker-ul ar trebui să facă asta).
        """
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel
        
        # Logăm userul
        self.client.login(username='testuser', password='password123')

        response = self.client.post(self.url, {
            'rating': 5,
            'content': 'Excelent film!'
        })

        self.assertEqual(response.status_code, 302)
        
        mock_channel.queue_declare.assert_called_with(queue='reviews_queue', durable=True)
        
        self.assertTrue(mock_channel.basic_publish.called)
        
        call_args = mock_channel.basic_publish.call_args
        published_body = json.loads(call_args[1]['body'])
        
        self.assertEqual(published_body['user_id'], self.user.id)
        self.assertEqual(published_body['movie_id'], self.movie.id)
        self.assertEqual(published_body['rating'], 5)
        self.assertEqual(published_body['content'], 'Excelent film!')

        self.assertEqual(Review.objects.count(), 0)

    @patch('core.views.pika.BlockingConnection')
    def test_review_publish_failure_fallback(self, mock_connection):
        mock_connection.side_effect = Exception("RabbitMQ Connection Error")
        
        self.client.login(username='testuser', password='password123')

        self.client.post(self.url, {
            'rating': 3,
            'content': 'Merge si fara coada.'
        })

        self.assertEqual(Review.objects.count(), 1)
        
        review = Review.objects.first()
        self.assertEqual(review.content, 'Merge si fara coada.')
        self.assertEqual(review.rating, 3)

    def test_worker_logic_simulation(self):
        payload = {
            'user_id': self.user.id,
            'movie_id': self.movie.id,
            'rating': 4,
            'content': 'Test worker logic'
        }

        user = User.objects.get(id=payload['user_id'])
        movie = Movie.objects.get(id=payload['movie_id'])
        Review.objects.create(
            user=user,
            movie=movie,
            rating=payload['rating'],
            content=payload['content']
        )

        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().content, 'Test worker logic')