from django.contrib import admin
from django_msteams_notify.models import TeamsNotification

@admin.register(TeamsNotification)
class TeamsNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "status", "sent_at")
    list_filter = ("status", "sent_at")
    search_fields = ("message",)
