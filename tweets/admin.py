from django.contrib import admin
from .models import Tweet, TweetLike

admin.site.site_header = 'For cats only'

class TweetLikeAdmin(admin.TabularInline):
    model = TweetLike

class TweetAdmin(admin.ModelAdmin):
    inlines = [TweetLikeAdmin]
    search_fields = ('user__username', 'user__email')
    list_display = ('id', 'user', 'content', 'image')
    list_filter = ('user',)
    class Meta:
        model = Tweet

admin.site.register(Tweet, TweetAdmin)
admin.site.register(TweetLike)