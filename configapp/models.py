from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.timezone import now
import random


class CustomUserManager(BaseUserManager):
    def create_user(self, username, phone_number=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Username kiritilishi shart")
        if not phone_number:
            raise ValueError("Telefon raqam kiritilishi shart")

        user = self.model(username=username, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_user", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # default False, OTP tasdiqlanmaguncha

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone_number"]

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin


class OTP(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.phone_number} - {self.code}"


class ToDoList(models.Model):
    title = models.CharField(max_length=50)
    bajarilgan = models.BooleanField(default=False)
    done_time = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="todos")

    def __str__(self):
        return f"{self.title} - {self.user.username}"
