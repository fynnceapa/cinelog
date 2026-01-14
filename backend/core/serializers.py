from rest_framework import serializers
from .models import Movie, Review

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'movie', 'rating', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Nota trebuie să fie între 1 și 5.")
        return value

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_date', 'poster_url', 'rating', 'created_at']