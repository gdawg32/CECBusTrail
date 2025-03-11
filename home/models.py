from django.db import models
from django.contrib.auth.models import User

# Bus Model
class BusStop(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.name

# Bus Model
class Bus(models.Model):
    number_plate = models.CharField(max_length=20, unique=True)
    route = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    current_location = models.CharField(max_length=255, blank=True, null=True)  # Stores live GPS location
    stops = models.ManyToManyField(BusStop, related_name='buses')  # Many buses can share stops
    tracking_enabled = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.number_plate} - {self.route}"

# Driver Model
class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    bus = models.OneToOneField(Bus, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

# Student Model
class Student(models.Model):
    BRANCH_CHOICES = [
        ('CS', 'Computer Science'),
        ('EC', 'Electronics and Communication'),
        ('EEE', 'Electrical and Electronics'),
        ('AD', 'Artificial Intelligence & Data Science'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    registered_id = models.CharField(max_length=255, unique=True)
    batch_year = models.CharField(max_length=9)  # Example: '2022-26'
    branch = models.CharField(max_length=5, choices=BRANCH_CHOICES)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    bus_stop = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.batch_year} - {self.get_branch_display()})"

# Payment Model
class Payment(models.Model):
    SEMESTER_CHOICES = [(f'Sem {i}', f'Semester {i}') for i in range(1, 9)]

    DISTANCE_CATEGORIES = [
        ('0-5', '0-5 km'),
        ('5-10', '5-10 km'),
        ('10-15', '10-15 km'),
        ('15-20', '15-20 km'),
        ('20-25', '20-25 km'),
        ('25-30', '25-30 km'),
        ('30-35', '30-35 km'),
        ('35-40', '35-40 km'),
        ('40+', '40+ km'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    distance_category = models.CharField(max_length=10, choices=DISTANCE_CATEGORIES, default='0-5')
    fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=2000)  # Auto-calculated
    date_paid = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ Automatically calculate fee based on distance category """
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
        self.fixed_fee = distance_fee_map.get(self.distance_category, 2000)  # Default to 2000
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.semester} - ₹{self.fixed_fee}"

class StudentApplication(models.Model):
    BRANCH_CHOICES = [
        ('CS', 'Computer Science'),
        ('EC', 'Electronics and Communication'),
        ('EEE', 'Electrical and Electronics'),
        ('AD', 'Artificial Intelligence & Data Science'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    registered_id = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    batch_year = models.CharField(max_length=9)  # Example: '2022-26'
    branch = models.CharField(max_length=5, choices=BRANCH_CHOICES)
    semester = models.CharField(max_length=10, blank=True, null=True)
    bus_route = models.ForeignKey("Bus", on_delete=models.SET_NULL, null=True, blank=True)
    preferred_stop = models.ForeignKey("BusStop", on_delete=models.SET_NULL, null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.batch_year} - {self.get_branch_display()})"
