from django.http import response
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
import datetime

class AllUrlsResponseTests(TestCase):

    def test_home(self):
        response = self.client.get(reverse('pet_calendar:home'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home_202112(self):
        response = self.client.get(reverse('pet_calendar:home', kwargs={'year':2021, 'month':12}))
        self.assertEqual(response.status_code, 200)

    def test_home_today(self):
        year = datetime.date.today().year
        month = datetime.date.today().month
        response = self.client.get(reverse('pet_calendar:home', kwargs={'year':year, 'month':month}))
        self.assertEqual(response.status_code, 200)

    def test_next_month(self):
        year = datetime.date.today().year
        month = datetime.date.today().month
        response = self.client.get(reverse('pet_calendar:next_month', kwargs={'year':year, 'month':month}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_before_month(self):
        year = datetime.date.today().year
        month = datetime.date.today().month
        response = self.client.get(reverse('pet_calendar:before_month', kwargs={'year':year, 'month':month}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_ajax_get_birthday_pets(self):
        month = datetime.date.today().month
        day = datetime.date.today().day
        response = self.client.get(reverse('pet_calendar:ajax_get_birthday_pets') + '?' + urlencode({'day':day, 'month':month}), follow=True)
        self.assertEqual(response.status_code, 200)

