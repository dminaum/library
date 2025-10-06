from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    phone = models.CharField(max_length=32, blank=True, null=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=Q(email__isnull=False) & ~Q(email=""),
                name="uniq_user_email_non_null",
            )
        ]

    def __str__(self):
        return self.get_username()
