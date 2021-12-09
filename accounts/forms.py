from django import forms
from .models import Pets, Users
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm

class RegistUserForm(forms.ModelForm):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='パスワード再入力', widget=forms.PasswordInput())

    username = forms.CharField(label='飼い主様の苗字')
    zip_code = forms.CharField(label="郵便番号", widget=forms.TextInput(attrs={'placeholder': '1001000'}))
    address1 = forms.CharField(label="住所")
    address2 = forms.CharField(label="番地", required=False)
    address3 = forms.CharField(label="方書", required=False)
    phone_number = forms.CharField(label="電話番号", widget=forms.TextInput(attrs={'placeholder': '090-0000-0000'}))

    field_order = ['username', 'email', 'password', 'confirm_password', 'zip_code', 'address1', 'address2', 'address3', 'phone_number']

    class Meta:
        model = Users
        fields = ['username', 'email', 'password', 'zip_code', 'address1', 'address2', 'address3', 'phone_number']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('パスワードが一致しません')

    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='ログイン状態を保持する', required=False)

class UpdateUserForm(forms.ModelForm):

    class Meta:
        model = Users
        fields = ['username', 'zip_code', 'address1', 'address2', 'address3', 'phone_number']
    
class RegistPetForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label="ペットの名前")
    gender = forms.ChoiceField(label="性別", choices=(
        (1, '男'), (2, '女'), (3, '不明')
    ), widget=forms.RadioSelect)
    birthday = forms.DateField(label="誕生日")
    picture = forms.FileField(required=False, label="写真")
    comment = forms.CharField(max_length=1000, label="アピールコメント", widget=forms.Textarea)

    class Meta:
        model = Pets
        fields = ['name', 'gender', 'birthday', 'picture', 'comment',]
    
    def save(self):
        pet = super().save(commit=False)
        pet.user = self.user
        return pet.save()

