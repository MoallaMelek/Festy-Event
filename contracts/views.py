from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from .models import Contract
from .forms import ContractForm


@staff_member_required
def contract_list(request):
    """List all contracts with filtering"""
    contracts = Contract.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        contracts = contracts.filter(status=status_filter)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        contracts = contracts.filter(contract_type=type_filter)
    
    # Statistics
    total_contracts = Contract.objects.count()
    draft_count = Contract.objects.filter(status='DRAFT').count()
    active_count = Contract.objects.filter(status='ACTIVE').count()
    completed_count = Contract.objects.filter(status='COMPLETED').count()
    
    context = {
        'contracts': contracts,
        'total_contracts': total_contracts,
        'draft_count': draft_count,
        'active_count': active_count,
        'completed_count': completed_count,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    return render(request, 'contracts/contract_list.html', context)


@staff_member_required
def contract_create(request):
    """Create a new contract"""
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.created_by = request.user
            contract.save()
            messages.success(request, f'Contrat "{contract.title}" créé avec succès!')
            return redirect('contract_detail', pk=contract.id)
    else:
        form = ContractForm()
    
    return render(request, 'contracts/contract_form.html', {'form': form, 'action': 'Créer'})


@staff_member_required
def contract_detail(request, pk):
    """View contract details"""
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, 'contracts/contract_detail.html', {'contract': contract})


@staff_member_required
def contract_update(request, pk):
    """Update an existing contract"""
    contract = get_object_or_404(Contract, pk=pk)
    
    # Only allow editing if contract is in DRAFT status
    if contract.status != 'DRAFT':
        messages.error(request, 'Seuls les contrats en brouillon peuvent être modifiés.')
        return redirect('contract_detail', pk=contract.id)
    
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contrat "{contract.title}" modifié avec succès!')
            return redirect('contract_detail', pk=contract.id)
    else:
        form = ContractForm(instance=contract)
    
    return render(request, 'contracts/contract_form.html', {
        'form': form,
        'contract': contract,
        'action': 'Modifier'
    })


@staff_member_required
def contract_activate(request, pk):
    """Activate a contract"""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        contract.activate()
        messages.success(request, f'Contrat "{contract.title}" activé avec succès!')
        return redirect('contract_detail', pk=contract.id)
    
    return redirect('contract_detail', pk=contract.id)


@staff_member_required
def contract_complete(request, pk):
    """Mark contract as completed"""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        contract.complete()
        messages.success(request, f'Contrat "{contract.title}" marqué comme terminé!')
        return redirect('contract_detail', pk=contract.id)
    
    return redirect('contract_detail', pk=contract.id)


@staff_member_required
def contract_cancel(request, pk):
    """Cancel a contract"""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        contract.cancel()
        messages.success(request, f'Contrat "{contract.title}" annulé!')
        return redirect('contract_detail', pk=contract.id)
    
    return redirect('contract_detail', pk=contract.id)


@staff_member_required
def contract_sign(request, pk):
    """Sign a contract (client signature)"""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        signature_data = request.POST.get('signature')
        if signature_data:
            contract.client_signature = signature_data
            contract.client_signed_at = timezone.now()
            contract.save()
            messages.success(request, 'Signature client enregistrée!')
            return redirect('contract_detail', pk=contract.id)
        else:
            messages.error(request, 'Signature manquante!')
    
    return render(request, 'contracts/contract_sign.html', {'contract': contract})


@staff_member_required
def contract_admin_sign(request, pk):
    """Admin signature for contract"""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        signature_data = request.POST.get('signature')
        if signature_data:
            contract.admin_signature = signature_data
            contract.admin_signed_at = timezone.now()
            contract.save()
            messages.success(request, 'Signature admin enregistrée!')
            return redirect('contract_detail', pk=contract.id)
        else:
            messages.error(request, 'Signature manquante!')
    
    return render(request, 'contracts/contract_admin_sign.html', {'contract': contract})
