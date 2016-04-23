# Project: image_collector
# File Name: classes
# Created by: bsquidwrd
# Created on: 4/9/2016

import os
import requests
from django.conf import settings
from django.core.files import File
from django.db.models.query import QuerySet
from jsonfield import JSONField

from image_collector.api.errors import *
from image_collector.models import Post, Image, ImageUser, Website, Credential, Storage


class ImageInstance:
    def __init__(self, **kwargs):
        if 'image' in kwargs.keys():
            if isinstance(kwargs.get('image'), Image):
                temp_image = kwargs.get('image')
            else:
                try:
                    temp_image = Image.objects.get(pk=kwargs.get('image'))
                except:
                    raise InvalidImage
            try:
                self.image = temp_image
                self.url = getattr(temp_image, 'url', '')
                self.title = kwargs.get('title', '')
                self.description = getattr(temp_image, 'description', '')
            except:
                raise InvalidImage
        else:
            self.image = None
            self.url = kwargs.get('url', '')
            self.title = kwargs.get('title', '')
            self.description = kwargs.get('description', '')

        if not isinstance(self.url, str):
            raise InvalidURL
        if not isinstance(self.title, str):
            raise InvalidTitle
        if not isinstance(self.description, str):
            raise InvalidDescription

    def process(self):
        if isinstance(self.image, Image):
            return self.image
        download_location = os.path.join(settings.BASE_DIR, 'tmp')
        if not os.path.isdir(download_location):
            os.makedirs(download_location)
        local_filename = os.path.join(download_location, self.url.split('/')[-1])
        r = requests.get(self.url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

        local_file = open(local_filename, 'rb')
        django_file = File(local_file)
        image = Image.objects.create(
            file=django_file,
            title=self.title,
            description=self.description
        )
        local_file.close()
        if os.path.isfile(local_filename):
            os.remove(local_filename)
        self.image = image
        return image

    def get_image(self):
        if isinstance(self.image, Image):
            return self.image
        else:
            return self.process()


class PostInstance:
    def __init__(self, **kwargs):
        if 'post' in kwargs.keys():
            if isinstance(kwargs.get('post'), Post):
                temp_post = kwargs.get('post')
            else:
                try:
                    temp_post = Post.objects.get(pk=kwargs.get('post'))
                except:
                    raise InvalidPost
            try:
                self.website = getattr(temp_post, 'website')
                self.post = temp_post
                self.title = getattr(temp_post, 'title', None)
                self.images = getattr(temp_post, 'images').all()
                self.user = getattr(temp_post, 'user', None)
                self.permalink = getattr(temp_post, 'permalink', None)
                self.description = getattr(temp_post, 'description', '')
                self.nsfw = getattr(temp_post, 'nsfw', False)
                self.etag = getattr(temp_post, 'etag', '')
                if isinstance(self.images, QuerySet):
                    self.images = [image for image in self.images]
            except:
                raise InvalidPost
        else:
            self.website = kwargs.get('website', None)
            self.post = None
            self.title = kwargs.get('title', None)
            self.images = kwargs.get('images', [])
            self.user = kwargs.get('user', None)
            self.permalink = kwargs.get('permalink', '')
            self.description = kwargs.get('description', '')
            self.nsfw = kwargs.get('nsfw', False)
            self.etag = kwargs.get('etag', '')

        if not isinstance(self.title, str):
            raise InvalidPost
        if not isinstance(self.images, list):
            raise InvalidImage
        if not isinstance(self.user, ImageUser):
            raise InvalidUser
        if not isinstance(self.description, str):
            raise InvalidDescription
        if not isinstance(self.etag, str):
            raise InvalidEtag

    def process(self):
        if self.post is None:
            possible_post = Post.objects.filter(permalink=self.permalink)
            if len(possible_post) == 1:
                self.post = possible_post[0]
            else:
                self.post = Post.objects.create(
                    website=self.website,
                    user=self.user,
                    title=self.title,
                    description=self.description,
                    permalink=self.permalink,
                    nsfw=self.nsfw,
                    etag=self.etag,
                )

        processed_images = []
        for image in self.images:
            if isinstance(image, Image):
                self.post.images.add(image)
                processed_images.append(image)
            else:
                raise InvalidImage
        self.images = processed_images
        return self.post

    def add_image(self, image):
        if isinstance(image, Image):
            self.post.images.add(image)
            self.images.append(image)
            return True
        else:
            raise InvalidImage

    def add_images(self, images):
        if isinstance(images, list):
            self.post.images.add(images)
            self.images.extend(images)
            return True
        else:
            raise InvalidImage

    def get_post(self):
        if isinstance(self.post, Post):
            return self.post
        else:
            return self.process()

    def get_images(self):
        if isinstance(self.images, list):
            return self.images
        elif isinstance(self.post, Post):
            self.images = self.post.images.all()
            return self.post.images.all()
        else:
            return self.process()

    def get_etag(self):
        if isinstance(self.etag, str):
            return self.etag
        else:
            return None

    def set_etag(self, etag):
        self.post.etag = etag
        self.post.save()
        self.etag = self.post.etag
        return self.etag


class UserInstance:
    def __init__(self, **kwargs):
        if 'user' in kwargs.keys():
            if isinstance(kwargs.get('user'), ImageUser):
                temp_user = kwargs.get('user')
            else:
                try:
                    temp_user = ImageUser.objects.get(pk=kwargs.get('user'))
                except:
                    raise InvalidUser
            try:
                self.user = temp_user
                self.username = getattr(temp_user, 'username', None)
            except:
                raise InvalidUser
        else:
            self.user = None
            self.username = kwargs.get('username', None)
            self.notes = kwargs.get('notes', '')

        if not isinstance(self.username, str):
            raise InvalidUser

    def process(self):
        if isinstance(self.user, ImageUser):
            return self.user
        possible_user = ImageUser.objects.filter(username=self.username)
        if len(possible_user) == 1:
            return possible_user[0]
        elif len(possible_user) > 1:
            raise InvalidUser
        else:
            self.user = ImageUser.objects.create(
                username=self.username,
                notes=self.notes
            )
            return self.user


class WebsiteInstance:
    def __init__(self, **kwargs):
        if 'website' in kwargs.keys():
            if isinstance(kwargs.get('website'), Website):
                temp_website = kwargs.get('website')
            else:
                try:
                    temp_website = Website.objects.get(pk=kwargs.get('website'))
                except:
                    raise InvalidWebsite
            try:
                self.website = temp_website
                self.name = getattr(temp_website, 'name', None)
                self.url = getattr(temp_website, 'url', None)
                self.short_name = getattr(temp_website, 'short_name', None)
                self.notes = getattr(temp_website, 'notes', '')
            except:
                raise InvalidWebsite
        else:
            self.website = None
            self.name = kwargs.get('name', None)
            self.url = kwargs.get('url', None)
            self.short_name = kwargs.get('short_name', None)
            self.notes = kwargs.get('notes', '')

        if not isinstance(self.name, str):
            raise InvalidWebsite
        if not isinstance(self.url, str):
            raise InvalidWebsite
        if not isinstance(self.short_name, str):
            raise InvalidWebsite

    def process(self):
        if isinstance(self.website, Website):
            return self.website
        possible_website = Website.objects.filter(short_name=self.short_name)
        if len(possible_website) == 1:
            self.website = possible_website[0]
            return self.website
        elif len(possible_website) > 1:
            possible_website = Website.objects.filter(url=self.url)
            if len(possible_website) == 1:
                self.website = possible_website[0]
                return self.website
            elif len(possible_website) > 1:
                raise InvalidWebsite
            else:
                pass

        self.website = Website.objects.create(
            name=self.name,
            url=self.url,
            short_name=self.short_name,
            notes=self.notes
        )
        return self.website

    def get_website(self):
        if not isinstance(self.website, Website):
            self.process()
        return self.website


class CredentialInstance:
    def __init__(self, **kwargs):
        if 'credential_key' in kwargs.keys():
            try:
                self.credential = Credential.objects.get(credential_key=kwargs.get('credential_key'))
                self.storage = None
            except:
                raise InvalidCredential
        else:
            raise InvalidCredential

    def get_credential(self):
        if isinstance(self.credential, Credential):
            return self.credential
        else:
            raise InvalidCredential

    def get_storage(self):
        if isinstance(self.storage, StorageInstance):
            return self.storage
        else:
            self.storage = StorageInstance(credential=self)
            return self.storage


class StorageInstance:
    def __init__(self, credential):
        if credential is None or not isinstance(credential, CredentialInstance):
            raise InvalidCredential
        self.credential = credential
        self.storage = None
        self.data = None

    def get_data(self):
        if isinstance(self.storage, Storage):
            self.data = self.storage.jsonData
            return self.data
        else:
            possible_storage = Storage.objects.filter(credential=self.credential.get_credential())
            if len(possible_storage) == 1:
                self.storage = possible_storage[0]
                self.data = self.storage.jsonData
            elif len(possible_storage) < 1:
                raise InvalidStorage
            elif len(possible_storage) > 1:
                self.storage = possible_storage[0]
                self.data = self.storage.jsonData
            else:
                self.storage = Storage.objects.create(credential=self.credential.get_credential())
                self.data = self.storage.jsonData
            return self.data

    def update_data(self, new_data):
        if not isinstance(self.storage, Storage):
            self.get_data()
        self.storage.jsonData = new_data
        self.storage.save()
        self.data = self.storage.jsonData
        return self.data








