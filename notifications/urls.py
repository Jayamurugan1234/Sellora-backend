from django.urls import path
from . import views

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notification_list"),
    path("read/<int:notification_id>/", views.MarkAsReadView.as_view(), name="mark_as_read"),
]