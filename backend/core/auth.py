from mozilla_django_oidc.auth import OIDCAuthenticationBackend
import unicodedata

class KeycloakOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(KeycloakOIDCAuthenticationBackend, self).create_user(claims)
        
        self.update_user(user, claims)
        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.email = claims.get('email', '')
        
        preferred_username = claims.get('preferred_username')
        if preferred_username:
            user.username = preferred_username
            
        user.save()
        return user