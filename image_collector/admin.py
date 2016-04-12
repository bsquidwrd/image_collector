from django.contrib import admin

from image_collector.models import Extension, MimeType, Website
from image_collector.models import Credential, ImageUser, Post, Image, Log, Storage


class ImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'title', 'description', 'mime_type',)
    list_display_links = ('image_id', 'title', 'description',)
    search_fields = ['description', 'image_id', 'title']
    fieldsets = [
        (None, {'fields': ['file', 'image_id', 'title', 'description', 'mime_type', ]})
    ]

admin.site.register(Extension)
admin.site.register(MimeType)
admin.site.register(Website)
admin.site.register(Credential)
admin.site.register(ImageUser)
admin.site.register(Post)
admin.site.register(Image, ImageAdmin)
admin.site.register(Log)
admin.site.register(Storage)
