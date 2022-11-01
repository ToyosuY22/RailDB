from django.views import generic


class SearchOperatorView(generic.TemplateView):
    template_name = 'library/database/search_operator.html'


class SearchLineView(generic.TemplateView):
    template_name = 'library/database/search_line.html'


class SearchStationView(generic.TemplateView):
    template_name = 'library/database/search_station.html'
