from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from .models import Event, EventRecommendation, RecommendationHelpful
from .forms import EventForm, RecommendationForm

def event_list(request):
    """Liste de tous les événements disponibles"""
    events = Event.objects.filter(status='CONFIRME').order_by('date')
    
    # Filtrage par catégorie
    category = request.GET.get('category')
    if category:
        events = events.filter(category=category)
    
    context = {
        'events': events,
        'categories': Event.CATEGORY_CHOICES,
        'selected_category': category,
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, pk):
    """Détails d'un événement"""
    event = get_object_or_404(Event, id=pk)
    
    # Récupérer les recommandations approuvées
    recommendations = event.recommendations.filter(is_approved=True).order_by('-is_featured', '-created_at')[:5]
    
    # Vérifier si l'utilisateur a déjà laissé une recommandation
    user_recommendation = None
    if request.user.is_authenticated:
        user_recommendation = event.recommendations.filter(user=request.user).first()
    
    context = {
        'event': event,
        'recommendations': recommendations,
        'user_recommendation': user_recommendation,
        'average_rating': event.get_average_rating(),
        'recommendations_count': event.get_recommendations_count(),
    }
    return render(request, 'events/event_detail.html', context)


# US 1.1 : Créer un événement (Admin)
@staff_member_required
def event_create(request):
    """Créer un nouveau événement (admin seulement)"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            # Par défaut, les nouveaux événements sont en brouillon
            if not event.status:
                event.status = 'BROUILLON'
            event.save()
            
            messages.success(
                request, 
                f"✅ Événement '{event.title}' créé avec succès ! Statut : {event.get_status_display()}"
            )
            return redirect('event_detail', pk=event.id)
    else:
        form = EventForm(initial={'status': 'BROUILLON'})
    
    context = {
        'form': form,
        'title': 'Créer un nouvel événement',
        'button_text': 'Créer l\'événement'
    }
    return render(request, 'events/event_form.html', context)


# Modifier un événement (Admin)
@staff_member_required
def event_update(request, pk):
    """Modifier un événement existant (admin seulement)"""
    event = get_object_or_404(Event, id=pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(
                request, 
                f"✅ Événement '{event.title}' modifié avec succès !"
            )
            return redirect('event_detail', pk=event.id)
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'title': f'Modifier : {event.title}',
        'button_text': 'Enregistrer les modifications'
    }
    return render(request, 'events/event_form.html', context)


# US 1.2 : Confirmer un événement (Admin)
@staff_member_required
def event_confirm(request, pk):
    """Confirmer un événement pour le rendre public"""
    event = get_object_or_404(Event, id=pk)
    
    if request.method == 'POST':
        if event.status == 'CONFIRME':
            messages.warning(request, "Cet événement est déjà confirmé.")
        else:
            event.status = 'CONFIRME'
            event.save()
            messages.success(
                request, 
                f"✅ Événement '{event.title}' confirmé et disponible au public !"
            )
        return redirect('event_detail', pk=event.id)
    
    context = {
        'event': event,
    }
    return render(request, 'events/event_confirm.html', context)


# Supprimer un événement (Admin)
@staff_member_required
def event_delete(request, pk):
    """Supprimer ou annuler un événement"""
    event = get_object_or_404(Event, id=pk)
    
    # Vérifier s'il y a des réservations
    has_reservations = event.reservation_set.exists()
    
    if request.method == 'POST':
        if has_reservations:
            # Soft delete : annuler l'événement
            event.status = 'ANNULE'
            event.save()
            messages.success(
                request, 
                f"✅ Événement '{event.title}' annulé (des réservations existaient)."
            )
        else:
            # Hard delete : supprimer complètement
            event_title = event.title
            event.delete()
            messages.success(
                request, 
                f"✅ Événement '{event_title}' supprimé définitivement."
            )
        return redirect('event_list')
    
    context = {
        'event': event,
        'has_reservations': has_reservations,
    }
    return render(request, 'events/event_delete.html', context)


# ===== SYSTÈME DE RECOMMANDATIONS =====

@login_required
@login_required
def recommendation_create(request, event_id):
    """Créer une recommandation pour un événement"""
    event = get_object_or_404(Event, id=event_id)
    
    # Vérifier si l'utilisateur a déjà une recommandation
    existing_recommendation = EventRecommendation.objects.filter(
        event=event,
        user=request.user
    ).first()
    
    if existing_recommendation:
        messages.warning(request, "Vous avez déjà laissé une recommandation pour cet événement.")
        return redirect('recommendation_update', pk=existing_recommendation.id)
    
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            recommendation = form.save(commit=False)
            recommendation.event = event
            recommendation.user = request.user
            
            # Convertir les valeurs string en int pour les ratings
            recommendation.rating = int(form.cleaned_data['rating'])
            recommendation.organization_rating = int(form.cleaned_data['organization_rating'])
            recommendation.ambiance_rating = int(form.cleaned_data['ambiance_rating'])
            recommendation.value_rating = int(form.cleaned_data['value_rating'])
            recommendation.venue_rating = int(form.cleaned_data['venue_rating'])
            
            recommendation.save()
            
            messages.success(request, "✅ Votre recommandation a été ajoutée avec succès !")
            return redirect('event_detail', pk=event.id)
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RecommendationForm()
    
    context = {
        'form': form,
        'event': event,
        'action': 'Créer'
    }
    return render(request, 'events/recommendation_form.html', context)


@login_required
@login_required
def recommendation_update(request, pk):
    """Modifier une recommandation"""
    recommendation = get_object_or_404(EventRecommendation, id=pk)
    
    # Vérifier que l'utilisateur est le propriétaire
    if recommendation.user != request.user and not request.user.is_staff:
        messages.error(request, "Vous ne pouvez pas modifier cette recommandation.")
        return redirect('event_detail', pk=recommendation.event.id)
    
    if request.method == 'POST':
        form = RecommendationForm(request.POST, instance=recommendation)
        if form.is_valid():
            updated_recommendation = form.save(commit=False)
            
            # Convertir les valeurs string en int pour les ratings
            updated_recommendation.rating = int(form.cleaned_data['rating'])
            updated_recommendation.organization_rating = int(form.cleaned_data['organization_rating'])
            updated_recommendation.ambiance_rating = int(form.cleaned_data['ambiance_rating'])
            updated_recommendation.value_rating = int(form.cleaned_data['value_rating'])
            updated_recommendation.venue_rating = int(form.cleaned_data['venue_rating'])
            
            updated_recommendation.save()
            messages.success(request, "✅ Votre recommandation a été mise à jour !")
            return redirect('event_detail', pk=recommendation.event.id)
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Initialiser le formulaire avec les valeurs converties en string pour les ChoiceFields
        initial_data = {
            'rating': str(recommendation.rating),
            'organization_rating': str(recommendation.organization_rating),
            'ambiance_rating': str(recommendation.ambiance_rating),
            'value_rating': str(recommendation.value_rating),
            'venue_rating': str(recommendation.venue_rating),
        }
        form = RecommendationForm(instance=recommendation, initial=initial_data)
    
    context = {
        'form': form,
        'event': recommendation.event,
        'recommendation': recommendation,
        'action': 'Modifier'
    }
    return render(request, 'events/recommendation_form.html', context)


@login_required
def recommendation_delete(request, pk):
    """Supprimer une recommandation"""
    recommendation = get_object_or_404(EventRecommendation, id=pk)
    event_id = recommendation.event.id
    
    # Vérifier que l'utilisateur est le propriétaire ou admin
    if recommendation.user != request.user and not request.user.is_staff:
        messages.error(request, "Vous ne pouvez pas supprimer cette recommandation.")
        return redirect('event_detail', pk=event_id)
    
    if request.method == 'POST':
        recommendation.delete()
        messages.success(request, "✅ Votre recommandation a été supprimée.")
        return redirect('event_detail', pk=event_id)
    
    context = {
        'recommendation': recommendation,
    }
    return render(request, 'events/recommendation_delete.html', context)


@login_required
def recommendation_helpful(request, pk):
    """Marquer une recommandation comme utile"""
    recommendation = get_object_or_404(EventRecommendation, id=pk)
    
    # Vérifier si l'utilisateur a déjà voté
    helpful, created = RecommendationHelpful.objects.get_or_create(
        recommendation=recommendation,
        user=request.user
    )
    
    if created:
        recommendation.helpful_count += 1
        recommendation.save()
        messages.success(request, "✅ Merci pour votre vote !")
    else:
        helpful.delete()
        recommendation.helpful_count -= 1
        recommendation.save()
        messages.info(request, "Vote retiré.")
    
    return redirect('event_detail', pk=recommendation.event.id)


def recommendation_list(request, event_id):
    """Liste de toutes les recommandations d'un événement"""
    event = get_object_or_404(Event, id=event_id)
    
    recommendations = event.recommendations.filter(is_approved=True).order_by('-is_featured', '-created_at')
    
    # Filtres
    rating_filter = request.GET.get('rating')
    if rating_filter:
        recommendations = recommendations.filter(rating=int(rating_filter))
    
    sort_by = request.GET.get('sort', 'recent')
    if sort_by == 'helpful':
        recommendations = recommendations.order_by('-helpful_count', '-created_at')
    elif sort_by == 'rating_high':
        recommendations = recommendations.order_by('-rating', '-created_at')
    elif sort_by == 'rating_low':
        recommendations = recommendations.order_by('rating', '-created_at')
    
    # Pagination
    paginator = Paginator(recommendations, 10)
    page_number = request.GET.get('page')
    recommendations_page = paginator.get_page(page_number)
    
    context = {
        'event': event,
        'recommendations': recommendations_page,
        'average_rating': event.get_average_rating(),
        'total_count': event.get_recommendations_count(),
        'rating_filter': rating_filter,
        'sort_by': sort_by,
    }
    return render(request, 'events/recommendation_list.html', context)


# ===== ADMIN: GESTION DES RECOMMANDATIONS =====

@staff_member_required
def admin_recommendation_list(request):
    """Liste de toutes les recommandations (admin)"""
    recommendations = EventRecommendation.objects.select_related('event', 'user').order_by('-created_at')
    
    # Filtres
    status = request.GET.get('status')
    if status == 'approved':
        recommendations = recommendations.filter(is_approved=True)
    elif status == 'pending':
        recommendations = recommendations.filter(is_approved=False)
    elif status == 'featured':
        recommendations = recommendations.filter(is_featured=True)
    
    rating_filter = request.GET.get('rating')
    if rating_filter:
        recommendations = recommendations.filter(rating=int(rating_filter))
    
    # Recherche
    search = request.GET.get('search')
    if search:
        recommendations = recommendations.filter(
            Q(title__icontains=search) |
            Q(comment__icontains=search) |
            Q(user__username__icontains=search) |
            Q(event__title__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(recommendations, 20)
    page_number = request.GET.get('page')
    recommendations_page = paginator.get_page(page_number)
    
    # Statistiques
    total_count = EventRecommendation.objects.count()
    approved_count = EventRecommendation.objects.filter(is_approved=True).count()
    pending_count = EventRecommendation.objects.filter(is_approved=False).count()
    featured_count = EventRecommendation.objects.filter(is_featured=True).count()
    average_rating = EventRecommendation.objects.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'recommendations': recommendations_page,
        'total_count': total_count,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'featured_count': featured_count,
        'average_rating': round(average_rating, 1),
        'status': status or '',
        'rating_filter': rating_filter or '',
        'search': search or '',
    }
    return render(request, 'events/admin_recommendation_list.html', context)


@staff_member_required
def admin_recommendation_detail(request, pk):
    """Détails d'une recommandation (admin)"""
    recommendation = get_object_or_404(EventRecommendation, id=pk)
    
    context = {
        'recommendation': recommendation,
    }
    return render(request, 'events/admin_recommendation_detail.html', context)


@staff_member_required
def admin_recommendation_approve(request, pk):
    """Approuver/désapprouver une recommandation"""
    recommendation = get_object_or_404(EventRecommendation, id=pk)
    
    recommendation.is_approved = not recommendation.is_approved
    recommendation.save()
    
    status = "approuvée" if recommendation.is_approved else "désapprouvée"
    messages.success(request, f"✅ Recommandation {status}.")
    
    return redirect('admin_recommendation_detail', pk=pk)


@staff_member_required
def admin_recommendation_feature(request, pk):
    """Mettre en avant/retirer la mise en avant d'une recommandation"""
    recommendation = get_object_or_404(EventRecommendation, id=pk)
    
    recommendation.is_featured = not recommendation.is_featured
    recommendation.save()
    
    status = "mise en avant" if recommendation.is_featured else "retirée de la mise en avant"
    messages.success(request, f"✅ Recommandation {status}.")
    
    return redirect('admin_recommendation_detail', pk=pk)


@staff_member_required
def admin_recommendation_respond(request, pk):
    """Répondre à une recommandation"""
    recommendation = get_object_or_404(EventRecommendation, id=pk)
    
    if request.method == 'POST':
        admin_response = request.POST.get('admin_response', '')
        recommendation.admin_response = admin_response
        recommendation.save()
        
        messages.success(request, "✅ Réponse enregistrée.")
        return redirect('admin_recommendation_detail', pk=pk)
    
    context = {
        'recommendation': recommendation,
    }
    return render(request, 'events/admin_recommendation_respond.html', context)


@staff_member_required
def admin_recommendation_delete(request, pk):
    """Supprimer une recommandation (admin)"""
    recommendation = get_object_or_404(EventRecommendation, id=pk)
    
    if request.method == 'POST':
        recommendation.delete()
        messages.success(request, "✅ Recommandation supprimée.")
        return redirect('admin_recommendation_list')
    
    context = {
        'recommendation': recommendation,
    }
    return render(request, 'events/admin_recommendation_delete.html', context)
