# Project: image_collector
# File Name: errors
# Created by: bsquidwrd
# Created on: 4/9/2016


class PostDoesNotExist(Exception):
    """Raised when a post does not exist"""
    pass


class ImageDoesNotExist(Exception):
    """Raised when an image does not exist"""
    pass


class InvalidWebsite(Exception):
    """Raised when a website is invalid"""
    pass


class InvalidURL(Exception):
    """Raised when a URL is invalid"""
    pass


class InvalidPost(Exception):
    """Raised when a Post is invalid"""
    pass


class InvalidImage(Exception):
    """Raised when an Image is invalid"""
    pass


class InvalidUser(Exception):
    """Raised when a User is invalid"""
    pass


class InvalidTitle(Exception):
    """Raised when a title is invalid"""
    pass


class InvalidDescription(Exception):
    """Raised when a Description is invalid"""
    pass


class InvalidCredential(Exception):
    """Raised when a Credential is invalid"""
    pass


class InvalidStorage(Exception):
    """Raised when a Storage is invalid"""
    pass


class InvalidEtag(Exception):
    """Raised when an Etag is invalid"""
    pass


