# Project: image_collector
# File Name: generators
# Created by: bsquidwrd
# Created on: 4/5/2016

import random
import string


def random_key(length=10):
    key = ''
    for i in range(length):
        key += random.choice(string.ascii_letters + string.digits)
    return key


def generate_image_id():
    from image_collector.models import Image
    try:
        image_id = random_key()
        if len(Image.objects.filter(image_id=image_id)) >= 1:
            image_id = generate_image_id()
        return image_id
    except:
        return False


def generate_credential_key():
    from image_collector.models import Credential
    try:
        credential_key = random_key(25)
        if len(Credential.objects.filter(credential_key=credential_key)) >= 1:
            credential_key = generate_credential_key()
        return credential_key
    except:
        return False

