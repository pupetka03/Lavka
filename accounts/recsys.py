from django.utils import timezone
from datetime import timedelta
from .models import Like, Publication, Tag, Comments
from django.db.models import Count
from django.db.models import Q
import math
import random
from random import shuffle
from django.core.cache import cache



def get_time_limit(days=3):
    return timezone.now() - timedelta(days=days)


from django.db.models import Value, FloatField, IntegerField
from django.db.models.functions import Now
from django.utils import timezone

def get_feed_for_user(user, page=1):
    page = max(1, page)
    items_per_page = 10
    offset = (page - 1) * items_per_page
    limit = offset + items_per_page
    time_limit = get_time_limit()
    
    # Кешування інтересів
    cache_key = f'user_interests_{user.id}'
    interests = cache.get(cache_key)
    
    if not interests:
        liked_query = Like.objects.filter(user=user)
        interests = {
            'author_ids': list(liked_query.values_list('publication__user_id', flat=True).distinct()),
            'tag_ids': list(Publication.tags.through.objects.filter(
                publication__likes__user=user
            ).values_list('tag_id', flat=True).distinct())
        }
        cache.set(cache_key, interests, timeout=300)
    
    author_ids = interests['author_ids']
    tag_ids = interests['tag_ids']
    
    # Константи для scoring
    SCORE_WEIGHTS = {
        'likes': 1,
        'comments': 2,
        'tag_match': 1,
        'favorite_author': 2,
        'freshness': 1,
        'popular': 2  # ✅ Новий: бонус за популярність
    }
    
    # ✅ Отримуємо ID популярних постів
    popular_ids = get_popular_feed().values_list('id', flat=True)[:20]
    
    candidates = Publication.objects.filter(
        Q(user_id__in=author_ids) | 
        Q(tags__id__in=tag_ids) |
        Q(id__in=popular_ids),  # ✅ Додано популярні
        created_at__gte=time_limit
    ).annotate(
        # Підрахунки
        l_cnt=Count('likes', distinct=True),
        c_cnt=Count('comments', distinct=True),
        t_match=Count('tags', filter=Q(tags__id__in=tag_ids), distinct=True),
        
        # Свіжість
        is_fresh=Case(
            When(created_at__gte=timezone.now() - timedelta(hours=24), then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        ),
        
        # ✅ Чи це популярний пост?

        is_popular=Case(
            When(id__in=popular_ids, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).annotate(
        # Фінальний score
        score=ExpressionWrapper(
            (F('l_cnt') * Value(SCORE_WEIGHTS['likes'])) +
            (F('c_cnt') * Value(SCORE_WEIGHTS['comments'])) +
            (F('t_match') * Value(SCORE_WEIGHTS['tag_match'])) +
            (F('is_fresh') * Value(SCORE_WEIGHTS['freshness'])) +
            (F('is_popular') * Value(SCORE_WEIGHTS['popular'])) +  # ✅ Бонус за популярність
            Case(
                When(user_id__in=author_ids, then=Value(SCORE_WEIGHTS['favorite_author'])),
                default=Value(0),
                output_field=IntegerField()
            ),
            output_field=IntegerField()
        )
    ).select_related('user').prefetch_related('tags', 'likes').order_by('-score', '-created_at')
    
    return candidates[offset:limit]



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


from django.db.models import Case, When, F, FloatField, ExpressionWrapper, Count, Q, IntegerField
from django.db.models.functions import Now

def get_exploration_feed_for_user(user, page):
    
    page = max(1, page)
    items_per_page = 10
    offset = (page - 1) * items_per_page
    limit = offset + items_per_page


    time_limit = get_time_limit()
    
    # 1. Збираємо інтереси одним махом (ID тегів та авторів)
    liked_query = Like.objects.filter(user=user)
    author_ids = liked_query.values_list('publication__user_id', flat=True).distinct()
    tag_ids = Publication.tags.through.objects.filter(
        publication__likes__user=user
    ).values_list('tag_id', flat=True).distinct()
    
    # ID постів, які вже лайкнув
    liked_post_ids = liked_query.values_list('publication_id', flat=True)

    # 2. Формуємо запит з анотаціями (математика на стороні БД)
    candidates = Publication.objects.filter(
        created_at__gte=time_limit
    ).exclude(
        id__in=list(liked_post_ids)[:1000] # Exploration: не показуємо те, що вже лайкнуто
    ).annotate(
        likes_cnt=Count('likes', distinct=True),
        comments_cnt=Count('comments', distinct=True),
        # Рахуємо кількість спільних тегів прямо в SQL
        matching_tags_count=Count('tags', filter=Q(tags__id__in=tag_ids), distinct=True)
    )

    # 3. Розумне ранжування (SQL Scoring)
    # Формула: (Лайки * 0.2) + (Коменти * 0.3) + (Теги * 0.5)
    # Мінус бал, якщо автор вже знайомий (щоб стимулювати нових авторів)
    candidates = candidates.annotate(
        score=ExpressionWrapper(
            (F('likes_cnt') * 0.2) + 
            (F('comments_cnt') * 0.3) + 
            (F('matching_tags_count') * 0.5) -
            Case(
                When(user_id__in=author_ids, then=1.5),
                default=0.0,
                output_field=IntegerField()
            ),
            output_field=IntegerField()
        )
    ).select_related('user').prefetch_related('tags')

    # Сортуємо за score та свіжістю
    return candidates.order_by('-score', '-created_at')[offset:limit]
    



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

