from django.contrib import admin

from image_collector.models import Extension, MimeType, Website
from image_collector.models import Credential, ImageUser, Post, Image, Log, Storage


class ImageAdmin(admin.ModelAdmin):
    def display_name(self, instance):
        return str(instance)
    display_name.short_description = 'Display Name'
    list_display = ('display_name', 'image_id', 'title', 'description', 'mime_type',)
    list_display_links = ('display_name',)
    search_fields = ['description', 'image_id', 'title']


class PostAdmin(admin.ModelAdmin):
    def display_name(self, instance):
        return str(instance)
    display_name.short_description = 'Display Name'
    readonly_fields = ('display_name',)
    list_display = ('display_name', 'title', 'user', 'active',)
    list_display_links = ('display_name',)
    search_fields = ['title', 'description']


class CredentialAdmin(admin.ModelAdmin):
    def display_name(self, instance):
        return str(instance)
    display_name.short_description = 'Display Name'
    readonly_fields = ('display_name',)
    list_display = ('display_name', 'notes',)
    list_display_links = ('display_name',)
    search_fields = ['name', 'website__name', 'notes', 'credential_key']


class WebsiteAdmin(admin.ModelAdmin):
    def display_name(self, instance):
        return str(instance)
    display_name.short_description = 'Display Name'
    readonly_fields = ('display_name',)
    list_display = ('display_name', 'name', 'url', 'short_name', 'notes',)
    list_display_links = ('display_name',)
    search_fields = ['name', 'url', 'short_name', 'notes']


class ImageUserAdmin(admin.ModelAdmin):
    def display_name(self, instance):
        return str(instance)
    display_name.short_description = 'Display Name'
    readonly_fields = ('display_name',)
    list_display = ('display_name', 'username', 'notes',)
    list_display_links = ('display_name',)
    search_fields = ['username', 'notes']


class MimeTypeAdmin(admin.ModelAdmin):
    def display_name(self, instance):
        return str(instance)
    display_name.short_description = 'Display Name'
    readonly_fields = ('display_name',)
    list_display = ('display_name', 'name', 'extension', 'mime', 'video',)
    list_display_links = ('display_name',)
    search_fields = ['name', 'extension__name', 'mime']


class ExtensionAdmin(admin.ModelAdmin):
    def display_name(self, instance):
        return str(instance)
    display_name.short_description = 'Display Name'
    readonly_fields = ('display_name',)
    list_display = ('display_name', 'name', 'extension',)
    list_display_links = ('display_name',)
    search_fields = ['name', 'extension']


class LogAdmin(admin.ModelAdmin):
    def display_name(self, instance):
        return str(instance)
    display_name.short_description = 'Display Name'
    readonly_fields = ('display_name',)
    list_display = ('display_name', 'timestamp', 'action', 'result', 'message', 'website', 'user', 'post', 'image',)
    list_display_links = ('display_name',)
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
