// Слушаем загрузку и выбор полей в форме добавления посещения
document.addEventListener('DOMContentLoaded', function () {
    const employeeField = document.getElementById('id_employee'); // Поле выбора сотрудника
    const serviceField = document.getElementById('id_service'); // Поле выбора услуг
    const dateField = document.getElementById('id_date'); // Поле выбора даты
    const timeField = document.getElementById('id_time'); // Поле выбора времени

    // Функция для обновления доступных слотов
    function updateTimeSlots() {
        const employee = employeeField.value; // Значение выбраного сотрудника
        const service = serviceField.value; // Значение выбранной услуги
        const date = dateField.value; // Значение выбраной даты

        // Проверяем, все ли поля заполнены
        if (employee && service && date) {
            // Отправляем запрос на получение доступных слотов
            fetch(`/get_available_time/?employee=${employee}&service=${service}&date=${date}`)
                .then(response => response.json())
                .then(data => {
                    timeField.innerHTML = '';  // Очистка старых значений

                    // Добавляем новые слоты в цикле for
                    data.available_time.forEach(slot => {
                        const option = document.createElement('option'); // Создаем тег опцию в html
                        option.value = slot; // Значение опции (время)
                        option.textContent = slot; // Текст опции (время)
                        timeField.appendChild(option); // Добавляем опцию в поле
                    });

                    // После получения слотов, снова поместим выбранное значение для отправки в базу данных
                    const selectedTime = timeField.getAttribute('data-selected-time');

                    // Если есть выбранное значение, то выберем его
                    if (selectedTime) {
                        const option = Array.from(timeField.options).find(opt => opt.value === selectedTime); // Создаем массив из элемента, выбранного значения пользователем времени

                        // Если опция нашлась
                        if (option) {
                            option.selected = true; // Выбираем опцию
                        }
                    }
                });
        }
    }

    // Слушаем изменения полей
    employeeField.addEventListener('change', updateTimeSlots);
    serviceField.addEventListener('change', updateTimeSlots);
    dateField.addEventListener('change', updateTimeSlots);
});
