from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Create your models here.


class UserDate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_date')  # Пользователь

    patronymic = models.CharField(max_length=255)  # Отчество

    date_of_birth = models.DateField()  # Дата рождения

    address = models.CharField(max_length=255)  # Адрес

    gender = models.CharField(max_length=10)  # Пол

    interests = models.CharField(max_length=255)  # Интересы

    url_vk = models.CharField(max_length=255, validators=[URLValidator])  # Ссылка на VK

    blood_type = models.CharField(max_length=10)  # Тип крови

    Rh_factor = models.CharField(max_length=10)  # резус-фактор

class Hall(models.Model):
    HALL_CHOICES = [
        (1, 'Зал 1'),
        (2, 'Зал 2'),
        (3, 'Зал 3'),
    ]
    number = models.IntegerField(choices=HALL_CHOICES, unique=True)





class Service(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, verbose_name='Зал', related_name='services')
    name = models.CharField(max_length=100, verbose_name='Название услуги')
    description = models.TextField(verbose_name='Описание услуги')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')
    image = models.URLField(verbose_name='Изображение услуги')

# Функция для создания залов
def create_initial_halls(sender, **kwargs):
    for hall_number in range(1, 4):  # Создаем 3 зала
        Hall.objects.get_or_create(number=hall_number)

# Связываем сигнал с функцией
@receiver(post_migrate)
def create_halls_signal(sender, **kwargs):
    if sender.name == 'volgtekapp':  # Замените 'yourappname' на имя вашего приложения
        create_initial_halls(sender)