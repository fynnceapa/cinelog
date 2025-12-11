from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Movie

@registry.register_document
class MovieDocument(Document):
    class Index:
        # Numele indexului in ElasticSearch
        name = 'movies'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Movie # Modelul asociat
        
        # Campurile pe care vrem sa le cautam
        fields = [
            'title',
            'description',
            'release_date',
            'poster_url', # Il luam si pe asta ca sa il afisam in rezultate
        ]