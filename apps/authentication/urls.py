from django.contrib import admin
from django.urls import path, include
from . views import *

urlpatterns = [
    path('home', home, name='home'),
    path('login', login_user, name='login'),
    path('change-password', change_password, name='change-password'),
    # if path is empty, redirect to /commercial/
    path('', root, name='root'),
]
