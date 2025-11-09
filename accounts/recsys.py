from django.utils import timezone
from datetime import timedelta
from .models import Like, Publication
from django.db.models import Count
from django.db.models import Q
import math





#this is recomendation systems only for publication

TIME_LIMIT = timezone.now() - timedelta(days=1)

def get_feed_for_user(user):

    # ============== збір інфи ============

    # множини з авторами і тегами які юзер лайкає
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




    # =============== Ранжування ===================== 



    #поєднує кандидатів за останнім часом
    candidates = Publication.objects.filter(
        Q(user__in=authors) |
        Q(tags__in=tags) |
        Q(id__in=popular_posts.values('id')),
        created_at__gte=TIME_LIMIT
    ).distinct()

    candidates = list(candidates)

    # ========== Ранжування ===========

    # Готуємо нормалізацію
    max_likes = max((p.likes.count() for p in candidates), default=1)
    vidlatka(authors, tags, popular_posts)

    def score_post(post):
        score = 0

        # Автор знайомий → сильний сигнал
        if post.user in authors:
            score += 2

        # Співпадіння тегів → середній сигнал
        score += post.tags.filter(id__in=[t.id for t in tags]).count()

        # Популярність нормована → легкий бонус
        score += 0.3 * (post.likes.count() / max_likes)

        # Новизна → посилюємо свіжі пости
        age_seconds = (timezone.now() - post.created_at).total_seconds()
        freshness = max(0, 1 - age_seconds / (60 * 60 * 24))  # за добу згасає
        score += 0.5 * freshness

        return score

    # Рахуємо оцінки та сортуємо
    candidates = sorted(candidates, key=score_post, reverse=True)

    # ---- Підмішування популярних (щоб фід був живим) ----
    popular_list = list(popular_posts)

    if popular_list:
        mix_count = max(1, math.ceil(len(candidates) * 0.35))
        pop_to_insert = popular_list[:mix_count]
        step = max(1, len(candidates) // mix_count)

        i = step
        for p in pop_to_insert:
            candidates.insert(i, p)
            i += step

    return candidates

    



def get_popular_feed():

    popular = (
        Publication.objects
        .filter(created_at__gte=TIME_LIMIT)
        .annotate(likes_count=Count('likes'))  # рахуємо лайки на рівні SQL
        .order_by('-likes_count')              # сортуємо від найбільш залайканих
    )

    return popular


def vidlatka(authors, tags, popular_posts):
        
    author_posts = Publication.objects.filter(
        user__in=authors,
        created_at__gte = TIME_LIMIT
    )

    tag_posts = Publication.objects.filter(
        tags__in=tags,
        created_at__gte=TIME_LIMIT
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
            f.write(f"{pub.title} | {pub.user.username} | {pub.created_at}\n")
        

def debug_feed(candidates, score_post):
    with open("file.txt", "w", encoding="utf-8") as f:
        f.write("=== SCORED FEED ===\n")
        for post in candidates:
            score = score_post(post)
            tag_names = ", ".join(tag.name for tag in post.tags.all())
            f.write(f"{post.title} | Автор: {post.user.username} | Теги: {tag_names} | Лайки: {post.likes.count()} | SCORE: {score:.3f} | {post.created_at}\n")
