from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User, Group
from django.views.generic import DetailView
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectElement, Material, Pricing
from .forms import UserRegisterForm, ManagerRegisterForm
from .forms import ManagerRegisterForm, ManagerLoginForm
from .models import Project, ProjectElement, Material, Pricing
from .forms import ProjectElementForm, MaterialForm

from django.http import JsonResponse












# Create your views here.


def home(request):
    return render(request, 'main/base.html')

def base(request):
    return render(request, 'main/base.html')  # Simple base dashboard template

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base')
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    # Your login logic
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to user dashboard
    return render(request, 'main/login.html')

@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'main/dashboard.html', {'projects': projects})

def logout_view(request):
    logout(request)
    return redirect('base')  #





from django.shortcuts import render, redirect
from .models import Project, ProjectElement, Material


@login_required
def request_quote(request):
    if request.method == 'POST':
        area_size = request.POST.get('area_size')
        project_elements = request.POST.getlist('project_elements')  # List of selected elements
        materials = request.POST.getlist('materials')  # List of selected materials

        # Create a new project for the quote request
        project = Project.objects.create(
            name=f"Quotation for {request.user.username}",
            description=f"Quotation for area size: {area_size} sq.m.",
            location="User-defined location",
            status="Pending",
            user=request.user
        )

        print("Created project:", project)

        # Link selected elements and materials to the project
        for element_name in project_elements:
            # Create ProjectElement associated with the project
            element = ProjectElement.objects.create(project=project, name=element_name)
            print("Created project element:", element)

            # For each material, create a Material instance associated with this element
            for material_name in materials:
                material = Material.objects.create(
                    element=element,
                    name=material_name,
                    qty=10,  # Example quantity; replace with actual input if needed
                    unit="sq.m",  # Example unit; replace as needed
                    price_per_qty=100.00,  # Example price; replace as needed
                    markup_percentage=10  # Example markup; replace as needed
                )
                print("Created material:", material)

        return redirect('dashboard')

    # Provide list of elements and materials for selection
    element_names = ["Framing", "Window and Door Installation", "Electrical", "Plumbing"]
    material_names = [
        "Exterior Wall Framing", "Roof Framing", "Door Framing", "Barn Door",
        "Sliding Door", "Light Switches", "Main Panel", "Shower Fixture", "Toilet Installation"
    ]

    return render(request, 'main/request_quote.html', {
        'element_names': element_names,
        'material_names': material_names
    })




class ProjectDetailView(DetailView):
        model = Project
        template_name = 'main/project_detail.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            project = self.get_object()

            # Fetch all elements and their related materials for the project
            elements_with_materials = []
            for element in project.elements.all():  # Access elements via 'elements' related name
                materials = element.materials.all()  # Access materials via 'materials' related name
                elements_with_materials.append({
                    'element': element,
                    'materials': materials
                })

            context['elements_with_materials'] = elements_with_materials
            return context


def manager_register(request):
    if request.method == 'POST':
        form = ManagerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add the user to the "Managers" group
            manager_group, created = Group.objects.get_or_create(name="Managers")
            user.groups.add(manager_group)
            messages.success(request, 'Manager account created successfully.')
            return redirect('manager_login')
    else:
        form = ManagerRegisterForm()
    return render(request, 'manager/register.html', {'form': form})

def manager_login(request):
    if request.method == 'POST':
        form = ManagerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if user is in the "Managers" group
                if user.groups.filter(name="Managers").exists():
                    login(request, user)
                    return redirect('manager_dashboard')
                else:
                    messages.error(request, "You are not authorized to log in as a manager.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = ManagerLoginForm()
    return render(request, 'manager/login.html', {'form': form})

@login_required
def manager_dashboard(request):
    # Only allow users in the "Managers" group to access this view
    if not request.user.groups.filter(name="Managers").exists():
        messages.error(request, "Access denied.")
        return redirect('manager_login')

    # Display pending projects by default on the dashboard
    projects = Project.objects.filter(status='Pending')
    return render(request, 'manager/dashboard.html', {'projects': projects, 'status': 'Pending'})

@login_required
def project_list(request, status):
    # Only allow users in the "Managers" group to access this view
    if not request.user.groups.filter(name="Managers").exists():
        messages.error(request, "Access denied.")
        return redirect('manager_login')

    # Filter projects based on status
    projects = Project.objects.filter(status=status.capitalize())
    return render(request, 'manager/project_list.html', {'projects': projects, 'status': status.capitalize()})

@login_required
def project_update(request, pk):
    # Ensure only users in "Managers" group can access this view
    if not request.user.groups.filter(name="Managers").exists():
        messages.error(request, "Access denied.")
        return redirect('manager_login')

    project = get_object_or_404(Project, pk=pk)

    # Handle form submissions if it's a POST request
    if request.method == 'POST':
        # Update project status
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Approved', 'Declined', 'Completed']:
            project.status = new_status
            project.save()
            messages.success(request, f'Project status updated to {new_status}.')

        # Handle AJAX updates for individual materials (if using AJAX)
        material_id = request.POST.get('material_id')
        qty = request.POST.get('qty')
        if material_id and qty:
            material = get_object_or_404(Material, id=material_id, element__project=project)
            material.qty = float(qty)
            material.save()
            return JsonResponse({'total_cost': material.total_cost})

        # If this is a regular POST (not AJAX), redirect back to avoid resubmission
        return redirect('project_update', pk=project.pk)

    # Prepare data for template rendering
    elements_with_materials = [
        {
            'element': element,
            'materials': element.materials.all()
        } for element in project.elements.all()
    ]

    return render(request, 'manager/project_update.html', {
        'project': project,
        'elements_with_materials': elements_with_materials,
        'statuses': ['Pending', 'Approved', 'Declined', 'Completed']
    })


@login_required
def update_material(request, material_id):
    # This view will handle AJAX requests for updating individual material prices and markups
    if request.method == 'POST':
        material = get_object_or_404(Material, pk=material_id)
        qty = request.POST.get('qty')
        markup = request.POST.get('markup')

        if qty:
            material.qty = float(qty)
        if markup:
            material.markup_percentage = float(markup)

        material.save()

        # Calculate the total cost after updates
        total_cost = material.total_cost  # Assuming total_cost is a calculated property

        # Return updated information as JSON
        return JsonResponse({
            'total_cost': total_cost,
            'markup_percentage': material.markup_percentage
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

def manager_logout(request):
    logout(request)
    return redirect('base')





@login_required
def list_project_elements(request):
    elements = ProjectElement.objects.all()
    return render(request, 'manager/list_project_elements.html', {'elements': elements})

@login_required
def list_materials(request):
    materials = Material.objects.all()
    return render(request, 'manager/list_materials.html', {'materials': materials})


@login_required
def add_project_element(request):
    if request.method == 'POST':
        form = ProjectElementForm(request.POST)
        if form.is_valid():
            project_element = form.save(commit=False)

            # Retrieve additional fields from POST data
            project_element.quotation_name = request.POST.get('quotation_name')
            project_element.description = request.POST.get('description')
            project_element.area_size = request.POST.get('area_size')
            project_element.project_element = request.POST.get('project_element')
            project_element.material = request.POST.get('material')

            project_element.save()
            messages.success(request, 'Project element added successfully.')
            return redirect('list_project_elements')
    else:
        form = ProjectElementForm()
    return render(request, 'manager/add_edit_project_element.html', {'form': form, 'action': 'Add'})


@login_required
def edit_project_element(request, pk):
    element = get_object_or_404(ProjectElement, pk=pk)
    if request.method == 'POST':
        form = ProjectElementForm(request.POST, instance=element)
        if form.is_valid():
            project_element = form.save(commit=False)

            # Update additional fields from POST data
            project_element.quotation_name = request.POST.get('quotation_name')
            project_element.description = request.POST.get('description')
            project_element.area_size = request.POST.get('area_size')
            project_element.project_element = request.POST.get('project_element')
            project_element.material = request.POST.get('material')

            project_element.save()
            messages.success(request, 'Project element updated successfully.')
            return redirect('list_project_elements')
    else:
        form = ProjectElementForm(instance=element)
    return render(request, 'manager/add_edit_project_element.html', {'form': form, 'action': 'Edit'})


@login_required
def delete_project_element(request, pk):
    element = get_object_or_404(ProjectElement, pk=pk)
    element.delete()
    messages.success(request, 'Project element deleted successfully.')
    return redirect('list_project_elements')

@login_required
def add_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material added successfully.')
            return redirect('list_materials')
    else:
        form = MaterialForm()
    return render(request, 'manager/add_edit_material.html', {'form': form, 'action': 'Add'})

@login_required
def edit_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material updated successfully.')
            return redirect('list_materials')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'manager/add_edit_material.html', {'form': form, 'action': 'Edit'})

@login_required
def delete_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    material.delete()
    messages.success(request, 'Material deleted successfully.')
    return redirect('list_materials')
