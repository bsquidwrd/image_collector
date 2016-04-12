import os
import inspect
from enum import Enum

from jsonfield import JSONField

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import *
from django.utils import timezone
from django.apps import apps

app_name = 'image_collector'


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        # get all members of the class
        members = inspect.getmembers(cls, lambda m: not(inspect.isroutine(m)))
        # filter down to just properties
        props = [m for m in members if not(m[0][:2] == '__')]
        # format into django choice tuple
        choices = tuple([(str(p[1].value), p[0]) for p in props])
        return choices

    @classmethod
    def choices_int(cls):
        # get all members of the class
        members = inspect.getmembers(cls, lambda m: not(inspect.isroutine(m)))
        # filter down to just properties
        props = [m for m in members if not(m[0][:2] == '__')]
        # format into django choice tuple
        choices = tuple([(int(p[1].value), p[0]) for p in props])
        return choices


class LogResult(ChoiceEnum):
    unknown = 0
    success = 1
    fail = 2


class Extension(models.Model):
    name = models.CharField(max_length=255, blank=False)
    extension = models.CharField(max_length=20, blank=False)

    def __str__(self):
        return self.extension


class MimeType(models.Model):
    name = models.CharField(max_length=255, blank=False)
    extension = models.ForeignKey(Extension)
    mime = models.CharField(max_length=255, blank=False)
    video = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Website(models.Model):
    name = models.CharField(max_length=255, blank=False)
    url = models.URLField()
    short_name = models.CharField(max_length=255, blank=False)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Credential(models.Model):
    website = models.ForeignKey(Website)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    access_token = models.CharField(max_length=255, blank=True)
    refresh_token = models.CharField(max_length=255, blank=True)
    authorization_code = models.CharField(max_length=255, blank=True)
    pin_code = models.CharField(max_length=255, blank=True)
    client_id = models.CharField(max_length=255, blank=True)
    # Doing this for easier reference in code and such
    # since there can be multiple credentials for 1 website
    credential_key = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "Credentials for %s %s" % (str(self.website), str(self.credential_key))


class ImageUser(models.Model):
    username = models.CharField(max_length=255, blank=False)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username


class Image(models.Model):
    def __str__(self):
        return self.file.name

    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    file = models.FileField()
    # user = models.ForeignKey(ImageUser, related_name='image_user', null=True)
    image_id = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=4000, blank=True)
    description = models.CharField(max_length=4000, blank=True)
    mime_type = models.ForeignKey(MimeType, null=True, blank=True)


class Post(models.Model):
    website = models.ForeignKey(Website, related_name='post_website')
    user = models.ForeignKey(ImageUser, related_name='post_user')
    timestamp = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=4000, blank=False, null=True)
    url_name = models.CharField(max_length=255, blank=False, null=True)
    description = models.CharField(max_length=4000, blank=True, null=True)
    permalink = models.URLField()
    nsfw = models.BooleanField(default=False)
    images = models.ManyToManyField(Image)
    active = models.BooleanField(default=True)
    etag = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.title


class Log(models.Model):
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    action = models.CharField(max_length=255, blank=False)
    result = models.IntegerField(choices=LogResult.choices_int())
    message = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    user = models.CharField(max_length=255, blank=True)
    post = models.CharField(max_length=255, blank=True)
    image = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "[%s] - %s\t%s" % (self.timestamp, self.action, self.message)


class Storage(models.Model):
    defaultJson = {
        "hello": "Hi there!",
        "information": "This is here for you to use as your storage of information if need be",
        "help": "Put some valid JSON in here and you'll do fine!"
    }
    credential = models.ForeignKey(Credential)
    jsonData = JSONField(default=defaultJson)

    def __str__(self):
        return "Storage for %s" % str(self.credential)

##
# Catch signals and do things with them
##


@receiver(post_save)
def populate_post_url_name(sender, instance, *args, **kwargs):
    instance_type = type(instance)
    mymodels = apps.get_app_config(app_name).models
    models = [mymodels[m] for m in mymodels]
    if instance_type not in models:
        return
    if "log" in instance.__class__.__name__.lower():
        return
    # post_save things for when a Post object is saved
    if isinstance(instance, Post):
        if not instance.url_name:
            url_name = instance.title
            url_name = url_name.lower().replace(' ', '-')
            instance.url_name = url_name
            instance.save()
            log_action(instance, 'generate post url name', LogResult.success.value, 'post url name generated "%s"' % url_name, post=str(instance))

    # Create a storage instance for each Credential
    # that's created/modified and doesn't already have one
    if isinstance(instance, Credential):
        possible_storages = Storage.objects.filter(credential=instance)
        if len(possible_storages) == 0:
            try:
                Storage.objects.create(credential=instance)
                log_action(instance, 'create storage object', LogResult.success.value, 'storage object generated for credential %s' % str(instance.credential_key))
            except Exception as e:
                log_action(instance, 'create storage object', LogResult.fail.value, 'failed to generate storage for credential %s. %s' % (str(instance.credential_key), str(e)))
        elif len(possible_storages) == 1:
            if possible_storages[0].jsonData == "":
                possible_storages[0].jsonData = Storage.defaultJson
                possible_storages[0].save()



@receiver(pre_save)
def log_changed_models(sender, instance, *args, **kwargs):
    instance_type = type(instance)
    mymodels = apps.get_app_config(app_name).models
    models = [mymodels[m] for m in mymodels]
    if instance_type not in models:
        return
    if "log" in instance.__class__.__name__.lower():
        return
    try:
        instance_type.objects.get(pk=instance.pk)
    except:
        return
    new_model = instance
    old_model = instance_type.objects.get(pk=instance.pk)
    attributes = [item.name for item in instance_type._meta.get_fields()]
    for attribute in attributes:
        try:
            old_value = getattr(old_model, attribute)
            new_value = getattr(new_model, attribute)
        except:
            continue
        if old_value != new_value:
            value_updated_msg = '%s was updated from "%s" to "%s"' % (attribute, old_value, new_value)
            log_item = log_action(instance, 'attribute updated', LogResult.unknown.value, value_updated_msg)
            setattr(log_item, instance.__class__.__name__, instance)
            if "image" in attributes:
                try:
                    log_item.image = str(getattr(old_model, "iamge", ""))
                except:
                    pass
            if "post" in attributes:
                try:
                    log_item.post = str(getattr(old_model, "post", ""))
                except:
                    pass
            if "website" in attributes:
                try:
                    log_item.website = str(getattr(old_model, "website", ""))
                except:
                    pass
            if "user" in attributes:
                try:
                    log_item.user = str(getattr(old_model, "user", ""))
                except:
                    pass
            log_item.save()


@receiver(post_save)
def populate_image_mime_type(sender, instance, *args, **kwargs):
    instance_type = type(instance)
    mymodels = apps.get_app_config(app_name).models
    models = [mymodels[m] for m in mymodels]
    if instance_type not in models:
        return
    if "log" in instance.__class__.__name__.lower():
        return
    if not isinstance(instance, Image):
        return
    if instance.mime_type:
        return
    try:
        image_info = instance.file.name.split('.')
        mime_type = MimeType.objects.get(extension__extension=image_info[-1])
        if instance.mime_type != mime_type:
            instance.mime_type = mime_type
            instance.save()
            log_action(instance, 'associate mime type', LogResult.success.value,
                       'associated mimetype %s' % str(instance.mime_type),
                       image=instance
                       )
    except Exception as e:
        log_action(instance, 'associate mime type', LogResult.fail.value, str(e),
                   image=instance
                   )


@receiver(post_save)
def populate_image_id(sender, instance, *args, **kwargs):
    # post_save things for when an Image object is saved
    instance_type = type(instance)
    mymodels = apps.get_app_config(app_name).models
    models = [mymodels[m] for m in mymodels]
    if instance_type not in models:
        return
    if "log" in instance.__class__.__name__.lower():
        return
    if isinstance(instance, Image):
        if not instance.image_id:
            from image_collector.api.generators import generate_image_id
            try:
                instance.image_id = generate_image_id()
                initial_path = instance.file.path
                new_image_name = instance.image_id + '.' + instance.mime_type.extension.extension
                instance.file.name = new_image_name
                new_path = os.path.join(settings.MEDIA_ROOT, new_image_name)
                os.rename(initial_path, new_path)
                instance.save()
                log_action(instance, 'generate image id', LogResult.success.value, 'image_id generated',
                           website=str(instance.website),
                           image=instance
                           )
            except Exception as e:
                log_action(instance, 'generate image id', LogResult.fail.value, str(e),
                           website=str(instance.website),
                           image=instance
                           )
    elif isinstance(instance, Credential):
        if not instance.credential_key:
            from image_collector.api.generators import generate_credential_key
            try:
                instance.credential_key = generate_credential_key()
                instance.save()
                log_action(instance, 'generate credential id for credential %s' % instance, LogResult.success.value, 'credential_key generated',
                           website=str(instance.website),
                           )
            except Exception as e:
                log_action(instance, 'generate credential id for credential %s' % instance, LogResult.fail.value, str(e),
                           website=str(instance.website)
                           )


@receiver(post_delete)
def delete_image_after_model_delete(sender, instance, *args, **kwargs):
    # This is to keep the files all nice and clean too so that
    # files are removed when removed from the database as well
    instance_type = type(instance)
    mymodels = apps.get_app_config(app_name).models
    models = [mymodels[m] for m in mymodels]
    if instance_type not in models:
        return
    if "log" in instance.__class__.__name__.lower():
        return
    if isinstance(instance, Image):
        try:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
                if not os.path.isfile(instance.file.path):
                    log_action(instance, 'delete image from disk', LogResult.success.value, '%s file no longer exists on disk' % str(instance.file),
                               image=instance
                               )
                else:
                    log_action(instance, 'delete image from disk', LogResult.fail.value, 'file still exists on disk',
                               image=instance
                               )
        except Exception as e:
            log_action(instance, 'delete image from disk', LogResult.fail.value, str(e),
                       image=instance
                       )
            print(e)


def log_action(instance, action, result, message='', website='', user='', post='', image=''):
    instance_type = type(instance)
    mymodels = apps.get_app_config(app_name).models
    models = [mymodels[m] for m in mymodels]
    if instance_type not in models:
        return
    if "log" in instance.__class__.__name__.lower():
        return

    return Log.objects.create(
        action=str(action),
        result=str(result),
        message=str(message),
        website=str(website),
        user=str(user),
        post=str(post),
        image=str(image),
    )
