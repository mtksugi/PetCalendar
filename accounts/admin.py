from django.contrib import admin

from accounts.models import Pets, Users

admin.site.register([Users, Pets])
