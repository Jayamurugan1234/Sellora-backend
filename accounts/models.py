from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        OWNER = "OWNER", "Owner/Seller"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=15, blank=True)
    is_owner_approved = models.BooleanField(default=False)

    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def is_seller(self):
        return self.role == self.Role.OWNER

    def is_site_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self):
        return self.username


class OwnerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="owner_profile")
    store_name = models.CharField(max_length=150)
    gst_number = models.CharField(max_length=20, blank=True)
    store_logo = models.ImageField(upload_to="store_logos/", blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.store_name