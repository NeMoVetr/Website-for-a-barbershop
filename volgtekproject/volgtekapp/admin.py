from django.contrib import admin

from .models import Client, Employee, Hall, Service, Visit, ServiceHall


# Register your models here.

class ClientAdmin(admin.ModelAdmin):
    # Указываем поля, которые будут отображаться в списке
    list_display = ('user', 'phone_number', 'date_of_birth', 'gender')

    # Поиск по имени пользователя и email через связь с моделью User
    search_fields = ('user__username', 'user__email')

    # Фильтрация по полу
    list_filter = ('gender',)


# Регистрация модели Employee в админке
class EmployeeAdmin(admin.ModelAdmin):
    # Указываем поля, которые будут отображаться в списке
    list_display = ('user', 'phone_number', 'position')

    # Поиск по имени пользователя и email через связь с моделью User
    search_fields = ('user__username', 'user__email')

    # Фильтрация по должности
    list_filter = ('position',)


# Регистрация модели Hall в админке
class HallAdmin(admin.ModelAdmin):
    # Указываем поля, которые будут отображаться в списке
    list_display = ('name', 'location', 'capacity', 'start_time', 'end_time')

    # Поиск по названию зала и местоположению
    search_fields = ('name', 'location')


# Регистрация модели Service в админке
class ServiceAdmin(admin.ModelAdmin):
    # Указываем поля, которые будут отображаться в списке
    list_display = ('name', 'description', 'price')

    # Поиск по имени и описанию услуги
    search_fields = ('name', 'description')

    # Фильтрация по цене
    list_filter = ('price',)

    # Возможность редактировать цену прямо в списке
    list_editable = ('price',)


# Регистрация модели Visit в админке
class VisitAdmin(admin.ModelAdmin):
    # Указываем поля, которые будут отображаться в списке
    list_display = ('client', 'employee', 'service', 'date', 'status')

    # Поиск по имени клиента, сотрудника, названию услуги и зала
    search_fields = ('client__user__username', 'employee__user__username', 'service__name', 'employee__halls__name')

    # Фильтрация по статусу и времени визита
    list_filter = ('status', 'date')


# Регистрация модели ServiceHall в админке
class ServiceHallAdmin(admin.ModelAdmin):
    list_display = ['service', 'hall']


# Регистрация моделей с соответствующими настройками админки
admin.site.register(Client, ClientAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Hall, HallAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(ServiceHall, ServiceHallAdmin)
