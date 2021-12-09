from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .forms import RegistUserForm, UpdateUserForm, UserLoginForm, RegistPetForm
from .models import Pets, Users

class RegistUserView(CreateView):
    template_name = 'accounts/regist_user.html'
    form_class = RegistUserForm

    success_url = reverse_lazy('accounts:success_regist')      

class SuccessRegistView(TemplateView):
    template_name = 'accounts/success_regist.html'

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


def page_not_found(request, exception):
    return render(request, '404.html', status=404)

def server_error(request):
    return render(request, '500.html', status=500)

# class UserView(LoginRequiredMixin, TemplateView):
#     template_name = 'user.html'

#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)