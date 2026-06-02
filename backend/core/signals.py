from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal handler for user creation"""
    if created:
        # Perform any necessary initialization here
        pass
