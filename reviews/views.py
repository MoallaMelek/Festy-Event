from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from .models import Review, ReviewHelpful, FAQ, ContactMessage


@login_required
def add_review(request, content_type_id, object_id):
    """Ajouter un avis"""
    if request.method == 'POST':
        content_type = get_object_or_404(ContentType, id=content_type_id)
        
        # Vérifier si l'utilisateur a déjà laissé un avis
        existing_review = Review.objects.filter(
            content_type=content_type,
            object_id=object_id,
            author=request.user
        ).first()
        
        if existing_review:
            messages.warning(request, 'Vous avez déjà laissé un avis pour cet élément.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Créer l'avis
        review = Review.objects.create(
            content_type=content_type,
            object_id=object_id,
            author=request.user,
            rating=int(request.POST.get('rating', 5)),
            title=request.POST.get('title', ''),
            comment=request.POST.get('comment', ''),
            cleanliness_rating=request.POST.get('cleanliness_rating') or None,
            service_rating=request.POST.get('service_rating') or None,
            value_rating=request.POST.get('value_rating') or None,
            location_rating=request.POST.get('location_rating') or None,
        )
        
        messages.success(request, 'Votre avis a été ajouté avec succès !')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return redirect('/')


@login_required
def mark_helpful(request, pk):
    """Marquer un avis comme utile"""
    review = get_object_or_404(Review, pk=pk)
    
    helpful, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user
    )
    
    if created:
        review.helpful_count += 1
        review.save()
        messages.success(request, 'Merci pour votre retour !')
    else:
        messages.info(request, 'Vous avez déjà marqué cet avis comme utile.')
    
    return redirect(request.META.get('HTTP_REFERER', '/'))


def faq_list(request):
    """Liste des FAQs"""
    category_filter = request.GET.get('category')
    search = request.GET.get('search')
    
    faqs = FAQ.objects.filter(is_active=True)
    
    if category_filter:
        faqs = faqs.filter(category=category_filter)
    
    if search:
        faqs = faqs.filter(
            Q(question__icontains=search) |
            Q(answer__icontains=search)
        )
    
    # Grouper par catégorie
    faq_categories = {}
    for faq in faqs:
        if faq.category not in faq_categories:
            faq_categories[faq.category] = []
        faq_categories[faq.category].append(faq)
    
    context = {
        'faq_categories': faq_categories,
        'all_categories': FAQ.CATEGORY_CHOICES,
        'current_category': category_filter,
        'search_query': search,
    }
    return render(request, 'reviews/faq_list.html', context)


def faq_helpful(request, pk):
    """Marquer une FAQ comme utile"""
    faq = get_object_or_404(FAQ, pk=pk)
    faq.helpful_count += 1
    faq.views_count += 1
    faq.save()
    
    messages.success(request, 'Merci pour votre retour !')
    return redirect('faq_list')


def contact(request):
    """Page de contact"""
    if request.method == 'POST':
        message = ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
            user=request.user if request.user.is_authenticated else None
        )
        
        messages.success(request, 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
        return redirect('contact')
    
    return render(request, 'reviews/contact.html')
