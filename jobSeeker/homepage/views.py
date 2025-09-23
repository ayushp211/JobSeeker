from django.shortcuts import render

# Create your views here.

def index(request):
    template_data = {'title': 'Job Seeker Platform'}
    return render(request, 'homepage/index.html', {'template_data': template_data})

def about(request):
    template_data = {'title': 'About'}
    return render(request, 'homepage/about.html', {'template_data': template_data})
