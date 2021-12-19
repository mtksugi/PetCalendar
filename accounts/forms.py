from django import forms
from .models import Pets, Users
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm

class RegistUserForm(forms.ModelForm):
    email = forms.EmailField(label='メールアドレス', widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirm_password = forms.CharField(label='パスワード再入力', widget=forms.PasswordInput(attrs={'class':'form-control'}))

    username = forms.CharField(label='飼い主様の苗字', widget=forms.TextInput(attrs={'class':'form-control'}))
    zip_code = forms.CharField(label="郵便番号", widget=forms.TextInput(attrs={'placeholder': '1001000', 'class':'form-control'}))
    address1 = forms.CharField(label="住所", widget=forms.TextInput(attrs={'class':'form-control'}))
    address2 = forms.CharField(label="番地", required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    address3 = forms.CharField(label="方書", required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    phone_number = forms.CharField(label="電話番号", widget=forms.TextInput(attrs={'placeholder': '090-0000-0000', 'class':'form-control'}))

    field_order = ['username', 'email', 'password', 'confirm_password', 'zip_code', 'address1', 'address2', 'address3', 'phone_number']

    class Meta:
        model = Users
        fields = ['username', 'email', 'password', 'zip_code', 'address1', 'address2', 'address3', 'phone_number']
    
    def clean_confirm_password(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('パスワードが一致しません')
        return confirm_password

    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス', widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    remember = forms.BooleanField(label='ログイン状態を保持する', required=False, widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))

class UpdateUserForm(forms.ModelForm):

    username = forms.CharField(label='飼い主様の苗字', widget=forms.TextInput(attrs={'class':'form-control'}))
    zip_code = forms.CharField(label="郵便番号", widget=forms.TextInput(attrs={'placeholder': '1001000', 'class':'form-control'}))
    address1 = forms.CharField(label="住所", widget=forms.TextInput(attrs={'class':'form-control'}))
    address2 = forms.CharField(label="番地", required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    address3 = forms.CharField(label="方書", required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    phone_number = forms.CharField(label="電話番号", widget=forms.TextInput(attrs={'placeholder': '090-0000-0000', 'class':'form-control'}))

    class Meta:
        model = Users
        fields = ['username', 'zip_code', 'address1', 'address2', 'address3', 'phone_number']

class EmailForm(forms.Form):
    email = forms.EmailField(label='メールアドレス', widget=forms.EmailInput(attrs={'class':'form-control'}))

    def clean_email(self):
        cleaned_data = super().clean()
        email = cleaned_data['email']
        if not Users.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError('入力されたメールアドレスは会員登録されていません')
        return email

class ResetPasswordForm(forms.ModelForm):

    password = forms.CharField(label='パスワード', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirm_password = forms.CharField(label='パスワード再入力', widget=forms.PasswordInput(attrs={'class':'form-control'}))

    class Meta:
        model = Users
        fields = ['password', ]

    def clean_confirm_password(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('パスワードが一致しません')
        return confirm_password

    def save(self, commit=False):
        user = super().save(commit=False)
        user = self.user
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

class RegistPetForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label="ペットの名前", widget=forms.TextInput(attrs={'class':'form-control'}))
    gender = forms.ChoiceField(label="性別", choices=(
        (1, 'オス'), (2, 'メス'), (3, '不明')
    ), widget=forms.Select(attrs={'class':'form-select'}))
    birthday = forms.DateField(label="誕生日", widget=forms.TextInput(attrs={'type':'date', 'class':'form-control'}))
    picture = forms.FileField(label="写真", widget=forms.FileInput(attrs={'class':'form-control'}))
    comment = forms.CharField(max_length=1000, label="アピールコメント", widget=forms.Textarea(attrs={'class':'form-control','rows':'3'}))

    class Meta:
        model = Pets
        fields = ['name', 'gender', 'birthday', 'picture', 'comment',]
    
    def save(self):
        pet = super().save(commit=False)
        pet.user = self.user
        return pet.save()

