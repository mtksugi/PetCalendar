from django.shortcuts import render
from django.views.generic.base import TemplateView, RedirectView
from django.urls import reverse_lazy
import calendar, datetime

class HomeView(TemplateView):
    template_name = 'pet_calendar/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = kwargs.get('year')
        month = kwargs.get('month')
        mr = calendar.monthrange(year, month)   # return (weekday of first, days in month) first=from monday
        context['first_weekday'] = mr[0]
        context['first_weekday_range'] = list(range(0,mr[0])) # template側でforloopするので、rangeで渡す
        context['days_in_month'] = list(range(1,mr[1]+1))
        return context

class TodayView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        year = datetime.date.today().year
        month = datetime.date.today().month
        return reverse_lazy('pet_calendar:home', kwargs={'year':year, 'month':month})
