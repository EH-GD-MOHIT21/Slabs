from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_staffuser(self, username, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.staff = True
        user.superuser = True
        user.save(using=self._db)
        return user



class User(AbstractUser):
    first_name = models.CharField(
        max_length=20
    )

    last_name = models.CharField(
        max_length=20
    )

    username = models.CharField(
        max_length=20,
        unique=True
    )

    email = models.EmailField(
        max_length=50
    )

    country = models.CharField(
        max_length=50
    )

    staff = models.BooleanField(
        'Staff_status',
        default=False
    )

    superuser = models.BooleanField(
        'super_user_status',
        default=False
    )

    profile_image = models.FileField(
        upload_to='others',
        null=True,
        blank=True
    )

    correct_submissions = models.IntegerField(
        default=0
    )

    incorrect_submissions = models.IntegerField(
        default=0
    )

    objects = UserManager()

    @property
    def is_adult(self):
        return self.adult

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_superuser(self):
        return self.superuser