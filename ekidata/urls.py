from django.urls import path

from ekidata import views

app_name = 'ekidata'


urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    )
]
