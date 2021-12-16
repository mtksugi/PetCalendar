from django.urls import path
from . import views
app_name = 'pet_calendar'

urlpatterns = [
    path('home/', views.TodayView.as_view(), name='home'),
    path('home/<int:year>/<int:month>', views.HomeView.as_view(), name='home'),
    path('next_month/<int:year>/<int:month>', views.NextMonthView.as_view(), name='next_month'),
    path('before_month/<int:year>/<int:month>', views.BeforeMonthView.as_view(), name='before_month'),
    path('day_list/<int:month>/<int:day>', views.DayListView.as_view(), name='day_list'),
    path('ajax_get_birthday_pets/', views.ajax_get_birthday_pets, name='ajax_get_birthday_pets'),
]
