from hashlib import sha256
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .utils import password_is_valid, email_html
from django.contrib.auth.models import User
from django.contrib.messages import constants 
from django.contrib import messages, auth
from django.conf import settings
from .models import Activation
import os

# Create your views here.
def signup(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'signup.html')
    elif request.method == 'POST':
        user_name = request.POST.get('user_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not password_is_valid(request, password, confirm_password):
            return redirect('/auth/signup')
        try:
            user = User.objects.create_user(username=user_name,
                                            email=email,
                                            password=password,
                                            is_active=False)
            user.save()

            token = sha256(f'{user_name}{email}'.encode()).hexdigest()
            activation = Activation(token=token, user=user)
            activation.save()

            path_template = os.path.join(settings.BASE_DIR, 'authentication/templates/emails/signup_confirmed.html')
            email_html(
                path_template,
                'Confirmar Cadastro', 
                [email,], 
                username=user_name, 
                link_activated=f'127.0.0.1:8000/auth/activate_account/{token}')
                
            messages.add_message(request, constants.SUCCESS, 'Usuario cadastrado com sucesso.')
            return redirect('/auth/login')
        except:
            messages.add_message(request, constants.ERROR, 'Error ao salvar usuario.')
            return redirect('/auth/signup')


def login(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        username = auth.authenticate(username=username, password=password)
        if not username:
            messages.add_message(request, constants.ERROR, 'Nome de usuario ou senha inválidos')
            return redirect('/auth/login')
        else:
            auth.login(request, username)
            return redirect('/')

def logout(request):
    auth.logout(request)

    return redirect('/auth/login')

def activate_account(request, token):
    token = get_object_or_404(Activation, token=token)
    if token.active:
        messages.add_message(request, constants.WARNING, 'Esse token já foi usado')
        return redirect('/auth/login')
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()
    token.active = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/login')
