# 📋 Guide Complet des URLs - Festy Event

## 🔐 Authentification
- `/accounts/login/` - Connexion
- `/accounts/logout/` - Déconnexion
- `/users/register/` - Inscription
- `/users/profile/` - Profil utilisateur

## 📅 Événements
- `/events/` - Liste des événements (PUBLIC)
- `/events/create/` - Créer événement (ADMIN)
- `/events/<id>/` - Détails événement
- `/events/<id>/edit/` - Modifier événement (ADMIN)
- `/events/<id>/delete/` - Supprimer événement (ADMIN)

## 🎫 Réservations
- `/reservations/` - Mes réservations (USER)
- `/reservations/create/<event_id>/` - Créer réservation
- `/reservations/<id>/` - Détails réservation
- `/reservations/<id>/cancel/` - Annuler réservation
- `/reservations/<id>/download-qr/` - Télécharger QR code
- `/reservations/admin/` - Liste admin (ADMIN)

## 💳 Paiements & Factures (NOUVEAU WORKFLOW)

### Client (USER)
- `/invoice/<id>/` - Voir ma facture (US 4.1)
- `/invoice/<id>/pay/` - Payer ma facture (US 4.2)

### Admin (SUPERVISION)
- `/payments/` - Supervision des paiements (US 4.4)
- `/invoices/` - Supervision des factures (US 4.3)
- `/payments/<id>/` - Détails paiement (lecture seule)
- `/invoices/<id>/` - Détails facture (lecture seule)

## 💬 Réclamations
- `/complaints/` - Mes réclamations (USER)
- `/complaints/create/` - Créer réclamation
- `/complaints/<id>/` - Détails réclamation
- `/complaints/admin/` - Liste admin (ADMIN)
- `/complaints/<id>/respond/` - Répondre (ADMIN)
- `/complaints/<id>/resolve/` - Résoudre (ADMIN)

## 📍 Lieux (Logistique)
- `/locations/` - Liste des lieux (ADMIN)
- `/locations/create/` - Créer lieu
- `/locations/<id>/` - Détails lieu
- `/locations/<id>/edit/` - Modifier lieu
- `/locations/<id>/delete/` - Supprimer lieu

## 📑 Contrats (Conventions)
- `/contracts/` - Liste des contrats (ADMIN)
- `/contracts/create/` - Créer contrat
- `/contracts/<id>/` - Détails contrat
- `/contracts/<id>/edit/` - Modifier contrat
- `/contracts/<id>/sign/` - Signer (CLIENT)
- `/contracts/<id>/admin-sign/` - Signer (ADMIN)
- `/contracts/<id>/activate/` - Activer
- `/contracts/<id>/complete/` - Compléter
- `/contracts/<id>/cancel/` - Annuler

## 📊 Dashboards
- `/` - Redirige vers `/events/`
- `/dashboard/` - Dashboard utilisateur (USER)
- `/admin/dashboard/` - Dashboard admin (ADMIN)

## ⚠️ IMPORTANT - Workflow Paiements

### Ancien workflow (SUPPRIMÉ) ❌
- ~~Admin crée factures manuellement~~
- ~~Admin enregistre paiements manuellement~~

### Nouveau workflow (ACTUEL) ✅
1. **Client crée réservation** → Statut CONFIRMEE
2. **Système génère facture automatiquement** avec TVA 19%
3. **Client voit facture dans ses réservations** (`/reservations/<id>/`)
4. **Client clique "Payer maintenant"** → `/invoice/<id>/pay/`
5. **Client remplit formulaire** (montant, méthode)
6. **Système marque facture payée** si montant suffisant
7. **Admin supervise** via `/payments/` et `/invoices/`

## 🔧 URLs Admin Django (Backend)
- `/admin/` - Interface d'administration Django
- **NE PAS CONFONDRE** avec `/payments/` et `/invoices/` (vos URLs custom)

## 📝 Notes
- Les URLs `/admin/payments/` et `/admin/invoices/` n'existent PAS
- Utilisez `/payments/` et `/invoices/` pour la supervision admin
- Les factures sont AUTOMATIQUES (pas de création manuelle)
- Les paiements sont faits par les CLIENTS (pas par admin)
