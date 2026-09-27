"""
Script pour créer du contenu de test pour le blog, reviews, FAQ et newsletter
"""
import os
import django
from datetime import datetime, timedelta
import random

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'festy_event.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import BlogCategory, BlogPost, BlogComment, Newsletter
from reviews.models import Review, FAQ, ContactMessage
from locations.models import Location
from events.models import Event
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

print("🚀 Création du contenu de test...\n")

# Récupérer ou créer un utilisateur admin
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.create_superuser('admin', 'admin@festyevent.tn', 'admin123')
    print("✅ Utilisateur admin créé")

# Récupérer des utilisateurs existants ou en créer
users = list(User.objects.all()[:5])
if len(users) < 5:
    for i in range(5 - len(users)):
        user, created = User.objects.get_or_create(
            username=f'user{i+1}',
            defaults={'email': f'user{i+1}@example.com'}
        )
        if created:
            user.set_password('password123')
            user.save()
        users.append(user)

print(f"✅ {len(users)} utilisateurs disponibles\n")

# Créer des catégories de blog
print("📚 Création des catégories de blog...")
categories_data = [
    {'name': 'Événements', 'icon': 'fas fa-calendar-star', 'color': '#fb923c', 'description': 'Actualités et tendances événementielles'},
    {'name': 'Conseils', 'icon': 'fas fa-lightbulb', 'color': '#3b82f6', 'description': 'Astuces pour organiser vos événements'},
    {'name': 'Lieux', 'icon': 'fas fa-building', 'color': '#10b981', 'description': 'Découvrez nos meilleurs lieux'},
    {'name': 'Témoignages', 'icon': 'fas fa-quote-left', 'color': '#f59e0b', 'description': 'Histoires de nos clients'},
    {'name': 'Actualités', 'icon': 'fas fa-newspaper', 'color': '#ef4444', 'description': 'Nouveautés Festy Event'},
]

categories = []
for cat_data in categories_data:
    category, created = BlogCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults=cat_data
    )
    categories.append(category)
    if created:
        print(f"  ✓ {category.name}")

# Créer des articles de blog
print("\n✍️ Création des articles de blog...")
posts_data = [
    {
        'title': '10 Conseils pour Organiser un Mariage Inoubliable en Tunisie',
        'category': categories[1],
        'excerpt': 'Découvrez nos meilleurs conseils pour planifier le mariage de vos rêves dans les plus beaux lieux de Tunisie.',
        'content': '''# Introduction

Organiser un mariage en Tunisie est une expérience unique qui allie tradition et modernité. Dans cet article, nous partageons avec vous 10 conseils essentiels pour faire de votre grand jour un moment inoubliable.

## 1. Choisissez le bon lieu

Le choix du lieu est crucial. La Tunisie offre une variété de lieux magnifiques, des palais aux jardins en passant par les plages.

## 2. Planifiez à l'avance

Commencez vos préparatifs au moins 6 mois à l'avance pour avoir le choix des dates et des prestataires.

## 3. Respectez votre budget

Établissez un budget réaliste et respectez-le. N'oubliez pas de prévoir une marge pour les imprévus.

## 4. Choisissez les bons prestataires

La qualité des prestataires (traiteur, photographe, DJ) fait toute la différence.

## 5. Personnalisez votre décoration

Ajoutez votre touche personnelle pour rendre votre mariage unique.

## Conclusion

Avec une bonne planification et les bons choix, votre mariage en Tunisie sera un succès garanti !''',
        'tags': 'mariage, tunisie, conseils, organisation',
        'is_featured': True,
    },
    {
        'title': 'Les Meilleurs Lieux pour Événements d\'Entreprise à Tunis',
        'category': categories[2],
        'excerpt': 'Découvrez notre sélection des lieux les plus prestigieux pour organiser vos événements professionnels à Tunis.',
        'content': '''# Les meilleurs lieux professionnels

Tunis regorge de lieux exceptionnels pour vos événements d'entreprise. Voici notre sélection :

## 1. Grand Hall Tunis
Capacité de 500 personnes, équipements modernes, parking privé.

## 2. Centre des Congrès
Parfait pour les grandes conférences et séminaires.

## 3. Jardins de Carthage
Pour un événement en plein air avec vue sur la mer.

## Conclusion
Choisissez le lieu qui correspond à vos besoins et à votre image de marque.''',
        'tags': 'entreprise, business, tunis, événements professionnels',
        'is_featured': False,
    },
    {
        'title': 'Témoignage : Comment Festy Event a Transformé Notre Gala de Charité',
        'category': categories[3],
        'excerpt': 'L\'histoire émouvante de l\'organisation d\'un gala caritatif réussi grâce à Festy Event.',
        'content': '''# Un gala inoubliable

Nous sommes l'association "Espoir pour Tous" et nous voulions organiser un gala pour lever des fonds.

## Notre expérience avec Festy Event

L'équipe de Festy Event nous a accompagnés de A à Z dans l'organisation de notre événement.

## Les résultats

Plus de 300 participants, 50 000 TND récoltés, et un événement dont tout le monde parle encore !

## Notre recommandation

Nous recommandons vivement Festy Event à toutes les associations.''',
        'tags': 'témoignage, gala, charité, success story',
        'is_featured': True,
    },
    {
        'title': 'Tendances Événementielles 2025 en Tunisie',
        'category': categories[0],
        'excerpt': 'Les nouvelles tendances qui vont marquer les événements en 2025.',
        'content': '''# Les tendances 2025

Découvrez ce qui va être à la mode dans l'événementiel tunisien cette année.

## 1. Événements éco-responsables
La durabilité est au cœur des préoccupations.

## 2. Technologie et innovation
Réalité virtuelle, streaming, applications dédiées.

## 3. Expériences immersives
Les invités veulent vivre des moments uniques.''',
        'tags': 'tendances, 2025, événements, innovation',
        'is_featured': False,
    },
    {
        'title': 'Nouveauté : Notre Système de Réservation en Ligne',
        'category': categories[4],
        'excerpt': 'Réservez vos lieux en quelques clics grâce à notre nouvelle plateforme.',
        'content': '''# La réservation devient simple

Festy Event lance sa nouvelle plateforme de réservation en ligne !

## Fonctionnalités
- Calendrier en temps réel
- Paiement sécurisé
- Gestion de vos réservations
- Support 24/7

## Comment ça marche ?
1. Choisissez votre lieu
2. Sélectionnez la date
3. Payez en ligne
4. Recevez votre confirmation

C'est aussi simple que ça !''',
        'tags': 'nouveauté, réservation, en ligne, plateforme',
        'is_featured': True,
    },
]

posts = []
for i, post_data in enumerate(posts_data):
    post, created = BlogPost.objects.get_or_create(
        title=post_data['title'],
        defaults={
            **post_data,
            'author': admin_user,
            'status': 'PUBLISHED',
            'published_at': timezone.now() - timedelta(days=random.randint(1, 30)),
            'views_count': random.randint(50, 500),
        }
    )
    posts.append(post)
    if created:
        print(f"  ✓ {post.title}")

# Créer des commentaires
print("\n💬 Création des commentaires...")
comments_texts = [
    "Article très intéressant ! Merci pour ces conseils.",
    "J'ai utilisé vos services et je confirme, c'est excellent !",
    "Super contenu, très utile pour mon prochain événement.",
    "Merci pour ce partage d'expérience.",
    "Exactement ce que je cherchais !",
]

for post in posts[:3]:  # Commentaires sur les 3 premiers articles
    for _ in range(random.randint(2, 5)):
        BlogComment.objects.get_or_create(
            post=post,
            author=random.choice(users),
            content=random.choice(comments_texts),
            defaults={'is_approved': True}
        )
print(f"  ✓ Commentaires ajoutés")

# Créer des FAQs
print("\n❓ Création des FAQs...")
faqs_data = [
    {
        'category': 'RESERVATION',
        'question': 'Comment réserver un lieu sur Festy Event ?',
        'answer': 'Pour réserver un lieu, connectez-vous à votre compte, choisissez le lieu souhaité, sélectionnez la date dans le calendrier, puis suivez les étapes de paiement.',
        'order': 1,
    },
    {
        'category': 'RESERVATION',
        'question': 'Puis-je annuler ma réservation ?',
        'answer': 'Oui, vous pouvez annuler votre réservation jusqu\'à 48h avant la date prévue. Des frais d\'annulation de 20% s\'appliquent.',
        'order': 2,
    },
    {
        'category': 'PAYMENT',
        'question': 'Quels modes de paiement acceptez-vous ?',
        'answer': 'Nous acceptons les cartes bancaires (Visa, Mastercard), les virements bancaires, et les chèques certifiés.',
        'order': 1,
    },
    {
        'category': 'PAYMENT',
        'question': 'Le paiement en ligne est-il sécurisé ?',
        'answer': 'Oui, tous nos paiements sont sécurisés avec un cryptage SSL et conformes aux normes PCI-DSS.',
        'order': 2,
    },
    {
        'category': 'LOCATION',
        'question': 'Quelle est la capacité maximale des lieux ?',
        'answer': 'Nos lieux ont des capacités variées allant de 50 à 1000 personnes. Consultez la fiche de chaque lieu pour plus de détails.',
        'order': 1,
    },
    {
        'category': 'EVENT',
        'question': 'Proposez-vous des services de traiteur ?',
        'answer': 'Certains de nos lieux proposent des services de traiteur. Contactez-nous pour plus d\'informations.',
        'order': 1,
    },
    {
        'category': 'ACCOUNT',
        'question': 'Comment créer un compte ?',
        'answer': 'Cliquez sur "S\'inscrire" dans le menu, remplissez le formulaire avec vos informations, puis validez votre email.',
        'order': 1,
    },
    {
        'category': 'GENERAL',
        'question': 'Où êtes-vous situés ?',
        'answer': 'Notre siège social est à Tunis, mais nos lieux sont répartis dans toute la Tunisie. Consultez la carte interactive pour les localiser.',
        'order': 1,
    },
]

for faq_data in faqs_data:
    faq, created = FAQ.objects.get_or_create(
        question=faq_data['question'],
        defaults={**faq_data, 'helpful_count': random.randint(5, 50)}
    )
    if created:
        print(f"  ✓ {faq.question}")

# Créer des avis pour les lieux
print("\n⭐ Création des avis...")
locations = list(Location.objects.all()[:3])
location_ct = ContentType.objects.get_for_model(Location)

reviews_data = [
    {
        'title': 'Lieu exceptionnel !',
        'comment': 'Nous avons organisé notre mariage ici et tout était parfait. Le personnel était professionnel et le lieu magnifique.',
        'rating': 5,
    },
    {
        'title': 'Très bon rapport qualité/prix',
        'comment': 'Lieu spacieux et bien équipé. Nous avons organisé un séminaire d\'entreprise et tout s\'est bien passé.',
        'rating': 4,
    },
    {
        'title': 'Expérience positive',
        'comment': 'Bel endroit, bien situé et facile d\'accès. Quelques petites améliorations à faire au niveau de la climatisation.',
        'rating': 4,
    },
    {
        'title': 'Recommandé !',
        'comment': 'Super lieu pour événements. Équipe réactive et professionnelle. Je recommande vivement.',
        'rating': 5,
    },
]

for location in locations:
    for review_data in random.sample(reviews_data, k=random.randint(2, 3)):
        try:
            review, created = Review.objects.get_or_create(
                content_type=location_ct,
                object_id=location.id,
                author=random.choice(users),
                defaults={
                    **review_data,
                    'cleanliness_rating': random.randint(4, 5),
                    'service_rating': random.randint(4, 5),
                    'value_rating': random.randint(3, 5),
                    'location_rating': random.randint(4, 5),
                    'helpful_count': random.randint(1, 15),
                    'is_verified': random.choice([True, False]),
                }
            )
            if created:
                print(f"  ✓ Avis pour {location.name}")
        except:
            pass  # Ignorer les doublons

# Créer des abonnés newsletter
print("\n📧 Création des abonnés newsletter...")
emails = [
    'alice@example.com',
    'bob@example.com',
    'charlie@example.com',
    'diana@example.com',
    'emma@example.com',
]

for email in emails:
    subscriber, created = Newsletter.objects.get_or_create(
        email=email,
        defaults={'name': email.split('@')[0].capitalize()}
    )
    if created:
        print(f"  ✓ {email}")

print("\n" + "="*60)
print("✨ CRÉATION TERMINÉE !")
print("="*60)
print(f"\n📊 Résumé :")
print(f"  • Catégories de blog : {BlogCategory.objects.count()}")
print(f"  • Articles de blog : {BlogPost.objects.count()}")
print(f"  • Commentaires : {BlogComment.objects.count()}")
print(f"  • FAQs : {FAQ.objects.count()}")
print(f"  • Avis : {Review.objects.count()}")
print(f"  • Abonnés newsletter : {Newsletter.objects.count()}")
print(f"\n🌐 Accédez au blog : http://127.0.0.1:8000/blog/")
print(f"👨‍💼 Admin : http://127.0.0.1:8000/admin/")
