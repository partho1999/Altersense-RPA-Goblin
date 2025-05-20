from django.db import models
from django.utils.safestring import mark_safe

from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER_TYPES = (
        ('Admin', 'Admin'),
        ('Staff', 'Staff'),
    )
    user_type = models.CharField(choices=USER_TYPES, max_length=200, default=USER_TYPES[0],
                                 help_text=mark_safe('<h2 style="color: #008CBA;">Set user type.</h2>'))
    contact = models.CharField(max_length=15, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
