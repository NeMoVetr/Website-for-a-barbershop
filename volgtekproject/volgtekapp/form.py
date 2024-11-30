from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Service, Hall, Client, Employee, Visit
from datetime import datetime, timedelta
from .time_slots import get_time_slots


# Форма для добавления/редактирования зала
class HallForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label='Название зала', )
    description = forms.CharField(max_length=100, label='Описание зала', required=False,
                                  )
    capacity = forms.IntegerField(label='Вместимость зала', )
    location = forms.CharField(max_length=100, label='Местоположение зала',
                               )
    start_time = forms.TimeField(label='Начало работы зала',
                                 widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'))

    end_time = forms.TimeField(label='Конец работы зала',
                               widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'))

    class Meta:
        model = Hall
        fields = ['name', 'description', 'capacity', 'location', 'start_time', 'end_time']
        labels = {
            'name': 'Название зала',
            'description': 'Описание зала',
            'capacity': 'Вместимость зала',
            'location': 'Местоположение зала',
            'start_time': 'Начало работы зала',
            'end_time': 'Конец работы зала',
        }


# Форма для регистрации клиента
class ClientForm(forms.ModelForm):
    username = forms.CharField(label='Логин', max_length=150)
    first_name = forms.CharField(label='Имя', max_length=150)
    last_name = forms.CharField(label='Фамилия', max_length=150)
    email = forms.EmailField(required=True)

    class Meta:
        model = Client
        fields = ['username', 'first_name', 'last_name']
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }


# Форма для добавления/редактирования услуги
class ServiceForm(forms.ModelForm):
    name = forms.CharField(label='Название услуги', )
    description = forms.CharField(label='Описание услуги', )
    price = forms.DecimalField(label='Стоимость', )
    duration = forms.TimeField(label='Продолжительность')

    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration']
        labels = {
            'name': 'Название услуги',
            'description': 'Описание услуги',
            'price': 'Стоимость',
            'duration': 'Продолжительность',

        }


# Форма для добавления/редактирования данных сотрудника
class EmployeeForm(forms.ModelForm):
    phone_number = forms.CharField(label='Номер телефона')
    position = forms.CharField(label='Должность')

    class Meta:
        model = Employee
        fields = ['phone_number', 'position', 'halls', 'services']
        labels = {
            'phone_number': 'Номер телефона',
            'position': 'Должность',
            'halls': 'Залы',
            'services': 'Услуги',
        }


# Форма для создания посещения
class VisitForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), label='Выберете нужного сотрудника',
                                      empty_label="Выберите сотрудника",
                                      widget=forms.Select(attrs={'id': 'id_employee'}))
    service = forms.ModelChoiceField(queryset=Service.objects.all(), label='Выберете нужную услугу',
                                     empty_label="Выберите услугу",
                                     widget=forms.Select(attrs={'id': 'id_service'}))

    date = forms.DateField(label='Дата  посещения',
                           widget=forms.DateInput(
                               attrs={'type': 'date', 'id': 'id_date', 'min': datetime.today().strftime('%Y-%m-%d'),

                                      'max': (datetime.today() + timedelta(days=7)).strftime('%Y-%m-%d')}))

    time = forms.ChoiceField(label='Время посещения', widget=forms.Select(attrs={'id': 'id_time'}))

    class Meta:
        model = Visit
        fields = ['employee', 'service', 'date', 'time']

    # Переопределение волшебного метода для инициализации контейнера класса VisitForm
    def __init__(self, *args, **kwargs):  # args - список аргументов, kwargs - словарь аргументов
        super(VisitForm, self).__init__(*args, **kwargs)

        # Добавим доступные слоты времени в поле time
        if 'employee' in self.data and 'service' in self.data and 'date' in self.data:
            employee_id = self.data.get('employee')
            service_id = self.data.get('service')
            date_id = self.data.get('date')

            employee = Employee.objects.get(id=employee_id)
            service = Service.objects.get(id=service_id)
            date = datetime.strptime(date_id, '%Y-%m-%d').date()

            hall = employee.service_halls.filter(service_id=service_id).first().hall
            available_time = get_time_slots(hall, service, date)

            # Преобразуем список доступных временных слотов в choices для поля
            self.fields['time'].choices = [(slot, slot) for slot in available_time]

    def save(self, commit=True):
        """Переопределяем сохранение формы, чтобы автоматически устанавливать зал и время и проверять переполненность зала"""
        instance = super().save(commit=False)

        # Устанавливаем значение для поля hall на основе выбранных сотрудника и услуги
        employee = self.cleaned_data.get('employee')
        service = self.cleaned_data.get('service')
        time = self.cleaned_data.get('time')  # Получаем выбранное время
        date = self.cleaned_data.get('date')  # Получаем выбранную дату

        if employee and service:
            # Найти доступные залы для сотрудника
            available_halls = employee.halls.all()

            if available_halls.exists():
                instance.hall = available_halls.first()  # Устанавливаем первый доступный зал

            # Проверяем, переполнен ли зал на выбранную дату и время
            hall = instance.hall
            existing_visits = Visit.objects.filter(hall=hall, date=date, time=time)

            if existing_visits.count() >= hall.capacity:
                # Если зал переполнен, генерируем ошибку
                raise forms.ValidationError(
                    "Зал переполнен на выбранное время. Пожалуйста, выберите другое время.")


        instance.time = time  # Устанавливаем выбранное время

        if commit:
            instance.save()
        return instance


# Форма регистрации клиента
class ClientRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')


# Форма регистрации сотрудника
class EmployeeRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')


# Форма для обновления данных клиента
class ClientUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(label='Номер телефона')
    date_of_birth = forms.DateField(required=True, label='Дата рождения',
                                    widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский')
    ], label='Пол')

    class Meta:
        model = Client
        fields = ['phone_number', 'date_of_birth', 'gender']
        labels = {
            'phone_number': 'Номер телефона',
            'date_of_birth': 'Дата рождения',
            'gender': 'Пол',
        }
