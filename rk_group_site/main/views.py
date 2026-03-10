from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import ContactMessage  # импортируем модель
from .utils import save_to_csv  # если хотите оставить и CSV

def index(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            # Сохраняем в базу данных
            contact = ContactMessage.objects.create(
                name=name,
                email=email,
                message=message
            )
            
            # Опционально: сохраняем и в CSV (если нужно)
            save_to_csv(name, email, message, source='Главная')
            
            # Добавляем сообщение об успехе
            messages.success(request, 'Спасибо! Ваше сообщение отправлено. Мы свяжемся с вами в ближайшее время.')
            
            # Редирект с якорем на форму
            return redirect(reverse('home') + '#contact-form')
        else:
            # Если не все поля заполнены
            messages.error(request, 'Пожалуйста, заполните все поля.')

    return render(request, 'main/index.html')