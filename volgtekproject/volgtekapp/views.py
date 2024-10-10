from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect

import pandas as pd

from .models import UserDate, Service
from .form import UserDateForm, UserRegisterForm, ServiceForm


# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    context_index = specifications(request)
    user_name = { "username": request.user.first_name}
    return render(request, 'index.html', locals())


def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        user_data = UserDateForm(request.POST)
        if user_form.is_valid() and user_data.is_valid():
            user = user_form.save()
            user_data_instance  = user_data.save(commit=False)
            user_data_instance.user = user
            user_data_instance.save()
            return redirect('index')
    else:
        user_form = UserRegisterForm()
        user_data = UserDateForm()
    return render(request, 'registration/register.html', {'user_form': user_form, 'user_data': user_data})


@login_required
def profile(request):
    user = request.user
    user_data = UserDate.objects.get(user=user)
    context_profile = {
        'user': user,
        'user_data': user_data
    }
    return render(request, 'profile.html', context_profile)


@login_required
def specifications(request):
    # Преобразование словарей в DataFrame с двумя столбцами: 'Характеристика' и 'Значение'
    basic_parameters = {
        "Характеристика": ["Бренд", "Вид инструмента", "Питание", "Длина шнура", "Технологии",
                           "Мощность, Вт", "Температурные режимы, °C", "Тип управления",
                           "Диаметр, мм", "Количество режимов нагрева", "Цвет", "Страна"],
        "Значение": ["Promozer", "Плойка", "Сеть", "2,5 м",
                     "Титановое покрытие, Турмалиновое покрытие", "45-65",
                     "180-210", "Механическое", "25", "2", "Черный", "Китай"]
    }

    size_weight_volume = {
        "Характеристика": ["Габариты (ДхШхВ), мм"],
        "Значение": ["370"]
    }

    warranty_expiration_date = {
        "Характеристика": ["Гарантия, мес"],
        "Значение": ["12"]
    }

    package_dimensions = {
        "Характеристика": ["Упаковка", "Вес в упаковке, г"],
        "Значение": ["Коробка", "475"]
    }

    # Преобразуем словари в DataFrame
    df_basic_parameters = pd.DataFrame(basic_parameters).to_html(
        classes=["table-bordered", "table-hover"], index=False, header=False)
    df_size_weight_volume = pd.DataFrame(size_weight_volume).to_html(
        classes=["table-bordered", "table-hover"], index=False, header=False)
    df_warranty_expiration_date = pd.DataFrame(warranty_expiration_date).to_html(
        classes=["table-bordered", "table-hover"], index=False, header=False)
    df_package_dimensions = pd.DataFrame(package_dimensions).to_html(
        classes=["table-bordered", "table-hover"], index=False, header=False)

    # Передача контекста в шаблон
    context_specifications = {
        'df_basic_parameters': df_basic_parameters,
        'df_size_weight_volume': df_size_weight_volume,
        'df_warranty_expiration_date': df_warranty_expiration_date,
        'df_package_dimensions': df_package_dimensions,
    }

    return context_specifications

@login_required
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('services')  # Перенаправляем на страницу со списком услуг
    else:
        form = ServiceForm()
    return render(request, 'create_service.html', {'form': form})

@login_required
def service_list(request):

    services = Service.objects.all()
    return render(request, 'service_list.html', {'services': services})