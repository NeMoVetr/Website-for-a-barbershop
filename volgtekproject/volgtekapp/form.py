from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, UserDate, Service, Hall


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']
        labels = {'username': 'Логин', 'first_name': 'Имя', 'last_name': 'Фамилия', 'password1': 'Пароль',
                  'password2': 'Повторите пароль'}


class UserDateForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский'),
    )
    BLOOD_TYPE_CHOICES = (
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
        ('IV', 'IV'),
    )

    RH_FACTOR_CHOICES = (
        ('+', '+'),
        ('-', '-'),
    )

    patronymic = forms.CharField(required=False, label='Отчество')
    date_of_birth = forms.DateField(required=True, label='Дата рождения',
                                    widget=forms.DateInput(attrs={'type': 'date'}))

    address = forms.CharField(label='Адрес')
    interests = forms.CharField(label='Интересы')
    url_vk = forms.CharField(label='Ссылка на страницу ВК', required=False)
    blood_type = forms.CharField(label='Группа крови', widget=forms.Select(choices=BLOOD_TYPE_CHOICES))
    Rh_factor = forms.CharField(label='Резус-фактор', widget=forms.Select(choices=RH_FACTOR_CHOICES))
    gender = forms.CharField(label='Пол', widget=forms.Select(choices=GENDER_CHOICES))

    class Meta:
        model = UserDate
        fields = ['patronymic', 'date_of_birth', 'address', 'gender', 'interests', 'url_vk', 'blood_type', 'Rh_factor']
        labels = {'patronymic': 'Отчество', 'date_of_birth': 'Дата рождения', 'address': 'Адрес', 'gender': 'Пол',
                  'interests': 'Интересы',
                  'url_vk': 'Ссылка на страницу ВК', 'blood_type': 'Группа крови', 'Rh_factor': 'Резус-фактор'}


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['hall', 'name', 'description', 'price', 'image']
        labels = {
            'hall': 'Зал',
            'name': 'Название услуги',
            'description': 'Описание услуги',
            'price': 'Стоимость',
            'image': 'Изображение услуги',
        }

    hall = forms.ModelChoiceField(queryset=Hall.objects.all())
