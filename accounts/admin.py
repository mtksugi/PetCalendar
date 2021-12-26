from django.contrib import admin

from accounts.models import Pets, Users, UserActivateTokens
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportMixin

class PetsResource(resources.ModelResource):
    class Meta:
        model = Pets

@admin.register(Pets)
class PetsAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = PetsResource

class UsersResource(resources.ModelResource):
    class Meta:
        model = Users

@admin.register(Users)
class PetsAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = UsersResource

admin.site.register([UserActivateTokens, ])


