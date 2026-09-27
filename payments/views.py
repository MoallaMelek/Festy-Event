from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from .models import Payment, Invoice
from .forms import PaymentForm, InvoiceForm
from reservations.models import Reservation
# from .pdf_generator import generate_invoice_pdf  # Désactivé temporairement


# ============= CLIENT VIEWS (US 4.2) =============

@login_required
def client_invoice_detail(request, invoice_id):
    """US 4.1 : Client voit le détail de sa facture"""
    invoice = get_object_or_404(Invoice, id=invoice_id, reservation__user=request.user)
    payments = Payment.objects.filter(reservation=invoice.reservation).order_by('-created_at')
    
    context = {
        'invoice': invoice,
        'payments': payments,
    }
    return render(request, 'payments/client_invoice_detail.html', context)


@login_required
def client_pay_invoice(request, invoice_id):
    """US 4.2 : Client effectue un paiement pour sa facture"""
    invoice = get_object_or_404(Invoice, id=invoice_id, reservation__user=request.user)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        amount = request.POST.get('amount')
        
        # Créer le paiement
        payment = Payment.objects.create(
            reservation=invoice.reservation,
            amount=amount,
            payment_method=payment_method,
            status='COMPLETED',  # Dans un vrai système, ce serait PENDING puis COMPLETED après validation
            notes=f"Paiement effectué par le client pour la facture {invoice.invoice_number}"
        )
        payment.mark_as_completed()
        
        # Marquer la facture comme payée si le montant est suffisant
        total_paid = Payment.objects.filter(
            reservation=invoice.reservation, 
            status='COMPLETED'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        if total_paid >= invoice.total_amount:
            invoice.mark_as_paid()
            invoice.reservation.is_paid = True
            invoice.reservation.save()
            messages.success(request, f'✅ Paiement effectué avec succès ! Facture {invoice.invoice_number} payée intégralement.')
        else:
            messages.success(request, f'✅ Paiement partiel effectué. Reste à payer : {invoice.total_amount - total_paid} TND')
        
        return redirect('reservation_detail', pk=invoice.reservation.id)
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'payments/client_pay_invoice.html', context)


@login_required
def download_invoice_pdf(request, invoice_id):
    """Afficher la facture en version imprimable (HTML)"""
    # Vérifier que l'utilisateur a accès à cette facture
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Vérification des permissions
    if not request.user.is_staff and invoice.reservation.user != request.user:
        messages.error(request, "Vous n'avez pas accès à cette facture.")
        return redirect('dashboard')
    
    # Générer QR code basique pour paiement
    import qrcode
    from io import BytesIO
    import base64
    
    payment_url = f"http://localhost:8000/invoice/{invoice.id}/pay/"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(payment_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    qr_code_data = f"data:image/png;base64,{img_str}"
    
    context = {
        'invoice': invoice,
        'reservation': invoice.reservation,
        'user': invoice.reservation.user,
        'event': invoice.reservation.event,
        'qr_code': qr_code_data,
        'is_print_view': True,
        'company_name': 'Festy Event',
        'company_address': 'Avenue Habib Bourguiba, Tunis 1000, Tunisie',
        'company_phone': '+216 71 123 456',
        'company_email': 'contact@festyevent.tn',
    }
    
    # Retourner le template PDF (HTML version imprimable)
    return render(request, 'payments/invoice_pdf_template.html', context)


# ============= ADMIN VIEWS (US 4.3, 4.4) =============

@staff_member_required
def admin_payment_list(request):
    """US 4.4 : Admin suit tous les paiements"""
    payments = Payment.objects.all().select_related('reservation', 'reservation__user', 'reservation__event').order_by('-created_at')
    
    # Filtres
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    # Statistiques
    total_amount = payments.filter(status='COMPLETED').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_count = payments.filter(status='PENDING').count()
    completed_count = payments.filter(status='COMPLETED').count()
    failed_count = payments.filter(status='FAILED').count()
    
    context = {
        'payments': payments,
        'total_amount': total_amount,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'failed_count': failed_count,
    }
    return render(request, 'payments/payment_list.html', context)


@staff_member_required
def payment_create(request):
    """Créer un nouveau paiement (admin)"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Paiement {payment.transaction_id} créé avec succès.')
            return redirect('payment_detail', pk=payment.id)
    else:
        # Pré-remplir si reservation_id dans l'URL
        reservation_id = request.GET.get('reservation')
        initial_data = {}
        if reservation_id:
            try:
                reservation = Reservation.objects.get(id=reservation_id)
                initial_data = {
                    'reservation': reservation,
                    'amount': reservation.total_price
                }
            except Reservation.DoesNotExist:
                pass
        form = PaymentForm(initial=initial_data)
    
    context = {'form': form}
    return render(request, 'payments/payment_form.html', context)


@staff_member_required
def payment_detail(request, pk):
    """Détails d'un paiement (admin)"""
    payment = get_object_or_404(Payment, id=pk)
    
    context = {'payment': payment}
    return render(request, 'payments/payment_detail.html', context)


@staff_member_required
def payment_complete(request, pk):
    """Marquer un paiement comme complété"""
    payment = get_object_or_404(Payment, id=pk)
    payment.mark_as_completed()
    messages.success(request, f'Paiement {payment.transaction_id} marqué comme complété.')
    return redirect('payment_detail', pk=pk)


@staff_member_required
def payment_refund(request, pk):
    """Rembourser un paiement"""
    payment = get_object_or_404(Payment, id=pk)
    payment.refund()
    messages.success(request, f'Paiement {payment.transaction_id} remboursé.')
    return redirect('payment_detail', pk=pk)


# ============= INVOICES =============

@staff_member_required
def admin_invoice_list(request):
    """US 4.3 : Admin visualise toutes les factures"""
    invoices = Invoice.objects.all().select_related('reservation', 'reservation__user', 'reservation__event').order_by('-created_at')
    
    # Filtres
    status_filter = request.GET.get('status', '')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    # Statistiques
    total_amount = invoices.filter(status='PAID').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    draft_count = invoices.filter(status='DRAFT').count()
    issued_count = invoices.filter(status='ISSUED').count()
    paid_count = invoices.filter(status='PAID').count()
    
    context = {
        'invoices': invoices,
        'total_amount': total_amount,
        'draft_count': draft_count,
        'issued_count': issued_count,
        'paid_count': paid_count,
        'status_filter': status_filter,
    }
    return render(request, 'payments/invoice_list.html', context)


@staff_member_required
def invoice_create(request):
    """Créer une nouvelle facture (admin)"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Facture {invoice.invoice_number} créée avec succès.')
            return redirect('invoice_detail', pk=invoice.id)
    else:
        # Pré-remplir si reservation_id dans l'URL
        reservation_id = request.GET.get('reservation')
        initial_data = {}
        if reservation_id:
            try:
                reservation = Reservation.objects.get(id=reservation_id)
                initial_data = {
                    'reservation': reservation,
                    'total_amount': reservation.total_price,
                    'tax_amount': reservation.total_price * 0.19
                }
            except Reservation.DoesNotExist:
                pass
        form = InvoiceForm(initial=initial_data)
    
    context = {'form': form}
    return render(request, 'payments/invoice_form.html', context)


@staff_member_required
def invoice_detail(request, pk):
    """Détails d'une facture (admin)"""
    invoice = get_object_or_404(Invoice, id=pk)
    
    context = {'invoice': invoice}
    return render(request, 'payments/invoice_detail.html', context)


@staff_member_required
def invoice_issue(request, pk):
    """Émettre une facture"""
    invoice = get_object_or_404(Invoice, id=pk)
    invoice.mark_as_issued()
    messages.success(request, f'Facture {invoice.invoice_number} émise.')
    return redirect('invoice_detail', pk=pk)


@staff_member_required
def invoice_mark_paid(request, pk):
    """Marquer une facture comme payée"""
    invoice = get_object_or_404(Invoice, id=pk)
    invoice.mark_as_paid()
    messages.success(request, f'Facture {invoice.invoice_number} marquée comme payée.')
    return redirect('invoice_detail', pk=pk)
