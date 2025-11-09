from django.db import models
import uuid
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from pytils.translit import slugify as pytils_slugify


class User(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=False)



    


class Publication(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="publications")
    title = models.CharField(max_length=15)
    text = models.CharField(max_length=100)
    tags = models.ManyToManyField("Tag", related_name="publications")
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)


    class Meta:
        ordering = ["-created_at"]



    
    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_title = slugify(self.title)
            self.slug = f"{pytils_slugify(self.title)}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.user}, {self.text}, {self.created_at}, {self.tags}'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('user', 'publication')

    def __str__(self):
        return f'{self.user.username}, {self.created_at}, {self.publication}'
    



class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.user}: {self.text}"
    



class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    usage_count = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.name



