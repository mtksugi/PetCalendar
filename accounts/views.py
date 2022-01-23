from django.http.response import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .forms import EmailForm, RegistUserForm, ResetPasswordForm, UpdateUserForm, UserLoginForm, RegistPetForm
from .models import Pets, Users, UserActivateTokens
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import requests
import json
from django.core.mail import send_mail
from django.template.loader import render_to_string

class RegistUserView(CreateView):
    template_name = 'accounts/regist_user.html'
    form_class = RegistUserForm

    success_url = reverse_lazy('accounts:success_regist')      

    def form_valid(self, form):
        http_redirect = super().form_valid(form)
        tokens = UserActivateTokens.objects.create(
            user=form.instance, token=str(uuid4()), expired_at=datetime.now(tz=timezone.utc) + timedelta(days=1)
        )
        # tokens = get_object_or_404(UserActivateTokens, user=form.instance)

        # ---- send mail
        subject = render_to_string('accounts/activate_user_mail_subject.txt')
        message = render_to_string('accounts/activate_user_mail_message.txt', context={
            'username':form.instance.username,
            'url':self.request._current_scheme_host + reverse_lazy('accounts:activate_user', kwargs={'token':tokens.token}),
        })
        try:
            send_mail(
                subject,
                message,
                None,   # from addressはsettings.DEFAULT_FROM_EMAILから取得
                [form.instance.email],
                fail_silently=False,
            )
        except Exception as e:
            print('activate_user send_mail exception', e)

        return http_redirect

class SuccessRegistView(TemplateView):
    template_name = 'accounts/success_regist.html'

class ActivateUserView(TemplateView):
    template_name = 'accounts/activate_user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            UserActivateTokens.objects.activate_user_by_token(kwargs['token'])
        except:
            context['error'] = True
        return context

    # def get(self, request, *args, **kwargs):
    #     try:
    #         UserActivateTokens.objects.activate_user_by_token(kwargs['token'])
    #     except:
    #         message = ''
    #         print(request)
    #     return super().get(request, *args, **kwargs)

class ForgotPasswordView(FormView):
    template_name = 'accounts/forgot_password.html'
    form_class = EmailForm

    def get_success_url(self):
        return reverse_lazy('accounts:sendmail_reset_password')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        if email:
            user = get_object_or_404(Users, email=email)    # 存在チェックはform側で実施済. is_activeはactivateしなかったユーザはリセットパスワードで再アクティブ化するために条件に入れない
            tokens = UserActivateTokens.objects.create(
                user=user, token=str(uuid4()), expired_at=datetime.now(tz=timezone.utc) + timedelta(days=1)
            )
            # ---- send mail
            subject = render_to_string('accounts/reset_password_mail_subject.txt')
            message = render_to_string('accounts/reset_password_mail_message.txt', context={
                'username':user.username,
                'url':self.request._current_scheme_host + reverse_lazy('accounts:reset_password', kwargs={'token':tokens.token}),
            })
            try:
                send_mail(
                    subject,
                    message,
                    None,   # from addressはsettings.DEFAULT_FROM_EMAILから取得
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print('reset_password send_mail exception', e)

        return super().form_valid(form)

class SendmailResetPasswordView(TemplateView):
    template_name = 'accounts/sendmail_reset_password.html'

class ResetPasswordView(SuccessMessageMixin, FormView):
    template_name = 'accounts/reset_password.html'
    form_class = ResetPasswordForm
    # success_message = 'パスワードを更新しました. ログインしてください. '
    success_url = reverse_lazy('accounts:user_login')
    
    def get_success_message(self, cleaned_data):
        return 'パスワードを更新しました. ログインしてください. '

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = context['view'].kwargs['token']
        if not UserActivateTokens.objects.filter(token=token, expired_at__gte=datetime.now(tz=timezone.utc)).exists():
            context['error'] = True
        return context

    def form_valid(self, form):
        token = self.request.POST.get('token')
        tokens = get_object_or_404(UserActivateTokens, token=token) # ここではあえて有効期限はみなくていいかな...
        form.user = tokens.user
        form.save()
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    authentication_form = UserLoginForm

    def form_valid(self, form):
        remember = form.cleaned_data['remember']
        if remember:
            self.request.session.set_expiry(1200000)
        return super().form_valid(form)

class UserLogoutView(LogoutView):
    pass

class UpdateUserView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'accounts/update_user.html'
    model = Users
    form_class = UpdateUserForm
    success_message = '会員情報を更新しました'

    def get(self, request, *args, **kwargs):
        if not request.user.id == kwargs['pk']:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('accounts:update_user', kwargs={'pk':self.object.pk})

class ListPetView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Pets
    template_name = 'accounts/list_pet.html'

    def get_queryset(self):
        query_set = Pets.objects.filter(user = self.request.user)
        return query_set

class RegistPetView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Pets
    template_name = 'accounts/regist_pet.html'
    form_class = RegistPetForm
    success_message = 'ペットを登録しました'

    def get_success_url(self):
        return reverse_lazy('accounts:list_pet')

    def form_valid(self, form):
        form.user = self.request.user
        return super().form_valid(form)

class UpdatePetView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Pets
    template_name = 'accounts/update_pet.html'
    form_class = RegistPetForm
    # success_message = 'ペットを修正しました'

    def get_success_url(self):
        return reverse_lazy('accounts:list_pet')

    def get_success_message(self, cleaned_data):
        return cleaned_data.get('name') + 'ちゃんを修正しました'

    def get(self, request, *args, **kwargs):
        pet = get_object_or_404(Pets, pk=kwargs['pk'])
        if not request.user.id == pet.user.id:
            raise Http404
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.user = self.request.user
        return super().form_valid(form)

class DeletePetView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Pets
    template_name = 'accounts/delete_pet.html'

    def get_success_url(self):
        return reverse_lazy('accounts:list_pet')

    # def get_success_message(self, cleaned_data):  DeleteViewはget_success_messageを使えない（継承していない）
    #     print(self.pet)
    #     return self.pet.name + 'ちゃんを削除しました'

    def get(self, request, *args, **kwargs):
        pet = get_object_or_404(Pets, pk=kwargs['pk'])
        if not request.user.id == pet.user.id:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pet'] = self.object
        return context

# def search_address_by_postal_code(request):

#     url = 'https://maps.googleapis.com/maps/api/geocode/json?address=4440241&language=ja&components=country:JP&key=AIzaSyCe6GOiIEmo1bPA43d5idRcIq4pxCoDtsU'
#     maps_response = requests.get(url)
#     maps_response_json = json.loads(maps_response.text)

#     administrative_area_level = [''] * 5
#     locality = ''
#     sublocality_level = [''] * 5
#     for component in maps_response_json['results'][0]['address_components']:
#         if 'administrative_area_level_1' in component['types']:
#             administrative_area_level[0] = component['long_name']
#         if 'administrative_area_level_2' in component['types']:
#             administrative_area_level[1] = component['long_name']
#         if 'administrative_area_level_3' in component['types']:
#             administrative_area_level[2] = component['long_name']
#         if 'administrative_area_level_4' in component['types']:
#             administrative_area_level[3] = component['long_name']
#         if 'administrative_area_level_5' in component['types']:
#             administrative_area_level[4] = component['long_name']
#         if 'locality' in component['types']:
#             locality = component['long_name']
#         if 'sublocality_level_1' in component['types']:
#             sublocality_level[0] = component['long_name']
#         if 'sublocality_level_2' in component['types']:
#             sublocality_level[1] = component['long_name']
#         if 'sublocality_level_3' in component['types']:
#             sublocality_level[2] = component['long_name']
#         if 'sublocality_level_4' in component['types']:
#             sublocality_level[3] = component['long_name']
#         if 'sublocality_level_5' in component['types']:
#             sublocality_level[4] = component['long_name']

#     address = ''.join(administrative_area_level) + locality + ''.join(sublocality_level)

#     response = json.dumps({'address':address})

#     return HttpResponse(response, content_type='application/json')

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

def server_error(request):
    return render(request, '500.html', status=500)

# class UserView(LoginRequiredMixin, TemplateView):
#     template_name = 'user.html'

#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)