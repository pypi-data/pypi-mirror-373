from django.apps import AppConfig


class NotifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_msteams_notify'

    def ready(self):
       import django_msteams_notify.signals 


