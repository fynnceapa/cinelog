from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, Review, UserProfile, WatchlistEntry

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followed_by_count = serializers.SerializerMethodField()
    follows_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'avatar_url', 'followed_by_count', 'follows_count']
        read_only_fields = ['user']
    
    def get_followed_by_count(self, obj):
        return obj.followed_by.count()
    
    def get_follows_count(self, obj):
        return obj.follows.count()

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    movie_title = serializers.ReadOnlyField(source='movie.title')

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_id', 'username', 'movie', 'movie_title', 'rating', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Nota trebuie să fie între 1 și 5.")
        return value

class MovieSerializer(serializers.ModelSerializer):
    review_count = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_date', 'poster_url', 'rating', 'review_count', 'reviews', 'created_at']
        read_only_fields = ['created_at', 'rating']
    
    def get_review_count(self, obj):
        return obj.reviews.count()

class WatchlistEntrySerializer(serializers.ModelSerializer):
    movie_title = serializers.ReadOnlyField(source='movie.title')
    movie_details = MovieSerializer(source='movie', read_only=True)

    class Meta:
        model = WatchlistEntry
        fields = ['id', 'profile', 'movie', 'movie_title', 'movie_details', 'created_at']
        read_only_fields = ['profile', 'created_at']