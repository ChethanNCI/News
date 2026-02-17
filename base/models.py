from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    # Add related_name attributes to avoid conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions_set",
        blank=True
    )

    def __str__(self):
        return self.username

User = get_user_model()  # Get the custom user model

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_subscribed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Subscribed' if self.is_subscribed else 'Not Subscribed'}"

class Advertisement(models.Model):
    title = models.CharField(max_length=200)
    image_url = models.URLField()
    target_url = models.URLField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title