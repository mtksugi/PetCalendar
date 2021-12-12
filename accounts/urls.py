from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('regist_user/', views.RegistUserView.as_view(), name='regist_user'),
    path('user_login/', views.UserLoginView.as_view(), name='user_login'),
    path('user_logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('success_regist/', views.SuccessRegistView.as_view() ,name='success_regist'),
    path('update_user/<int:pk>', views.UpdateUserView.as_view(), name='update_user'),
    path('list_pet/', views.ListPetView.as_view(), name='list_pet'),
    path('regist_pet/', views.RegistPetView.as_view(), name='regist_pet'),
    path('update_pet/<int:pk>', views.UpdatePetView.as_view(), name='update_pet'),
    path('delete_pet/<int:pk>', views.DeletePetView.as_view(), name='delete_pet'),
]

