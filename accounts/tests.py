from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import response
from django.test import TestCase, Client
from django.urls import reverse
from .models import Users, UserActivateTokens, Pets
from uuid import uuid4
from datetime import datetime, timedelta, timezone, date
from .forms import EmailForm, RegistPetForm, RegistUserForm, ResetPasswordForm
from django.core.files.uploadedfile import SimpleUploadedFile

class SetUpBase(TestCase):

    def setUp(self):
        USERNAME = ["test name", "test name2", "test name3(not active)"]
        EMAIL = ["test@mail.com", "test2@mail.com", "test3@mail.com"]
        PET_NAME = ["test pet name", "test2 pet name", ""]
        GENDER = 1
        BIRTHDAY = datetime.now(tz=timezone.utc) - timedelta(days=365)
        COMMENT = "test comment!!!"
        # PASSWORD = "password1234"
        # -- User 1 --
        user = Users.objects.create(username=USERNAME[0], 
            email=EMAIL[0],
            # password=PASSWORD,
            is_active=True)
        token = UserActivateTokens.objects.create(token=uuid4(),
            expired_at=datetime.now(tz=timezone.utc) + timedelta(days=1),
            user=user)
        pet = Pets.objects.create(name=PET_NAME[0],
            gender=GENDER,
            birthday=BIRTHDAY,
            comment=COMMENT,
            user=user)

        # -- User 2 --
        user2 = Users.objects.create(username=USERNAME[1], 
            email=EMAIL[1],
            # password=PASSWORD,
            is_active=True)
        token2 = UserActivateTokens.objects.create(token=uuid4(),
            expired_at=datetime.now(tz=timezone.utc) + timedelta(days=1),
            user=user2)
        pet2 = Pets.objects.create(name=PET_NAME[1],
            gender=GENDER,
            birthday=BIRTHDAY,
            comment=COMMENT,
            user=user2)

        # -- User 3 --
        user3 = Users.objects.create(username=USERNAME[2], 
            email=EMAIL[2],
            is_active=False)

        # self.client.login(email=EMAIL, password=PASSWORD)
        self.client.force_login(user)
        
        self.user = user
        self.token = token
        self.pet = pet
        self.user2 = user2
        self.token2 = token2
        self.pet2 = pet2
        self.user3 = user3
        return super().setUp()

class AllUrlsResponseTests(SetUpBase, TestCase):
    
    def setUp(self):
        return super().setUp()

    def test_regist_user(self):
        response = self.client.get(reverse('accounts:regist_user'))
        self.assertEqual(response.status_code, 200)

    def test_user_login(self):
        response = self.client.get(reverse('accounts:user_login'))
        self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        response = self.client.get(reverse('accounts:user_logout'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_success_regist(self):
        response = self.client.get(reverse('accounts:success_regist'))
        self.assertEqual(response.status_code, 200)

    def test_activate_user(self):
        response = self.client.get(reverse('accounts:activate_user', kwargs={'token':self.token.token}))
        self.assertEqual(response.status_code, 200)

    def test_forgot_password(self):
        response = self.client.get(reverse('accounts:forgot_password'))
        self.assertEqual(response.status_code, 200)

    def test_sendmail_reset_password(self):
        response = self.client.get(reverse('accounts:sendmail_reset_password'))
        self.assertEqual(response.status_code, 200)

    def test_reset_password(self):
        response = self.client.get(reverse('accounts:reset_password', kwargs={'token':self.token.token}))
        self.assertEqual(response.status_code, 200)

    def test_update_user(self):
        response = self.client.get(reverse('accounts:update_user', kwargs={'pk':self.user.id}))
        self.assertEqual(response.status_code, 200)

    def test_list_pet(self):
        response = self.client.get(reverse('accounts:list_pet'))
        self.assertEqual(response.status_code, 200)

    def test_regist_pet(self):
        response = self.client.get(reverse('accounts:regist_pet'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_update_pet(self):
        response = self.client.get(reverse('accounts:update_pet', kwargs={'pk':self.pet.id}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_pet(self):
        response = self.client.get(reverse('accounts:delete_pet', kwargs={'pk':self.pet.id}), follow=True)
        self.assertEqual(response.status_code, 200)


class LoginRequiredTests(SetUpBase, TestCase):

    def setUp(self):
        return super().setUp()
    
    def test_login_update_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:update_user', kwargs={'pk':self.user.id}))
        self.assertEqual(response.status_code, 200)

    def test_nologin_update_user(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:update_user', kwargs={'pk':self.user.id}), follow=True)
        self.assertRedirects(response, expected_url=reverse('accounts:user_login') + "?next=/accounts/update_user/" + str(self.user.id), 
                status_code=302, target_status_code=200)

    def test_otheruser_update_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:update_user', kwargs={'pk':self.user2.id}))
        self.assertEqual(response.status_code, 404)

    def test_login_list_pet(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:list_pet'))
        self.assertEqual(response.status_code, 200)

    def test_nologin_list_pet(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:list_pet'), follow=True)
        self.assertRedirects(response, expected_url=reverse('accounts:user_login') + "?next=/accounts/list_pet/", 
                status_code=302, target_status_code=200)

    def test_login_regist_pet(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:regist_pet'))
        self.assertEqual(response.status_code, 200)

    def test_nologin_regist_pet(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:regist_pet'), follow=True)
        self.assertRedirects(response, expected_url=reverse('accounts:user_login') + "?next=/accounts/regist_pet/", 
                status_code=302, target_status_code=200)

    def test_login_update_pet(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:update_pet', kwargs={'pk':self.pet.id}))
        self.assertEqual(response.status_code, 200)

    def test_nologin_update_pet(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:update_pet', kwargs={'pk':self.pet.id}), follow=True)
        self.assertRedirects(response, expected_url=reverse('accounts:user_login') + "?next=/accounts/update_pet/" + str(self.pet.id), 
                status_code=302, target_status_code=200)

    def test_otheruser_update_pet(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:update_pet', kwargs={'pk':self.pet2.id}))
        self.assertEqual(response.status_code, 404)

    def test_login_delete_pet(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:delete_pet', kwargs={'pk':self.pet.id}))
        self.assertEqual(response.status_code, 200)

    def test_nologin_delete_pet(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:delete_pet', kwargs={'pk':self.pet.id}), follow=True)
        self.assertRedirects(response, expected_url=reverse('accounts:user_login') + "?next=/accounts/delete_pet/" + str(self.pet.id), 
                status_code=302, target_status_code=200)

    def test_otheruser_delete_pet(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:delete_pet', kwargs={'pk':self.pet2.id}))
        self.assertEqual(response.status_code, 404)

class FormUnitTest(SetUpBase, TestCase):
    def setUp(self):
        userData = {
            'username':'会員　タロウ',
            'email':'user@mail.com',
            'password':'PetCalendar001',
            'confirm_password':'PetCalendar001',
            'zip_code':'1001000',
            'address1':'東京都千代田区１丁目',
            'address2':'１番地',
            'address3':'六本木ヒルズ１階',
            'phone_number':'09012345678'
        }

        emailData = [{'email':'test@mail.com'}, {'email':'user@mail.com'}, {'email':'test3@mail.com'}]

        resetPasswordData = [
            {'password':'PetCalendar001', 'confirm_password':'PetCalendar001'}, 
            {'password':'PetCalendar001', 'confirm_password':'PetCalendar002'}, 
            {'password':'12345678', 'confirm_password':'12345678'}, 
        ]

        petData = {
            'name':'ペット　名前',
            'gender':1,
            'birthday':datetime.now(tz=timezone.utc),
            'comment':'がんばります！'
        }
        petFileData = {
            'picture':SimpleUploadedFile('test.jpg', b"file data", content_type="image/jpeg"),
        }

        self.userData = userData
        self.emailData = emailData
        self.resetPasswordData = resetPasswordData
        self.petData = petData
        self.petFileData = petFileData
        return super().setUp()

    def test_registuserform_valid(self):
        form = RegistUserForm(self.userData)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_registuserform_invalid_password_not_equal_confirm(self):
        userData = self.userData
        userData['confirm_password'] = 'abcd12345'
        form = RegistUserForm(userData)
        self.assertFalse(form.is_valid())
        # self.assertEqual(form.errors['confirm_password'], ['パスワードが一致しません'])

    def test_registuserform_invalid_password_simple(self):
        userData = self.userData
        userData['password'] = userData['confirm_password']  = '1111'
        form = RegistUserForm(userData)
        # with self.assertRaises(ValidationError):
        #     form.save()
        self.assertFalse(form.is_valid())

    def test_emailform_valid(self):
        form = EmailForm(self.emailData[0])
        self.assertTrue(form.is_valid())

    def test_emailform_invalid_not_exists(self):
        form = EmailForm(self.emailData[1])
        self.assertFalse(form.is_valid())
        # self.assertEqual(form.errors['email'], ['入力されたメールアドレスは会員登録されていません'])

    # def test_emailform_invalid_not_active(self):
    #     form = EmailForm(self.emailData[2])
    #     self.assertTrue(Users.objects.filter(email=self.emailData[2]['email']).exists())
    #     self.assertFalse(form.is_valid())

    def test_resetpasswordform_valid(self):
        form = ResetPasswordForm(self.resetPasswordData[0])
        self.assertTrue(form.is_valid())

    def test_resetpasswordform_invalid_not_equal_confirm_password(self):
        form = ResetPasswordForm(self.resetPasswordData[1])
        self.assertFalse(form.is_valid())

    def test_resetpasswordform_invalid_simple_password(self):
        form = ResetPasswordForm(self.resetPasswordData[2])
        form.user = self.user
        # with self.assertRaises(ValidationError):
        #     form.save()
        self.assertFalse(form.is_valid())

    def test_registpetform_valid(self):
        form = RegistPetForm(self.petData, self.petFileData)
        self.assertTrue(form.is_valid())

    def test_registpetform_invalid(self):
        petData = self.petData
        petData['birthday'] = datetime.now(tz=timezone.utc) + timedelta(days=1)
        form = RegistPetForm(self.petData, self.petFileData)
        self.assertFalse(form.is_valid())


class ViewAndIntegrationTests(TestCase):
    def test_registuserview(self):
        username = '会員　タロウ'
        email = 'user@mail.com'
        password = 'PetCalendar001'
        input_data = {
            'username':username,
            'email':email,
            'password':password,
            'confirm_password':password,
        }
        expired_at = datetime.now(tz=timezone.utc) + timedelta(days=1)
        response = self.client.post(reverse('accounts:regist_user'), input_data)
        user = Users.objects.get(id=1)
        token = UserActivateTokens.objects.get(user=user)
        # redirect check
        self.assertEqual(response.status_code, 302)
        # input check user
        self.assertTrue(user.username, username)
        self.assertTrue(user.email, email)
        # input check token
        self.assertTrue(token.expired_at.date(), expired_at.date())

    def test_activateuserview_valid(self):
        self.test_registuserview()
        user = Users.objects.get(id=1)
        token = UserActivateTokens.objects.get(user=user)
        # update check
        self.assertFalse(user.is_active)
        response = self.client.get(reverse('accounts:activate_user', kwargs={'token':token.token}))
        self.assertEqual(response.status_code, 200)
        # page check
        self.assertContains(response, 'ユーザーの本登録が完了しました。')
        user = Users.objects.get(id=1)
        # update check
        self.assertTrue(user.is_active)

    def test_activateuserview_past_token(self):
        self.test_registuserview()
        user = Users.objects.get(id=1)
        token = UserActivateTokens.objects.get(user=user)
        UserActivateTokens.objects.filter(user=user).update(
            expired_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
        )
        response = self.client.get(reverse('accounts:activate_user', kwargs={'token':token.token}))
        self.assertEqual(response.status_code, 200)
        # error page check
        self.assertContains(response, 'URLに誤りがあるか、URLの有効期限が切れています。')

    def test_activateuserview_invalid_token(self):
        response = self.client.get(reverse('accounts:activate_user', kwargs={'token':uuid4()}))
        self.assertEqual(response.status_code, 200)
        # error page check
        self.assertContains(response, 'URLに誤りがあるか、URLの有効期限が切れています。')

    def test_forgotpasswordview(self):
        email = 'user@mail.com'
        user = Users.objects.create(username='test name', 
            email=email,
            password='PetCalendar001',
            is_active=True)
        input_data = {
            'email':email,
        }
        expired_at = datetime.now(tz=timezone.utc) + timedelta(days=1)
        response = self.client.post(reverse('accounts:forgot_password'), input_data)
        user = Users.objects.get(id=1)
        token = UserActivateTokens.objects.get(user=user)
        # redirect check
        self.assertEqual(response.status_code, 302)
        # input check token
        self.assertTrue(token.expired_at.date(), expired_at.date())

    def test_resetpasswordview_get_valid(self):
        self.test_forgotpasswordview()
        user = Users.objects.get(id=1)
        token = UserActivateTokens.objects.get(user=user)
        response = self.client.get(reverse('accounts:reset_password', kwargs={'token':token.token}))
        self.assertEqual(response.status_code, 200)
        # page check
        self.assertContains(response, 'パスワードを設定する')

    def test_resetpasswordview_get_past_token(self):
        self.test_forgotpasswordview()
        user = Users.objects.get(id=1)
        token = UserActivateTokens.objects.get(user=user)
        UserActivateTokens.objects.filter(user=user).update(
            expired_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
        )
        response = self.client.get(reverse('accounts:reset_password', kwargs={'token':token.token}))
        self.assertEqual(response.status_code, 200)
        # page check
        self.assertContains(response, 'URLに誤りがあるか、URLの有効期限が切れています。')

    def test_resetpasswordview_get_invalid_token(self):
        response = self.client.get(reverse('accounts:reset_password', kwargs={'token':uuid4()}))
        self.assertEqual(response.status_code, 200)
        # page check
        self.assertContains(response, 'URLに誤りがあるか、URLの有効期限が切れています。')

    def test_resetpasswordview_post_valid(self):
        password = 'resetpasswordview1234'
        self.test_forgotpasswordview()
        user = Users.objects.get(id=1)
        token = UserActivateTokens.objects.get(user=user)
        input_data = {
            'password':password,
            'confirm_password':password,
            'token':token.token
        }
        response = self.client.post(reverse('accounts:reset_password', kwargs={'token':token.token}), input_data)
        # print(response.content.decode('utf-8'))
        # redirect check
        self.assertEqual(response.status_code, 302)
        # login check
        self.assertTrue(self.client.login(username=user.email, password=password))
    
    def test_from_past_token_to_resetpassword(self):
        # no activate, past token
        self.test_activateuserview_past_token()
        user = Users.objects.get(id=1)
        self.assertFalse(user.is_active)
        # request forgot password
        response = self.client.post(reverse('accounts:forgot_password'), {'email':user.email,})
        self.assertEqual(response.status_code, 302)
        # reset password
        token = UserActivateTokens.objects.filter(user=user, expired_at__gte=datetime.now(tz=timezone.utc)).first()
        password = 'test_from_past_token_to_resetpassword1234'
        input_data = {
            'password':password,
            'confirm_password':password,
            'token':token.token
        }
        response = self.client.post(reverse('accounts:reset_password', kwargs={'token':token.token}), input_data)
        self.assertEqual(response.status_code, 302)
        user = Users.objects.get(id=1)
        # is_active
        self.assertTrue(user.is_active)
        # login check
        self.assertTrue(self.client.login(username=user.email, password=password))

    def test_updateuserview_valid(self):
        self.test_activateuserview_valid()
        username = '会員　タロウ　修正'
        input_data = {
            'username':username,
        }
        user = Users.objects.get(id=1)
        response = self.client.post(reverse('accounts:update_user', kwargs={'pk':user.id}), input_data, follow=True)
        # loginrequiredのため、user_loginからのリダイレクトになる
        self.assertRedirects(response, expected_url=reverse('accounts:user_login') + "?next=/accounts/update_user/" + str(user.id), 
                status_code=302, target_status_code=200)
        user = Users.objects.get(id=1)
        self.assertTrue(user.username, username)

    def test_registpetview_valid(self):
        # pet input data
        name = 'ペット　名前'
        gender = 2
        birthday = datetime.now(tz=timezone.utc) - timedelta(days=1000)
        comment = 'コメント\nコメント'
        input_data = {
            'name':name,
            'gender':gender,
            'birthday':birthday.date(),
            'comment':comment,
            'picture':SimpleUploadedFile('test.jpg', b"file data", content_type="image/jpeg"),
        }
        # user data
        email = 'user@mail.com'
        password = 'PetCalendar001'
        user = Users.objects.create(username='test name', 
            password=password,
            email=email,
            is_active=True)
        user.set_password(password)
        user.save()
        login_result = self.client.login(username=email, password=password)
        self.assertTrue(login_result)
        response = self.client.post(reverse('accounts:regist_pet'), input_data)
        # check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:list_pet'))
        # check input to db
        pet = Pets.objects.get(user=user)
        self.assertEqual(pet.name, name)
        self.assertEqual(pet.gender, gender)
        self.assertEqual(pet.birthday, birthday.date())
        self.assertEqual(pet.comment, comment)
        self.assertRegex(pet.picture.url, '/media/pet/test.*\.jpg$')

    def test_listpetview_valid(self):
        self.test_registpetview_valid()
        user = Users.objects.get(id=1)
        Pets.objects.create(name='ペット テスト2',
            gender=1,
            birthday=date(2021, 10, 1),
            comment='コメント　テスト2',
            user=user)
        user2 = Users.objects.create(username='test name 2', 
            password='passpasspass11111',
            email='test2@mail.com',
            is_active=True)
        Pets.objects.create(name='ユーザー2 ペット',
            gender=1,
            birthday=date(2021, 10, 2),
            comment='ユーザー2 ペット　コメント',
            user=user2)

        pets = Pets.objects.filter(user=user).all()
        pets_other = Pets.objects.filter(user=user2).all()
        self.assertTrue(pets.count(), 2)
        self.assertTrue(pets_other.count(), 1)
        response = self.client.get(reverse('accounts:list_pet'))
        self.assertTrue(response.status_code, 200)
        # print(response.content.decode('utf-8'))
        # check pet count & user1 pet
        self.assertContains(response, '"card mb-3"', 2)
        self.assertContains(response, pets[0].name, 1)
        self.assertContains(response, pets[1].name, 1)
        # check not contain other user
        self.assertNotContains(response, pets_other[0].name)

    def test_updatepetview_valid(self):
        # pet input data
        name = 'ペット　名前　更新'
        gender = 1
        birthday = date(2021, 8, 4)
        picture_file = 'updatetest.jpg'
        comment = 'コメント\nコメント更新'
        input_data = {
            'name':name,
            'gender':gender,
            'birthday':birthday,
            'comment':comment,
            'picture':SimpleUploadedFile(picture_file, b"file data", content_type="image/jpeg"),
        }

        self.test_registpetview_valid()
        pet = Pets.objects.get(id=1)
        # check get contents
        response = self.client.get(reverse('accounts:update_pet', kwargs={'pk':pet.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, pet.name, 1)
        
        response = self.client.post(reverse('accounts:update_pet', kwargs={'pk':pet.id}), input_data)
        # check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:list_pet'))

        # check input to db
        pet = Pets.objects.get(id=1)
        self.assertEqual(pet.name, name)
        self.assertEqual(pet.gender, gender)
        self.assertEqual(pet.birthday, birthday)
        self.assertEqual(pet.comment, comment)
        self.assertRegex(pet.picture.url, '/media/pet/updatetest.*\.jpg$')
        
    def test_deletepetview_valid(self):
        self.test_registpetview_valid()
        pet = Pets.objects.get(id=1)
        # check get contents
        response = self.client.get(reverse('accounts:delete_pet', kwargs={'pk':pet.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, pet.name)
        
        response = self.client.post(reverse('accounts:delete_pet', kwargs={'pk':pet.id}))
        # check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:list_pet'))

        # check delete
        pets = Pets.objects.filter(id=1).all()
        self.assertEqual(pets.count(), 0)
        

