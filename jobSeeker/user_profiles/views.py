from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def profile(request):
    return HttpResponse("User profile - To be implemented")

def edit_profile(request):
    return HttpResponse("Edit profile - To be implemented")
