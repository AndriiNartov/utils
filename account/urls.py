from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import LoginUserView,\
    MainCompanyCreateView,\
    MainCompanyDetailView,\
    RegisterUserView,\
    RegisterUserByInvitationView, \
    MainCompanyManageView, \
    UnconfirmedUsersView, \
    GroupCreateView, \
    GroupListView, \
    ActiveUsersView, \
    UserUpdateView, \
    GroupUpdateView



urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('register/<uuid:invitation_link>/', RegisterUserByInvitationView.as_view(), name='register_by_invite'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('company/create/', MainCompanyCreateView.as_view(), name='create_company'),
    path('company/<int:pk>/', MainCompanyDetailView.as_view(), name='company_detail'),
    path('company/manage/', MainCompanyManageView.as_view(), name='company_manage'),
    path('company/manage/unconfirmed/', UnconfirmedUsersView.as_view(), name='unconfirmed_users'),
    path('company/manage/active/', ActiveUsersView.as_view(), name='active_users'),
    path('company/manage/groups/create/', GroupCreateView.as_view(), name='group_create'),
    path('company/manage/groups/', GroupListView.as_view(), name='group_all'),
    path('company/manage/groups/<int:pk>/', GroupUpdateView.as_view(), name='group_update'),
    path('user/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
]