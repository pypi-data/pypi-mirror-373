from django.db.models.signals import post_save
from django.dispatch import receiver
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message

@receiver(post_save, sender=TeamsNotification)
def send_notification_signal(sender, instance, created, **kwargs):
    if created:
        send_teams_message(instance)
