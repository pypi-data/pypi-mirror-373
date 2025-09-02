import requests
from django.conf import settings
from django_msteams_notify.models import TeamsNotification

def send_teams_message(notification: TeamsNotification):
    """Send a Teams message and update notification status."""
    webhook_url = getattr(settings, "TEAMS_WEBHOOK_URL", None)

    if not webhook_url:
        notification.status = "failed"
        notification.save(update_fields=["status"])
        return False

    try:
        payload = {"text": notification.message}
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 200:
            notification.status = "sent"
        else:
            notification.status = "failed"

    except Exception:
        notification.status = "failed"

    notification.save(update_fields=["status"])
    return notification.status == "sent"
