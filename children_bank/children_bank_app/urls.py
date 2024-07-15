from django.contrib import admin
from django.urls import path
from .views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', SignUpView.as_view(), name='signup'),
]
