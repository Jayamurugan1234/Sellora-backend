from django.db import models
from django.conf import settings


class Feedback(models.Model):
    ROLE_CHOICES = [
        ("OWNER", "Seller"),
        ("CUSTOMER", "Shopper"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    feedback_type = models.CharField(max_length=60)
    rating = models.PositiveSmallIntegerField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role}) — {self.feedback_type}"