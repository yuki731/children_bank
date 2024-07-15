from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('children_bank_app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
