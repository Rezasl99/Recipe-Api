# database models


from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class Usermanager(BaseUserManager):
    def create_user(self,email, password=None, **extra_fields):
        # Creating normal user
        if not email:
            raise ValueError('Enter your email address please!!')
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self,email, password):
        # Super user creation
        user = self.create_user(email, password)
        user.is_staff= True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(max_length=254, unique = True)
    name = models.CharField(max_length=254)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = Usermanager()
    USERNAME_FIELD = 'email'