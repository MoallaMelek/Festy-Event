from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .forms import UserRegistrationForm, UserProfileForm, UserDeleteForm
from reservations.models import Reservation


# US 2.1 : Inscription
def register(request):
    """Créer un nouveau compte utilisateur"""
    if request.user.is_authenticated:
        return redirect('event_list')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Connexion automatique après inscription
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Bienvenue {username} ! Votre compte a été créé avec succès.')
            return redirect('event_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


# US 2.2 : Connexion
def user_login(request):
    """Se connecter à son compte"""
    if request.user.is_authenticated:
        # Redirection selon le rôle
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirection selon le rôle après login
            if user.is_staff:
                messages.success(request, f'Bienvenue Administrateur {user.username} !')
                return redirect('admin_dashboard')
            else:
                messages.success(request, f'Bienvenue {user.first_name or username} !')
                return redirect('dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'users/login.html')


# US 2.3 : Déconnexion
@login_required
def user_logout(request):
    """Se déconnecter de son compte"""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Vous avez été déconnecté avec succès.')
        return redirect('event_list')
    return redirect('event_list')


# US 2.4 : Modification du profil
@login_required
def profile(request):
    """Afficher et modifier le profil utilisateur"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Statistiques utilisateur
    reservations = Reservation.objects.filter(user=request.user)
    total_reservations = reservations.count()
    active_reservations = reservations.filter(status='CONFIRMEE').count()
    
    context = {
        'form': form,
        'total_reservations': total_reservations,
        'active_reservations': active_reservations,
    }
    
    return render(request, 'users/profile.html', context)


# US 2.5 : Suppression du compte
@login_required
def delete_account(request):
    """Supprimer définitivement son compte utilisateur"""
    if request.method == 'POST':
        form = UserDeleteForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            
            # Vérifier le mot de passe
            if request.user.check_password(password):
                user = request.user
                logout(request)
                user.delete()
                messages.success(request, 'Votre compte a été supprimé définitivement.')
                return redirect('event_list')
            else:
                messages.error(request, 'Mot de passe incorrect.')
    else:
        form = UserDeleteForm()
    
    # Compter les réservations actives
    active_reservations = Reservation.objects.filter(
        user=request.user,
        status='CONFIRMEE'
    ).count()
    
    context = {
        'form': form,
        'active_reservations': active_reservations,
    }
    
    return render(request, 'users/delete_account.html', context)


# ===== CRUD UTILISATEURS POUR ADMIN =====

def admin_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Vous devez être connecté.')
            return redirect('users:login')
        if not request.user.is_staff:
            messages.error(request, 'Accès réservé aux administrateurs.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_user_list(request):
    """Liste de tous les utilisateurs avec filtres et recherche"""
    users = User.objects.annotate(
        reservation_count=Count('reservations')
    ).order_by('-date_joined')
    
    # Filtres
    user_type = request.GET.get('user_type', '')
    if user_type == 'admin':
        users = users.filter(is_staff=True)
    elif user_type == 'client':
        users = users.filter(is_staff=False)
    
    status = request.GET.get('status', '')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    # Statistiques
    total_users = User.objects.count()
    admin_count = User.objects.filter(is_staff=True).count()
    client_count = User.objects.filter(is_staff=False).count()
    active_count = User.objects.filter(is_active=True).count()
    
    context = {
        'users': users_page,
        'total_users': total_users,
        'admin_count': admin_count,
        'client_count': client_count,
        'active_count': active_count,
        'search': search,
        'user_type': user_type,
        'status': status,
    }
    
    return render(request, 'users/admin_user_list.html', context)


@admin_required
def admin_user_detail(request, user_id):
    """Détails d'un utilisateur"""
    user = get_object_or_404(User, pk=user_id)
    
    # Réservations de l'utilisateur
    reservations = Reservation.objects.filter(user=user).order_by('-created_at')[:10]
    
    # Statistiques
    total_reservations = Reservation.objects.filter(user=user).count()
    confirmed_reservations = Reservation.objects.filter(user=user, status='CONFIRMEE').count()
    cancelled_reservations = Reservation.objects.filter(user=user, status='ANNULEE').count()
    
    context = {
        'user_detail': user,
        'reservations': reservations,
        'total_reservations': total_reservations,
        'confirmed_reservations': confirmed_reservations,
        'cancelled_reservations': cancelled_reservations,
    }
    
    return render(request, 'users/admin_user_detail.html', context)


@admin_required
def admin_user_create(request):
    """Créer un nouvel utilisateur"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Définir le rôle
            is_admin = request.POST.get('is_admin') == 'on'
            user.is_staff = is_admin
            user.is_superuser = is_admin
            user.save()
            
            messages.success(request, f'Utilisateur {user.username} créé avec succès.')
            return redirect('users:admin_user_detail', user_id=user.id)
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/admin_user_form.html', {'form': form, 'action': 'Créer'})


@admin_required
def admin_user_update(request, user_id):
    """Modifier un utilisateur"""
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        # Mise à jour des informations
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Changement de mot de passe (optionnel)
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, f'Utilisateur {user.username} modifié avec succès.')
        return redirect('users:admin_user_detail', user_id=user.id)
    
    context = {
        'user_detail': user,
        'action': 'Modifier'
    }
    
    return render(request, 'users/admin_user_update.html', context)


@admin_required
def admin_user_delete(request, user_id):
    """Supprimer un utilisateur"""
    user = get_object_or_404(User, pk=user_id)
    
    # Empêcher la suppression de son propre compte
    if user == request.user:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('users:admin_user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Utilisateur {username} supprimé avec succès.')
        return redirect('users:admin_user_list')
    
    # Compter les réservations
    reservations_count = Reservation.objects.filter(user=user).count()
    
    context = {
        'user_detail': user,
        'reservations_count': reservations_count,
    }
    
    return render(request, 'users/admin_user_delete.html', context)


@admin_required
def admin_user_toggle_status(request, user_id):
    """Activer/Désactiver un utilisateur"""
    user = get_object_or_404(User, pk=user_id)
    
    if user == request.user:
        messages.error(request, 'Vous ne pouvez pas modifier votre propre statut.')
        return redirect('users:admin_user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'activé' if user.is_active else 'désactivé'
    messages.success(request, f'Utilisateur {user.username} {status}.')
    
    return redirect('users:admin_user_detail', user_id=user.id)

