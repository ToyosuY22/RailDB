"""プロフィール

原則: auth.py はログイン前／profile.py はログイン後の処理を記述
"""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from home import forms
from home.models import EmailToken
from raildb.tasks import send_email


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    """プロフィール
    """
    template_name = 'home/profile/profile.html'


class EmailUpdateEmailView(LoginRequiredMixin, generic.CreateView):
    """Eメールアドレス変更（Eメールアドレス入力）
    """
    template_name = 'home/profile/email_update_email.html'
    model = EmailToken
    form_class = forms.EmailTokenUniqueForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        # 種別を登録
        form.instance.kind = EmailToken.KindChoices.EMAIL_UPDATE

        # 作成ユーザーを登録
        form.instance.create_user = self.request.user

        # Eメールトークンを作成
        response = super().form_valid(form)

        # Email を送信
        send_email(
            'Eメールアドレス変更の手続きを続行してください',
            self.object.email,
            'home/mails/profile_email_update_email.txt',
            {'email_token': self.object},
        )

        # 成功メッセージを追加
        messages.warning(
            self.request,
            'Eメールアドレス変更用Eメールを入力した（新しい）アドレスに送信しました。'
            'メールの指示に従い、手続きを続けてください。'
        )

        return response


class EmailUpdateView(LoginRequiredMixin,  generic.RedirectView):
    """Eメールアドレス変更
    """
    url = reverse_lazy('home:profile')

    def get(self, request, *args, **kwargs):
        # Eメールトークンを取得
        email_token = \
            get_object_or_404(EmailToken, id=kwargs.get('email_token_id'))

        # 有効性を判定
        if not email_token.validate(EmailToken.KindChoices.EMAIL_UPDATE):
            raise Http404

        with transaction.atomic():
            # Eメールアドレスを変更
            user = email_token.create_user
            user.email = email_token.email
            user.save()

            # トークンを無効化
            email_token.is_used = True
            email_token.save()

        # Email を送信
        send_email(
            'Eメールアドレスを変更しました',
            email_token.email,
            'home/mails/update_email.txt'
        )

        # メッセージを追加
        messages.success(request, 'Eメールアドレスを変更しました！')

        return super().get(request, *args, **kwargs)


class DisplayNameUpdateView(LoginRequiredMixin, generic.UpdateView):
    """表示名変更
    """
    template_name = 'home/profile/display_name_update.html'
    model = get_user_model()
    fields = ['display_name']
    success_url = reverse_lazy('home:profile')

    def get_object(self, queryset=None):
        # ログインしている自身の User についてのみ変更可能
        return self.request.user

    def form_valid(self, form):
        # 保存
        response = super().form_valid(form)
        # 成功メッセージを追加
        messages.warning(self.request, '表示名を変更しました！')
        return response


class PasswordUpdateView(LoginRequiredMixin, PasswordChangeView):
    """パスワード変更
    """
    template_name = 'home/profile/password_update.html'
    form_class = forms.PasswordUpdateForm
    success_url = reverse_lazy('home:profile')

    def form_valid(self, form):
        # パスワード変更
        response = super().form_valid(form)
        # 成功メッセージを追加
        messages.success(self.request, 'パスワードを変更しました。')
        return response

    def form_invalid(self, form):
        # 両方のパスワードについてエラーを登録
        form.add_error('old_password', ValidationError('', code='invalid'))
        form.add_error('new_password', ValidationError('', code='invalid'))

        return super().form_invalid(form)


class UserDeleteView(LoginRequiredMixin, generic.DeleteView):
    """アカウント削除
    """
    template_name = 'home/profile/user_delete.html'
    model = get_user_model()
    success_url = reverse_lazy('home:index')

    def get_object(self, queryset=None):
        # ログインしている自身の User についてのみ削除可能
        return self.request.user

    def form_valid(self, form):
        # ユーザーを削除
        response = super().form_valid(form)

        # Email を送信
        send_email(
            'アカウントを削除しました',
            self.object.email,
            'home/mails/profile_user_delete.txt'
        )

        # 成功メッセージを追加
        messages.success(self.request, 'アカウントを削除しました。')

        return response
