from django.urls import path
from . import views
app_name = 'pet_calendar'

urlpatterns = [
    path('home/', views.TodayView.as_view(), name='home'),
    path('home/<int:year>/<int:month>', views.HomeView.as_view(), name='home'),
]
