from django.urls import path

from home import views

app_name = 'home'


urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
]
