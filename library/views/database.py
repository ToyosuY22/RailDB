from django.db.models import Sum
from django.views import generic

from library.models import Line, Operator, Station


class SearchOperatorView(generic.TemplateView):
    template_name = 'library/database/search_operator.html'


class SearchLineView(generic.TemplateView):
    template_name = 'library/database/search_line.html'


class SearchStationView(generic.TemplateView):
    template_name = 'library/database/search_station.html'


class DetailOperatorView(generic.DetailView):
    template_name = 'library/database/detail_operator.html'
    model = Operator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 事業者の情報を取得
        operator = self.object

        # 初期化
        line_list = []

        # 種別／状態／事業ごとに集計
        for kind in Line.KindChoices:
            for status in Line.StatusChoices:
                for category in Line.CategoryChoices:
                    # 路線一覧を取得
                    line_queryset = Line.objects.filter(
                        operator=operator,
                        kind=kind,
                        status=status,
                        category=category
                    )

                    # 該当件数が 1 件以上であれば追加
                    if line_queryset.exists():
                        line_list.append({
                            'kind': kind,
                            'status': status,
                            'category': category,
                            'queryset': line_queryset,
                            'distance_sum': line_queryset.aggregate(
                                Sum('distance'))['distance__sum']
                        })

        # 路線一覧を登録
        context['line_list'] = line_list

        return context


class DetailLineView(generic.DetailView):
    template_name = 'library/database/detail_line.html'
    model = Line

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 駅一覧を登録
        context['object_list'] = [{
            'station': station,
            'gap': self.get_gap(station.order)
        } for station in Station.objects.filter(line=self.object)]

        return context

    def get_gap(self, order):
        if order == 0:
            return None
        else:
            this_station = Station.objects.get(line=self.object, order=order)
            previous_station = \
                Station.objects.get(line=self.object, order=order-1)

            try:
                return this_station.distance - previous_station.distance
            except TypeError:
                # キロ程 None
                return None


class DetailStationView(generic.DetailView):
    template_name = 'library/database/detail_station.html'
    model = Station
