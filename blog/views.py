from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import BlogPost, BlogCategory, BlogComment, Newsletter


def blog_list(request):
    """Liste des articles de blog"""
    posts = BlogPost.objects.filter(status='PUBLISHED').select_related('category', 'author')
    
    # Filtrage par catégorie
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Recherche
    search = request.GET.get('search')
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    # Articles à la une
    featured_posts = BlogPost.objects.filter(status='PUBLISHED', is_featured=True)[:3]
    
    # Catégories
    categories = BlogCategory.objects.all()
    
    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search,
    }
    return render(request, 'blog/blog_list.html', context)


def blog_category(request, slug):
    """Articles d'une catégorie"""
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = BlogPost.objects.filter(status='PUBLISHED', category=category).select_related('author')
    
    # Pagination
    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/blog_category.html', context)


def blog_detail(request, slug):
    """Détail d'un article"""
    post = get_object_or_404(
        BlogPost.objects.select_related('category', 'author'),
        slug=slug,
        status='PUBLISHED'
    )
    
    # Incrémenter les vues
    post.increment_views()
    
    # Commentaires approuvés
    comments = post.comments.filter(is_approved=True, parent=None).select_related('author')
    
    # Articles similaires (même catégorie)
    related_posts = BlogPost.objects.filter(
        status='PUBLISHED',
        category=post.category
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
    }
    return render(request, 'blog/blog_detail.html', context)


@login_required
def add_comment(request, slug):
    """Ajouter un commentaire"""
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, slug=slug, status='PUBLISHED')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            comment = BlogComment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )
            messages.success(request, 'Votre commentaire a été ajouté avec succès !')
        else:
            messages.error(request, 'Le commentaire ne peut pas être vide.')
    
    return redirect('blog_detail', slug=slug)


def newsletter_subscribe(request):
    """Inscription à la newsletter"""
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name', '')
        
        if email:
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'name': name, 'is_active': True}
            )
            
            if created:
                messages.success(request, 'Merci de vous être abonné à notre newsletter !')
            else:
                if not newsletter.is_active:
                    newsletter.is_active = True
                    newsletter.unsubscribed_at = None
                    newsletter.save()
                    messages.success(request, 'Votre abonnement à la newsletter a été réactivé !')
                else:
                    messages.info(request, 'Vous êtes déjà abonné à notre newsletter.')
        else:
            messages.error(request, 'Veuillez fournir une adresse email valide.')
    
    return redirect(request.META.get('HTTP_REFERER', 'blog_list'))
