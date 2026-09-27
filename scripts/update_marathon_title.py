"""
Script pour mettre à jour le titre du Marathon
"""
import os
import django

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'festy_event.settings')
django.setup()

from events.models import Event

# Mettre à jour le titre du marathon
try:
    event = Event.objects.get(title='Marathon de Paris')
    event.title = 'Marathon de Tunis'
    event.save()
    print(f'✅ Titre mis à jour: {event.title}')
except Event.DoesNotExist:
    print('ℹ️ Événement déjà mis à jour ou inexistant')
