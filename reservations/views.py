from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg, F
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from django.contrib.auth.models import User
from .models import Reservation
from events.models import Event
from .email_service import send_reservation_confirmation_email
from .qr_generator import get_qr_code_url
import json
from datetime import datetime, timedelta
from django.utils import timezone

# User Story 3.2 : Liste de mes réservations
@login_required
def reservation_list(request):
    """Afficher toutes les réservations de l'utilisateur connecté"""
    reservations = Reservation.objects.filter(user=request.user).select_related('event')
    
    context = {
        'reservations': reservations,
        'active_reservations': reservations.filter(status='CONFIRMEE'),
        'cancelled_reservations': reservations.filter(status='ANNULEE'),
    }
    return render(request, 'reservations/reservation_list.html', context)

# User Story 3.1 : Créer une réservation
@login_required
def reservation_create(request, event_id):
    """Créer une nouvelle réservation pour un événement"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        number_of_seats = int(request.POST.get('number_of_seats', 1))
        notes = request.POST.get('notes', '')
        
        # Vérifications
        if not event.is_available():
            messages.error(request, "Cet événement n'est pas disponible pour la réservation.")
            return redirect('event_list')
        
        if event.available_seats < number_of_seats:
            messages.error(request, f"Seulement {event.available_seats} places disponibles.")
            return redirect('reservation_create', event_id=event.id)
        # Créer la réservation
        from payments.models import Invoice
        
        reservation = Reservation.objects.create(
            user=request.user,
            event=event,
            number_of_seats=number_of_seats,
            notes=notes,
            status='CONFIRMEE'
        )
        
        # Mettre à jour les places disponibles
        event.available_seats -= number_of_seats
        event.save()
        
        # US 4.1 : Générer automatiquement une facture pour le client
        from payments.models import Invoice
        from decimal import Decimal
        
        tax_rate = Decimal('0.19')  # TVA 19%
        subtotal = reservation.total_price
        tax_amount = subtotal * tax_rate
        total_with_tax = subtotal + tax_amount
        
        invoice = Invoice.objects.create(
            reservation=reservation,
            total_amount=total_with_tax,
            tax_amount=tax_amount,
            discount_amount=Decimal('0.00'),
            status='ISSUED',  # Facture émise automatiquement
            notes=f"Facture générée automatiquement pour la réservation {reservation.reservation_code}"
        )
        invoice.mark_as_issued()  # Marquer comme émise avec date
        
        # Envoyer l'email de confirmation avec le QR code
        email_sent, email_message = send_reservation_confirmation_email(reservation)
        
        if email_sent:
            messages.success(
                request, 
                f"✅ Réservation confirmée ! Code : {reservation.reservation_code}. "
                f"Facture N° {invoice.invoice_number} générée. "
                f"Un email de confirmation avec votre billet et QR code a été envoyé à {request.user.email or 'moalla.melek09@gmail.com'}."
            )
        else:
            messages.success(
                request, 
                f"✅ Réservation confirmée ! Code : {reservation.reservation_code}. "
                f"Facture N° {invoice.invoice_number} générée."
            )
            messages.warning(
                request,
                f"⚠️ Erreur d'envoi d'email : {email_message}. Veuillez vérifier votre configuration email."
            )
        
        return redirect('reservation_detail', pk=reservation.id)
    
    context = {
        'event': event,
    }
    return render(request, 'reservations/reservation_create.html', context)
# Détail d'une réservation
@login_required
def reservation_detail(request, pk):
    """Afficher les détails d'une réservation avec facture"""
    reservation = get_object_or_404(Reservation, id=pk, user=request.user)
    
    # Générer le QR code
    qr_code_url = get_qr_code_url(reservation)
    
    # US 4.1 : Récupérer la facture associée
    from payments.models import Invoice, Payment
    try:
        invoice = Invoice.objects.get(reservation=reservation)
    except Invoice.DoesNotExist:
        invoice = None
    
    # Récupérer les paiements associés
    payments = Payment.objects.filter(reservation=reservation).order_by('-created_at')
    
    context = {
        'reservation': reservation,
        'qr_code_url': qr_code_url,
        'invoice': invoice,
        'payments': payments,
    }
    return render(request, 'reservations/reservation_detail.html', context)
    return render(request, 'reservations/reservation_detail.html', context)

# User Story 3.3 : Annuler une réservation
@login_required
def reservation_cancel(request, pk):
    """Annuler une réservation"""
    reservation = get_object_or_404(Reservation, id=pk, user=request.user)
    
    if request.method == 'POST':
        if not reservation.can_be_cancelled():
            messages.error(request, "Cette réservation ne peut pas être annulée.")
        else:
            reservation.cancel()
            messages.success(request, "Réservation annulée avec succès.")
        
        return redirect('reservation_list')
    
    context = {
        'reservation': reservation,
    }
    return render(request, 'reservations/reservation_cancel.html', context)

# Modifier une réservation
@login_required
def reservation_update(request, pk):
    """Modifier une réservation"""
    reservation = get_object_or_404(Reservation, id=pk, user=request.user)
    
    if reservation.status == 'ANNULEE':
        messages.error(request, "Impossible de modifier une réservation annulée.")
        return redirect('reservation_list')
    
    if request.method == 'POST':
        old_seats = reservation.number_of_seats
        new_seats = int(request.POST.get('number_of_seats', old_seats))
        notes = request.POST.get('notes', '')
        
        # Vérifier la disponibilité si augmentation
        seats_diff = new_seats - old_seats
        if seats_diff > 0:
            if reservation.event.available_seats < seats_diff:
                messages.error(
                    request, 
                    f"Seulement {reservation.event.available_seats} places supplémentaires disponibles."
                )
                return redirect('reservation_update', pk=pk)
            
            # Réduire les places disponibles
            reservation.event.available_seats -= seats_diff
            reservation.event.save()
        elif seats_diff < 0:
            # Libérer des places
            reservation.event.available_seats += abs(seats_diff)
            reservation.event.save()
        
        # Mettre à jour la réservation
        reservation.number_of_seats = new_seats
        reservation.notes = notes
        reservation.total_price = reservation.event.price_per_person * new_seats
        reservation.save()
        
        messages.success(request, "Réservation modifiée avec succès.")
        return redirect('reservation_detail', pk=pk)
    
    context = {
        'reservation': reservation,
    }
    return render(request, 'reservations/reservation_update.html', context)

# Renvoyer l'email de confirmation
@login_required
def resend_confirmation_email(request, pk):
    """Renvoyer l'email de confirmation avec le billet"""
    reservation = get_object_or_404(Reservation, id=pk, user=request.user)
    
    if reservation.status == 'ANNULEE':
        messages.error(request, "Impossible d'envoyer un email pour une réservation annulée.")
        return redirect('reservation_detail', pk=pk)
    
    # Envoyer l'email
    email_sent, email_message = send_reservation_confirmation_email(reservation)
    
    if email_sent:
        messages.success(
            request,
            f"✅ Email de confirmation renvoyé avec succès à {request.user.email or 'moalla.melek09@gmail.com'} !"
        )
    else:
        messages.error(
            request,
            f"❌ Erreur lors de l'envoi : {email_message}"
        )
    
    return redirect('reservation_detail', pk=pk)

# Tableau de bord avec statistiques
@login_required
def dashboard(request):
    """Afficher les statistiques personnelles de l'utilisateur"""
    user = request.user
    
    # Récupérer toutes les réservations de l'utilisateur
    all_reservations = Reservation.objects.filter(user=user).select_related('event')
    active_reservations = all_reservations.filter(status='CONFIRMEE')
    
    # 1. Nombre total de réservations
    total_reservations = all_reservations.count()
    total_active = active_reservations.count()
    total_cancelled = all_reservations.filter(status='ANNULEE').count()
    
    # 2. Montant total dépensé (uniquement réservations confirmées)
    total_spent = active_reservations.aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # 3. Nombre total de places réservées
    total_seats = active_reservations.aggregate(
        total=Sum('number_of_seats')
    )['total'] or 0
    
    # 4. Catégorie préférée (événements les plus fréquentés)
    category_stats = active_reservations.values(
        'event__category'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    favorite_category = None
    favorite_category_count = 0
    category_distribution = []
    
    if category_stats:
        favorite_category_code = category_stats[0]['event__category']
        favorite_category_count = category_stats[0]['count']
        
        # Obtenir le nom lisible de la catégorie
        category_choices = dict(Event.CATEGORY_CHOICES)
        favorite_category = category_choices.get(favorite_category_code, favorite_category_code)
        
        # Distribution par catégorie pour le graphique
        for cat in category_stats:
            cat_code = cat['event__category']
            category_distribution.append({
                'name': category_choices.get(cat_code, cat_code),
                'value': cat['count']
            })
    
    # 5. Réservations par mois (pour le graphique)
    # Créer les 12 derniers mois avec les données réelles + simulation
    from dateutil.relativedelta import relativedelta
    
    months_labels = []
    reservations_count = []
    spending_data = []
    
    # Générer les 12 derniers mois
    current_date = datetime.now()
    for i in range(11, -1, -1):
        month_date = current_date - relativedelta(months=i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculer le début du mois suivant
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Compter les réservations réelles pour ce mois
        real_count = all_reservations.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        real_amount = all_reservations.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # Ajouter au graphique
        month_name = month_date.strftime('%B %Y')
        months_labels.append(month_name)
        reservations_count.append(real_count)
        spending_data.append(float(real_amount))
    
    # 6. Événement à venir le plus proche
    upcoming_event = active_reservations.filter(
        event__date__gte=datetime.now()
    ).order_by('event__date').first()
    
    # 7. Prochain événement passé (dernier événement assisté)
    last_attended_event = active_reservations.filter(
        event__date__lt=datetime.now()
    ).order_by('-event__date').first()
    
    context = {
        'total_reservations': total_reservations,
        'total_active': total_active,
        'total_cancelled': total_cancelled,
        'total_spent': total_spent,
        'total_seats': total_seats,
        'favorite_category': favorite_category,
        'favorite_category_count': favorite_category_count,
        'category_distribution': json.dumps(category_distribution),
        'months_labels': json.dumps(months_labels),
        'reservations_count': json.dumps(reservations_count),
        'spending_data': json.dumps(spending_data),
        'upcoming_event': upcoming_event,
        'last_attended_event': last_attended_event,
    }
    
    return render(request, 'reservations/dashboard.html', context)


# ==================== DASHBOARD ADMINISTRATEUR ====================

@staff_member_required
def admin_dashboard(request):
    """Dashboard administrateur avec statistiques complètes de la plateforme"""
    
    now = timezone.now()
    
    # ============ STATISTIQUES GLOBALES ============
    
    # Totaux généraux
    total_users = User.objects.count()
    total_events = Event.objects.count()
    total_reservations = Reservation.objects.count()
    active_reservations = Reservation.objects.filter(status='CONFIRMEE').count()
    cancelled_reservations = Reservation.objects.filter(status='ANNULEE').count()
    
    # Revenus
    total_revenue = Reservation.objects.filter(
        status='CONFIRMEE'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    cancelled_revenue = Reservation.objects.filter(
        status='ANNULEE'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Places vendues
    total_seats_sold = Reservation.objects.filter(
        status='CONFIRMEE'
    ).aggregate(total=Sum('number_of_seats'))['total'] or 0
    
    # Capacité totale
    total_capacity = Event.objects.aggregate(total=Sum('capacity'))['total'] or 0
    available_capacity = Event.objects.aggregate(total=Sum('available_seats'))['total'] or 0
    occupied_capacity = total_capacity - available_capacity
    occupation_rate = (occupied_capacity / total_capacity * 100) if total_capacity > 0 else 0
    
    # Revenus moyens par réservation
    avg_reservation_value = Reservation.objects.filter(
        status='CONFIRMEE'
    ).aggregate(avg=Avg('total_price'))['avg'] or 0
    
    # ============ ÉVÉNEMENTS ============
    
    # Événements par statut
    events_by_status = Event.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    events_status_labels = []
    events_status_data = []
    for item in events_by_status:
        status_dict = dict(Event.STATUS_CHOICES)
        events_status_labels.append(status_dict.get(item['status'], item['status']))
        events_status_data.append(item['count'])
    
    # Événements par catégorie
    events_by_category = Event.objects.values('category').annotate(
        count=Count('id'),
        total_capacity=Sum('capacity'),
        total_reservations=Count('reservations')
    ).order_by('-count')
    
    category_labels = []
    category_events = []
    category_reservations = []
    for item in events_by_category:
        category_dict = dict(Event.CATEGORY_CHOICES)
        category_labels.append(category_dict.get(item['category'], item['category']))
        category_events.append(item['count'])
        category_reservations.append(item['total_reservations'])
    
    # Top 5 événements par réservations
    top_events = Event.objects.annotate(
        reservation_count=Count('reservations', filter=Q(reservations__status='CONFIRMEE'))
    ).order_by('-reservation_count')[:5]
    
    top_events_labels = [e.title[:30] for e in top_events]
    top_events_data = [e.reservation_count for e in top_events]
    
    # Événements à venir
    upcoming_events = Event.objects.filter(
        date__gte=now,
        status='CONFIRME'
    ).order_by('date')[:10]
    
    # Événements complets
    full_events = Event.objects.filter(
        available_seats=0,
        status='CONFIRME'
    ).count()
    
    # ============ RÉSERVATIONS ============
    
    # Réservations des 30 derniers jours
    thirty_days_ago = now - timedelta(days=30)
    recent_reservations = Reservation.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    # Réservations par jour (7 derniers jours)
    seven_days_ago = now - timedelta(days=7)
    daily_reservations = Reservation.objects.filter(
        created_at__gte=seven_days_ago
    ).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        total=Count('id'),
        confirmed=Count('id', filter=Q(status='CONFIRMEE')),
        cancelled=Count('id', filter=Q(status='ANNULEE'))
    ).order_by('day')
    
    daily_labels = []
    daily_confirmed = []
    daily_cancelled = []
    for item in daily_reservations:
        daily_labels.append(item['day'].strftime('%d/%m'))
        daily_confirmed.append(item['confirmed'])
        daily_cancelled.append(item['cancelled'])
    
    # Réservations par mois (12 derniers mois)
    twelve_months_ago = now - timedelta(days=365)
    monthly_reservations = Reservation.objects.filter(
        created_at__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Count('id'),
        revenue=Sum('total_price', filter=Q(status='CONFIRMEE'))
    ).order_by('month')
    
    monthly_labels = []
    monthly_counts = []
    monthly_revenue = []
    for item in monthly_reservations:
        monthly_labels.append(item['month'].strftime('%b %Y'))
        monthly_counts.append(item['total'])
        monthly_revenue.append(float(item['revenue'] or 0))
    
    # Réservations par statut
    reservations_by_status = Reservation.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    status_labels = []
    status_data = []
    for item in reservations_by_status:
        status_dict = dict(Reservation.STATUS_CHOICES)
        status_labels.append(status_dict.get(item['status'], item['status']))
        status_data.append(item['count'])
    
    # Distribution des places par réservation
    seats_distribution = Reservation.objects.filter(
        status='CONFIRMEE'
    ).values('number_of_seats').annotate(
        count=Count('id')
    ).order_by('number_of_seats')
    
    seats_labels = [f"{item['number_of_seats']} place(s)" for item in seats_distribution]
    seats_data = [item['count'] for item in seats_distribution]
    
    # ============ UTILISATEURS ============
    
    # Utilisateurs actifs (avec au moins une réservation)
    active_users = User.objects.annotate(
        reservation_count=Count('reservations')
    ).filter(reservation_count__gt=0).count()
    
    # Top 10 utilisateurs par nombre de réservations
    top_users = User.objects.annotate(
        reservation_count=Count('reservations', filter=Q(reservations__status='CONFIRMEE')),
        total_spent=Sum('reservations__total_price', filter=Q(reservations__status='CONFIRMEE'))
    ).filter(reservation_count__gt=0).order_by('-reservation_count')[:10]
    
    # Nouveaux utilisateurs (30 derniers jours)
    new_users = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).count()
    
    # ============ ANALYSES ============
    
    # Taux de conversion (événements avec réservations / total événements)
    events_with_reservations = Event.objects.annotate(
        res_count=Count('reservations')
    ).filter(res_count__gt=0).count()
    
    conversion_rate = (events_with_reservations / total_events * 100) if total_events > 0 else 0
    
    # Taux d'annulation
    cancellation_rate = (cancelled_reservations / total_reservations * 100) if total_reservations > 0 else 0
    
    # Prix moyen par place
    avg_price_per_seat = (total_revenue / total_seats_sold) if total_seats_sold > 0 else 0
    
    # Réservations récentes (5 dernières)
    latest_reservations = Reservation.objects.select_related(
        'user', 'event'
    ).order_by('-created_at')[:5]
    
    # ============ CONTEXTE ============
    
    context = {
        # Totaux généraux
        'total_users': total_users,
        'total_events': total_events,
        'total_reservations': total_reservations,
        'active_reservations': active_reservations,
        'cancelled_reservations': cancelled_reservations,
        'total_revenue': total_revenue,
        'cancelled_revenue': cancelled_revenue,
        'total_seats_sold': total_seats_sold,
        'avg_reservation_value': avg_reservation_value,
        'recent_reservations_count': recent_reservations,
        'new_users': new_users,
        'active_users': active_users,
        
        # Capacité
        'total_capacity': total_capacity,
        'available_capacity': available_capacity,
        'occupied_capacity': occupied_capacity,
        'occupation_rate': round(occupation_rate, 2),
        
        # Taux et moyennes
        'conversion_rate': round(conversion_rate, 2),
        'cancellation_rate': round(cancellation_rate, 2),
        'avg_price_per_seat': round(avg_price_per_seat, 2),
        
        # Événements
        'full_events': full_events,
        'upcoming_events': upcoming_events,
        'top_events': top_events,
        'events_status_labels': json.dumps(events_status_labels),
        'events_status_data': json.dumps(events_status_data),
        'category_labels': json.dumps(category_labels),
        'category_events': json.dumps(category_events),
        'category_reservations': json.dumps(category_reservations),
        'top_events_labels': json.dumps(top_events_labels),
        'top_events_data': json.dumps(top_events_data),
        
        # Réservations
        'daily_labels': json.dumps(daily_labels),
        'daily_confirmed': json.dumps(daily_confirmed),
        'daily_cancelled': json.dumps(daily_cancelled),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_counts': json.dumps(monthly_counts),
        'monthly_revenue': json.dumps(monthly_revenue),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'seats_labels': json.dumps(seats_labels),
        'seats_data': json.dumps(seats_data),
        'latest_reservations': latest_reservations,
        
        # Utilisateurs
        'top_users': top_users,
    }
    
    return render(request, 'reservations/admin_dashboard.html', context)
