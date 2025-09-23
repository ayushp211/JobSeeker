from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}! You can now log in.')
            return redirect('user_accounts.login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'user_accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('homepage.index')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'homepage.index')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'user_accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    username = request.user.username
    logout(request)
    messages.success(request, f'You have been logged out successfully, {username}!')
    return redirect('homepage.index')
