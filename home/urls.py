from django.urls import path

from home import views

app_name = 'home'


urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        'signin',
        views.SigninView.as_view(),
        name='signin'
    ),
    path(
        'signup_email',
        views.SignupEmailView.as_view(),
        name='signup_email'
    ),
    path(
        'signup/<uuid:token_id>',
        views.SignupView.as_view(),
        name='signup'
    ),
    path(
        'signout',
        views.SignoutView.as_view(),
        name='signout'
    ),
]
