from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.serializers import TeamsNotificationSerializer
from django_msteams_notify.utils import send_teams_message

class TeamsNotificationListAPIView(ListAPIView):
    queryset = TeamsNotification.objects.all().order_by('-sent_at')
    serializer_class = TeamsNotificationSerializer

class TeamsNotificationCreateAPIView(CreateAPIView):
    serializer_class = TeamsNotificationSerializer

    def perform_create(self, serializer):
        notification = serializer.save()
        send_teams_message(notification)  

class TeamsNotificationDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = TeamsNotification.objects.all()
    serializer_class = TeamsNotificationSerializer

    def perform_update(self, serializer):
        notification = serializer.save()
        send_teams_message(notification)
