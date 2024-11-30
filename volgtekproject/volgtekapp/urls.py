from django.urls import path

from .views import index, registration_client, registration_employee, client_update, employee_update, client_profile, \
    employee_profile, hall_add, hall_show, hall_delete, hall_update, service_add, service_show, service_delete, \
    service_update, book_visit, visit_confirmation, visit_show_employee, visit_show_client, visit_update_client, \
    visit_delete_client, employee_delete, employee_show, visit_show_admin, get_available_time

urlpatterns = [
    path('', index, name='index'),

    # Регистрация клиентов и сотрудников
    path('registration/client/', registration_client, name='registration_client'),
    path('registration/employee/', registration_employee, name='registration_employee'),

    # Обновление профиля клиента и сотрудника
    path('client/update/', client_update, name='client_update'),
    path('employee/update/<int:employee_id>/', employee_update, name='employee_update'),

    # Профили клиента и сотрудника
    path('client/profile/', client_profile, name='client_profile'),
    path('employee/profile/', employee_profile, name='employee_profile'),

    # Управление сотрудниками
    path('employee/delete/<int:employee_id>/', employee_delete, name='employee_delete'),
    path('employee/show/', employee_show, name='employee_show'),

    # Управление залами
    path('hall/add/', hall_add, name='hall_add'),
    path('hall/show/', hall_show, name='hall_show'),
    path('hall/delete/<int:hall_id>/', hall_delete, name='hall_delete'),
    path('hall/update/<int:hall_id>/', hall_update, name='hall_update'),

    # Управление услугами
    path('service/add/', service_add, name='service_add'),
    path('service/show/', service_show, name='service_show'),
    path('service/delete/<int:service_id>/', service_delete, name='service_delete'),
    path('service/update/<int:service_id>/', service_update, name='service_update'),

    # Бронирование посещений
    path('book/visit/', book_visit, name='book_visit'),
    path('visit/confirmation/', visit_confirmation, name='visit_confirmation'),
    path('visit/show/', visit_show_employee, name='visit_show_employee'),
    path('visit/show/client/', visit_show_client, name='visit_show_client'),

    # Обновление и удаление визитов
    path('visit/update/<int:visit_id>/', visit_update_client, name='visit_update_client'),
    path('visit/delete/<int:visit_id>/', visit_delete_client, name='visit_delete_client'),
    path('visit/show/admin/', visit_show_admin, name='visit_show_admin'),
    path('get_available_time/', get_available_time, name='get_available_time'),
]
