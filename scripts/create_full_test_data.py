"""
Script pour créer des données de test pour Payments, Locations et Contracts
Usage: python create_full_test_data.py
"""

import os
import django
import random
from datetime import timedelta
from decimal import Decimal

# Configuration Django
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'festy_event.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event
from reservations.models import Reservation
from payments.models import Payment, Invoice
from locations.models import Location
from contracts.models import Contract


def create_locations():
    """Créer des lieux de test"""
    print("\n🏢 Création des lieux...")
    
    admin = User.objects.filter(is_staff=True).first()
    
    locations_data = [
        {
            'name': 'Grand Hall Tunis',
            'address': '15 Avenue Habib Bourguiba',
            'city': 'Tunis',
            'postal_code': '1000',
            'location_type': 'INDOOR',
            'capacity': 500,
            'area': Decimal('800.00'),
            'hourly_rate': Decimal('150.000'),
            'daily_rate': Decimal('1200.000'),
            'status': 'AVAILABLE',
            'amenities': 'WiFi, Climatisation, Sonorisation, Écran géant, Parking',
            'description': 'Salle de réception moderne au cœur de Tunis',
            'contact_person': 'Ahmed Ben Ali',
            'contact_phone': '+216 71 123 456',
            'contact_email': 'contact@grandhall.tn',
        },
        {
            'name': 'Jardins de Carthage',
            'address': 'Route de La Marsa',
            'city': 'Carthage',
            'postal_code': '2016',
            'location_type': 'OUTDOOR',
            'capacity': 1000,
            'area': Decimal('2000.00'),
            'hourly_rate': Decimal('200.000'),
            'daily_rate': Decimal('1800.000'),
            'status': 'AVAILABLE',
            'amenities': 'Jardin, Tente, Éclairage, Scène extérieure, Parking VIP',
            'description': 'Espace en plein air avec vue sur la mer',
            'contact_person': 'Leila Mansour',
            'contact_phone': '+216 71 987 654',
            'contact_email': 'info@jardinscarthage.tn',
        },
        {
            'name': 'Centre des Congrès Sousse',
            'address': 'Boulevard 14 Janvier',
            'city': 'Sousse',
            'postal_code': '4000',
            'location_type': 'HYBRID',
            'capacity': 800,
            'area': Decimal('1500.00'),
            'hourly_rate': Decimal('180.000'),
            'daily_rate': Decimal('1500.000'),
            'status': 'AVAILABLE',
            'amenities': 'Salles multiples, WiFi, Équipement audiovisuel, Restaurant, Parking',
            'description': 'Centre polyvalent pour événements professionnels et privés',
            'contact_person': 'Mohamed Trabelsi',
            'contact_phone': '+216 73 456 789',
            'contact_email': 'reservation@congress-sousse.tn',
        },
        {
            'name': 'Palais des Arts Sfax',
            'address': 'Avenue Majida Boulila',
            'city': 'Sfax',
            'postal_code': '3000',
            'location_type': 'INDOOR',
            'capacity': 400,
            'area': Decimal('600.00'),
            'hourly_rate': Decimal('120.000'),
            'daily_rate': Decimal('900.000'),
            'status': 'MAINTENANCE',
            'amenities': 'Théâtre, Galerie, Acoustique professionnelle, Loges',
            'description': 'Espace culturel idéal pour spectacles et galas',
            'contact_person': 'Fatma Jebali',
            'contact_phone': '+216 74 321 654',
            'contact_email': 'contact@palaisarts-sfax.tn',
        },
        {
            'name': 'Villa Moderne Gammarth',
            'address': 'Route de Raoued',
            'city': 'Gammarth',
            'postal_code': '2088',
            'location_type': 'HYBRID',
            'capacity': 200,
            'area': Decimal('400.00'),
            'hourly_rate': Decimal('250.000'),
            'daily_rate': Decimal('2000.000'),
            'status': 'OCCUPIED',
            'amenities': 'Piscine, Jardin privé, Terrasse, Vue mer, Parking sécurisé',
            'description': 'Villa de luxe pour événements intimes',
            'contact_person': 'Sami Bouzid',
            'contact_phone': '+216 71 741 852',
            'contact_email': 'villa@gammarth.tn',
        },
    ]
    
    created_locations = []
    for data in locations_data:
        location, created = Location.objects.get_or_create(
            name=data['name'],
            defaults={**data, 'created_by': admin}
        )
        if created:
            created_locations.append(location)
            print(f"✅ {location.name} - {location.city}")
        else:
            print(f"⚠️  {location.name} existe déjà")
    
    return created_locations


def create_payments_and_invoices():
    """Créer des paiements et factures pour les réservations existantes"""
    print("\n💳 Création des paiements et factures...")
    
    reservations = Reservation.objects.filter(status='CONFIRMED')[:10]
    
    payment_methods = ['CASH', 'CARD', 'BANK_TRANSFER', 'MOBILE', 'CHEQUE']
    payment_statuses = ['COMPLETED', 'PENDING', 'COMPLETED', 'COMPLETED']  # Plus de COMPLETED
    
    created_payments = []
    created_invoices = []
    
    for reservation in reservations:
        # Créer paiement
        payment_status = random.choice(payment_statuses)
        payment = Payment.objects.create(
            reservation=reservation,
            amount=reservation.total_price,
            payment_method=random.choice(payment_methods),
            status=payment_status,
            notes=f"Paiement pour réservation #{reservation.id}"
        )
        
        if payment_status == 'COMPLETED':
            payment.mark_as_completed()
        
        created_payments.append(payment)
        print(f"✅ Paiement {payment.transaction_id} - {payment.amount} TND ({payment.get_payment_method_display()})")
        
        # Créer facture si paiement complété
        if payment_status == 'COMPLETED' and not hasattr(reservation, 'invoice'):
            invoice = Invoice.objects.create(
                reservation=reservation,
                total_amount=reservation.total_price,
                tax_amount=reservation.total_price * Decimal('0.19'),  # TVA 19%
                discount_amount=Decimal('0.000'),
                status='ISSUED',
                notes=f"Facture pour événement: {reservation.event.title}"
            )
            invoice.mark_as_paid()
            created_invoices.append(invoice)
            print(f"   📄 Facture {invoice.invoice_number} générée")
    
    return created_payments, created_invoices


def create_contracts():
    """Créer des contrats de test"""
    print("\n📜 Création des contrats...")
    
    admin = User.objects.filter(is_staff=True).first()
    events = Event.objects.all()[:5]
    
    contract_types = ['SERVICE', 'PARTNERSHIP', 'SPONSORSHIP', 'VENUE', 'SUPPLIER']
    clients = [
        {'name': 'TechCorp Tunisia', 'email': 'contact@techcorp.tn', 'phone': '+216 71 111 222'},
        {'name': 'EventPro SARL', 'email': 'info@eventpro.tn', 'phone': '+216 71 333 444'},
        {'name': 'Catering Excellence', 'email': 'hello@catering.tn', 'phone': '+216 71 555 666'},
        {'name': 'Sound & Light Co', 'email': 'booking@soundlight.tn', 'phone': '+216 71 777 888'},
        {'name': 'Décor Premium', 'email': 'contact@decorpremium.tn', 'phone': '+216 71 999 000'},
    ]
    
    created_contracts = []
    
    for i, event in enumerate(events):
        client = clients[i % len(clients)]
        contract_type = contract_types[i % len(contract_types)]
        
        start_date = timezone.now().date() + timedelta(days=random.randint(1, 30))
        end_date = start_date + timedelta(days=random.randint(1, 90))
        
        contract = Contract.objects.create(
            title=f"Contrat {contract_type} - {event.title}",
            contract_type=contract_type,
            event=event,
            client_name=client['name'],
            client_email=client['email'],
            client_phone=client['phone'],
            client_address=f"{random.randint(1, 100)} Rue {random.choice(['Principale', 'de la République', 'Bourguiba'])}, Tunis",
            start_date=start_date,
            end_date=end_date,
            amount=Decimal(str(random.randint(500, 5000))) + Decimal('0.000'),
            terms=f"""
CONTRAT DE {contract_type.upper()}

Article 1 - Objet du contrat
Le présent contrat a pour objet de définir les conditions dans lesquelles {client['name']} 
s'engage à fournir des services pour l'événement "{event.title}".

Article 2 - Durée
Le contrat prend effet le {start_date.strftime('%d/%m/%Y')} et expire le {end_date.strftime('%d/%m/%Y')}.

Article 3 - Montant et modalités de paiement
Le montant total du contrat s'élève à {random.randint(500, 5000)} TND.
Paiement en 2 versements: 50% à la signature, 50% à la fin de la prestation.

Article 4 - Obligations des parties
- Le prestataire s'engage à respecter les délais convenus
- Le client s'engage à fournir toutes les informations nécessaires

Article 5 - Résiliation
Le contrat peut être résilié par l'une ou l'autre des parties avec un préavis de 15 jours.
            """.strip(),
            status=random.choice(['DRAFT', 'PENDING', 'ACTIVE']),
            created_by=admin
        )
        
        # Signer certains contrats
        if contract.status in ['PENDING', 'ACTIVE']:
            contract.signed_by_client = True
            contract.client_signature = "CLIENT_SIGNATURE_BASE64_PLACEHOLDER"
            
            if contract.status == 'ACTIVE':
                contract.signed_by_admin = True
                contract.admin_signature = "ADMIN_SIGNATURE_BASE64_PLACEHOLDER"
                contract.signed_date = timezone.now()
            
            contract.save()
        
        created_contracts.append(contract)
        print(f"✅ Contrat {contract.contract_number} - {contract.title} ({contract.get_status_display()})")
    
    return created_contracts


def main():
    """Fonction principale"""
    print("=" * 70)
    print("🚀 CRÉATION DES DONNÉES DE TEST")
    print("   Payments, Locations, Contracts")
    print("=" * 70)
    
    try:
        locations = create_locations()
        payments, invoices = create_payments_and_invoices()
        contracts = create_contracts()
        
        print("\n" + "=" * 70)
        print("✅ RÉSUMÉ")
        print("=" * 70)
        print(f"📍 Lieux créés: {len(locations)}")
        print(f"💳 Paiements créés: {len(payments)}")
        print(f"📄 Factures créées: {len(invoices)}")
        print(f"📜 Contrats créés: {len(contracts)}")
        print("\n🎉 Données de test créées avec succès!")
        print(f"🌐 Accédez à l'admin: http://localhost:8000/admin/")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
