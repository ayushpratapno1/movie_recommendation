from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls')),  # Main app URLs
    path('users/', include('users.urls')),  # User-related URLs
    path('api/', include('api.urls')),  # API URLs
]
