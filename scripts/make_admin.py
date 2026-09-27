"""
Script pour rendre un utilisateur administrateur
"""
import os
import django

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'festy_event.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 60)
print("GESTION DES ADMINISTRATEURS")
print("=" * 60)

# Afficher tous les utilisateurs
print("\nUtilisateurs existants:")
users = User.objects.all()
for i, user in enumerate(users, 1):
    status = "ADMIN" if user.is_staff else "Utilisateur"
    superuser = " (Superuser)" if user.is_superuser else ""
    print(f"{i}. {user.username} - {user.email} [{status}]{superuser}")

print("\n" + "=" * 60)
username = input("Entrez le nom d'utilisateur à promouvoir admin (ou 'quit' pour quitter): ")

if username.lower() != 'quit':
    try:
        user = User.objects.get(username=username)
        
        if user.is_staff:
            print(f"\n✓ {username} est déjà administrateur!")
        else:
            user.is_staff = True
            user.save()
            print(f"\n✓ {username} est maintenant administrateur!")
            print(f"  Peut accéder à: /reservations/admin-dashboard/")
            
    except User.DoesNotExist:
        print(f"\n✗ Utilisateur '{username}' introuvable!")

print("\n" + "=" * 60)
