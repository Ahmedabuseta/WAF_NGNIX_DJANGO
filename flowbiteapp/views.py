from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection

def health(request):
    """Simple health check endpoint for Docker health checks"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'service': 'django'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'service': 'django'
        }, status=500)

def index(request):
    if request.user.is_authenticated:
        # For authenticated users, redirect to admin panel to avoid tenant issues
        return redirect('admin:index')
    return redirect('account_login')

def accordion(request):
    return render(request, 'accordion.html')

def carousel(request):
    return render(request, 'carousel.html')

def collapse(request):
    return render(request, 'collapse.html')

def dial(request):
    return render(request, 'dial.html')

def dismiss(request):
    return render(request, 'dismiss.html')

def modal(request):
    return render(request, 'modal.html')

def drawer(request):
    return render(request, 'drawer.html')

def dropdown(request):
    return render(request, 'dropdown.html')

def popover(request):
    return render(request, 'popover.html')

def tooltip(request):
    return render(request, 'tooltip.html')

def tabs(request):
    return render(request, 'tabs.html')

def input_counter(request):
    return render(request, 'input-counter.html')

def datepicker(request):
    return render(request, 'datepicker.html')