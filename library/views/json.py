"""datatable 向け API
"""

from django_datatables_view.base_datatable_view import BaseDatatableView
from library.models import Line, Operator, Station


class OperatorAPI(BaseDatatableView):
    """事業者データ
    """
    model = Operator
    columns = [
        'name', 'name_kana', 'id', 'order'
    ]
    max_display_length = 500

    def get_filter_method(self):
        # 部分一致
        return self.FILTER_ICONTAINS


class LineAPI(BaseDatatableView):
    """路線データ
    """
    model = Line
    columns = [
        'name', 'name_kana', 'operator', 'start', 'via', 'end',
        'area', 'kind', 'status', 'category', 'distance', 'id', 'order'
    ]
    max_display_length = 500

    def get_filter_method(self):
        # 部分一致
        return self.FILTER_ICONTAINS


class StationAPI(BaseDatatableView):
    """駅データ
    """
    model = Station
    columns = [
        'name', 'name_kana', 'line.operator', 'line',
        'distance', 'label', 'id', 'line.order', 'order'
    ]
    max_display_length = 500

    def get_filter_method(self):
        # 部分一致
        return self.FILTER_ICONTAINS
