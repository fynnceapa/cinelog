from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Movie, Review
from .serializers import MovieSerializer, ReviewSerializer
import pika
import json
import os

from rest_framework.decorators import action
from django.db.models import Count


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all().order_by('-created_at')
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        top_movies = Movie.objects.order_by('-rating')[:10]
        serializer = self.get_serializer(top_movies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        popular_movies = Movie.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:10]
        
        serializer = self.get_serializer(popular_movies, many=True)
        return Response(serializer.data)
    
    filterset_fields = ['rating', 'release_date']
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'rating']

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
