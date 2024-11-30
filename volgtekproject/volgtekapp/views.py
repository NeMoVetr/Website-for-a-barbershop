from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages

import pandas as pd
import locale
from datetime import datetime

from .models import Hall, Service, Client, Employee, Visit
from .form import ClientForm, VisitForm, HallForm, ServiceForm, EmployeeForm, ClientRegistrationForm, \
    EmployeeRegistrationForm, ClientUpdateForm
from .decorator import is_client, is_employee

from .time_slots import get_time_slots, update_status_visits

locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')  # Для локализации месяца


# Create your views here.

# Главная страница. Если пользователь не аутентифицирован, перенаправляется на страницу входа.
def index(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Получаем все сотрудников
    employees = Employee.objects.all()

    # Получаем информацию по поисковому запросу (если он есть)
    search_term = request.GET.get('search', '').strip()

    search_term = ' '.join([word.capitalize() for word in search_term.split()])

    if search_term:
        employees = employees.filter(services__name__icontains=search_term) | employees.filter(
            halls__name__icontains=search_term) | employees.filter(user__first_name=search_term) | employees.filter(
            user__last_name=search_term) | employees.filter(position=search_term)

    return render(request, 'index.html', {'employees': employees, 'search_term': search_term})


def registration_client(request):
    if request.method == 'POST':

        form = ClientRegistrationForm(request.POST)  # Форма регистрации пользователя
        client_data_form = ClientForm(request.POST)  # Форма данных клиента

        if form.is_valid() and client_data_form.is_valid():
            user = form.save()  # Сохраняем пользователя
            client = client_data_form.save(commit=False)  # Создаем объект клиента
            client.user = user  # Связываем клиента с пользователем
            client.save()
            return redirect('login')
    else:
        form = ClientRegistrationForm()  # Пустая форма для регистрации
        client_data_form = ClientForm()  # Пустая форма для данных клиента
    return render(request, 'registration/register_client.html', locals())


# Страница регистрации сотрудника. Доступна только для администратора.
@staff_member_required
def registration_employee(request):
    if request.method == 'POST':

        form = EmployeeRegistrationForm(request.POST)  # Форма регистрации сотрудника
        employee_data_form = EmployeeForm(request.POST)  # Форма данных сотрудника

        if form.is_valid() and employee_data_form.is_valid():
            user = form.save()  # Сохраняем пользователя
            employee = employee_data_form.save(commit=False)  # Создаем объект сотрудника
            employee.user = user  # Связываем сотрудника с пользователем
            employee.save()
            employee_data_form.save_m2m()  # Сохраняем ManyToMany поля

            return redirect('index')
    else:
        form = EmployeeRegistrationForm()  # Пустая форма для регистрации сотрудника
        employee_data_form = EmployeeForm()  # Пустая форма для данных сотрудника

    return render(request, 'registration/register_employee.html', locals())


# Страница обновления данных клиента. Доступна только для клиента или администратора.
@user_passes_test(is_client)
def client_update(request):
    client = request.user  # Получаем данные клиента из базы

    try:
        client_form = Client.objects.get(user=client)

    except Client.DoesNotExist:
        client_form = None

    if request.method == 'POST':
        form = ClientUpdateForm(request.POST, instance=client_form)  # Форма обновления клиента
        client_data_form = ClientForm(request.POST, instance=client_form)  # Форма обновления данных клиента

        if form.is_valid() and client_data_form.is_valid():
            client = form.save()  # Сохраняем обновления пользователя
            client_form = client_data_form.save(commit=False)  # Обновляем данные клиента
            client_form.user = client
            client_form.save()

            return redirect('client_profile')
    else:
        form = ClientUpdateForm(instance=client_form)  # Загружаем форму с данными клиента
        client_data_form = ClientForm(instance=client_form) if client_form else None
    return render(request, 'update/client_update.html', locals())


# Страница обновления данных сотрудника. Доступна только для администраторов.
@staff_member_required
def employee_update(request, employee_id):
    employee = Employee.objects.get(id=employee_id)  # Получаем данные сотрудника

    if request.method == 'POST':

        form = EmployeeForm(request.POST, instance=employee)  # Форма обновления данных сотрудника

        if form.is_valid():
            employee = form.save(commit=False)  # Сохраняем объект без коммита
            employee.save()  # Сохраняем обновления сотрудника

            # Теперь сохраняем ManyToMany связи
            form.save_m2m()  # Сохраняем связи ManyToMany (залы и услуги)

        return redirect('employee_show')

    else:
        form = EmployeeForm(initial={
            'phone_number': employee.phone_number,
            'position': employee.position,
            'halls': employee.halls.all(),  # Включаем связанные залы
            'services': employee.services.all(),  # Включаем связанные услуги
        })  # Пустая форма с начальными данными

    return render(request, 'update/employee_update.html', {'form': form})


# Страница профиля клиента. Доступна только для клиента или администратора.
@user_passes_test(is_client)
def client_profile(request):
    client = request.user
    client_form = Client.objects.get(user=client)  # Получаем данные клиента

    return render(request, 'profile/client_profile.html', {'client_form': client_form, 'client': client})


# Страница профиля сотрудника. Доступна только для сотрудника.
@user_passes_test(is_employee)
def employee_profile(request):
    employee = request.user
    employee_form = Employee.objects.get(user=employee)

    return render(request, 'profile/employee_profile.html', locals())


# Страница отображения всех сотрудников. Доступна только для администраторов.
@staff_member_required
def employee_show(request):
    employee = Employee.objects.all()
    return render(request, 'show/employee_show.html', locals())


# Страница удаления сотрудника. Доступна только для администраторов.
@staff_member_required
def employee_delete(request, employee_id):
    employee = Employee.objects.get(id=employee_id)

    if request.method == 'POST':
        employee.delete()  # Удаляем сотрудника и перенаправляем на список сотрудников

        return redirect('employee_show')

    return render(request, 'delete/employee_delete.html', {'employee': employee})


# Страница добавления нового зала. Доступна только для администраторов.
@staff_member_required
def hall_add(request):
    if request.method == 'POST':

        form = HallForm(request.POST)  # Форма добавления нового зала

        if form.is_valid():
            form.save()  # Сохраняем новый зал

            return redirect('hall_show')  # Перенаправляем на страницу отображения залов
    else:
        form = HallForm()  # Пустая форма для добавления зала
    return render(request, 'add/hall_add.html', locals())


# Страница отображения всех залов. Доступна только для авторизованных пользователей.
@login_required
def hall_show(request):
    hall = Hall.objects.all()  # Получаем все залы из базы данных

    return render(request, 'show/hall_show.html', locals())


# Страница удаления зала. Доступна только для администраторов.
@staff_member_required
def hall_delete(request, hall_id):
    hall = Hall.objects.get(id=hall_id)  # Форма для удаления зала

    if request.method == 'POST':
        hall.delete()  # Удаляем зал

        return redirect('hall_show')  # Перенаправляем на страницу отображения залов

    return render(request, 'delete/hall_delete.html', {'hall': hall})


# Страница обновления данных зала. Доступна только для администраторов.
@staff_member_required
def hall_update(request, hall_id):
    hall = Hall.objects.get(id=hall_id)  # Получаем зал по ID

    if request.method == 'POST':

        form = HallForm(request.POST, instance=hall)  # Форма обновления данных зала

        if form.is_valid():
            # Обновляем данные зала

            form.save()  # Сохраняем обновления

            return redirect('hall_show')  # Перенаправляем на страницу отображения залов
    else:
        form = HallForm(instance=hall)  # Подаём форму с уже существующими данными зала

    return render(request, 'update/hall_update.html', {'form': form})


# Страница добавления новой услуги. Доступна только для администраторов.
@staff_member_required
def service_add(request):
    if request.method == 'POST':

        form = ServiceForm(request.POST)  # Форма добавления новой услуги

        if form.is_valid():
            form.save()  # Сохраняем услугу

            return redirect('service_show')  # Перенаправляем на страницу отображения услуг
    else:
        form = ServiceForm()  # Пустая форма для добавления услуги

    return render(request, 'add/service_add.html', {'form': form})


# Страница отображения всех услуг. Доступна только для авторизованных пользователей.
@login_required
def service_show(request):
    service = Service.objects.all()  # Получаем все услуги из базы данных

    return render(request, 'show/service_show.html', locals())


# Страница удаления услуги. Доступна только для администраторов.
@staff_member_required
def service_delete(request, service_id):
    service = Service.objects.get(id=service_id)

    if request.method == 'POST':
        service.delete()  # Удаляем услугу

        return redirect('service_show')  # Перенаправляем на страницу отображения услуг

    return render(request, 'delete/service_delete.html', {'service': service})


# Страница обновления данных услуги. Доступна только для администраторов.
@staff_member_required
def service_update(request, service_id):
    service = Service.objects.get(id=service_id)

    if request.method == 'POST':

        form = ServiceForm(request.POST, instance=service)  # Форма обновления услуги

        if form.is_valid():
            # Обновляем данные услуги

            form.save()  # Сохраняем обновления

            return redirect('service_show')  # Перенаправляем на страницу отображения услуг

    else:
        form = ServiceForm(instance=service)  # Пустая форма для обновления услуги

    return render(request, 'update/service_update.html', {'form': form})


# Страница добавления визита. Доступна только для клиентов.
@user_passes_test(is_client)
def book_visit(request):
    if request.method == 'POST':
        print(request.POST.get('time'))

        form = VisitForm(request.POST)  # Форма добавления визита

        if form.is_valid():
            try:
                visit = form.save(commit=False)
                visit.client = request.user.client
                visit.save()  # Сохраняем визит

                return redirect('visit_confirmation')  # Перенаправляем на страницу подтверждения
            except ValidationError as e:
                # Если возникла ошибка валидации (например, переполнен зал), выводим сообщение об ошибке
                messages.error(request, e)
    else:
        form = VisitForm()  # Пустая форма для добавления визита

    return render(request, 'add/book_visit.html', {'form': form})


# Функция для получения доступных временных слотов. Доступна только для клиентов.
@user_passes_test(is_client)
def get_available_time(request):
    employee_id = request.GET.get('employee')  # id сотрудника
    service_id = request.GET.get('service')  # id услуги
    date_id = request.GET.get('date')  # id даты

    if employee_id and service_id and date_id:
        employee = Employee.objects.get(id=employee_id)  # Получаем сотрудника
        hall = employee.service_halls.filter(service_id=service_id).first().hall  # Получаем зал

        service = Service.objects.get(id=service_id)  # Получаем услугу
        date = datetime.strptime(date_id, '%Y-%m-%d').date()  # Получаем дату

        available_time = get_time_slots(hall, service, date)  # Получаем список доступных временных слотов

        # Возвращаем данные в формате JSON
        return JsonResponse({
            'available_time': available_time,
        })

    return JsonResponse({'available_time': []})


# Страница подтверждения визита. Доступна только для авторизованных пользователей.
@login_required
def visit_confirmation(request):
    return render(request, 'show/visit_confirmation.html')


# Страница отображения всех визитов. Доступна только для сотрудников.
@user_passes_test(is_employee)
def visit_show_employee(request):
    employee = request.user.employee  # Получаем сотрудника

    visits = Visit.objects.filter(employee=employee)  # Фильтруем визиты по сотруднику

    # Создаем DataFrame для отображения визитов
    data_visit = {
        'Имя и фамилия клиента': [visit.client for visit in visits],
        'Номер телефона клиента': [visit.client.phone_number for visit in visits],
        'Название услуги': [visit.service.name for visit in visits],
        'Дата и время начала': [f'{visit.date.strftime('%d %B %Y')} {visit.time}' for visit in visits],
        'Время работы мастера (час)': [visit.service.duration.strftime('%H:%M') for visit in visits],
        'Зал': [visit.hall for visit in visits],
        'Цена (рубли)': [visit.service.price for visit in visits],
        'Статус': [visit.status for visit in visits],
    }

    df_data_visit = pd.DataFrame(data_visit)

    if df_data_visit.empty:
        html_df_data_visit = None  # Если датафрейм пустой
    else:

        # Переводим DataFrame в HTML
        html_df_data_visit = df_data_visit.to_html(classes=["table-bordered", "table-striped", "table-hover"],
                                                   index=False)

    update_status_visits()  # Обновляем статусы

    return render(request, 'show/visit_show_employee.html', {'html_df_data_visit': html_df_data_visit})


# Страница отображения всех визитов. Доступна только для клиентов.
@user_passes_test(is_client)
def visit_show_client(request):
    client = request.user.client  # Получаем клиента

    visits = Visit.objects.filter(client=client)  # Фильтруем визиты по клиенту
    # Создаем DataFrame для отображения визитов
    data_visit = {
        'Имя и фамилия мастера': [visit.employee for visit in visits],
        'Номер телефона мастера': [visit.employee.phone_number for visit in visits],
        'Название услуги': [visit.service for visit in visits],
        'Дата и время начала': [f'{visit.date.strftime('%d %B %Y')} {visit.time}' for visit in visits],
        'Время работы мастера (час)': [visit.service.duration.strftime('%H:%M') for visit in visits],
        'Зал': [visit.hall for visit in visits],
        'Цена (час)': [visit.service.price for visit in visits],
        'Статус': [visit.status for visit in visits],
    }

    df_data_visit = pd.DataFrame(data_visit)

    if df_data_visit.empty:
        html_df_data_visit = None  # Если датафрейм пустой
    else:

        # Переводим DataFrame в HTML
        html_df_data_visit = df_data_visit.to_html(
            classes=["table-bordered", "table-striped", "table-hover", "table-responsive", "w-100"], index=False)

    flag = any(visit.status == 'Запланирована' for visit in visits)

    context = {
        'html_df_data_visit': html_df_data_visit,
        'visits': visits,
        'status_flag': flag
    }

    update_status_visits()  # Обновляем статусы

    return render(request, 'show/visit_show_client.html', context)


# Страница отображения всех визитов. Доступна только для администраторов.
@staff_member_required
def visit_show_admin(request):
    visits = Visit.objects.all()  # Получаем все визиты

    data_visit = {
        'Имя и фамилия клиента': [visit.client for visit in visits],
        'Номер телефона клиента': [visit.client.phone_number for visit in visits],
        'Имя и фамилия мастера': [f"{visit.employee}" for visit in visits],
        'Номер телефона мастера': [visit.employee.phone_number for visit in visits],
        'Название услуги': [visit.service for visit in visits],
        'Дата и время начала': [f'{visit.date.strftime('%d %B %Y')} {visit.time}' for visit in visits],
        'Время работы мастера (час)': [visit.service.duration.strftime('%H:%M') for visit in visits],
        'Зал': [visit.hall for visit in visits],
        'Цена (час)': [visit.service.price for visit in visits],
        'Статус': [visit.status for visit in visits],
    }

    df_data_visit = pd.DataFrame(data_visit)

    if df_data_visit.empty:
        html_df_data_visit = None  # Если датафрейм пустой
    else:
        # Переводим DataFrame в HTML
        html_df_data_visit = df_data_visit.to_html(classes=["table-bordered", "table-striped", "table-hover"],
                                                   index=False)

    update_status_visits()  # Обновляем статусы

    return render(request, 'show/visit_show_admin.html', {'html_df_data_visit': html_df_data_visit})


#  Страница обновления визита. Доступна только для клиентов.
@user_passes_test(is_client)
def visit_update_client(request, visit_id):
    visit = Visit.objects.get(id=visit_id)  # Получаем визит

    if request.method == 'POST':
        form = VisitForm(request.POST, instance=visit)  # Форма обновления визита

        try:
            if form.is_valid():
                form.save()
                return redirect('visit_show_client')

        except ValidationError as e:
            # Если возникла ошибка валидации (например, переполнен зал), выводим сообщение об ошибке
            messages.error(request, e)

    else:
        form = VisitForm(instance=visit)

    return render(request, 'update/visit_update_client.html', {'form': form})


# Страница удаления визита. Доступна только для клиентов.
@user_passes_test(is_client)
def visit_delete_client(request, visit_id):
    visit = Visit.objects.get(id=visit_id)

    if request.method == 'POST':
        visit.delete()
        return redirect('visit_show_client')

    return render(request, 'delete/visit_delete_client.html', {'visit': visit})
