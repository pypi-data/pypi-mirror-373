from django.urls import path
from django_msteams_notify.views import (
    TeamsNotificationListAPIView,
    TeamsNotificationCreateAPIView
)

urlpatterns = [
    path('send-teams/', TeamsNotificationListAPIView.as_view(), name='teamsnotifications-list'),
    path('send-teams/create/', TeamsNotificationCreateAPIView.as_view(), name='teamsnotifications-create'),
]
