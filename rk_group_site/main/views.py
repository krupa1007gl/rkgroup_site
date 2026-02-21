from django.shortcuts import render, redirect
from django.urls import reverse
from .utils import save_to_csv

def index(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            save_to_csv(name, email, message, source='Главная')
            return redirect(reverse('home') + '?sent=1')

    return render(request, 'main/index.html')