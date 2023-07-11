
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .forms import LoginForm, RegistroForm
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class IngresoView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get(self, request):
        context = {'formulario_login': LoginForm()}
        return render(request, "registration/login.html", context)

    def post(self, request):
        usuario = authenticate(
            request, email=request.POST['email'], password=request.POST['password'])
        if usuario is not None:
            login(request, usuario)
            return redirect('home')
        else:
            context = {"error": "Usuario no encontrado",
                       'formulario_login': LoginForm()}
            print(context)
            return render(request, 'registration/login.html', context)

# Registro de usuarios

class RegistroView(View):
   def get(self, request):
       formulario = RegistroForm()
       context = {'formulario': formulario}
       template_name = "registration/registro.html"
       return render(request, template_name, context)
   
   def post(self, request):
       formulario = RegistroForm(request.POST)
       if formulario.is_valid():
           random_pass = User.objects.make_random_password(
               length=8, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
           user = User.objects.create_user(
               username=formulario.cleaned_data['username'],
               email=formulario.cleaned_data['email'],
               password=random_pass)
           user.is_active = True
           user.save()
           send_mail(
               'Registro teloenvio.com',
               'Bienvenido a teloenvio, su contraseña es: ' + random_pass,
               settings.EMAIL_HOST_USER,
               (user.email,),
               fail_silently=False,
           )
           print(
               f'El username {user.username}, cuyo correo es {user.email} tiene la contraseña: {random_pass}')
           return redirect('login')
       else:
           print(formulario.errors)
           context = {'formulario': formulario}
           return render(request, 'registration/signup.html', context)

