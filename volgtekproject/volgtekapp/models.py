from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.utils.timezone import now


# Create your models here.

class Hall(models.Model):
    name = models.CharField(max_length=255)  # Название зала

    description = models.TextField()  # Описание зала

    capacity = models.PositiveIntegerField()  # Вместимость зала

    location = models.CharField(max_length=255)  # Местоположение зала

    start_time = models.TimeField()  # Начало рабочего дня

    end_time = models.TimeField()  # Конец рабочего дня

    def __str__(self):
        return self.name


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')  # Пользователь

    phone_number = models.CharField(max_length=255, blank=True, null=True, validators=[
        RegexValidator(r'^\+7\d{10}$', message='Номер телефона должен быть в формате +7XXXXXXXXXX')])  # Номер телефона

    date_of_birth = models.DateField(blank=True, null=True)

    gender = models.CharField(max_length=10, choices=[
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский'),
    ])

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Service(models.Model):
    name = models.CharField(max_length=255)  # Название услуги

    description = models.TextField()  # Описание услуги

    price = models.DecimalField(decimal_places=2, max_digits=10)  # Стоимость услуги

    duration = models.TimeField()  # Длительность услуги

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')  # Пользователь

    phone_number = models.CharField(max_length=255, blank=True, null=True, validators=[
        RegexValidator(r'^\+7\d{10}$', message='Номер телефона должен быть в формате +7XXXXXXXXXX')])  # Номер телефона

    position = models.CharField(max_length=255)  # Должность

    halls = models.ManyToManyField(Hall, related_name='employees')  # Залы

    services = models.ManyToManyField(Service, related_name='employees')  # Услуги

    # Дополнительная модель для связи услуги с залом
    service_halls = models.ManyToManyField('ServiceHall', related_name='employees')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        """Метод сохранения сотрудника и связи с услугами и залами."""

        super().save(*args, **kwargs)  # Сначала сохраняем сотрудника

        # Логика автоматического заполнения service_halls
        for hall in self.halls.all():
            for service in self.services.all():
                service_hall, created = ServiceHall.objects.get_or_create(service=service,
                                                                          hall=hall)  # Проверяем, существует ли связь между Hall и Service. Если такой записи в ServiceHall нет, то создаём.
                self.service_halls.add(service_hall)


class ServiceHall(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  # Услуга
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)  # Зал

    def __str__(self):
        return f"{self.service.name} - {self.hall.name}"


class Visit(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='visits')  # Клиент

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='visits')  # Сотрудник

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='visits')  # Услуга

    date = models.DateField(default=now)  # Дата

    time = models.TimeField() # Время визита, строка в формате HH:MM

    status = models.CharField(max_length=255, choices=[
        ('Запланирована', 'Запланирована'),
        ('Выполнена', 'Выполнена'),
    ], default='Запланирована')  # Статус

    # Автоматически выбираем зал в зависимости от услуги и мастера
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='visits', null=True, blank=True)

    def save(self, *args, **kwargs):
        """Метод сохранения визита и автоматического выбора зала."""
        if not self.hall:
            service_hall = self.employee.service_halls.get(service=self.service)
            self.hall = service_hall.hall



        super(Visit, self).save(*args, **kwargs) # Сохраняем визит

    def __str__(self):
        return f"{self.client} - {self.service.name} с {self.employee}"
