from django.urls import path

from library import views

app_name = 'library'


urlpatterns = [
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
        'database/list_line_relationship',
        views.database.ListLineRelationshipView.as_view(),
        name='database_list_line_relationship'
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
    path(
        'database/create_operator',
        views.database.CreateOperatorView.as_view(),
        name='database_create_operator'
    ),
    path(
        'database/create_line_relationship',
        views.database.CreateLineRelationshipView.as_view(),
        name='database_create_line_relationship'
    ),
    path(
        'database/update_line_relationship/<uuid:pk>',
        views.database.UpdateLineRelationshipView.as_view(),
        name='database_update_line_relationship'
    ),
    path(
        'database/delete_line_relationship/<uuid:pk>',
        views.database.DeleteLineRelationshipView.as_view(),
        name='database_delete_line_relationship'
    ),
    path(
        'database/order_operator/<uuid:pk>',
        views.database.OrderOperatorView.as_view(),
        name='database_order_operator'
    ),
    path(
        'database/update_operator/<uuid:pk>',
        views.database.UpdateOperatorView.as_view(),
        name='database_update_operator'
    ),
    path(
        'database/delete_operator/<uuid:pk>',
        views.database.DeleteOperatorView.as_view(),
        name='database_delete_operator'
    ),
    path(
        'database/create_line/<uuid:operator_pk>',
        views.database.CreateLineView.as_view(),
        name='database_create_line'
    ),
    path(
        'database/order_line/<uuid:pk>',
        views.database.OrderLineView.as_view(),
        name='database_order_line'
    ),
    path(
        'database/update_line/<uuid:pk>',
        views.database.UpdateLineView.as_view(),
        name='database_update_line'
    ),
    path(
        'database/update_line_operator/<uuid:pk>',
        views.database.UpdateLineOperatorView.as_view(),
        name='database_update_line_operator'
    ),
    path(
        'database/delete_line/<uuid:pk>',
        views.database.DeleteLineView.as_view(),
        name='database_delete_line'
    ),
    path(
        'database/create_station/<uuid:line_pk>',
        views.database.CreateStationView.as_view(),
        name='database_create_station'
    ),
    path(
        'database/order_station/<uuid:pk>',
        views.database.OrderStationView.as_view(),
        name='database_order_station'
    ),
    path(
        'database/update_station/<uuid:pk>',
        views.database.UpdateStationView.as_view(),
        name='database_update_station'
    ),
    path(
        'database/update_station_line/<uuid:pk>',
        views.database.UpdateStationLineView.as_view(),
        name='database_update_station_line'
    ),
    path(
        'database/delete_station/<uuid:pk>',
        views.database.DeleteStationView.as_view(),
        name='database_delete_station'
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
    # views/summary.py
    path(
        'summary/area',
        views.summary.AreaView.as_view(),
        name='summary_area'
    ),
    path(
        'summary/kind',
        views.summary.KindView.as_view(),
        name='summary_kind'
    ),
    path(
        'summary/check',
        views.summary.CheckView.as_view(),
        name='summary_check'
    ),
    path(
        'summary/download_csv',
        views.summary.DownloadCSVView.as_view(),
        name='download_csv'
    ),
]
