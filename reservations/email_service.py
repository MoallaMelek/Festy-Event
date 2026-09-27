"""
Module pour envoyer des emails de confirmation de réservation
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .qr_generator import generate_qr_code
import qrcode
from io import BytesIO
from email.mime.image import MIMEImage

def send_reservation_confirmation_email(reservation):
    """
    Envoie un email de confirmation avec le billet en PDF/HTML et le QR code
    """
    # Générer le QR code
    qr_img_base64, qr_data = generate_qr_code(reservation)
    
    # Générer aussi le QR code comme image pour l'attachment
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir en bytes pour l'email
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Contexte pour le template email
    context = {
        'reservation': reservation,
        'event': reservation.event,
        'user': reservation.user,
        'qr_code_data': qr_img_base64,
        'qr_text': qr_data,
    }
    
    # Rendre le template HTML
    html_content = render_to_string('emails/reservation_confirmation.html', context)
    text_content = f"""
    Confirmation de réservation - Festy Event
    
    Bonjour {reservation.user.first_name or reservation.user.username},
    
    Votre réservation a été confirmée avec succès !
    
    DÉTAILS DE LA RÉSERVATION
    ━━━━━━━━━━━━━━━━━━━━━━━━━━
    Code de réservation : {reservation.reservation_code}
    
    ÉVÉNEMENT
    ━━━━━━━━━━━━━━━━━━━━━━━━━━
    Titre : {reservation.event.title}
    Date : {reservation.event.date.strftime('%d/%m/%Y à %H:%M')}
    Lieu : {reservation.event.location}
    Catégorie : {reservation.event.get_category_display()}
    
    VOTRE RÉSERVATION
    ━━━━━━━━━━━━━━━━━━━━━━━━━━
    Nombre de places : {reservation.number_of_seats}
    Prix par place : {reservation.event.price_per_person} TND
    Prix total : {reservation.total_price} TND
    
    IMPORTANT
    ━━━━━━━━━━━━━━━━━━━━━━━━━━
    - Présentez ce billet (QR code) à l'entrée
    - L'accès est possible jusqu'à 10 minutes après le début
    - Ce billet est unique et nominatif
    
    Merci de votre confiance !
    L'équipe Festy Event
    """
    
    # Créer l'email
    subject = f'🎫 Confirmation de réservation - {reservation.event.title}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = reservation.user.email or settings.ADMIN_EMAIL
    
    # Créer le message avec HTML et texte
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email]
    )
    
    # Attacher la version HTML
    email.attach_alternative(html_content, "text/html")
    
    # Attacher le QR code comme image inline
    qr_image = MIMEImage(qr_buffer.read())
    qr_image.add_header('Content-ID', '<qrcode>')
    qr_image.add_header('Content-Disposition', 'inline', filename='qrcode.png')
    email.attach(qr_image)
    
    # Envoyer l'email
    try:
        email.send(fail_silently=False)
        return True, "Email envoyé avec succès"
    except Exception as e:
        return False, f"Erreur lors de l'envoi: {str(e)}"
