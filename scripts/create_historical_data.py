"""
Script pour créer des réservations historiques (12 derniers mois)
Pour avoir une belle courbe dynamique dans le tableau de bord
"""

import os
import django
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'festy_event.settings')
django.setup()

from django.contrib.auth.models import User
from reservations.models import Reservation
from events.models import Event
from django.utils import timezone

def create_historical_reservations():
    """Créer des réservations pour les 12 derniers mois"""
    
    # Récupérer l'utilisateur Melek
    user = User.objects.filter(username__icontains='Melek').first()
    
    if not user:
        print("❌ L'utilisateur 'Melek' n'existe pas.")
        return
    
    print(f"👤 Utilisateur : {user.username}\n")
    
    # Récupérer tous les événements
    events = list(Event.objects.all())
    
    if not events:
        print("❌ Aucun événement disponible")
        return
    
    # Supprimer les anciennes réservations pour recommencer
    old_count = Reservation.objects.filter(user=user).count()
    Reservation.objects.filter(user=user).delete()
    print(f"🗑️ {old_count} anciennes réservations supprimées\n")
    
    # Données pour chaque mois (nombre de réservations)
    # Plus de réservations en été et en automne
    monthly_pattern = [
        2,  # Décembre 2024
        1,  # Janvier 2025
        1,  # Février
        3,  # Mars
        4,  # Avril
        5,  # Mai
        6,  # Juin
        7,  # Juillet (été)
        5,  # Août
        4,  # Septembre
        3,  # Octobre
        7,  # Novembre (actuel - le plus actif)
    ]
    
    total_created = 0
    current_date = datetime.now()
    
    print("📅 Création des réservations historiques...\n")
    
    for i in range(12):
        # Calculer le mois
        month_date = current_date - relativedelta(months=(11 - i))
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Nombre de réservations pour ce mois
        num_reservations = monthly_pattern[i]
        
        print(f"📆 {month_start.strftime('%B %Y')} : {num_reservations} réservation(s)")
        
        for j in range(num_reservations):
            # Choisir un événement aléatoire
            event = random.choice(events)
            
            # Nombre de places aléatoire (1-3)
            num_seats = random.randint(1, 3)
            
            # Date de création aléatoire dans le mois
            day = random.randint(1, 28)  # Éviter les problèmes de fin de mois
            hour = random.randint(9, 21)
            minute = random.randint(0, 59)
            
            created_date = month_start.replace(day=day, hour=hour, minute=minute)
            
            # Créer la réservation
            reservation = Reservation(
                user=user,
                event=event,
                number_of_seats=num_seats,
                notes=f"Réservation historique - {month_start.strftime('%B %Y')}",
                status='CONFIRMEE',
                created_at=created_date
            )
            reservation.save()
            
            # Mettre à jour created_at manuellement (car auto_now_add=True)
            Reservation.objects.filter(id=reservation.id).update(created_at=created_date)
            
            total_created += 1
            print(f"  ✅ {reservation.reservation_code} - {event.title} ({num_seats} places) - {event.price_per_person * num_seats}€")
        
        print()
    
    # Statistiques finales
    total_reservations = Reservation.objects.filter(user=user).count()
    total_spent = sum([r.total_price for r in Reservation.objects.filter(user=user, status='CONFIRMEE')])
    total_seats = sum([r.number_of_seats for r in Reservation.objects.filter(user=user, status='CONFIRMEE')])
    
    print("="*60)
    print(f"✨ {total_created} réservations historiques créées avec succès !")
    print(f"\n📊 Statistiques finales pour {user.username}:")
    print(f"   Total réservations : {total_reservations}")
    print(f"   Total dépensé : {total_spent}€")
    print(f"   Total places : {total_seats}")
    print("="*60)

if __name__ == '__main__':
    create_historical_reservations()
