from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Avg

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    poster_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0.0, blank=True, null=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    movie = models.ForeignKey(Movie, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, help_text="Câteva cuvinte despre tine")
    avatar_url = models.URLField(blank=True, null=True, default="https://static.vecteezy.com/system/resources/thumbnails/002/534/006/small/social-media-chatting-online-blank-profile-picture-head-and-body-icon-people-standing-icon-grey-background-free-vector.jpg")
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False, blank=True)
    watchlist = models.ManyToManyField(
        Movie, 
        related_name='watchlisted_by', 
        blank=True,
        through='WatchlistEntry' 
    )    
    def __str__(self):
        return f"Profile of {self.user.username}"

class WatchlistEntry(models.Model):
    profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='watchlist_entries')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_movie_rating(sender, instance, **kwargs):
    movie = instance.movie
    avg = movie.reviews.aggregate(Avg('rating'))['rating__avg']
    movie.rating = avg if avg is not None else 0.0
    movie.save()