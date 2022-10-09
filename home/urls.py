from django.urls import path

from home import views

app_name = 'home'


urlpatterns = [
    # views/base.py
    path(
        '',
        views.base.IndexView.as_view(),
        name='index'
    ),
    # views/auth.py
    path(
        'auth/signin',
        views.auth.SigninView.as_view(),
        name='auth_signin'
    ),
    path(
        'auth/signup_email',
        views.auth.SignupEmailView.as_view(),
        name='auth_signup_email'
    ),
    path(
        'auth/signup/<uuid:email_token_id>',
        views.auth.SignupView.as_view(),
        name='auth_signup'
    ),
    path(
        'auth/signout',
        views.auth.SignoutView.as_view(),
        name='auth_signout'
    ),
    path(
        'auth/password_reset_email',
        views.auth.PasswordResetEmailView.as_view(),
        name='auth_password_reset_email'
    ),
    path(
        'auth/password_reset/<uuid:email_token_id>',
        views.auth.PasswordResetView.as_view(),
        name='auth_password_reset'
    ),
    # views/profile.py
    path(
        'profile',
        views.profile.ProfileView.as_view(),
        name='profile'
    ),
    path(
        'profile/email_update_email',
        views.profile.EmailUpdateEmailView.as_view(),
        name='profile_email_update_email'
    ),
    path(
        'profile/email_update/<uuid:email_token_id>',
        views.profile.EmailUpdateView.as_view(),
        name='profile_email_update'
    ),
    path(
        'profile/display_name_update',
        views.profile.DisplayNameUpdateView.as_view(),
        name='profile_display_name_update'
    ),
    path(
        'profile/password_update',
        views.profile.PasswordUpdateView.as_view(),
        name='profile_password_update'
    ),
    path(
        'profile/user_delete',
        views.profile.UserDeleteView.as_view(),
        name='profile_user_delete'
    ),
    # views/user.py
    path(
        'user/list',
        views.user.ListView.as_view(),
        name='user_list'
    ),
    path(
        'user/update/<uuid:pk>',
        views.user.UpdateView.as_view(),
        name='user_update'
    ),
    path(
        'user/delete/<uuid:pk>',
        views.user.DeleteView.as_view(),
        name='user_delete'
    ),
    # views/permission.py
    path(
        'permission/management',
        views.permission.ManagementView.as_view(),
        name='permission_management'
    ),
    path(
        'permission/staff_register',
        views.permission.StaffRegisterView.as_view(),
        name='permission_register_staff'
    ),
    path(
        'permission/staff_unregister/<uuid:pk>',
        views.permission.StaffUnregisterView.as_view(),
        name='permission_unregister_staff'
    ),
    path(
        'permission/group_create',
        views.permission.GroupCreateView.as_view(),
        name='permission_create_group'
    ),
    path(
        'permission/group_update/<int:pk>',
        views.permission.GroupUpdateView.as_view(),
        name='permission_update_group'
    ),
    path(
        'permission/group_delete/<int:pk>',
        views.permission.GroupDeleteView.as_view(),
        name='permission_delete_group'
    ),
    # views/news.py
    path(
        'news/list',
        views.news.ListView.as_view(),
        name='news_list'
    ),
    path(
        'news/create',
        views.news.CreateView.as_view(),
        name='news_create'
    ),
    path(
        'news/update/<uuid:pk>',
        views.news.UpdateView.as_view(),
        name='news_update'
    ),
    path(
        'news/delete/<uuid:pk>',
        views.news.DeleteView.as_view(),
        name='news_delete'
    ),
    path(
        'news/detail/<uuid:pk>',
        views.news.DetailView.as_view(),
        name='news_detail'
    ),
    # json.py
    path(
        'json/user',
        views.json.UserAPI.as_view(),
        name='json_user'
    ),
]
