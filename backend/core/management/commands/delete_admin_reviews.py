from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Review


class Command(BaseCommand):
    help = 'Șterge toate review-urile făcute de admin'

    def handle(self, *args, **options):
        try:
            admin_user = User.objects.get(username='admin')
            
            reviews_count = Review.objects.filter(user=admin_user).count()
            
            if reviews_count == 0:
                self.stdout.write(
                    self.style.WARNING(f'Admin nu are niciun review de șters.')
                )
                return
            
            Review.objects.filter(user=admin_user).delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Au fost șterse cu succes {reviews_count} review-uri de admin'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Eroare: Userul admin nu există în baza de date.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Eroare: {str(e)}')
            )
