from rest_framework import serializers
from django_msteams_notify.models import TeamsNotification

class TeamsNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamsNotification
        fields = ['id', 'message', 'status', 'sent_at']
        read_only_fields = ['id', 'sent_at', 'status']

