"""
Module pour générer des QR codes pour les réservations
"""
import qrcode
from io import BytesIO
import base64
from django.conf import settings

def generate_qr_code(reservation):
    """
    Génère un QR code pour une réservation
    Le QR code contient le code de réservation et l'ID
    """
    # Données encodées dans le QR code
    qr_data = f"FESTY-{reservation.reservation_code}-{reservation.id}"
    
    # Créer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Créer l'image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir en base64 pour l'email
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64, qr_data

def get_qr_code_url(reservation):
    """
    Retourne l'URL data du QR code pour utilisation dans les templates
    """
    img_base64, _ = generate_qr_code(reservation)
    return f"data:image/png;base64,{img_base64}"
