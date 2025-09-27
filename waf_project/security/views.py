from django.shortcuts import render
from django.http import HttpResponse

def blocked_request(request):
    """Blocked request page"""
    return render(request, 'security/blocked.html')

def access_denied(request):
    """Access denied page"""
    return HttpResponse("Access Denied", status=403)

def rate_limited(request):
    """Rate limited page"""
    return HttpResponse("Rate Limited", status=429)
