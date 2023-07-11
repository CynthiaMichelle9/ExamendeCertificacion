from django.urls import path
from .views import IngresoView, RegistroView
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', IngresoView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/', RegistroView.as_view(), name='registro'),
]