"""ユーザー管理

権限 home.raildb_manage_user が必要
"""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from home import forms


class ListView(PermissionRequiredMixin, generic.TemplateView):
    """ユーザー管理

    Datatable を利用しているため、ListView ではなく TemplateView を継承
    """
    template_name = 'home/user/list.html'
    permission_required = 'home.raildb_manage_user'
    raise_exception = True


class UpdateView(PermissionRequiredMixin, generic.UpdateView):
    """ユーザー編集（スタッフ専用）
    """
    template_name = 'home/user/update.html'
    permission_required = 'home.raildb_manage_user'
    raise_exception = True
    model = get_user_model()
    form_class = forms.UpdateUserStaffForm

    def get_success_url(self):
        return reverse(
            'home:user_update', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        # スタッフの場合は拒否
        if self.object.is_staff:
            messages.error(self.request, 'スタッフの情報は編集できません！')
            return redirect('home:user_update', pk=self.object.id)

        # 編集
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request, f'{self.object} さんのユーザー情報を編集しました！')

        return response


class DeleteView(PermissionRequiredMixin, generic.DeleteView):
    """お知らせ削除
    """
    permission_required = 'home.raildb_manage_user'
    raise_exception = True
    template_name = 'home/user/delete.html'
    model = get_user_model()
    success_url = reverse_lazy('home:user_list')

    def form_valid(self, form):
        # スタッフの場合は拒否
        if self.object.is_staff:
            messages.error(self.request, 'スタッフの情報は編集できません！')
            return redirect('home:user_list')
        # 削除
        response = super().form_valid(form)

        # メッセージを追加
        messages.success(
            self.request,
            f'ユーザー "{self.object}" を削除しました！'
        )

        return response
