from django.utils import timezone
from datetime import timedelta
from .models import Like, Publication, Tag, Comments
from django.db.models import Count
from django.db.models import Q
import math
import random
from random import shuffle






#this is recomendation systems only for publication
#TIME_LIMIT = timezone.now() - timedelta(days=100)

def get_time_limit(days=1):
    return timezone.now() - timedelta(days=days)



def get_feed_for_user(user):

    # ============== збір інфи ============

    authors = set() 
    tags = set()

    #пости які юзер лайкає
    user_liked_author_posts = Like.objects.filter(user=user) 
    
    # популярні пости (відфільтровані з часом)
    popular_posts = get_popular_feed()


    #додає в множини інфу (працює тому не треба нічого чіпати)
    for like in user_liked_author_posts:
        authors.add(like.publication.user)
        for tag in like.publication.tags.all():
            tags.add(tag)


    fresh_post = get_random_fresh_posts()


    #поєднує кандидатів за останнім часом
    candidates = Publication.objects.filter(
        Q(user__in=authors) |
        Q(tags__in=tags) |
        Q(id__in=popular_posts.values('id')) |
        Q(id__in=[p.id for p in fresh_post]),
        created_at__gte=get_time_limit()
    ).annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments')
    ).distinct()

    candidates = list(candidates)





    # ========== Ранжування ===========

    max_likes = max((p.likes.count() for p in candidates), default=1)
    if max_likes == 0:
        max_likes = 1
    max_comments = max((Comments.objects.filter(publication=pub1).count() for pub1 in candidates), default=1)
    if max_comments == 0:
        max_comments = 1

    def score_post(post):
        score = 0

        #Співпадіння авторів
        if post.user in authors:
            score += 2

        # Співпадіння тегів
        score += post.tags.filter(id__in=[t.id for t in tags]).count()

        # Популярність (бонус)
        score += 0.3 * (post.likes.count() / max_likes)
        score += 0.5 * (post.comments.count() / max_comments)

        # Новизна (бонус)
        age_seconds = (timezone.now() - post.created_at).total_seconds()
        freshness = max(0, 1 - age_seconds / (60 * 60 * 24))  # за добу згасає
        score += 0.5 * freshness

        return score


    # Рахуємо оцінки та сортуємо
    candidates = sorted(candidates, key=score_post, reverse=True)
    
    #підмішування популярних публікацій 
    popular_list = list(popular_posts)
    

    if popular_list:
        mix_count = max(1, math.ceil(len(candidates) * 0.35))
        pop_to_insert = popular_list[:mix_count]
        step = max(1, len(candidates) // mix_count)
        

        i = step
        for p in pop_to_insert:
            if p not in candidates:
                candidates.insert(i, p)
                i += step
    return candidates



def get_popular_feed(limit=10):
    return (
        Publication.objects
        .filter(created_at__gte=get_time_limit())
        .annotate(likes_count=Count('likes'))
        .order_by('-likes_count')
        [:limit]
    )



def get_random_fresh_posts():
    fresh_posts = list(Publication.objects.order_by('-created_at')[:5])
    random.shuffle(fresh_posts)
    return fresh_posts[:3]



def tegs_feed_popular(max_tags=3):
    popular_pub = get_popular_feed().prefetch_related('tags')

    tag_counts = {}
    for pub in popular_pub:
        for tag in pub.tags.all():
            tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1

    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    return [tag for tag, count in sorted_tags[:max_tags]]



def get_exploration_feed_for_user(user):
    # ======= Збір інфи про юзера ==========
    authors = set()
    tags = set()

    # Оптимізація: prefetch щоб уникнути N+1
    user_liked_author_posts = (
        Like.objects
        .filter(user=user)
        .select_related('publication__user')
        .prefetch_related('publication__tags')
    )

    for like in user_liked_author_posts:
        authors.add(like.publication.user)
        for tag in like.publication.tags.all():
            tags.add(tag)

    # Всі пости за останній період з аннотаціями
    candidates = (
        Publication.objects
        .filter(created_at__gte=get_time_limit())
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )
    )
    
    # Отримуємо ID постів які юзер вже лайкнув
    user_liked_post_ids = set(
        Like.objects
        .filter(user=user)
        .values_list('publication_id', flat=True)
    )
    
    candidates = list(candidates)

    # ======== Ранжування =========
    max_likes = max((p.likes_count for p in candidates), default=1)
    max_comments = max((p.comments_count for p in candidates), default=1)

    if max_comments == 0:
        max_comments = 1
    if max_likes == 0:
        max_likes = 1

    now = timezone.now()  # Рахуємо один раз

    def score_post(post):
        score = 0

        # бінус бав для знайомих авторів
        if post.user in authors:
            score -= 1.5

        # мінус баф пости які юзер вже лайкнув
        if post.id in user_liked_post_ids:
            score -= 3  # Сильна кара

        # ЗАОХОЧУЄ свіжі пости 
        age_seconds = (now - post.created_at).total_seconds()
        freshness = max(0, 1 - age_seconds / (60 * 60 * 24))
        score += 1.5 * freshness  # Збільшив вагу свіжості

        # Легкий бонус за популярність
        score += 0.2 * (post.likes_count / max_likes)
        score += 0.3 * (post.comments_count / max_comments)

        # баф якщо пост від автора з тегами юзера (але не сам автор)
        if post.user not in authors:
            matching_tags = post.tags.filter(id__in=[t.id for t in tags]).count()
            if matching_tags > 0:
                score += 0.5 * matching_tags  # Схожі інтереси, але новий автор

        return score

    candidates = sorted(candidates, key=score_post, reverse=True)
    debug_feed(candidates, score_post)
    return candidates
    



# лише для тесту (відкладка)
def vidlatka(authors, tags, popular_posts):
        
    author_posts = Publication.objects.filter(
        user__in=authors,
        created_at__gte = get_time_limit()
    )

    tag_posts = Publication.objects.filter(
        tags__in=tags,
        created_at__gte=get_time_limit()
    )

    with open("file.txt", "w", encoding="utf-8") as f:
        f.write("=== Авторські пости ===\n")
        for pub in author_posts:
            f.write(f"{pub.title} | {pub.user.username} | {pub.created_at}\n")

        f.write("\n=== Пости з тегами ===\n")
        for pub in tag_posts:
            f.write(f"{pub.title} | {pub.user.username} | {pub.created_at}\n")

        f.write("\n=== Популярні пости ===\n")
        for pub in popular_posts:
            f.write(f"{pub.title} | {pub.user.username} | {pub.created_at} | {list(pub.tags.all())}\n")
        
def debug_feed(candidates, score_post):
    with open("file.txt", "w", encoding="utf-8") as f:
        f.write("=== SCORED FEED ===\n")
        for post in candidates:
            score = score_post(post)
            tag_names = ", ".join(tag.name for tag in post.tags.all())
            f.write(f"{post.title} | Автор: {post.user.username} | Теги: {tag_names} | Лайки: {post.likes.count()} | SCORE: {score:.3f} | {post.created_at}\n")

