from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from .models import Location
from .forms import LocationForm
from .calendar_service import get_location_calendar_data, get_all_locations_availability


@staff_member_required
def location_list(request):
    """List all locations with filtering"""
    locations = Location.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        locations = locations.filter(status=status_filter)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        locations = locations.filter(location_type=type_filter)
    
    # Statistics
    total_locations = Location.objects.count()
    available_count = Location.objects.filter(status='AVAILABLE').count()
    occupied_count = Location.objects.filter(status='OCCUPIED').count()
    
    context = {
        'locations': locations,
        'total_locations': total_locations,
        'available_count': available_count,
        'occupied_count': occupied_count,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    return render(request, 'locations/location_list.html', context)


@staff_member_required
def location_create(request):
    """Create a new location"""
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.created_by = request.user
            location.save()
            messages.success(request, f'Lieu "{location.name}" créé avec succès!')
            return redirect('location_detail', pk=location.id)
    else:
        form = LocationForm()
    
    return render(request, 'locations/location_form.html', {'form': form, 'action': 'Créer'})


@staff_member_required
def location_detail(request, pk):
    """View location details"""
    location = get_object_or_404(Location, pk=pk)
    return render(request, 'locations/location_detail.html', {'location': location})


@staff_member_required
def location_update(request, pk):
    """Update an existing location"""
    location = get_object_or_404(Location, pk=pk)
    
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lieu "{location.name}" modifié avec succès!')
            return redirect('location_detail', pk=location.id)
    else:
        form = LocationForm(instance=location)
    
    return render(request, 'locations/location_form.html', {
        'form': form,
        'location': location,
        'action': 'Modifier'
    })


@staff_member_required
def location_delete(request, pk):
    """Delete a location"""
    location = get_object_or_404(Location, pk=pk)
    
    if request.method == 'POST':
        location_name = location.name
        location.delete()
        messages.success(request, f'Lieu "{location_name}" supprimé avec succès!')
        return redirect('location_list')
    
    return render(request, 'locations/location_confirm_delete.html', {'location': location})


@staff_member_required
def location_calendar(request, pk):
    """Afficher le calendrier de disponibilité d'un lieu"""
    location = get_object_or_404(Location, pk=pk)
    
    # Récupérer année et mois depuis les paramètres GET
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if year:
        year = int(year)
    if month:
        month = int(month)
    
    # Obtenir les données du calendrier
    calendar_data = get_location_calendar_data(location, year, month)
    
    context = {
        'location': location,
        **calendar_data
    }
    return render(request, 'locations/location_calendar.html', context)


@staff_member_required
def locations_availability(request):
    """Vue d'ensemble de la disponibilité de tous les lieux"""
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if year:
        year = int(year)
    if month:
        month = int(month)
    
    availability_data = get_all_locations_availability(year, month)
    
    context = {
        'availability_data': availability_data,
        'year': year or timezone.now().year,
        'month': month or timezone.now().month,
    }
    return render(request, 'locations/locations_availability.html', context)


def tunisia_map(request):
    """Afficher la carte interactive de Tunisie pour sélectionner un gouvernorat"""
    governorate_filter = request.GET.get('governorate')
    
    # Obtenir tous les lieux
    locations = Location.objects.filter(status='AVAILABLE')
    
    # Filtrer par gouvernorat si sélectionné
    if governorate_filter:
        locations = locations.filter(governorate=governorate_filter)
    
    # Compter les lieux par gouvernorat
    from django.db.models import Count
    governorate_counts = Location.objects.filter(
        status='AVAILABLE'
    ).values('governorate').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Créer un dict pour accès rapide
    counts_dict = {item['governorate']: item['count'] for item in governorate_counts}
    
    # Liste des gouvernorats avec leurs infos
    governorates_info = []
    for code, name in Location.GOVERNORATE_CHOICES:
        governorates_info.append({
            'code': code,
            'name': name,
            'count': counts_dict.get(code, 0),
            'is_selected': code == governorate_filter
        })
    
    context = {
        'locations': locations,
        'governorates': governorates_info,
        'selected_governorate': governorate_filter,
        'selected_governorate_name': dict(Location.GOVERNORATE_CHOICES).get(governorate_filter, 'Tous') if governorate_filter else 'Tous',
    }
    return render(request, 'locations/tunisia_map.html', context)


