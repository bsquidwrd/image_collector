# Project: image_collector
# File Name: methods
# Created by: bsquidwrd
# Created on: 4/9/2016

from image_collector.models import Image, Post, ImageUser, Website


def post_exists(permalink):
    if len(Post.objects.filter(permalink=permalink)) >= 1:
        return True
    else:
        return False


def image_exists(image_id):
    if len(Image.objects.filter(image_id=image_id)) >= 1:
        return True
    else:
        return False


def user_exists(username):
    if len(ImageUser.objects.filter(username=username)) >= 1:
        return True
    else:
        return False


def website_exists(short_name):
    if len(Website.objects.filter(short_name=short_name)) >= 1:
        return True
    else:
        return False
