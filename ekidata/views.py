from django.views import generic

from ekidata.models import Join, Line


class DetailLineView(generic.DetailView):
    template_name = 'ekidata/detail_line.html'
    model = Line

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        station_list = []

        for station in self.object.station_set.all():
            station_list.append({
                'station': station,
                'join_next_list': [
                    join.station_2 for join in Join.objects.filter(
                        line=self.object, station_1=station
                    )],
                'join_prev_list': [
                    join.station_1 for join in Join.objects.filter(
                        line=self.object, station_2=station
                    )],
            })

        context['station_list'] = station_list

        return context
