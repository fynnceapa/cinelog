from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Movie, Review, UserProfile, WatchlistEntry
from .serializers import (
    MovieSerializer, ReviewSerializer, UserSerializer, 
    UserProfileSerializer, WatchlistEntrySerializer
)
import pika
import json
import os


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff


class MovieViewSet(viewsets.ModelViewSet):
    """
    API ViewSet pentru gestiunea filmelor.
    
    Acțiuni disponibile:
    - GET /api/movies/ - Listează toate filmele
    - POST /api/movies/ - Crează un nou film (autentificare necesară)
    - GET /api/movies/{id}/ - Detalii film
    - PUT /api/movies/{id}/ - Actualizează film
    - DELETE /api/movies/{id}/ - Șterge film
    - GET /api/movies/top_rated/ - Top 10 filme cu rating maxim
    - GET /api/movies/popular/ - Top 10 filme după numărul de recenzii
    """
    queryset = Movie.objects.all().order_by('-created_at')
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    filterset_fields = ['rating', 'release_date', 'title']
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'rating', 'created_at']

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Returnează top 10 filme cu cel mai mare rating"""
        top_movies = Movie.objects.order_by('-rating')[:10]
        serializer = self.get_serializer(top_movies, many=True)
        return Response({
            'count': len(top_movies),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Returnează top 10 filme cu cele mai multe recenzii"""
        popular_movies = Movie.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:10]
        
        serializer = self.get_serializer(popular_movies, many=True)
        return Response({
            'count': len(popular_movies),
            'results': serializer.data
        })


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API ViewSet pentru gestiunea recenziilor.
    
    Acțiuni disponibile:
    - GET /api/reviews/ - Listează toate recenziile
    - POST /api/reviews/ - Crează o nouă recenzie (autentificare necesară)
    - GET /api/reviews/{id}/ - Detalii recenzie
    - PUT /api/reviews/{id}/ - Actualizează recenzie (doar proprietar)
    - DELETE /api/reviews/{id}/ - Șterge recenzie (doar proprietar)
    """
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    filterset_fields = ['movie', 'rating', 'user']
    search_fields = ['content', 'user__username']
    ordering_fields = ['created_at', 'rating']

    def perform_create(self, serializer):
        """Setează utilizatorul curent la crearea unei recenzii"""
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        """Filtrează recenzii după film dacă este specificat"""
        queryset = Review.objects.all()
        movie_id = self.request.query_params.get('movie_id', None)
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        return queryset.order_by('-created_at')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet pentru vizualizarea utilizatorilor.
    
    Acțiuni disponibile:
    - GET /api/users/ - Listează toți utilizatorii
    - GET /api/users/{id}/ - Detalii utilizator
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API ViewSet pentru gestiunea profilurilor utilizatorilor.
    
    Acțiuni disponibile:
    - GET /api/profiles/ - Listează toate profilurile
    - GET /api/profiles/{id}/ - Detalii profil
    - PUT /api/profiles/{id}/ - Actualizează profil propriu
    - GET /api/profiles/{id}/follow/ - Urmărește un utilizator
    - GET /api/profiles/{id}/unfollow/ - Încearcă urmărire utilizator
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly]
    search_fields = ['user__username', 'bio']
    ordering_fields = ['user__date_joined']

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        profile = self.get_object()
        user_profile = request.user.profile
        
        if user_profile == profile:
            return Response(
                {'error': 'Nu poți să te urmărești pe tine'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if profile in user_profile.follows.all():
            return Response(
                {'error': 'Deja urmărești acest utilizator'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_profile.follows.add(profile)
        return Response(
            {'message': 'Urmărire reușită'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        profile = self.get_object()
        user_profile = request.user.profile
        
        if profile not in user_profile.follows.all():
            return Response(
                {'error': 'Nu urmărești acest utilizator'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_profile.follows.remove(profile)
        return Response(
            {'message': 'Urmărire anulată'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        profile = self.get_object()
        followers = profile.followed_by.all()
        serializer = self.get_serializer(followers, many=True)
        return Response({
            'count': followers.count(),
            'results': serializer.data
        })

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        profile = self.get_object()
        following = profile.follows.all()
        serializer = self.get_serializer(following, many=True)
        return Response({
            'count': following.count(),
            'results': serializer.data
        })


class WatchlistViewSet(viewsets.ModelViewSet):
    """
    API ViewSet pentru gestiunea watchlist-ului.
    
    Acțiuni disponibile:
    - GET /api/watchlist/ - Listează filme din watchlist
    - POST /api/watchlist/ - Adaugă film la watchlist
    - DELETE /api/watchlist/{id}/ - Elimină film din watchlist
    """
    serializer_class = WatchlistEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WatchlistEntry.objects.filter(
            profile=self.request.user.profile
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)

    @action(detail=False, methods=['post'])
    def add_movie(self, request):
        movie_id = request.data.get('movie_id')
        
        if not movie_id:
            return Response(
                {'error': 'movie_id este necesar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        movie = get_object_or_404(Movie, id=movie_id)
        profile = request.user.profile
        
        if WatchlistEntry.objects.filter(profile=profile, movie=movie).exists():
            return Response(
                {'error': 'Filmul este deja în watchlist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        entry = WatchlistEntry.objects.create(profile=profile, movie=movie)
        serializer = self.get_serializer(entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove_movie(self, request):
        movie_id = request.data.get('movie_id')
        
        if not movie_id:
            return Response(
                {'error': 'movie_id este necesar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        entry = get_object_or_404(
            WatchlistEntry,
            profile=request.user.profile,
            movie_id=movie_id
        )
        entry.delete()
        return Response(
            {'message': 'Film eliminat din watchlist'},
            status=status.HTTP_204_NO_CONTENT
        )
