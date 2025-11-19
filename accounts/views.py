from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Publication, Like, Comments, Tag
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CreatePublicationForm, CreateCommentsForms
from django.http import JsonResponse
from .recsys import get_feed_for_user, get_popular_feed, tegs_feed_popular, get_random_feed_for_user
from rapidfuzz import process
from django_ratelimit.decorators import ratelimit





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


    return render(request, "register.html")

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

    return render(request, "login.html")

def out(request):
    logout(request)
    return redirect("login")


# ====== For User Interaction ==========

def home_page(request):
    #інфа якщо користувач не залогінений
    if not request.user.is_authenticated:
        likes = Like.objects.all()
        publication = get_popular_feed()
        tag_info = list(tegs_feed_popular())
        tags = Tag.objects.filter(name__in=tag_info)

        context = {
            "tags":tags,
            "publication":publication,
            "likes":likes,
        }
        return render(request, "home_page.html", context=context)
    
    
    #якщо залогінений
    publication = get_feed_for_user(request.user)
    likes = Like.objects.all()
    
    #вивід популярних тегів
    tag_info = list(tegs_feed_popular())
    tags = Tag.objects.filter(name__in=tag_info)

    #другий фід
    explore_publications =  get_random_feed_for_user(request.user)


    #liked_posts_ids = set(Like.objects.filter(user=request.user).values_list('publication_id', flat=True))
    #publication = [p for p in publication if p.id not in liked_posts_ids]

    

    return render(request, "home_page.html", {"publication":publication, "explore_publications":explore_publications, "likes":likes, "tags":tags})


@ratelimit(key='ip', rate='2/m', method='POST', block=True)
def create_publication(request):
    if request.user.is_authenticated:

        if request.method == "POST":
            tags_all = Tag.objects.all()

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

@login_required
@ratelimit(key='ip', rate='2/m', method='POST', block=True)
def create_comments(request, slug, parent=None):
    if request.method == "POST":
        pub = Publication.objects.get(slug=slug)
        form = CreateCommentsForms(request.POST)

        if form.is_valid():
            obj = form.save(commit = False)
            obj.user = request.user
            obj.publication = pub
            if parent:
                par = Comments.objects.get(id=parent)
                obj.parent = par
                obj.save()
            else:
                obj.save()

        return redirect('pub', slug=pub.slug)

    else:
        form = CreateCommentsForms()

    return render(request, "create_c.html", {"form":form})

def open_publication(request, slug):
    pub = get_object_or_404(Publication, slug=slug)
    return render(request, "pub.html", {"pub":pub})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    publications = Publication.objects.filter(user=profile_user).order_by('-id')
    likes_publication = Like.objects.filter(user=profile_user).order_by('-created_at')
    coments_user = Comments.objects.filter(user=profile_user).order_by('-created_at')
    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'publications': publications,
        'likes_publication': likes_publication,
        'coments_user':coments_user,
    })

def search(request, search):
    tags = list(Tag.objects.values_list('name', flat=True))
    best_match = process.extractOne(search, tags)

    tag_info = list(tegs_feed_popular())
    tags = Tag.objects.filter(name__in=tag_info)

    if best_match:
        tags_pub = Tag.objects.get(name=best_match[0])
        posts = Publication.objects.filter(tags=tags_pub)
        

    
    return render(request, "result_of_search.html", {"posts":posts, "tags":tags})








