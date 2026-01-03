from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Publication, Like, Comments, Tag
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CreatePublicationForm, CreateCommentsForms
from django.http import JsonResponse
from .recsys import get_feed_for_user, get_popular_feed, tegs_feed_popular, get_exploration_feed_for_user
from rapidfuzz import process
from django_ratelimit.decorators import ratelimit
from .utils import paginator
import json
from django.views.decorators.cache import cache_page
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.template.loader import render_to_string






# ======= Autorisation and logout =================
def page_register(request):
    if request.method == "POST":
        user_name = request.POST.get("user_name")
        meno = request.POST.get("first_name")
        priezvisko = request.POST.get("last_name")
        email = request.POST.get("email")
        heslo = request.POST.get("password")
        gender = request.POST.get("gender")


        if User.objects.filter(username=user_name).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Uz existuje")
            return redirect("register")
            
        else:
            User.objects.create_user(
            username=user_name,
            email=email,
            password=heslo,
            first_name=meno,
            last_name=priezvisko,
            gender=gender
            )

        return redirect("login")


    return render(request, "auth/register.html")

def page_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        heslo = request.POST.get("password")

        user = authenticate(request, username=username, password=heslo)
        if user is not None:
            login(request, user)
            return redirect("home_page")
        else:
            messages.error(request, "Nesprávne prihlasovacie meno alebo heslo")
            return redirect("login")

    return render(request, "auth/login.html")

def out(request):
    logout(request)
    return redirect("login")


# ====== For User Interaction ==========
#@cache_page(60)
from django.http import JsonResponse
from django.template.loader import render_to_string

def home_page(request):
    if not request.user.is_authenticated:
        likes = Like.objects.all()
        publication = get_popular_feed()[:10]  # Перші 10
        tag_info = list(tegs_feed_popular())
        tags = Tag.objects.filter(name__in=tag_info)
        context = {
            "tags": tags,
            "publication": publication,
            "likes": likes,
        }
        return render(request, "feed/home_page.html", context=context)
    
    # Для залогінених
    page_feed = int(request.GET.get("page_feed", 0))
    page_explore = int(request.GET.get("page_explore", 0))
    
    page_publications = get_feed_for_user(request.user, page=page_feed)
    page_explores = get_exploration_feed_for_user(request.user, page=page_explore)

    
    # Якщо це AJAX запит - повертаємо JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        feed_type = request.GET.get('feed_type', 'feed1')
        
        if feed_type == 'feed1':
            html = render_to_string('feed/modal_parts/publication_list.html', {
                'publications': page_publications,
                'request': request
            })
            return JsonResponse({
                'html': html,
                'has_more': len(page_publications) == 10
            })
        else:
            html = render_to_string('feed/modal_parts/publication_list.html', {
                'publications': page_explores,
                'request': request
            })
            return JsonResponse({
                'html': html,
                'has_more': len(page_explores) == 10
            })
    
    # Звичайний запит
    likes = Like.objects.all()
    tag_info = list(tegs_feed_popular())
    tags = Tag.objects.filter(name__in=tag_info)
    
    context = {
        "publication": page_publications,
        "explore_publications": page_explores,
        "likes": likes,
        "tags": tags,
        "page_feed": page_feed,
        "page_explore": page_explore,
    }
    return render(request, "feed/home_page.html", context=context)



def create_post_page(request):
    tag_info = list(tegs_feed_popular())
    tags = Tag.objects.filter(name__in=tag_info)
    return render(request, "post_users/create_post_page.html", {"tags": tags})


@ratelimit(key='ip', rate='2/m', method='POST', block=True)
def create_publication(request):
    if request.user.is_authenticated:

        if request.method == "POST":
            title = request.POST.get("title")
            text = request.POST.get("text")

            tags = request.POST.get("tags")

      
            if title and text and len(title.strip()) > 3 and len(text.strip()) > 3:
                pub = Publication.objects.create(user=request.user, title=title, text=text)

                for tag in tags.split():
                    obj, created = Tag.objects.get_or_create(name=tag.lower())
                    obj.usage_count += 1
                    obj.save()
                    pub.tags.add(obj)
            
        return redirect("home_page")
    
    else:
        return redirect("login")

@login_required
def like_publication(request, slug):
    pub = Publication.objects.get(slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, publication=pub)
    if not created:
        like.delete()
    likes_count = pub.likes.count()
    return JsonResponse({"likes": likes_count})


@require_POST
@login_required
#@ratelimit(key='ip', rate='2/m', method='POST', block=True)
def create_comments(request, slug, parent=None):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("JSON ^^.")
        
    text = data.get('text', '').strip()
    
    if not text:
        return HttpResponseBadRequest("???")

    publication = get_object_or_404(Publication, slug=slug)

    parent_comment = None
    if parent:
        try:
            parent_comment = Comments.objects.get(id=parent, publication=publication)
        except Comments.DoesNotExist:
            return HttpResponseBadRequest("???")

    Comments.objects.create(
        publication=publication,
        user=request.user,
        text=text,
        parent=parent_comment
    )

    return JsonResponse({"status": "success", "message": "Spravne"})



def open_publication(request, slug):
    pub = get_object_or_404(Publication, slug=slug)
    tag_info = list(tegs_feed_popular())
    tags = Tag.objects.filter(name__in=tag_info)

    return render(request, "post_users/pub.html", {"pub":pub, "tags":tags})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    publications = Publication.objects.filter(user=profile_user).order_by('-id')
    likes_publication = Like.objects.filter(user=profile_user).order_by('-created_at')
    coments_user = Comments.objects.filter(user=profile_user).order_by('-created_at')

    tag_info = list(tegs_feed_popular())
    tags = Tag.objects.filter(name__in=tag_info)

    
 
    return render(request, 'auth/profile.html', {
        'profile_user': profile_user,
        'publications': publications,
        'likes_publication': likes_publication,
        'coments_user':coments_user,
        'tags':tags,
    })


def search(request, search):
    pub_queryset = Publication.objects.order_by("created_at")
    pub_dict = {pub.text: pub for pub in pub_queryset}
    pub_texts = list(pub_dict.keys())
    
    all_matches = process.extract(search, pub_texts, limit=None)
    
    SIMILARITY_THRESHOLD = 56
    
    filtered_matches = [
        (text, score) for text, score, _ in all_matches 
        if score >= SIMILARITY_THRESHOLD
    ]
    filtered_matches.sort(key=lambda x: x[1], reverse=True)
 
    matched_texts = [match[0] for match in filtered_matches]
    posts = [pub_dict[text] for text in matched_texts if text in pub_dict]
    
    # Теги
    tag_info = list(tegs_feed_popular())
    tags = Tag.objects.filter(name__in=tag_info)
    
    return render(request, "feed/result_of_search.html", {
        "posts": posts, 
        "tags": tags
    })










