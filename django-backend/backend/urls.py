# backend/urls.py

from django.contrib import admin
from django.urls import path, include   # import include!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('crawler.urls')),  # add this line
]
