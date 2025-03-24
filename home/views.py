from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import *
from .models import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from math import radians, sin, cos, sqrt, atan2
from django.utils.timezone import now
import datetime
from django.utils.dateparse import parse_date

# Create your views here.

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance_km = R * c
    return distance_km




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
    messages = list(request.session.pop('messages', []))
    return render(request, "admin_dashboard.html", {'messages': messages})

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


@csrf_exempt
def delete_bus(request, bus_id):
    """Delete a bus by ID and return a JSON response."""
    if request.method == "DELETE":
        bus = get_object_or_404(Bus, id=bus_id)
        bus.delete()
        return JsonResponse({"message": "Bus deleted successfully"}, status=200)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def driver_management(request):
    if request.method == 'POST':
        # Handle new driver creation
        try:
            # Create user account
            user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email']
            )
            
            # Create driver profile
            bus = None
            if request.POST.get('bus'):
                bus = get_object_or_404(Bus, id=request.POST['bus'])
            
            Driver.objects.create(
                user=user,
                bus=bus
            )
            
            messages.success(request, 'Driver added successfully!')
            return redirect('driver_management')
            
        except Exception as e:
            messages.error(request, f'Error adding driver: {str(e)}')
            
    # Get all drivers and available buses
    drivers = Driver.objects.select_related('user', 'bus').all()
    available_buses = Bus.objects.filter(driver__isnull=True)
    
    context = {
        'drivers': drivers,
        'available_buses': available_buses,
    }
    
    return render(request, 'driver_management.html', context)

def delete_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    driver.delete()
    return redirect('driver_management')

def get_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    return JsonResponse({
        "first_name": driver.user.first_name,
        "last_name": driver.user.last_name,
        "email": driver.user.email,
        "bus_id": driver.bus.id if driver.bus else None
    })

@csrf_exempt
def edit_driver(request, driver_id):
    if request.method == "POST":
        driver = get_object_or_404(Driver, id=driver_id)
        user = driver.user

        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()

        bus_id = request.POST.get("bus_id")
        if bus_id:
            driver.bus = Bus.objects.get(id=bus_id)
        else:
            driver.bus = None
        driver.save()

        return JsonResponse({"success": True})
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def driver_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if Driver.objects.filter(user=user).exists():  # Ensure user is a driver
                login(request, user)
                return redirect("driver_dashboard")  # Redirect to driver dashboard
            else:
                messages.error(request, "You are not authorized as a driver.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "driver_login.html")

def driver_logout(request):
    logout(request)
    return redirect("driver_login")

@login_required
def driver_tracking_page(request):
    try:
        driver = request.user.driver_profile  # Get the driver's profile
        bus = driver.bus  # Get assigned bus (can be None)
    except Driver.DoesNotExist:
        driver = None
        bus = None

    return render(request, "driver_bus_control.html", {
        'driver': driver,
        'bus': bus,
    })

@login_required
def toggle_tracking(request):
    try:
        driver = request.user.driver_profile
        bus = driver.bus
        if not bus:
            messages.error(request, "You are not assigned to any bus.")
            return redirect('driver_dashboard')

        # If tracking is already on, turn it off
        if bus.tracking_enabled:
            bus.tracking_enabled = False
            bus.save()
            messages.success(request, "Tracking turned OFF for your bus.")
        else:
            # Turn off tracking for any other bus first
            Bus.objects.filter(tracking_enabled=True).update(tracking_enabled=False)
            bus.tracking_enabled = True
            bus.save()
            messages.success(request, "Tracking turned ON for your bus.")

    except Driver.DoesNotExist:
        messages.error(request, "Driver profile not found.")

    return redirect('driver_dashboard')

def student_application(request):
    available_buses = Bus.objects.all()
    available_stops = BusStop.objects.all()
    branch_choices = StudentApplication.BRANCH_CHOICES

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        batch_year = request.POST.get("batch_year")
        branch = request.POST.get("branch")
        bus_id = request.POST.get("bus_route")
        stop_id = request.POST.get("preferred_stop")
        registered_id = request.POST.get("registered_id")
        semester = request.POST.get("semester")

        bus_route = Bus.objects.get(id=bus_id) if bus_id else None
        preferred_stop = BusStop.objects.get(id=stop_id) if stop_id else None

        # Save application
        application = StudentApplication(
            full_name=full_name, email=email, phone=phone,
            batch_year=batch_year, branch=branch,
            bus_route=bus_route, preferred_stop=preferred_stop,
            registered_id=registered_id,
            semester=semester

        )
        application.save()

        messages.success(request, "Your application has been submitted successfully!")
        return redirect("student_application")

    return render(request, "student_application.html", {
        "available_buses": available_buses,
        "available_stops": available_stops,
        "branch_choices": branch_choices,
    })

def student_register(request):
    applications = StudentApplication.objects.all()

    return render(request, "student_management.html", {
        "applications": applications,
    })

def approve_student(request, application_id):
    application = get_object_or_404(StudentApplication, id=application_id)

    # Create a username and password using registered_id
    username = f"student{application.registered_id}"  # Example: student2023123
    password = f"pass{application.registered_id}"  # Example: pass2023123

    # Create a new User
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=application.full_name.split()[0],
        last_name=" ".join(application.full_name.split()[1:]),
        email=application.email,
    )

    # Create the Student instance linked to the new User
    student = Student.objects.create(
        user=user,
        batch_year=application.batch_year,
        branch=application.branch,
        bus=application.bus_route,
        bus_stop=application.preferred_stop,
        registered_id=application.registered_id,
        semester=application.semester
    )

    # Remove the approved application
    application.delete()

    messages.success(request, f"Student approved! Username: {username}, Password: {password}")
    return redirect("student_management")


def reject_student(request, application_id):
    application = get_object_or_404(StudentApplication, id=application_id)
    application.delete()  # Delete application

    messages.success(request, "Student application rejected!")
    return redirect("student_management")


def advance_semester(request):
    students = Student.objects.all()
    removed_count = 0
    updated_count = 0

    for student in students:
        try:
            current_sem = int(student.semester.strip().split()[-1])  # e.g., "Sem 5" -> 5
            if current_sem >= 8:
                student.user.delete()
                removed_count += 1
            else:
                student.semester = f"Sem {current_sem + 1}"
                student.save()
                updated_count += 1
        except:
            continue  # skip malformed semesters

    messages.success(request, f"{updated_count} students advanced, {removed_count} students removed.")
    return redirect('admin_dashboard')  # or wherever you want to go after

def student_login(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'student_profile'):
            login(request, user)
            return redirect("student_dashboard")
        else:
            messages.error(request, "Invalid credentials or not a student account!")

    return render(request, "student_login.html")

@login_required
def student_dashboard(request):
    student = request.user.student_profile
    distance_km = None

    if student.bus_stop:
        stop_lat = float(student.bus_stop.latitude)
        stop_lon = float(student.bus_stop.longitude)
        college_lat = 9.743520
        college_lon = 76.281570

        straight_km = haversine_distance(stop_lat, stop_lon, college_lat, college_lon)
        adjusted_km = round(straight_km * 1.4, 2)  # Apply road correction

        distance_km = adjusted_km

    return render(request, "student_dashboard.html", {
        "student": student,
        "distance_km": distance_km,
    })

def student_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("student_login")

@login_required
def edit_student_profile(request):
    student = request.user.student_profile  # Fetch the logged-in student's profile

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        batch_year = request.POST.get("batch_year")
        branch = request.POST.get("branch")
        password = request.POST.get("password")

        # Update student details
        request.user.first_name, request.user.last_name = full_name.split(" ", 1) if " " in full_name else (full_name, "")
        request.user.email = email
        student.batch_year = batch_year
        student.branch = branch

        # Change password if provided
        if password:
            request.user.set_password(password)

        request.user.save()
        student.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("student_dashboard")

    return render(request, "edit_student_profile.html", {"student": student})

def get_distance_category(distance):
    # Define your range brackets
    brackets = [
        (0, 5, '0-5'),
        (5, 10, '5-10'),
        (10, 15, '10-15'),
        (15, 20, '15-20'),
        (20, 25, '20-25'),
        (25, 30, '25-30'),
        (30, 35, '30-35'),
        (35, 40, '35-40'),
        (40, 1000, '40+'),
    ]
    for low, high, label in brackets:
        if low <= distance < high:
            return label
    return '0-5'  # Fallback

@login_required
def student_payment(request):
    student = request.user.student_profile
    
    # 1. Get paid & unpaid semesters
    paid_sems = student.payments.values_list('semester', flat=True)
    all_sems = [sem[0] for sem in Payment.SEMESTER_CHOICES]
    unpaid_sems = [sem for sem in all_sems if sem not in paid_sems]

    # 2. Calculate distance to college and fee
    distance_km = None
    distance_category = '0-5'  # default
    fee_category, fee_amount = '0-5', 2000  # default

    if student.bus_stop:
        college_lat, college_lon = 9.743520, 76.281570
        stop_lat = float(student.bus_stop.latitude)
        stop_lon = float(student.bus_stop.longitude)
        straight_km = haversine_distance(stop_lat, stop_lon, college_lat, college_lon)
        adjusted_km = straight_km * 1.4  # apply real-world correction factor
        distance_km = round(adjusted_km, 2)
        distance_category = get_distance_category(distance_km)
        fee_category, fee_amount = calculate_fee_by_distance(distance_km)

    # 3. Handle Payment Submission
    current_sem = student.semester  # assuming student has a current semester field

    if request.method == 'POST':
        if current_sem not in paid_sems:
            # create and save payment
            payment = Payment(
                student=student,
                semester=current_sem,
                distance_category=distance_category
            )
            payment.save()
            messages.success(request, f'Payment for {current_sem} successful!')
            return redirect('student_payment')
        else:
            messages.error(request, 'Invalid or already paid semester.')

    # 4. Prepare form only if unpaid
    form = PaymentForm(student=student) if current_sem not in paid_sems else None

    payments = student.payments.all().order_by('-date_paid')
    return render(request, 'make_payment.html', {
        'form': form,
        'payments': payments,
        'unpaid_sems': unpaid_sems,
        'distance_km': distance_km,
        'distance_category': distance_category,
        'fee': fee_amount,
        'student': student
    })

def calculate_fee_by_distance(distance_km):
    """
    Returns the distance category and corresponding fee for the given distance.
    """
    distance_fee_map = {
        '0-5': 2000,
        '5-10': 2500,
        '10-15': 3000,
        '15-20': 3500,
        '20-25': 4000,
        '25-30': 4500,
        '30-35': 5000,
        '35-40': 5500,
        '40+': 6000,
    }

    if distance_km <= 5:
        category = '0-5'
    elif distance_km <= 10:
        category = '5-10'
    elif distance_km <= 15:
        category = '10-15'
    elif distance_km <= 20:
        category = '15-20'
    elif distance_km <= 25:
        category = '20-25'
    elif distance_km <= 30:
        category = '25-30'
    elif distance_km <= 35:
        category = '30-35'
    elif distance_km <= 40:
        category = '35-40'
    else:
        category = '40+'

    fee = distance_fee_map[category]
    return category, fee

@csrf_exempt
@login_required
def update_bus_location(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            lat = data.get("latitude")
            lon = data.get("longitude")

            if not lat or not lon:
                return JsonResponse({'error': 'Latitude or longitude missing'}, status=400)

            driver = request.user.driver_profile
            bus = driver.bus

            if bus:
                bus.current_location = f"{lat},{lon}"
                bus.tracking_enabled = True
                bus.save()
                return JsonResponse({'status': 'success'})

            return JsonResponse({'error': 'No bus assigned'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_bus_location(request, bus_id):
    try:
        bus = Bus.objects.get(id=bus_id, tracking_enabled=True)
        if bus.current_location:
            lat, lon = map(float, bus.current_location.split(','))
            return JsonResponse({'latitude': lat, 'longitude': lon})
        else:
            return JsonResponse({'error': 'Location not available'}, status=404)
    except Bus.DoesNotExist:
        return JsonResponse({'error': 'Bus not found'}, status=404)

@csrf_exempt
@login_required
def stop_bus_tracking(request):
    if request.method == 'POST':
        driver = request.user.driver_profile
        bus = driver.bus
        if bus:
            bus.tracking_enabled = False
            bus.current_location = None
            bus.save()
            return JsonResponse({'status': 'stopped'})
    return JsonResponse({'status': 'failed'}, status=400)

def track_bus(request):
    buses = Bus.objects.filter(tracking_enabled=True)
    return render(request, 'track_bus.html', {'buses': buses})

def track_student_bus(request):
    # Get the student associated with the current user
    student = Student.objects.get(user=request.user)
    
    # Check if student has an assigned bus
    if student.bus and student.bus.tracking_enabled:
        buses = [student.bus]  # List containing only the student's bus
        return render(request, 'track_bus.html', {'buses': buses})
    else:
        # If no bus assigned or tracking not enabled
        messages.info(request, "No trackable bus is currently assigned to your account.")
        return redirect('student_dashboard')  # Redirect back to dashboard

def payment_transactions(request):
    payments = Payment.objects.select_related('student__user').order_by('-date_paid')
    return render(request, 'payment_transactions.html', {'payments': payments})

@login_required
def student_management(request):
    # Group students by branch
    branches = dict(Student.BRANCH_CHOICES)
    grouped_students = {}

    for code, name in branches.items():
        students = Student.objects.filter(branch=code).select_related('user', 'bus', 'bus_stop')
        grouped_students[name] = students

    buses = Bus.objects.all()
    bus_stops = BusStop.objects.all()

    return render(request, 'student_list_by_branch.html', {
        'grouped_students': grouped_students,
        'buses': buses,
        'bus_stops': bus_stops,
    })

def update_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.admission_number = request.POST.get('admission_number', '')
    student.semester = request.POST.get('semester', student.semester)
    bus_id = request.POST.get('bus_id')
    stop_id = request.POST.get('bus_stop_id')

    student.bus = Bus.objects.get(id=bus_id) if bus_id else None
    student.bus_stop = BusStop.objects.get(id=stop_id) if stop_id else None
    student.save()
    return redirect('student_management')
@login_required
def driver_dashboard(request):
    try:
        driver = request.user.driver_profile
        bus = driver.bus  # This can be None if not assigned
    except Driver.DoesNotExist:
        # Redirect to login or show an error
        return redirect('driver_login')

    return render(request, 'driver_dashboard.html', {
        'driver': driver,
        'bus': bus
    })

@login_required
def scan_student_qr(request):
    return render(request, "scan_student_qr.html")

@csrf_exempt
@login_required
@csrf_exempt
def validate_admission_number(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        admission_number = data.get("admission_number", "").strip()

        try:
            student = Student.objects.select_related('user').get(admission_number=admission_number)
            has_paid = Payment.objects.filter(student=student, semester=student.semester).exists()

            return JsonResponse({
                "valid": True,
                "name": student.user.get_full_name(),
                "admission_number": student.admission_number,
                "has_paid": has_paid
            })
        except Student.DoesNotExist:
            return JsonResponse({ "valid": False })

    return JsonResponse({ "error": "Invalid request" }, status=400)
@csrf_exempt
def mark_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        admission_number = data.get('admission_number')
        route = data.get('route')
        date_str = data.get('date')

        try:
            student = Student.objects.get(admission_number=admission_number)

            # Check payment
            if not student.payments.filter(semester=student.semester).exists():
                return JsonResponse({'success': False, 'error': 'Student has not paid for current semester.'})

            # Parse date
            date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()

            # Mark attendance (unique by date + route)
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                date=date,
                route=route
            )
            return JsonResponse({'success': True, 'student': student.user.get_full_name(), 'created': created})

        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Student not found'}, status=404)

    return JsonResponse({'error': 'Invalid method'}, status=405)

def view_attendance(request):
    buses = Bus.objects.all()
    attendances = []

    selected_bus_id = request.GET.get('bus')
    selected_date = request.GET.get('date')
    selected_route = request.GET.get('route') 

    print(selected_bus_id, selected_date, selected_route)

    if selected_bus_id and selected_date and selected_route:
        try:
            parsed_date = parse_date(selected_date)
            if parsed_date:
                attendances = Attendance.objects.select_related('student__user') \
                    .filter(
                        student__bus_id=selected_bus_id,
                        date=parsed_date,
                        route=selected_route
                    ).order_by('time')
        except Exception as e:
            print("Error:", e)

    context = {
        'buses': buses,
        'attendances': attendances,
        'selected_bus_id': selected_bus_id,
        'selected_date': selected_date,
        'selected_route': selected_route,
        'branch_choices': Student.BRANCH_CHOICES,
    }
    return render(request, 'view_attendance.html', context)
