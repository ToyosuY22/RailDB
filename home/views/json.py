"""datatable 向け API
"""

from django.contrib.auth import get_user_model
from django.contrib.auth import mixins as auth_mixins
from django_datatables_view.base_datatable_view import BaseDatatableView


class UserAPI(
        auth_mixins.PermissionRequiredMixin, BaseDatatableView):
    """ユーザー管理
    """
    permission_required = 'home.raildb_manage_user'
    raise_exception = True
    model = get_user_model()
    columns = [
        'email', 'display_name', 'is_active', 'is_staff', 'is_superuser', 'id'
    ]
    max_display_length = 500
