from logging import exception
from django.core import exceptions
from django.http import response
from django.test import TestCase, testcases
from django.urls import reverse
from django.utils.http import urlencode
from django.urls.exceptions import NoReverseMatch
from accounts.models import Users, Pets
import datetime
from datetime import date
import json

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

class ViewAndIntegrationTests(TestCase):
    def setUp(self):
        self.year = datetime.date.today().year
        self.month = datetime.date.today().month
        self.day = datetime.date.today().day
        return super().setUp()

    def test_homeview_year_month_valid(self):
        test_year = 2021
        test_month = 13
        response = self.client.get(reverse('pet_calendar:home', kwargs={'year':test_year, 'month':test_month}))
        self.assertEqual(response.status_code, 200)
        disp_year_month = f'{self.year}年{self.month}月'
        self.assertContains(response, disp_year_month)

        test_year = 2021
        test_month = 'a'
        with self.assertRaises(NoReverseMatch):
            response = self.client.get(reverse('pet_calendar:home', kwargs={'year':test_year, 'month':test_month}))

        test_year = 'a'
        test_month = 1
        with self.assertRaises(NoReverseMatch):
            response = self.client.get(reverse('pet_calendar:home', kwargs={'year':test_year, 'month':test_month}))

    def test_homeview_year_within_range(self):
        test_year = 1900
        test_month = 1
        response = self.client.get(reverse('pet_calendar:home', kwargs={'year':test_year, 'month':test_month}))
        self.assertEqual(response.status_code, 200)
        disp_year_month = f'{test_year}年{test_month}月'
        self.assertContains(response, disp_year_month)
        test_year = 2100
        test_month = 12
        response = self.client.get(reverse('pet_calendar:home', kwargs={'year':test_year, 'month':test_month}))
        self.assertEqual(response.status_code, 200)
        disp_year_month = f'{test_year}年{test_month}月'
        self.assertContains(response, disp_year_month)

    def test_homeview_year_out_of_range(self):
        test_year = 1899
        test_month = 12
        response = self.client.get(reverse('pet_calendar:home', kwargs={'year':test_year, 'month':test_month}))
        self.assertEqual(response.status_code, 200)
        disp_year_month = f'{self.year}年{self.month}月'
        self.assertContains(response, disp_year_month)
        test_year = 2101
        test_month = 1
        response = self.client.get(reverse('pet_calendar:home', kwargs={'year':test_year, 'month':test_month}))
        self.assertEqual(response.status_code, 200)
        disp_year_month = f'{self.year}年{self.month}月'
        self.assertContains(response, disp_year_month)

    def test_next_month_valid(self):
        test_year = 2021
        test_month = 12
        test_year_next = 2022
        test_month_next = 1
        response = self.client.get(reverse('pet_calendar:next_month', kwargs={'year':test_year, 'month':test_month}), follow=True)
        self.assertRedirects(response, expected_url=reverse('pet_calendar:home', kwargs={'year':test_year_next, 'month':test_month_next}), 
                status_code=302, target_status_code=200)
        disp_year_month = f'{test_year_next}年{test_month_next}月'
        self.assertContains(response, disp_year_month)

    def test_before_month_valid(self):
        test_year = 2021
        test_month = 1
        test_year_next = 2020
        test_month_next = 12
        response = self.client.get(reverse('pet_calendar:before_month', kwargs={'year':test_year, 'month':test_month}), follow=True)
        self.assertRedirects(response, expected_url=reverse('pet_calendar:home', kwargs={'year':test_year_next, 'month':test_month_next}), 
                status_code=302, target_status_code=200)
        disp_year_month = f'{test_year_next}年{test_month_next}月'
        self.assertContains(response, disp_year_month)

    def test_homeview_pets_birthday_and_count(self):
        # user data
        email = 'user@mail.com'
        password = 'PetCalendar001'
        user = Users.objects.create(username='test name', 
            password=password,
            email=email,
            is_active=True)
        # pet data
        pet_name = 'ペット　なまえ'
        birthday_day = 10
        Pets.objects.create(name=pet_name,
            gender=1,
            birthday=date(self.year, self.month, birthday_day),
            comment='コメント　テスト',
            user=user)

        response = self.client.get(reverse('pet_calendar:home', kwargs={'year':self.year, 'month':self.month}))
        # 登録したペットをajax表示させるためのfunction
        self.assertContains(response, f'birthday_pets({birthday_day})')
        # 登録したペットの数の表示...1
        self.assertContains(response, f'<div class="regist-number">(1)</div>')
        # print(response.content.decode('utf-8'))

        # add pet
        Pets.objects.create(name='ペット　テスト２',
            gender=1,
            birthday=date(self.year, self.month, birthday_day),
            comment='コメント　テスト２',
            user=user)
        response = self.client.get(reverse('pet_calendar:home', kwargs={'year':self.year, 'month':self.month}))
        # 登録したペットの数の表示...2
        self.assertContains(response, f'<div class="regist-number">(2)</div>')

    def test_ajax_get_birthday_pets_response_valid(self):
        # user data
        email = 'user@mail.com'
        password = 'PetCalendar001'
        user = Users.objects.create(username='test name', 
            password=password,
            email=email,
            is_active=True)
        # pet data
        pet_name = 'ペット　なまえ'
        birthday_day = 10
        picture_path = 'pet/picture.jpg'
        Pets.objects.create(name=pet_name,
            gender=1,
            birthday=date(self.year, self.month, birthday_day),
            comment='コメント　テスト',
            picture=picture_path,
            user=user)
        
        response = self.client.get(reverse('pet_calendar:ajax_get_birthday_pets') + '?' + urlencode({'day':birthday_day, 'month':self.month}), follow=True)
        self.assertEqual(response.status_code, 200)
        # print(response.content.decode('utf-8'))
        pets_response_data = json.loads(response.content)
        # print(pets_response_data['pets_model'][0]['fields']['name'])
        # print(pets_response_data['pets_model'][0]['pk'])
        # pk = pets_response_data['pets_model'][0]['pk']
        # print(pets_response_data['pets_media_url'][str(pk)])

        self.assertEqual(len(pets_response_data['pets_model']), 1)
        self.assertEqual(pets_response_data['pets_model'][0]['fields']['name'], pet_name)
        pk = pets_response_data['pets_model'][0]['pk']
        pet = Pets.objects.get(pk=pk)
        self.assertEqual(pets_response_data['pets_media_url'][str(pk)], pet.picture.url)

        # add pet data
        pet_name_2 = 'ペット　なまえ２'
        picture_path_2 = 'pet/picture2.jpg'
        Pets.objects.create(name=pet_name_2,
            gender=1,
            birthday=date(self.year, self.month, birthday_day),
            comment='コメント　テスト２',
            picture=picture_path_2,
            user=user)
        
        response = self.client.get(reverse('pet_calendar:ajax_get_birthday_pets') + '?' + urlencode({'day':birthday_day, 'month':self.month}), follow=True)
        self.assertEqual(response.status_code, 200)
        # print(response.content.decode('utf-8'))
        pets_response_data = json.loads(response.content)

        self.assertEqual(len(pets_response_data['pets_model']), 2)
        # first pet
        pk = pets_response_data['pets_model'][0]['pk']
        pet = Pets.objects.get(pk=pk)
        self.assertEqual(pets_response_data['pets_model'][0]['fields']['name'], pet.name)
        self.assertEqual(pets_response_data['pets_media_url'][str(pk)], pet.picture.url)
        # second pet
        pk = pets_response_data['pets_model'][1]['pk']
        pet = Pets.objects.get(pk=pk)
        self.assertEqual(pets_response_data['pets_model'][1]['fields']['name'], pet.name)
        self.assertEqual(pets_response_data['pets_media_url'][str(pk)], pet.picture.url)


'''
- カレンダーの正しさ...1日目の最初の曜日、月の日数
- カードの画像の正しさ（画像リンクが正常）
...これらはseleniumで確認する必要がある. 肉球クリックでペットが正しく表示されるかどうかも
'''
