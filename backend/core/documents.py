from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Movie
from django.contrib.auth.models import User

@registry.register_document
class MovieDocument(Document):
    class Index:
        name = 'movies'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Movie
        fields = ['title', 'description', 'release_date', 'poster_url']

@registry.register_document
class UserDocument(Document):
    class Index:
        name = 'users'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = User
        fields = ['username']