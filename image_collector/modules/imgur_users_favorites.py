# Project: image_collector
# File Name: imgur_users_submitted
# Created by: bsquidwrd
# Created on: 4/6/2016

import requests
import json
import time
import math
import re
import datetime

from django.utils import timezone

from image_collector.api.classes import WebsiteInstance, UserInstance
from image_collector.api.classes import PostInstance, ImageInstance
from image_collector.api.classes import CredentialInstance
from image_collector.api.methods import post_exists


credential_key = 'AdP5NrasPDIkrPixyVuUjQlvC'
credential_instance = CredentialInstance(credential_key=credential_key)
credentials = credential_instance.get_credential()
storage = credential_instance.get_storage()
if isinstance(storage.get_data(), dict):
    storageData = storage.get_data()
else:
    storageData = json.dumps(storage.get_data())
    if '""' == storageData:
        print("Blank storage!")
        storageData = {"website": str(credentials.website)}
        storage.update_data(storageData)

base_api_url = 'https://api.imgur.com/3'
client_id = credentials.client_id

global_parameters = "_format=json&"

# 401 - Authentication required
# 403 - Permission denied
# 429 - Rate limit hit for application or users ip
quit_codes = {
    401: "Authentication is required for this action.",
    403: "Permission denied for this action.",
    429: "This application or the IP you're using has hit the daily rate limit."
}
request_headers = {
    'Authorization': ('Client-ID %s' % client_id)
}
hashes = {}
users_to_download = []

linkRegex = re.compile(r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:\([\w\d]+\)|([^%s\s]|/)))')


class RateLimitHit(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self, *args, **kwargs)

    def __str__(self):
        return "Rate Limit Hit!"


def download_user_favorites(username, bad_tries=0):
    error_tries = bad_tries

    # Get the gallery profile of the user to know how many favorites there should be
    gallery_url = '%s/account/%s/gallery_profile' % (base_api_url, username)
    gallery_profile = requests.get(url=gallery_url, headers=request_headers)
    gallery_info = json.loads(gallery_profile.text)['data']

    if gallery_profile.ok and gallery_profile.status_code not in quit_codes.keys():
        # Get total gallery favorites and divide by 60, which for now
        # seems to be the amount sent by the favorites API endpoint
        total_posts = int(float(gallery_info['total_gallery_favorites']))
        total_pages = math.ceil(total_posts / 60)
        for page_num in range(0, total_pages + 1):

            favorites_url = '%s/account/%s/gallery_favorites/%s/?%s' % (base_api_url, username, page_num, global_parameters)

            user_response = requests.get(url=favorites_url, headers=request_headers)
            if user_response.ok:
                user_json = json.loads(user_response.text)

                for item in user_json['data']:
                    post_username = item.get('account_url', username)
                    if post_username is None:
                        post_username = username
                    user = UserInstance(
                        username=post_username
                    ).process()

                    album_id = None
                    if post_exists(item.get('link')):
                        continue
                    post_description = item.get('description')
                    if post_description is None:
                        post_description = ''
                    post_nsfw = item.get('nsfw', False)
                    if post_nsfw is None:
                        post_nsfw = False

                    post = PostInstance(
                        website=credentials.website,
                        title=item.get('title', ''),
                        description=linkRegex.sub(r'<a target="_blank" href="\1">\1</a>', post_description).replace('\n', ' <br/> '),
                        user=user,
                        permalink=item.get('link'),
                        nsfw=post_nsfw,
                        timestamp=timezone.make_aware(datetime.datetime.fromtimestamp(item.get('datetime'))),
                    )
                    try:
                        post.process()
                    except:
                        continue

                    # If the favorite is an album, get the album and loop through it
                    # This will also save the album in a folder named by the album id
                    if item['is_album']:
                        album_url = '%s/album/%s/images?%s' % (base_api_url, item['id'], global_parameters)
                        album_id = item['id']
                        album_response = requests.get(url=album_url, headers=request_headers)
                        album_etag = album_response.headers['ETag']
                        if album_response.ok:
                            if album_etag == post.get_etag():
                                continue
                            album_json = json.loads(album_response.text)
                            for image in album_json['data']:
                                process_image(image=image, username=username, post=post)
                            post.set_etag(album_etag)
                        else:
                            pass
                    else:
                        try:
                            image_url = "%s/gallery/image/%s?%s" % (base_api_url, item['id'], global_parameters)
                            image_response = requests.get(url=image_url, headers=request_headers)
                            image_etag = image_response.headers['ETag']
                            if image_response.ok:
                                if image_etag == post.get_etag():
                                    continue
                            process_image(image=item, username=username, post=post)
                            post.set_etag(image_etag)
                        except:
                            continue
                    if len(post.get_post().images.all()) == 0:
                        post.get_post().delete()
            else:
                # Error handling since the response wasn't ok
                # This also checks if the app should quit based on quit_codes
                # If the status_code is not in quit_codes it tries again in 1 minute
                # just in case the servers are having issues
                response_json = json.loads(user_response.text)

                status_code = user_response.status_code
                if status_code in quit_codes.keys():
                    status_message = quit_codes[status_code]
                    if status_code == 429:
                        raise RateLimitHit(status_message)
                    else:
                        raise Exception
                else:
                    print(response_json['data']['error'])

                error_tries += 1
                if error_tries < 5:
                    # After waiting 1 minute, try to download the user favorites again
                    time.sleep(60)
                    download_user_favorites(username, error_tries)
                else:
                    # If I've tried 5 times, quit and let the user figure out the issue
                    pass
        return True

    else:
        status_code = gallery_profile.status_code
        if status_code in quit_codes.keys():
            status_message = quit_codes[status_code]
            if status_code == 429:
                raise RateLimitHit(status_message)
            else:
                print(status_message)
                return False
        else:
            return False


def process_image(image, username, post=None):
    image_type = image['type']

    # Image locations are named differently if it's a GIF
    # So far it seems all GIF's have a webm attribute, so check for that
    if image_type == 'image/gif':
        try:
            image_url = image['webm']
        except:
            try:
                image_url = image['gifv']
            except:
                try:
                    image_url = image['link']
                except:
                    return False
    else:
        image_url = image['link']

    try:
        image_title = image.get('title', '')
        if image_title is None:
            image_title = ''
        image_description = image.get('description', '')
        if image_description is None:
            image_description = ''
        processed_image = ImageInstance(
            url=image_url,
            title=image_title,
            description=linkRegex.sub(r'<a target="_blank" href="\1">\1</a>', image_description).replace('\n', '<br/>'),
            timestamp=timezone.make_aware(datetime.datetime.fromtimestamp(image.get('datetime'))),
        ).process()
        post.add_image(processed_image)
        print("Processed favorite for %s image %s for post %s" % (username, processed_image, post.get_post()))
    except:
        pass


def handle_command():
    if not isinstance(storageData, dict):
        print("Storage Data is not a dictionary")
        return
    website = WebsiteInstance(
        name='Imgur',
        url='http://imgur.com',
        short_name='imgur'
    ).get_website()
    if website != credentials.website:
        print("Website does not match Credential")
        return
    users = storageData.get('users', ['bsquidwrd'])
    for user in users:
        try:
            download_user_favorites(user)
        except RateLimitHit:
            print("RateLimit Reached")
            break
        except Exception as e:
            print("Got error for %s: %s" % (user, e))
            continue

