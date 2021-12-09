from django.urls import path
from . import views
app_name = 'pet_calendar'

urlpatterns = [
    path('home/', views.TodayView.as_view(), name='home'),
    path('home/<int:year>/<int:month>', views.HomeView.as_view(), name='home'),
    path('next_month/<int:year>/<int:month>', views.NextMonthView.as_view(), name='next_month'),
    path('before_month/<int:year>/<int:month>', views.BeforeMonthView.as_view(), name='before_month'),
    # path('before_month/', views.before, name='before_month'),
]
