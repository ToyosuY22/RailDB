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
    path(
        'password_reset_email',
        views.PasswordResetEmailView.as_view(),
        name='password_reset_email'
    ),
    path(
        'password_reset/<uuid:token_id>',
        views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'profile',
        views.ProfileView.as_view(),
        name='profile'
    ),
    path(
        'update_email_email',
        views.UpdateEmailEmailView.as_view(),
        name='update_email_email'
    ),
    path(
        'update_email/<uuid:token_id>',
        views.UpdateEmailView.as_view(),
        name='update_email'
    ),
    path(
        'update_display_name',
        views.UpdateDisplayNameView.as_view(),
        name='update_display_name'
    ),
    path(
        'update_password',
        views.UpdatePasswordView.as_view(),
        name='update_password'
    ),
    path(
        'delete_user',
        views.DeleteUserView.as_view(),
        name='delete_user'
    ),
]
