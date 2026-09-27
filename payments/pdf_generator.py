"""
Service de génération de factures PDF professionnelles
"""
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS
from io import BytesIO
import qrcode
import base64


def generate_invoice_qr_code(invoice):
    """Générer un QR code pour le paiement de la facture"""
    # Données du QR code (URL de paiement)
    payment_url = f"http://localhost:8000/invoice/{invoice.id}/pay/"
    
    # Créer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payment_url)
    qr.make(fit=True)
    
    # Convertir en image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir en base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def generate_invoice_pdf(invoice):
    """
    Générer un PDF professionnel pour une facture
    
    Args:
        invoice: Instance de modèle Invoice
        
    Returns:
        BytesIO: Buffer contenant le PDF généré
    """
    # Générer le QR code de paiement
    qr_code_data = generate_invoice_qr_code(invoice)
    
    # Préparer le contexte pour le template
    context = {
        'invoice': invoice,
        'reservation': invoice.reservation,
        'user': invoice.reservation.user,
        'event': invoice.reservation.event,
        'qr_code': qr_code_data,
        'company_name': 'Festy Event',
        'company_address': 'Avenue Habib Bourguiba, Tunis 1000',
        'company_phone': '+216 71 123 456',
        'company_email': 'contact@festyevent.tn',
    }
    
    # Rendre le template HTML
    html_string = render_to_string('payments/invoice_pdf_template.html', context)
    
    # CSS personnalisé pour le PDF
    css_string = """
    @page {
        size: A4;
        margin: 2cm;
    }
    body {
        font-family: 'DejaVu Sans', sans-serif;
        color: #333;
        line-height: 1.6;
    }
    .header {
        border-bottom: 3px solid #fb923c;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    .company-info {
        text-align: right;
    }
    .invoice-title {
        color: #fb923c;
        font-size: 32px;
        font-weight: bold;
    }
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin: 30px 0;
    }
    .info-box {
        border: 1px solid #e5e7eb;
        padding: 15px;
        border-radius: 8px;
        background: #f9fafb;
    }
    .info-box h3 {
        color: #fb923c;
        margin-top: 0;
        font-size: 14px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    th {
        background: #fb923c;
        color: white;
        padding: 12px;
        text-align: left;
    }
    td {
        padding: 10px 12px;
        border-bottom: 1px solid #e5e7eb;
    }
    .totals {
        margin-top: 30px;
        text-align: right;
    }
    .totals table {
        width: 300px;
        margin-left: auto;
    }
    .total-row {
        font-size: 18px;
        font-weight: bold;
        color: #fb923c;
    }
    .footer {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 2px solid #e5e7eb;
        text-align: center;
        font-size: 12px;
        color: #6b7280;
    }
    .qr-section {
        text-align: center;
        margin: 30px 0;
        padding: 20px;
        background: #f9fafb;
        border-radius: 8px;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .status-paid {
        background: #d1fae5;
        color: #065f46;
    }
    .status-issued {
        background: #dbeafe;
        color: #1e40af;
    }
    """
    
    # Convertir HTML en PDF
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(
        pdf_file,
        stylesheets=[CSS(string=css_string)]
    )
    pdf_file.seek(0)
    
    return pdf_file
