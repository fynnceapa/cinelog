from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.conf import settings
from .models import Movie
import urllib.parse

def home(request):
    movies = Movie.objects.all()
    return render(request, 'home.html', {'movies': movies})

def keycloak_logout(request):
    logout(request)
    
    params = urllib.parse.urlencode({
        'post_logout_redirect_uri': settings.LOGOUT_REDIRECT_URL_EXTERNAL,
        'client_id': settings.OIDC_RP_CLIENT_ID
    })
    
    logout_url = f"{settings.OIDC_OP_LOGOUT_ENDPOINT}?{params}"
    
    return redirect(logout_url)

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    
    return render(request, 'movie_detail.html', {'movie': movie})

def keycloak_register(request):
    register_endpoint = settings.OIDC_OP_AUTHORIZATION_ENDPOINT.replace('/auth', '/registrations')
    
    params = {
        'client_id': settings.OIDC_RP_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid email profile',
        # Important: După înregistrare, Keycloak te loghează automat și te trimite aici:
        'redirect_uri': request.build_absolute_uri('/oidc/callback/'), 
    }
    
    register_url = f"{register_endpoint}?{urllib.parse.urlencode(params)}"
    return redirect(register_url)