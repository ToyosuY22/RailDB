"""datatable 向け API
"""

from django.contrib.auth import get_user_model
from django_datatables_view.base_datatable_view import BaseDatatableView

from raildb.mixins import SuperUserOnlyMixin


class UserAPI(SuperUserOnlyMixin, BaseDatatableView):
    """ユーザー管理
    """
    model = get_user_model()
    columns = [
        'email', 'display_name', 'is_active', 'is_superuser', 'id'
    ]
    max_display_length = 500
