from django.urls import path

from library import views

app_name = 'library'


urlpatterns = [
    # views/csv.py
    path(
        'csv/upload/<str:mode>',
        views.csv.UploadView.as_view(),
        name='csv_upload'
    ),
    path(
        'csv/download/<str:mode>',
        views.csv.DownloadView.as_view(),
        name='csv_download'
    ),
    # views/database.py
    path(
        'database/search_operator',
        views.database.SearchOperatorView.as_view(),
        name='database_search_operator'
    ),
    path(
        'database/search_line',
        views.database.SearchLineView.as_view(),
        name='database_search_line'
    ),
    path(
        'database/search_station',
        views.database.SearchStationView.as_view(),
        name='database_search_station'
    ),
    path(
        'database/detail_operator/<uuid:pk>',
        views.database.DetailOperatorView.as_view(),
        name='database_detail_operator'
    ),
    path(
        'database/detail_line/<uuid:pk>',
        views.database.DetailLineView.as_view(),
        name='database_detail_line'
    ),
    path(
        'database/detail_station/<uuid:pk>',
        views.database.DetailStationView.as_view(),
        name='database_detail_station'
    ),
    # views/json.py
    path(
        'json/operator',
        views.json.OperatorAPI.as_view(),
        name='json_operator'
    ),
    path(
        'json/line',
        views.json.LineAPI.as_view(),
        name='json_line'
    ),
    path(
        'json/station',
        views.json.StationAPI.as_view(),
        name='json_station'
    ),
]
