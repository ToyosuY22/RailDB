"""権限管理

システム管理者権限が必要
"""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from home import forms
from raildb.mixins import SuperUserOnlyMixin


class ManagementView(SuperUserOnlyMixin, generic.TemplateView):
    """ユーザー権限管理
    """
    template_name = 'home/permission/management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()

        # スタッフ一覧
        context['staff_list'] = \
            user_model.objects.filter(is_staff=True)

        # グループ一覧
        context['group_list'] = Group.objects.all()

        return context


class StaffRegisterView(SuperUserOnlyMixin, generic.FormView):
    """スタッフ権限付与
    """
    template_name = 'home/permission/staff_register.html'
    form_class = forms.StaffRegisterForm
    success_url = reverse_lazy('home:permission_management')

    def form_valid(self, form):
        # フォームからユーザーの情報を取得
        user = form.cleaned_data.get('user')
        user.is_staff = True
        user.save()

        # メッセージを追加
        messages.success(
            self.request,
            f'{user} さんがスタッフになりました。'
        )

        return super().form_valid(form)


class StaffUnregisterView(SuperUserOnlyMixin,  generic.RedirectView):
    """スタッフ解除
    """
    url = reverse_lazy('home:permission_management')

    def get(self, request, *args, **kwargs):
        # URL からユーザーを取得
        user = get_object_or_404(get_user_model(), id=kwargs.get('pk'))

        # システム管理者の場合は操作不可
        if user.is_superuser:
            messages.error(
                request,
                'システム担当者の権限は解除できません！'
            )
            return super().get(request, *args, **kwargs)

        # スタッフ権限を解除
        user.is_staff = False
        user.save()

        # メッセージを追加
        messages.success(
            request,
            f'{user} のスタッフ権限を解除しました！'
        )

        return super().get(request, *args, **kwargs)


class GroupCreateView(SuperUserOnlyMixin, generic.CreateView):
    """グループ作成
    """
    template_name = 'home/permission/group_create.html'
    form_class = forms.GroupForm
    success_url = reverse_lazy('home:permission_management')
    model = Group

    def form_valid(self, form):
        with transaction.atomic():
            # Group を保存
            response = super().form_valid(form)

            # 権限
            self.object.permissions.set(
                form.cleaned_data.get('permissions')
            )

            # メンバーを追加
            for user in form.cleaned_data.get('user_list'):
                user.groups.add(self.object)
                user.save()

        messages.success(
            self.request,
            f'グループ "{self.object}" を作成しました！'
        )

        return response


class GroupUpdateView(SuperUserOnlyMixin, generic.UpdateView):
    """グループ編集
    """
    template_name = 'home/permission/group_update.html'
    form_class = forms.GroupForm
    success_url = reverse_lazy('home:permission_management')
    model = Group

    def get_initial(self):
        initial = super().get_initial()

        # M2M の initial が自動で設定されないので、ここで設定
        initial.update({
            'permissions': self.object.permissions.all(),
            'user_list': self.object.user_set.all()
        })

        return initial

    def form_valid(self, form):
        with transaction.atomic():
            # Group を保存
            response = super().form_valid(form)

            # 権限
            self.object.permissions.set(
                form.cleaned_data.get('permissions')
            )

            # 一旦メンバーを全解除
            for user in self.object.user_set.all():
                user.groups.remove(self.object)

            # メンバーを追加
            for user in form.cleaned_data.get('user_list'):
                user.groups.add(self.object)
                user.save()

        messages.success(
            self.request,
            f'グループ "{self.object}" を編集しました！'
        )

        return response


class GroupDeleteView(SuperUserOnlyMixin, generic.DeleteView):
    """グループ削除
    """
    template_name = 'home/permission/group_delete.html'
    model = Group
    success_url = reverse_lazy('home:permission_management')

    def form_valid(self, form):
        # 削除
        response = super().form_valid(form)

        # メッセージを追加
        messages.success(
            self.request,
            f'グループ "{self.object.name}" を削除しました！'
        )

        return response
