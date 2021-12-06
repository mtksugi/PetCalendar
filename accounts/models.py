from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Enter Email')
        user = self.model(
            username=username,
            email=email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.model(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, verbose_name="飼い主様の苗字")
    email = models.EmailField(max_length=255, unique=True, verbose_name="メールアドレス")
    is_active = models.BooleanField(default=False, verbose_name="有効")
    is_staff = models.BooleanField(default=False, verbose_name="管理者")
    zip_code = models.CharField(max_length=10, verbose_name="郵便番号")
    address1 = models.CharField(max_length=100, verbose_name="住所")
    address2 = models.CharField(max_length=100, verbose_name="番地")
    address3 = models.CharField(max_length=200, verbose_name="方書")
    phone_number = models.CharField(max_length=20, verbose_name="電話番号")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self) -> str:
        return f'{self.username} : {self.email}'

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'ユーザー'

class Pets(models.Model):
    name = models.CharField(max_length=100, verbose_name="名前")
    gender = models.PositiveIntegerField(verbose_name="性別")
    birthday = models.DateField(verbose_name="誕生日")
    picture = models.FileField(blank=True, upload_to='pet/', verbose_name="画像")
    comment = models.CharField(max_length=1000)
    user = models.ForeignKey(
        'Users', on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'pets'
        verbose_name_plural = 'ペット'
        ordering = ('user',)

    def __str__(self) -> str:
        return f'{self.user.username} : {self.name}'