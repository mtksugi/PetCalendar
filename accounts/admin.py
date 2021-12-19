from django.contrib import admin

from accounts.models import Pets, Users, UserActivateTokens

admin.site.register([Users, Pets, UserActivateTokens, ])
