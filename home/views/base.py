"""ホーム画面
"""

from django.views import generic

from home.models import News


class IndexView(generic.TemplateView):
    """ホーム
    """
    template_name = 'home/base/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # お知らせ
        context['news_list'] = News.objects.all()
        return context


class RailMapView(generic.TemplateView):
    """路線図
    """
    template_name = 'home/base/railmap.html'
