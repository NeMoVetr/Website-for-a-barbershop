from django.contrib import admin

from .models import UserDate, Service, Hall


# Register your models here.

class UserDateAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'date_of_birth', 'address', 'gender', 'interests', 'url_vk', 'blood_type', 'Rh_factor')

    def user_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('hall', 'name', 'description', 'price')

class HallAdmin(admin.ModelAdmin):
    list_display = ('number', )



admin.site.register(UserDate, UserDateAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Hall, HallAdmin)
