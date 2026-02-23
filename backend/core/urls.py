from . import api_views
from . import views

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Configurarea routerului REST API
router = DefaultRouter()
router.register(r'api/movies', api_views.MovieViewSet, basename='api-movie')
router.register(r'api/reviews', api_views.ReviewViewSet, basename='api-review')
router.register(r'api/users', api_views.UserViewSet, basename='api-user')
router.register(r'api/profiles', api_views.UserProfileViewSet, basename='api-profile')
router.register(r'api/watchlist', api_views.WatchlistViewSet, basename='api-watchlist')

urlpatterns = [
    # Rute tradicionale HTML
    path('', views.home, name='home'),
    path('feed/', views.feed, name='feed'),
    path('search/', views.search, name='search'),

    path('register/', views.keycloak_register, name='oidc_register'),
    path('logout/', views.keycloak_logout, name='oidc_logout'),

    path('movies/', views.all_movies, name='all_movies'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/watchlist/', views.toggle_watchlist, name='toggle_watchlist'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),

    path('follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
    path('u/<str:username>/', views.user_profile, name='user_profile'),

    # Rute REST API
    path('', include(router.urls)), 
]