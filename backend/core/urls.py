from . import api_views
from . import views

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/movies', api_views.MovieViewSet, basename='api-movie')
router.register(r'api/reviews', api_views.ReviewViewSet, basename='api-review')

urlpatterns = [
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

    path('', include(router.urls)), 
]