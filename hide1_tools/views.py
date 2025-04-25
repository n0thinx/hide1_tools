from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.static import serve
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('/login')

def serve_files(request, path):
    print(path)
    response = serve(request, path, document_root="")
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@login_required
def index(request):
    username = request.user.username
    context = {
        'mode': 'HOME',
        'username': username,
    }
    return render(request, 'index.html', context)