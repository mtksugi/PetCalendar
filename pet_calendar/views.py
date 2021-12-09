from django.http import request
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView, RedirectView
from django.urls import reverse_lazy
from accounts.models import Pets
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
        context['pet_list'] = self.create_pet_list(month, mr[1])
        context['year'] = year
        context['month'] = month
        return context
    
    def create_pet_list(self, birth_month, month_range):
        pets = Pets.objects.get_birthday_pet(birth_month)
        print(pets)
        pet_list = [None] * month_range
        for pet in pets:
            pet_list[pet.birthday_day - 1] = pet
        print(pet_list)
        return pet_list


class TodayView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        year = datetime.date.today().year
        month = datetime.date.today().month
        return reverse_lazy('pet_calendar:home', kwargs={'year':year, 'month':month})

class BeforeMonthView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')
        # before month = firstday - 1
        firstday = datetime.date(year, month, 1)
        lastday = firstday + datetime.timedelta(days=-1)
        return reverse_lazy('pet_calendar:home', kwargs={'year':lastday.year, 'month':lastday.month})

class NextMonthView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')
        # next month = lastday + 1
        mr = calendar.monthrange(year,month)
        lastday = datetime.date(year, month, mr[1])
        firstday = lastday + datetime.timedelta(days=1)
        return reverse_lazy('pet_calendar:home', kwargs={'year':firstday.year, 'month':firstday.month})

