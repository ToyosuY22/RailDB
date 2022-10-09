import datetime
import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.urls import reverse
from django.utils import timezone


class RailDBUserManager(UserManager):
    """username field が存在しないケースに対応

    https://github.com/django/django/blob/f0c06f8ab7904e1fd082f2de57337f6c7e05f177/django/contrib/auth/models.py#L136
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        permissions = [
            ('raildb_manage_users', 'ユーザー管理'),
        ]
        ordering = ['-is_superuser', '-is_staff']

    def __str__(self):
        return f'{self.display_name}（{self.email}）'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    email = models.EmailField(
        verbose_name='Eメールアドレス',
        unique=True,
        help_text='例：tokino_sora@hololive.com'
    )

    display_name = models.CharField(
        verbose_name='表示名',
        max_length=50,
        help_text='例：そらちゃん'
    )

    is_staff = models.BooleanField(
        verbose_name='スタッフ権限',
        default=False
    )

    is_active = models.BooleanField(
        '有効',
        default=True,
        help_text='無効にするとログインできなくなります',
    )

    objects = RailDBUserManager()


class EmailToken(models.Model):
    class Meta:
        verbose_name = 'Eメールトークン'
        verbose_name_plural = 'Eメールトークン'

    def __str__(self):
        return self.email

    @property
    def url(self):
        """Eメールトークンに対応する URL を取得する
        """
        path = {
            self.KindChoices.SIGNUP:
                reverse('home:signup', kwargs={'token_id': self.id}),
            self.KindChoices.PASSWORD_RESET:
                reverse('home:password_reset', kwargs={'token_id': self.id}),
            self.KindChoices.EMAIL_UPDATE:
                reverse('home:update_email', kwargs={'token_id': self.id}),
        }
        return f'{settings.BASE_URL}{path.get(self.kind)}'

    def validate(self, kind):
        """Eメールトークンの有効性を確認

        有効と判定された後、自動的に token が無効化されることはないので注意
        別途無効化処理を行うこと

        Args:
            kind(str): 種別

        Returns:
            bool: 有効なら True
        """
        # 種別確認
        if self.kind != kind:
            return False

        # 現在時刻
        datetime_now = timezone.now()
        # トークンの有効期限
        datetime_exp = self.created_datetime + datetime.timedelta(
            minutes=settings.EMAIL_TOKEN_EXP
        )

        # Eメールトークンが有効期限内、かつ使用済みでない場合は True
        return datetime_now <= datetime_exp and not self.is_used

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    email = models.EmailField(
        verbose_name='Eメールアドレス'
    )

    class KindChoices(models.TextChoices):
        SIGNUP = 'signup', 'アカウント新規登録'
        PASSWORD_RESET = 'password_reset', 'パスワード再設定'
        EMAIL_UPDATE = 'email_update', 'Eメールアドレス変更'

    kind = models.CharField(
        verbose_name='種別',
        max_length=20,
        choices=KindChoices.choices
    )

    created_datetime = models.DateTimeField(
        verbose_name='作成日時',
        auto_now_add=True
    )

    is_used = models.BooleanField(
        verbose_name='使用済み',
        default=False
    )

    created_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='作成ユーザー',
        null=True, blank=True
    )
