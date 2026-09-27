"""
Script de vérification de la configuration email
"""
import os

print("=" * 70)
print("🔍 VÉRIFICATION DE LA CONFIGURATION EMAIL")
print("=" * 70)

# Vérifier si le fichier .env existe
env_file = '.env'
if not os.path.exists(env_file):
    print("\n❌ ERREUR : Le fichier .env n'existe pas !")
    print("💡 Créez-le avec les informations de configuration email.")
    exit(1)

print(f"\n✅ Fichier .env trouvé")

# Lire le fichier .env
with open(env_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Vérifier les variables
checks = {
    'EMAIL_HOST_USER': False,
    'EMAIL_HOST_PASSWORD': False,
    'EMAIL_RECIPIENT': False,
}

for line in content.split('\n'):
    line = line.strip()
    if line.startswith('#') or not line:
        continue
    
    if '=' in line:
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        if key == 'EMAIL_HOST_USER':
            if 'eventfesty55@gmail.com' in value:
                print(f"✅ EMAIL_HOST_USER configuré : {value}")
                checks['EMAIL_HOST_USER'] = True
            else:
                print(f"⚠️  EMAIL_HOST_USER : {value}")
                print("   Devrait être : eventfesty55@gmail.com")
        
        elif key == 'EMAIL_HOST_PASSWORD':
            if value and value != 'COLLEZ_VOTRE_MOT_DE_PASSE_ICI':
                # Vérifier s'il y a des espaces
                if ' ' in value:
                    print(f"❌ EMAIL_HOST_PASSWORD contient des ESPACES !")
                    print(f"   Valeur actuelle : {value}")
                    print("💡 ENLEVEZ les espaces ! Ex: abcdefghijklmnop (pas abcd efgh ijkl mnop)")
                else:
                    print(f"✅ EMAIL_HOST_PASSWORD configuré ({len(value)} caractères)")
                    checks['EMAIL_HOST_PASSWORD'] = True
            else:
                print(f"❌ EMAIL_HOST_PASSWORD non configuré !")
                print("💡 Allez sur https://myaccount.google.com/apppasswords")
                print("   et créez un mot de passe d'application")
        
        elif key == 'EMAIL_RECIPIENT':
            if 'moalla.melek09@gmail.com' in value:
                print(f"✅ EMAIL_RECIPIENT configuré : {value}")
                checks['EMAIL_RECIPIENT'] = True
            else:
                print(f"⚠️  EMAIL_RECIPIENT : {value}")

print("\n" + "=" * 70)
print("📊 RÉSUMÉ DE LA CONFIGURATION")
print("=" * 70)

all_ok = all(checks.values())

for key, ok in checks.items():
    status = "✅" if ok else "❌"
    print(f"{status} {key}")

if all_ok:
    print("\n🎉 TOUT EST BON ! Vous pouvez tester l'envoi d'email.")
    print("\n📝 Prochaines étapes :")
    print("   1. Redémarrez le serveur : python manage.py runserver")
    print("   2. Faites une réservation")
    print("   3. Vérifiez l'email sur moalla.melek09@gmail.com")
else:
    print("\n⚠️  CONFIGURATION INCOMPLÈTE !")
    print("\n📝 À faire :")
    if not checks['EMAIL_HOST_USER']:
        print("   - Vérifiez EMAIL_HOST_USER dans .env")
    if not checks['EMAIL_HOST_PASSWORD']:
        print("   - Obtenez un mot de passe d'application Gmail")
        print("     https://myaccount.google.com/apppasswords")
        print("   - Collez-le dans .env (SANS ESPACES !)")
    if not checks['EMAIL_RECIPIENT']:
        print("   - Vérifiez EMAIL_RECIPIENT dans .env")

print("\n" + "=" * 70)
