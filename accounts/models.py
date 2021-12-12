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
    zip_code = models.CharField(max_length=10, verbose_name="郵便番号", blank=True)
    address1 = models.CharField(max_length=100, verbose_name="住所", blank=True)
    address2 = models.CharField(max_length=100, verbose_name="番地", blank=True)
    address3 = models.CharField(max_length=200, verbose_name="方書", blank=True)
    phone_number = models.CharField(max_length=20, verbose_name="電話番号", blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self) -> str:
        return f'{self.username} : {self.email}'

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'ユーザー'

class PetsManager(models.Manager):

    def get_birthday_pet(self, month):
        return Pets.objects.filter(birthday_month=month).all()

class Pets(models.Model):
    name = models.CharField(max_length=100, verbose_name="名前")
    gender = models.PositiveIntegerField(verbose_name="性別")
    birthday = models.DateField(verbose_name="誕生日")
    birthday_month = models.PositiveIntegerField(verbose_name="誕生日の月")
    birthday_day = models.PositiveIntegerField(verbose_name="誕生日の日付")
    picture = models.FileField(upload_to='pet/', verbose_name="画像")   # 画像が表示されなければ意味がないので登録必須
    comment = models.CharField(max_length=1000, blank=True)
    user = models.ForeignKey(
        'Users', on_delete=models.CASCADE
    )

    objects = PetsManager()

    class Meta:
        db_table = 'pets'
        verbose_name_plural = 'ペット'
        ordering = ('user',)

    def __str__(self) -> str:
        return f'{self.user.username} : {self.name}'

    def save(self):
        self.birthday_month = self.birthday.month
        self.birthday_day = self.birthday.day
        return super().save()
