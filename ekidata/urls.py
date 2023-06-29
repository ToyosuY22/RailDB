from django.urls import path

from ekidata import views

app_name = 'ekidata'


urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        'detail_line/<int:pk>',
        views.DetailLineView.as_view(),
        name='detail_line'
    )
]
