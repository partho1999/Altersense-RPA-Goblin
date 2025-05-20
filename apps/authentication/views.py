from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.

def home(request):
    print("================= home ===============")
    return render(request, 'home.html')


def login_user(request):
    print("========= I am here ======== ")
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            print("============", username, password)

            user = authenticate(request, username=username, password=password)
            print("user: ", user)

            if user is not None:
                login(request, user)
                return redirect('authentication:home')
            else:
                messages.info(request, 'Username or Password incorrect')
                return render(request, "authentication/login.html")
        context = {}
        return render(request, "authentication/login.html", context)


def change_password(request):
    return render(request, "authentication/change_password.html")


def root(request):
    return redirect('/commercial')
