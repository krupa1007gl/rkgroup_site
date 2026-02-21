from django.shortcuts import render, redirect
from django.urls import reverse
from main.utils import save_to_csv   # импортируем правильную функцию

def about(request):
    return render(request, 'pages/about.html')

def services(request):
    return render(request, 'pages/services.html')

def projects(request):
    return render(request, 'pages/projects.html')

def partners(request):
    return render(request, 'pages/partners.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            # ВАЖНО: используем save_to_csv, а не save_to_txt
            save_to_csv(name, email, message, source='Контакты')
            return redirect(reverse('contact') + '?sent=1')

    return render(request, 'pages/contact.html')