from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.shortcuts import get_object_or_404
from home.models import EmailToken


class CheckEmailTokenMixin:
    """Eメールトークンの有効性を判定

    Note:
        - URL で email_token_id を渡すこと
        - class で email_token_id を渡すこと (e.g., 'signup')
    """
    email_token_kind = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # email_token_kind が与えらていない場合は error
        if not self.email_token_kind:
            raise ImproperlyConfigured('Please assign email_token_kind.')

        # Eメールトークンを取得
        email_token = get_object_or_404(
            EmailToken, id=kwargs.get('email_token_id')
        )

        # 有効性を判定
        if email_token.validate(self.email_token_kind):
            self.email_token = email_token
        else:
            # Eメールトークンが見つかっても無効だった場合は 404
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Eメールトークンを辞書に追加
        context.update({'email_token': self.email_token})
        return context


class SuperUserOnlyMixin(UserPassesTestMixin):
    """システム管理者のみアクセス可能

    違反した場合は 403
    """
    raise_exception = True

    def test_func(self):
        # システム管理者のみアクセス可能
        return self.request.user.is_authenticated \
            and self.request.user.is_superuser
