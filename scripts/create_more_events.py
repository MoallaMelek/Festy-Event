"""
Script pour créer plus d'événements tunisiens
"""
import os
import django
from datetime import datetime, timedelta

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'festy_event.settings')
django.setup()

from events.models import Event

# Nouveaux événements tunisiens
events_data = [
    # GASTRONOMIE
    {
        'title': 'Festival de la Cuisine Tunisienne',
        'description': 'Découvrez les saveurs authentiques de la cuisine tunisienne. Chefs renommés, dégustations, ateliers culinaires.',
        'category': 'GASTRONOMIE',
        'date': datetime.now() + timedelta(days=35),
        'location': 'Sidi Bou Saïd, Restaurant Dar Zarrouk',
        'capacity': 500,
        'price_per_person': 170.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800'
    },
    {
        'title': 'Marché Gastronomique de Hammamet',
        'description': 'Produits du terroir, spécialités locales, huile d\'olive premium. Un voyage culinaire unique.',
        'category': 'GASTRONOMIE',
        'date': datetime.now() + timedelta(days=40),
        'location': 'Hammamet, La Belle Étoile',
        'capacity': 800,
        'price_per_person': 136.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800'
    },
    {
        'title': 'Soirée Gastronomique à La Marsa',
        'description': 'Dîner d\'exception avec vue sur la mer. Menu dégustation par les meilleurs chefs tunisiens.',
        'category': 'GASTRONOMIE',
        'date': datetime.now() + timedelta(days=50),
        'location': 'La Marsa, Le Golfe',
        'capacity': 300,
        'price_per_person': 204.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800'
    },
    {
        'title': 'Festival Culinaire de Djerba',
        'description': 'Saveurs de l\'île, poissons frais, spécialités méditerranéennes. Ambiance conviviale.',
        'category': 'GASTRONOMIE',
        'date': datetime.now() + timedelta(days=55),
        'location': 'Djerba, Chez Hassan',
        'capacity': 400,
        'price_per_person': 153.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800'
    },
    
    # MUSIQUE
    {
        'title': 'Festival International de Hammamet',
        'description': 'Musique classique et contemporaine. Artistes internationaux dans un cadre exceptionnel.',
        'category': 'MUSIQUE',
        'date': datetime.now() + timedelta(days=42),
        'location': 'Hammamet, Centre culturel international',
        'capacity': 2000,
        'price_per_person': 187.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800'
    },
    {
        'title': 'Nuits de Jazz à Tabarka',
        'description': 'Festival de jazz légendaire. Musiciens de renommée mondiale, bord de mer, ambiance unique.',
        'category': 'MUSIQUE',
        'date': datetime.now() + timedelta(days=65),
        'location': 'Tabarka, Festival de Jazz',
        'capacity': 3000,
        'price_per_person': 221.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=800'
    },
    {
        'title': 'Concert Oriental à Sousse',
        'description': 'Musique orientale traditionnelle et moderne. Orchestre complet, chanteurs célèbres.',
        'category': 'MUSIQUE',
        'date': datetime.now() + timedelta(days=48),
        'location': 'Sousse, Dar El Jeld',
        'capacity': 1500,
        'price_per_person': 136.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800'
    },
    {
        'title': 'Festival de Musique Électronique Djerba',
        'description': 'DJs internationaux, plage, musique électronique. L\'événement de l\'été !',
        'category': 'MUSIQUE',
        'date': datetime.now() + timedelta(days=70),
        'location': 'Djerba, Centre culturel',
        'capacity': 4000,
        'price_per_person': 170.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800'
    },
    
    # BUSINESS
    {
        'title': 'Sommet Économique Tunisien',
        'description': 'Rencontres d\'affaires, networking, conférences économiques. Leaders économiques africains.',
        'category': 'BUSINESS',
        'date': datetime.now() + timedelta(days=38),
        'location': 'Gammarth, Le Palace Hotel',
        'capacity': 1000,
        'price_per_person': 680.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=800'
    },
    {
        'title': 'Forum Innovation & Startups',
        'description': 'Startups, investisseurs, innovation technologique. Pitch sessions, workshops.',
        'category': 'BUSINESS',
        'date': datetime.now() + timedelta(days=44),
        'location': 'Tunis, Les Berges du Lac',
        'capacity': 800,
        'price_per_person': 442.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800'
    },
    {
        'title': 'Conférence E-commerce Maghreb',
        'description': 'Commerce électronique, transformation digitale, stratégies marketing digital.',
        'category': 'BUSINESS',
        'date': datetime.now() + timedelta(days=52),
        'location': 'Sfax, Centre des affaires',
        'capacity': 600,
        'price_per_person': 510.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800'
    },
    
    # SPORT
    {
        'title': 'Semi-Marathon de Sousse',
        'description': 'Course sur la côte tunisienne. Parcours panoramique, ambiance festive.',
        'category': 'SPORT',
        'date': datetime.now() + timedelta(days=68),
        'location': 'Sousse, Stade Olympique',
        'capacity': 3000,
        'price_per_person': 102.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800'
    },
    {
        'title': 'Tournoi de Football Bizerte',
        'description': 'Compétition inter-régionale. Équipes amateurs et semi-professionnelles.',
        'category': 'SPORT',
        'date': datetime.now() + timedelta(days=75),
        'location': 'Bizerte, Stade 15 Octobre',
        'capacity': 5000,
        'price_per_person': 68.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800'
    },
    {
        'title': 'Championnat d\'Athlétisme El Menzah',
        'description': 'Compétitions d\'athlétisme, épreuves variées, athlètes nationaux.',
        'category': 'SPORT',
        'date': datetime.now() + timedelta(days=80),
        'location': 'Tunis, Complexe Sportif El Menzah',
        'capacity': 8000,
        'price_per_person': 51.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800'
    },
    
    # CULTURE
    {
        'title': 'Festival d\'El Jem',
        'description': 'Spectacles dans l\'amphithéâtre romain. Concerts symphoniques, opéra, théâtre.',
        'category': 'CULTURE',
        'date': datetime.now() + timedelta(days=58),
        'location': 'El Jem, Amphithéâtre romain',
        'capacity': 2500,
        'price_per_person': 119.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1503095396549-807759245b35?w=800'
    },
    {
        'title': 'Exposition Musée du Bardo',
        'description': 'Collection exceptionnelle de mosaïques romaines. Visite guidée, conférences.',
        'category': 'CULTURE',
        'date': datetime.now() + timedelta(days=33),
        'location': 'Tunis, Musée du Bardo',
        'capacity': 500,
        'price_per_person': 68.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=800'
    },
    {
        'title': 'Visite Culturelle de Dougga',
        'description': 'Site archéologique romain exceptionnel. Guides experts, histoire antique.',
        'category': 'CULTURE',
        'date': datetime.now() + timedelta(days=62),
        'location': 'Dougga, Site archéologique',
        'capacity': 300,
        'price_per_person': 85.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1564415315949-7a0c4c73aab4?w=800'
    },
    {
        'title': 'Festival Culturel de Sidi Bou Saïd',
        'description': 'Arts, musique, expositions. Le charme du village bleu et blanc.',
        'category': 'CULTURE',
        'date': datetime.now() + timedelta(days=46),
        'location': 'Sidi Bou Saïd, Centre culturel',
        'capacity': 600,
        'price_per_person': 102.00,
        'status': 'CONFIRME',
        'image_url': 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800'
    },
]

print("🎪 Création de nouveaux événements tunisiens...\n")
created_count = 0

for event_data in events_data:
    if not Event.objects.filter(title=event_data['title']).exists():
        event = Event.objects.create(**event_data)
        event.available_seats = event.capacity  # Tous les événements sont disponibles
        event.save()
        print(f"✅ {event.title}")
        print(f"   📍 {event.location}")
        print(f"   💰 {event.price_per_person} TND")
        print(f"   🎫 {event.capacity} places\n")
        created_count += 1
    else:
        print(f"ℹ️  {event_data['title']} - Déjà existant\n")

print(f"\n✨ {created_count} nouveaux événements créés !")
print("🇹🇳 Votre plateforme tunisienne est maintenant complète !")
print("\n🌐 Rafraîchissez la page: http://localhost:8000/events/")
