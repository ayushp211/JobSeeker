from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def signup(request):
    return HttpResponse("Signup page - To be implemented")

def login(request):
    return HttpResponse("Login page - To be implemented")

def logout(request):
    return HttpResponse("Logout - To be implemented")
