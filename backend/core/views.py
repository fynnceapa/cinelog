import os
import profile
from sys import stdout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.conf import settings
from requests import request
from .models import Movie, User, Review, WatchlistEntry
import urllib.parse
from django.db.models import Avg
from elasticsearch_dsl import Q
from .documents import MovieDocument, UserDocument

from django.contrib.auth.decorators import login_required

import pika
import json

from itertools import chain
from operator import attrgetter

# api
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import MovieSerializer, ReviewSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncDate


def home(request):
    movies = Movie.objects.all().order_by('-created_at')[:5]
    return render(request, 'home.html', {'movies': movies})

def all_movies(request):
    sort_option = request.GET.get('sort', 'release_date_desc')

    if sort_option == 'release_date_asc':
        movies = Movie.objects.all().order_by('release_date')
    elif sort_option == 'rating_desc':
        movies = Movie.objects.all().annotate(avg_rating=Avg('rating')).order_by('-avg_rating')
    elif sort_option == 'rating_asc':
        movies = Movie.objects.all().annotate(avg_rating=Avg('rating')).order_by('avg_rating')
    elif sort_option == 'name':
        movies = Movie.objects.all().order_by('title')
    else:
        movies = Movie.objects.all().order_by('-release_date')

    context = {
        'movies': movies,
        'current_sort': sort_option
    }
    return render(request, 'all_movies.html', context)

def keycloak_logout(request):
    logout(request)
    
    params = urllib.parse.urlencode({
        'post_logout_redirect_uri': settings.LOGOUT_REDIRECT_URL_EXTERNAL,
        'client_id': settings.OIDC_RP_CLIENT_ID
    })
    
    logout_url = f"{settings.OIDC_OP_LOGOUT_ENDPOINT}?{params}"
    
    return redirect(logout_url)

def keycloak_register(request):
    register_endpoint = settings.OIDC_OP_AUTHORIZATION_ENDPOINT.replace('/auth', '/registrations')
    
    params = {
        'client_id': settings.OIDC_RP_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid email profile',
        'redirect_uri': request.build_absolute_uri('/oidc/callback/'), 
    }
    
    register_url = f"{register_endpoint}?{urllib.parse.urlencode(params)}"
    return redirect(register_url)

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    if request.method == 'POST' and request.user == profile_user:
        new_bio = request.POST.get('bio')
        new_avatar = request.POST.get('avatar_url')
        
        profile = profile_user.profile
        profile.bio = new_bio
        if new_avatar:
            profile.avatar_url = new_avatar
        profile.save()
        return redirect('user_profile', username=username)

    reviews = profile_user.review_set.all().order_by('-created_at')
    watchlist = profile_user.profile.watchlist.all().order_by('-created_at')
    
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        my_profile = request.user.profile
        is_following = profile_user.profile in my_profile.follows.all()
    
    context = {
        'profile_user': profile_user,
        'reviews': reviews,
        'watchlist': watchlist, # Trimitem lista către template
        'is_own_profile': (request.user == profile_user),
        'is_following': is_following
    }
    return render(request, 'user_profile.html', context)


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    in_watchlist = False

    if request.user.is_authenticated:
        in_watchlist = movie in request.user.profile.watchlist.all()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        content = request.POST.get('content')

        rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        
        payload = {
            'user_id': request.user.id,
            'movie_id': movie.id,
            'rating': int(rating),
            'content': content
        }

        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host)
            )
            channel = connection.channel()
                
            channel.queue_declare(queue='reviews_queue', durable=True)

            channel.basic_publish(
                exchange='',
                routing_key='reviews_queue',
                body=json.dumps(payload),
                properties=pika.BasicProperties(
                delivery_mode=2,
                )
            )
            connection.close()
            stdout.write("Mesaj trimis catre RabbitMQ\n")
            return redirect('movie_detail', movie_id=movie.id)
                
        except Exception as e:
            stdout.write(f"Eroare conectare RabbitMQ: {e}\n")
            Review.objects.create(
                user=request.user,
                movie=movie,
                rating=rating,
                content=content
            )

            return redirect('movie_detail', movie_id=movie.id)

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'in_watchlist': in_watchlist, 
    })

def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    
    if request.user == review.user:
        movie_id = review.movie.id
        review.delete()
        return redirect('movie_detail', movie_id=movie_id)
    
    return redirect('movie_detail', movie_id=review.movie.id)

def search(request):
    query = request.GET.get('q')
    movies = []
    users = []

    if query:
        movies = MovieDocument.search().query(
            "multi_match", 
            query=query, 
            fields=['title', 'description']
        )

        users = UserDocument.search().query(
            Q("wildcard", username=f"*{query}*") | Q("match", username=query)
        )

    return render(request, 'search.html', {
        'query': query,
        'movies': movies,
        'users': users
    })

# feed
@login_required
def toggle_follow(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    target_profile = target_user.profile
    my_profile = request.user.profile

    if target_profile in my_profile.follows.all():
        my_profile.follows.remove(target_profile)
    else:
        my_profile.follows.add(target_profile)
        
        payload = {
            'type': 'follow_notification',
            'follower_username': request.user.username,
            'target_email': target_user.email,
            'target_username': target_user.username
        }
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='notifications_queue', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key='notifications_queue',
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
        except Exception as e:
            print(f"Eroare RabbitMQ Notificari: {e}")

    return redirect('user_profile', username=target_user.username)

@login_required
def feed(request):
    my_profile = request.user.profile
    following_profiles = my_profile.follows.all()
    following_users = [p.user for p in following_profiles]
    
    reviews = Review.objects.filter(user__in=following_users)
    
    watchlist_entries = WatchlistEntry.objects.filter(profile__in=following_profiles)

    feed_items = sorted(
        chain(reviews, watchlist_entries),
        key=attrgetter('created_at'),
        reverse=True
    )
    
    return render(request, 'feed.html', {'feed_items': feed_items})

@login_required
def toggle_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    profile = request.user.profile
    
    entry = WatchlistEntry.objects.filter(profile=profile, movie=movie).first()

    if entry:
        entry.delete()
    else:
        WatchlistEntry.objects.create(profile=profile, movie=movie)
        
    return redirect('movie_detail', movie_id=movie_id)