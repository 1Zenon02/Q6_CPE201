from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



# Create your models here.

class Project(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
        ('Completed', 'Completed'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by_admin = models.BooleanField(default=False)
    approved_by_user = models.BooleanField(default=False)
    declined_by_admin = models.BooleanField(default=False)
    declined_by_user = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ProjectElement(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='elements')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # Ensure 'location' is defined here

    def __str__(self):
        return f"{self.name} in {self.project.name}"


class Material(models.Model):
    element = models.ForeignKey(ProjectElement, on_delete=models.CASCADE, related_name='materials')  # Ensure 'element' field exists
    name = models.CharField(max_length=100)
    qty = models.IntegerField()
    unit = models.CharField(max_length=50)
    price_per_qty = models.DecimalField(max_digits=10, decimal_places=2)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.total_cost = None

    def __str__(self):
        return self.name

class Pricing(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pricing for {self.material.name} in {self.project.name} on {self.date}"


