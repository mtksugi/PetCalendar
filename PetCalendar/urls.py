from django.contrib import admin
from django.urls import path, include
from accounts.views import page_not_found, server_error

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pet_calendar/', include('pet_calendar.urls')),
    path('accounts/', include('accounts.urls')),
]

handler404 = page_not_found
handler500 = server_error
