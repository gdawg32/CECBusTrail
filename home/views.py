from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import BusForm, BusStopForm
from .models import Bus, BusStop
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def index(request):
    return render(request, "index.html")

def admin_login(request):
    return render(request, "admin_login.html")

def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')  

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:  
                login(request, user)
                return redirect('admin_dashboard')  
            else:
                messages.error(request, "You are not authorized to access the admin panel.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'admin_login.html')

def admin_dashboard(request):
    return render(request, "admin_dashboard.html")

def admin_logout(request):
    logout(request)
    return redirect('index')

def bus_management(request):
    bus_stop_form = BusStopForm()
    bus_form = BusForm()

    if request.method == 'POST':
        if 'bus_stop_form' in request.POST:
            bus_stop_form = BusStopForm(request.POST)
            if bus_stop_form.is_valid():
                bus_stop = bus_stop_form.save()
                return JsonResponse({'success': True, 'bus_stop': bus_stop.name})
            else:
                return JsonResponse({'success': False, 'errors': bus_stop_form.errors})
        
        elif 'bus_form' in request.POST:
            bus_form = BusForm(request.POST)
            if bus_form.is_valid():
                bus = bus_form.save()
                return JsonResponse({'success': True, 'bus': bus.number_plate})
            else:
                return JsonResponse({'success': False, 'errors': bus_form.errors})

    context = {
        'bus_stop_form': bus_stop_form,
        'bus_form': bus_form,
        'bus_stops': BusStop.objects.all(),
        'buses': Bus.objects.all(),
    }
    return render(request, 'bus_management.html', context)

def get_bus_stops(request):
    stops = BusStop.objects.all().values('id', 'name', 'latitude', 'longitude')
    return JsonResponse(list(stops), safe=False)

def get_buses(request):
    buses = Bus.objects.all().values('id', 'number_plate', 'route', 'capacity')
    return JsonResponse(list(buses), safe=False)

@csrf_exempt
def add_bus_stop(request):
    if request.method == "POST":
        data = json.loads(request.body)
        stop = BusStop.objects.create(name=data['name'], latitude=data['latitude'], longitude=data['longitude'])
        return JsonResponse({"message": "Bus stop added", "id": stop.id})

@csrf_exempt
def add_bus(request):
    if request.method == "POST":
        data = json.loads(request.body)
        bus = Bus.objects.create(number_plate=data['number_plate'], route=data['route'], capacity=data['capacity'])
        bus.stops.set(BusStop.objects.filter(id__in=data['stops']))
        return JsonResponse({"message": "Bus added", "id": bus.id})

def bus_stops_for_bus(request, bus_id):
    try:
        bus = Bus.objects.get(id=bus_id)
    except Bus.DoesNotExist:
        raise Http404("Bus not found")
    
    # Get all bus stops associated with this bus
    stops = bus.stops.all().values('id', 'name', 'latitude', 'longitude')
    return JsonResponse(list(stops), safe=False)
