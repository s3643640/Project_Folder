from django.contrib import admin
from .models import Tweet, TweetLike

class TweetLikeAdmin(admin.TabularInline):
        model=TweetLike

class TweetAdmin(admin.ModelAdmin):
    inlines=[TweetLikeAdmin]
    search_fields=['user__username', 'user__email', 'content']
    list_display=['content', 'user']

    class Meta:
        model=Tweet
# Register your models here.
admin.site.register(Tweet, TweetAdmin)
