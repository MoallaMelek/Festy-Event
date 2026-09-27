from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from .models import Complaint
from .forms import ComplaintForm, ComplaintResponseForm


# US 6.1 : Soumettre une réclamation (Utilisateur)
@login_required
def complaint_create(request):
    """Créer une nouvelle réclamation"""
    if request.method == 'POST':
        form = ComplaintForm(request.POST, user=request.user)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            
            messages.success(
                request,
                f'Votre réclamation #{complaint.id} a été soumise avec succès. '
                'Notre équipe vous répondra dans les plus brefs délais.'
            )
            return redirect('complaint_detail', pk=complaint.id)
    else:
        form = ComplaintForm(user=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'complaints/complaint_form.html', context)


# US 6.2 : Voir mes réclamations (Utilisateur)
@login_required
def complaint_list(request):
    """Liste des réclamations de l'utilisateur"""
    complaints = Complaint.objects.filter(user=request.user)
    
    # Statistiques
    total_complaints = complaints.count()
    new_complaints = complaints.filter(status='NEW').count()
    in_progress = complaints.filter(status='IN_PROGRESS').count()
    resolved = complaints.filter(status='RESOLVED').count()
    
    context = {
        'complaints': complaints,
        'total_complaints': total_complaints,
        'new_complaints': new_complaints,
        'in_progress': in_progress,
        'resolved': resolved,
    }
    return render(request, 'complaints/complaint_list.html', context)


# Détails d'une réclamation (Utilisateur)
@login_required
def complaint_detail(request, pk):
    """Voir les détails d'une réclamation"""
    complaint = get_object_or_404(Complaint, id=pk, user=request.user)
    
    context = {
        'complaint': complaint,
    }
    return render(request, 'complaints/complaint_detail.html', context)


# US 6.3 : Gérer les réclamations (Admin)
@staff_member_required
def admin_complaint_list(request):
    """Liste de toutes les réclamations (admin)"""
    # Filtrage
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    
    complaints = Complaint.objects.all().select_related('user', 'reservation', 'event')
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    
    # Statistiques
    total_complaints = Complaint.objects.count()
    new_complaints = Complaint.objects.filter(status='NEW').count()
    in_progress = Complaint.objects.filter(status='IN_PROGRESS').count()
    resolved = Complaint.objects.filter(status='RESOLVED').count()
    
    context = {
        'complaints': complaints,
        'total_complaints': total_complaints,
        'new_complaints': new_complaints,
        'in_progress': in_progress,
        'resolved': resolved,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': Complaint.STATUS_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
    }
    return render(request, 'complaints/admin_complaint_list.html', context)


# US 6.3 & 6.4 : Répondre à une réclamation (Admin)
@staff_member_required
def admin_complaint_respond(request, pk):
    """Répondre à une réclamation"""
    complaint = get_object_or_404(Complaint, id=pk)
    
    if request.method == 'POST':
        form = ComplaintResponseForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint = form.save(commit=False)
            
            # Enregistrer qui a répondu et quand
            if complaint.admin_response and not complaint.responded_at:
                complaint.responded_by = request.user
                complaint.responded_at = timezone.now()
            
            complaint.save()
            
            messages.success(
                request,
                f'Votre réponse à la réclamation #{complaint.id} a été enregistrée.'
            )
            return redirect('admin_complaint_list')
    else:
        form = ComplaintResponseForm(instance=complaint)
    
    context = {
        'form': form,
        'complaint': complaint,
    }
    return render(request, 'complaints/admin_complaint_respond.html', context)
