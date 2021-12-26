from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('regist_user/', views.RegistUserView.as_view(), name='regist_user'),
    path('user_login/', views.UserLoginView.as_view(), name='user_login'),
    path('user_logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('success_regist/', views.SuccessRegistView.as_view() ,name='success_regist'),
    path('activate_user/<uuid:token>', views.ActivateUserView.as_view(), name='activate_user'),
    path('forgot_password/', views.ForgotPasswordView.as_view() ,name='forgot_password'),
    path('sendmail_reset_password/', views.SendmailResetPasswordView.as_view() ,name='sendmail_reset_password'),
    path('reset_password/<uuid:token>', views.ResetPasswordView.as_view(), name='reset_password'),
    path('update_user/<int:pk>', views.UpdateUserView.as_view(), name='update_user'),
    path('list_pet/', views.ListPetView.as_view(), name='list_pet'),
    path('regist_pet/', views.RegistPetView.as_view(), name='regist_pet'),
    path('update_pet/<int:pk>', views.UpdatePetView.as_view(), name='update_pet'),
    path('delete_pet/<int:pk>', views.DeletePetView.as_view(), name='delete_pet'),
    path('search_address_by_postal_code/', views.search_address_by_postal_code, name='search_address_by_postal_code'),
]

