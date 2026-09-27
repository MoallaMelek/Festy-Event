from django.urls import path
from . import views

urlpatterns = [
    # Client - Payer une facture (US 4.2)
    path('invoice/<int:invoice_id>/pay/', views.client_pay_invoice, name='client_pay_invoice'),
    path('invoice/<int:invoice_id>/', views.client_invoice_detail, name='client_invoice_detail'),
    path('invoice/<int:invoice_id>/pdf/', views.download_invoice_pdf, name='download_invoice_pdf'),
    
    # Admin - Supervision des paiements et factures (US 4.3, 4.4)
    path('payments/', views.admin_payment_list, name='admin_payment_list'),
    path('invoices/', views.admin_invoice_list, name='admin_invoice_list'),
    
    # Anciennes URLs admin pour les détails (lecture seule)
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
]
