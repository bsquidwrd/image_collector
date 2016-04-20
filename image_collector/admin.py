from django.contrib import admin

from image_collector.models import Extension, MimeType, Website
from image_collector.models import Credential, ImageUser, Post, Image, Log, Storage


class ImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'title', 'description', 'mime_type',)
    list_display_links = ('image_id',)
    search_fields = ['description', 'image_id', 'title']


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'active',)
    list_display_links = ('title',)
    search_fields = ['title', 'description']


class CredentialAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'notes',)
    list_display_links = ('name',)
    search_fields = ['name', 'website__name', 'notes', 'credential_key']


class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'short_name', 'notes',)
    list_display_links = ('name',)
    search_fields = ['name', 'url', 'short_name', 'notes']


class ImageUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'notes',)
    list_display_links = ('username',)
    search_fields = ['username', 'notes']


class MimeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'extension', 'mime', 'video',)
    list_display_links = ('name',)
    search_fields = ['name', 'extension__name', 'mime']


class ExtensionAdmin(admin.ModelAdmin):
    list_display = ('name', 'extension',)
    list_display_links = ('name',)
    search_fields = ['name', 'extension']


class LogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'result', 'message', 'website', 'user', 'post', 'image',)
    list_display_links = ('timestamp',)
    search_fields = ['timestamp', 'action', 'result', 'message', 'website', 'user', 'post', 'image']


admin.site.register(Extension, ExtensionAdmin)
admin.site.register(MimeType, MimeTypeAdmin)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(Credential, CredentialAdmin)
admin.site.register(ImageUser, ImageUserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Storage)
