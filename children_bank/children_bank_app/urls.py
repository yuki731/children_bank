from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import SignUpView, parent_dashboard_view, check_permissions_and_redirect, child_dashboard_view, create_user_account, children_in_family_view, child_pocket_money_view, create_job_card, delete_job_card, task_view, report_job_view, create_withdrawal_request_view, approval_job_request, approval_withdrawal_request

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
    path('job_card/delete/<int:job_card_id>/', delete_job_card, name='delete_job_card'),
    path('job_card/approval_job/<int:job_report_id>/', approval_job_request, name='approval_job_request'),
    path('job_card/approval_withdrawal/<int:withdrawal_request_id>/', approval_withdrawal_request, name='approval_withdrawal_request'),
    path('task_view/', task_view, name='task_view'),
    path('report_job/<int:job_id>/', report_job_view, name='report_job'),
    path('create_withdrawal_request/', create_withdrawal_request_view, name='create_withdrawal_request'),
]
