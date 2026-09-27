"""
Service de calendrier pour la disponibilité des lieux
"""
from datetime import datetime, timedelta
from django.utils import timezone
from events.models import Event


def get_location_calendar_data(location, year=None, month=None):
    """
    Obtenir les données du calendrier pour un lieu spécifique
    
    Args:
        location: Instance de Location
        year: Année (par défaut année actuelle)
        month: Mois (par défaut mois actuel)
        
    Returns:
        dict: Données du calendrier avec événements et dates bloquées
    """
    from locations.models import BlockedDate
    
    now = timezone.now()
    year = year or now.year
    month = month or now.month
    
    # Début et fin du mois
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Événements dans ce lieu pour ce mois
    events = Event.objects.filter(
        location__icontains=location.name,
        date__gte=first_day,
        date__lte=last_day
    ).order_by('date')
    
    # Dates bloquées pour ce lieu ce mois
    blocked_dates = BlockedDate.objects.filter(
        location=location,
        date__gte=first_day.date(),
        date__lte=last_day.date()
    ).select_related('location')
    
    # Convertir en dict pour accès rapide
    blocked_dates_dict = {bd.date: bd for bd in blocked_dates}
    
    # Créer la structure du calendrier
    calendar_days = []
    current_day = first_day
    
    while current_day <= last_day:
        # Événements pour ce jour
        day_events = [e for e in events if e.date.date() == current_day.date()]
        
        # Vérifier si ce jour est bloqué
        blocked_info = blocked_dates_dict.get(current_day.date())
        is_blocked = blocked_info is not None
        
        calendar_days.append({
            'date': current_day,
            'day': current_day.day,
            'is_today': current_day.date() == now.date(),
            'is_weekend': current_day.weekday() >= 5,  # Samedi=5, Dimanche=6
            'events': day_events,
            'is_occupied': len(day_events) > 0,
            'event_count': len(day_events),
            'is_blocked': is_blocked,
            'blocked_reason': blocked_info.get_reason_display() if blocked_info else None,
            'blocked_notes': blocked_info.notes if blocked_info else None,
        })
        
        current_day += timedelta(days=1)
    
    # Statistiques du mois
    total_days = len(calendar_days)
    occupied_days = sum(1 for day in calendar_days if day['is_occupied'])
    blocked_days = sum(1 for day in calendar_days if day['is_blocked'])
    free_days = total_days - occupied_days - blocked_days
    occupation_rate = (occupied_days / total_days * 100) if total_days > 0 else 0
    
    # Mois précédent et suivant
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    return {
        'year': year,
        'month': month,
        'month_name': first_day.strftime('%B'),
        'month_name_fr': get_french_month_name(month),
        'days': calendar_days,
        'total_days': total_days,
        'occupied_days': occupied_days,
        'blocked_days': blocked_days,
        'free_days': free_days,
        'occupation_rate': round(occupation_rate, 1),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'first_weekday': first_day.weekday(),  # 0=Lundi, 6=Dimanche
    }


def get_french_month_name(month):
    """Retourner le nom du mois en français"""
    months = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    return months.get(month, '')


def get_all_locations_availability(year=None, month=None):
    """
    Obtenir un résumé de disponibilité pour tous les lieux
    
    Returns:
        list: Liste de dictionnaires avec infos de disponibilité par lieu
    """
    from locations.models import Location
    
    locations = Location.objects.filter(status='AVAILABLE')
    availability_data = []
    
    for location in locations:
        calendar_data = get_location_calendar_data(location, year, month)
        availability_data.append({
            'location': location,
            'occupied_days': calendar_data['occupied_days'],
            'free_days': calendar_data['free_days'],
            'occupation_rate': calendar_data['occupation_rate'],
        })
    
    return availability_data
