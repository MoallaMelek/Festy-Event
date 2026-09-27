# 📧 Configuration Gmail pour Festy Event

## Étapes pour configurer l'envoi d'emails

### 1. Activer l'authentification à deux facteurs (2FA) sur Gmail

1. Allez sur : https://myaccount.google.com/security
2. Dans "Connexion à Google", cliquez sur "Validation en deux étapes"
3. Activez la validation en deux étapes

### 2. Créer un mot de passe d'application

1. Allez sur : https://myaccount.google.com/apppasswords
2. Connectez-vous si nécessaire
3. Dans "Sélectionnez l'application", choisissez "Autre (nom personnalisé)"
4. Entrez "Festy Event Django" comme nom
5. Cliquez sur "Générer"
6. **COPIEZ le mot de passe de 16 caractères** (format: xxxx xxxx xxxx xxxx)

### 3. Configurer le fichier .env

Ouvrez le fichier `.env` et modifiez :

```env
# Configuration Email Gmail
EMAIL_HOST_USER=moalla.melek09@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # ← Collez ici le mot de passe d'application (sans espaces)
EMAIL_RECIPIENT=moalla.melek09@gmail.com
```

**Exemple avec un vrai mot de passe d'application :**
```env
EMAIL_HOST_USER=moalla.melek09@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
EMAIL_RECIPIENT=moalla.melek09@gmail.com
```

### 4. Tester l'envoi d'email

1. Relancez le serveur Django :
   ```bash
   python manage.py runserver
   ```

2. Connectez-vous avec le superuser : **admin / admin123**

3. Réservez un événement

4. Vérifiez votre boîte mail **moalla.melek09@gmail.com**

### 5. Vérifier les emails dans les spams

Si vous ne recevez pas l'email :
- Vérifiez le dossier **Spam/Courrier indésirable**
- Marquez l'email comme "Non spam" si nécessaire

## 🔧 Résolution des problèmes

### Erreur "Username and Password not accepted"
- Vérifiez que la validation en deux étapes est activée
- Créez un nouveau mot de passe d'application
- Assurez-vous de copier le mot de passe sans espaces

### Erreur "SMTPAuthenticationError"
- Le mot de passe d'application est incorrect
- Régénérez un nouveau mot de passe d'application

### L'email n'arrive pas
- Vérifiez les spams
- Vérifiez que EMAIL_HOST_USER est correct
- Vérifiez les logs du serveur Django

## 📝 Note importante

Pour les tests, tous les emails seront envoyés à : **moalla.melek09@gmail.com**

Le système utilisera l'email de l'utilisateur connecté s'il est configuré, sinon il utilisera l'email par défaut défini dans `.env`.

## 🎯 Ce qui sera envoyé

Chaque fois qu'une réservation est créée, un email sera envoyé contenant :
- ✅ Le code de réservation unique
- ✅ Les détails de l'événement (date, lieu, prix)
- ✅ Le nombre de places réservées
- ✅ Un QR code unique à scanner à l'entrée
- ✅ Les informations importantes (style Pathé Cinéma)

## 🚀 Pour activer l'envoi maintenant

1. Suivez les étapes ci-dessus
2. Éditez le fichier `.env`
3. Redémarrez le serveur
4. Testez une réservation !
