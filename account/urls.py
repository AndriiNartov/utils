from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import LoginUserView,\
    MainCompanyCreateView,\
    MainCompanyDetailView,\
    RegisterUserView,\
    RegisterUserByInvitationView, \
    MainCompanyManageView



urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('register/<uuid:invitation_link>/', RegisterUserByInvitationView.as_view(), name='register_by_invite'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('company/create/', MainCompanyCreateView.as_view(), name='create_company'),
    path('company/<int:pk>/', MainCompanyDetailView.as_view(), name='company_detail'),
    path('company/manage/', MainCompanyManageView.as_view(), name='company_manage'),
]