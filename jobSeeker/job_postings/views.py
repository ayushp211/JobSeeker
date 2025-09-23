from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Job listings - To be implemented")

def show(request, id):
    return HttpResponse(f"Job details for job {id} - To be implemented")

def create(request):
    return HttpResponse("Create job posting - To be implemented")

def edit(request, id):
    return HttpResponse(f"Edit job {id} - To be implemented")

def delete(request, id):
    return HttpResponse(f"Delete job {id} - To be implemented")
