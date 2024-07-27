from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import SignUpView, parent_dashboard_view, check_permissions_and_redirect, child_dashboard_view, create_user_account, children_in_family_view, child_pocket_money_view, create_job_card

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('check_permissions_and_redirect/', check_permissions_and_redirect, name='check_permissions_and_redirect'),
    path('parent_dashboard/', parent_dashboard_view, name='parent_dashboard'),
    path('child_dashboard/', child_dashboard_view, name='child_dashboard'),
    path('create_user_account/', create_user_account, name='create_user_account'),
    path('children_in_family/', children_in_family_view, name='children_in_family'),
    path('child/<int:child_id>/', child_pocket_money_view, name='child_pocket_money'),
    path('create_job_card/', create_job_card, name='create_job_card'),
]
