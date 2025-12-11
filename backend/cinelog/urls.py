from django.contrib import admin
from django.urls import path, include
from core.views import home, keycloak_logout, movie_detail, keycloak_register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oidc/', include('mozilla_django_oidc.urls')),
    
    path('logout/', keycloak_logout, name='oidc_logout'), 
    path('movie/<int:movie_id>/', movie_detail, name='movie_detail'),
    path('register/', keycloak_register, name='oidc_register'),
    path('', home, name='home'),
]