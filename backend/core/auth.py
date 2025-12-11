from mozilla_django_oidc.auth import OIDCAuthenticationBackend
import unicodedata

class KeycloakOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        # Suprascriem crearea utilizatorului pentru a salva username-ul corect
        user = super(KeycloakOIDCAuthenticationBackend, self).create_user(claims)
        
        # Actualizăm imediat câmpurile cu datele din Keycloak
        self.update_user(user, claims)
        return user

    def update_user(self, user, claims):
        # Această funcție se apelează la FIECARE login
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.email = claims.get('email', '')
        
        # AICI este modificarea importantă: luăm 'preferred_username'
        preferred_username = claims.get('preferred_username')
        if preferred_username:
            user.username = preferred_username
            
        user.save()
        return user