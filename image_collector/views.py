import os
import mimetypes
import random
import operator
import zipfile
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


from image_collector.models import Post, Image, ImageUser, Website, MimeType, Extension

items_per_page = '48'


def reduce(func, items):
    result = items.pop()
    for item in items:
        result = func(result, item)
    return result


def index_view(request):
    template = 'image_collector/base_layout.html'
    breadcrumbs = []
    search_key = None
    page_title = "Home"

    post_list = Post.objects.filter(active=True)
    try:
        search_key = request.GET.get('search')
        search_terms = search_key.split()
        qset = reduce(operator.__or__, [
            Q(title__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(user__username__icontains=search_term) |
            Q(website__name__icontains=search_term)
            for search_term in search_terms])
        post_list = post_list.filter(qset)
    except:
        pass
    sort_key = request.GET.get('sort', 'desc')
    if sort_key == 'asc':
        sort_by = '-timestamp'
    else:
        sort_by = 'timestamp'
    post_list = post_list.order_by(sort_by)
    paginator = Paginator(post_list, items_per_page)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    breadcrumbs.append({
        'name': 'Home',
        'link': reverse('ic:index'),
        'active': True,
        'home': True,
    })

    if len(posts) == 0:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': 'No posts found',
            'search': (search_key if search_key else False),
            'page_title': page_title,
            'home': True,
        })

    context = {
        'posts': posts,
        'breadcrumbs': breadcrumbs,
        'search': (search_key if search_key else False),
        'page_title': page_title,
        'home': True,
    }
    return render(request, template, context=context)


def sites_view(request):
    template = 'image_collector/list_layout.html'
    breadcrumbs = []
    search_key = None
    page_title = "Websites"
    breadcrumbs.append({
        'name': 'Home',
        'link': reverse('ic:index'),
        'active': False,
    })
    breadcrumbs.append({
        'name': 'Websites',
        'active': True,
    })
    try:
        site_list = Website.objects.all()
        try:
            search_key = request.GET.get('search')
            search_terms = search_key.split()
            qset = reduce(operator.__or__, [
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(user__username__icontains=search_term)
                for search_term in search_terms])
            searched_posts = Post.objects.filter(active=True).filter(qset)
            site_list = []
            for post in searched_posts:
                if post.website not in site_list:
                    site_list.append(post.website)
        except:
            searched_posts = Post.objects.filter(active=True)
        paginator = Paginator(site_list, items_per_page)
        page = request.GET.get('page')
        try:
            sites = paginator.page(page)
        except PageNotAnInteger:
            sites = paginator.page(1)
        except EmptyPage:
            sites = paginator.page(paginator.num_pages)

        if len(sites) < 1:
            return render(request, template, context={
                'breadcumbs': breadcrumbs,
                'error': True,
                'error_msg': 'No websites found',
                'search': (search_key if search_key else False),
                'page_title': page_title,
                'website': True,
            })

        objects = []
        for site in sites:
            site_posts = searched_posts.filter(website=site)
            site_link = reverse('ic:site_view', args=[site.short_name])
            if search_key:
                site_posts = searched_posts.filter(website=site)
                site_link = "%s?search=%s" % (site_link, search_key)
            if len(site_posts) == 0:
                continue
            objects.append({
                'name': site.name,
                'link': site_link,
                'notes': site.notes,
                'count': len(site_posts),
            })

        context = {
            'objects': objects,
            'breadcrumbs': breadcrumbs,
            'sites': sites,
            'search': (search_key if search_key else False),
            'page_title': page_title,
            'website': True,
        }
        return render(request, template, context=context)
    except Exception as e:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': str(e),
            'search': (search_key if search_key else False),
            'page_title': page_title,
            'website': True,
        })


def site_view(request, site):
    template = 'image_collector/base_layout.html'
    breadcrumbs = []
    search_key = None
    page_title = "Site not found"
    breadcrumbs.append({
        'name': 'Home',
        'link': reverse('ic:index'),
        'active': False,
    })
    breadcrumbs.append({
        'name': 'Websites',
        'link': reverse('ic:sites_view'),
        'active': False,
    })
    try:
        requested_website = Website.objects.get(short_name=site)
        page_title = str(requested_website.name)
    except Exception as e:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': str(e),
            'page_title': page_title,
            'website': True,
        })

    breadcrumbs.append({
        'name': requested_website.name,
        'active': True,
    })

    post_list = Post.objects.filter(website=requested_website, active=True)
    try:
        search_key = request.GET.get('search')
        search_terms = search_key.split()
        qset = reduce(operator.__or__, [
            Q(title__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(user__username__icontains=search_term)
            for search_term in search_terms])
        post_list = post_list.filter(qset)
    except:
        pass
    paginator = Paginator(post_list, items_per_page)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if len(posts) == 0:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': 'No posts found for requested site',
            'search': (search_key if search_key else False),
            'page_title': page_title,
            'website': True,
        })
    context = {
        'posts': posts,
        'site': requested_website,
        'breadcrumbs': breadcrumbs,
        'search': (search_key if search_key else False),
        'page_title': page_title,
        'website': True,
    }
    return render(request, template, context=context)


def post_view(request, post_id):
    template = 'image_collector/post.html'
    index_template = 'image_collector/base_layout.html'
    breadcrumbs = []
    page_title = "Post not found"

    try:
        post = Post.objects.get(pk=post_id)
        page_title = str(post.title)
    except Exception as e:
        return render(request, index_template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'page_title': page_title,
            'error_msg': str(e),
        })

    breadcrumbs.append({
        'name': 'Home',
        'link': reverse('ic:index'),
        'active': False,
    })

    breadcrumbs.append({
        'name': 'Users',
        'link': reverse('ic:users_view'),
        'active': False,
    })
    breadcrumbs.append({
        'name': post.user.username,
        'link': reverse('ic:user_view', args=[post.user]),
        'active': False,
    })
    breadcrumbs.append({
        'name': post.title,
        'active': True,
    })

    context = {
        'post': post,
        'breadcrumbs': breadcrumbs,
        'page_title': page_title,
    }
    return render(request, template, context=context)


def users_view(request):
    template = 'image_collector/list_layout.html'
    breadcrumbs = []
    search_key = None
    page_title = "Users"
    breadcrumbs.append({
        'name': 'Home',
        'link': reverse('ic:index'),
        'active': False,
    })
    breadcrumbs.append({
        'name': 'Users',
        'active': True,
    })
    try:
        user_list = ImageUser.objects.all()
        try:
            search_key = request.GET.get('search')
            search_terms = search_key.split()
            qset = reduce(operator.__or__, [
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(user__username__icontains=search_term) |
                Q(website__name__icontains=search_term)
                for search_term in search_terms])
            searched_posts = Post.objects.filter(active=True).filter(qset)
            user_list = []
            for post in searched_posts:
                if post.user not in user_list:
                    user_list.append(post.user)
        except:
            searched_posts = Post.objects.filter(active=True)
        paginator = Paginator(user_list, items_per_page)
        page = request.GET.get('page')
        try:
            image_users = paginator.page(page)
        except PageNotAnInteger:
            image_users = paginator.page(1)
        except EmptyPage:
            image_users = paginator.page(paginator.num_pages)

        if len(image_users) < 1:
            return render(request, template, context={
                'breadcrumbs': breadcrumbs,
                'error': True,
                'error_msg': 'No users found',
                'page_title': page_title,
                'image_user': True,
            })

        objects = []
        for image_user in image_users:
            user_posts = searched_posts.filter(user=image_user)
            user_link = reverse('ic:user_view', args=[image_user.username])
            if search_key:
                user_link = "%s?search=%s" % (user_link, search_key)
            if len(user_posts) == 0:
                continue
            objects.append({
                'name': image_user.username,
                'link': user_link,
                'notes': image_user.notes,
                'count': len(user_posts),
            })

        context = {
            'objects': objects,
            'breadcrumbs': breadcrumbs,
            'users': image_users,
            'search': (search_key if search_key else False),
            'page_title': page_title,
            'image_user': True,
        }
        return render(request, template, context=context)
    except Exception as e:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': str(e),
            'search': (search_key if search_key else False),
            'page_title': page_title,
        })


def user_view(request, username):
    template = 'image_collector/base_layout.html'
    breadcrumbs = []
    search_key = None
    page_title = "User not found"
    try:
        image_user = ImageUser.objects.get(username__iexact=username)
        page_title = str(image_user.username)
        breadcrumbs.append({
            'name': 'Home',
            'link': reverse('ic:index'),
            'active': False,
        })
        breadcrumbs.append({
            'name': 'Users',
            'link': reverse('ic:users_view'),
            'active': False,
        })
        breadcrumbs.append({
            'name': image_user.username,
            'active': True,
        })

        if image_user.username != username:
            return redirect(reverse('ic:user_view', args=(image_user.username,)))

        post_list = Post.objects.filter(user=image_user, active=True)
        try:
            search_key = request.GET.get('search')
            if search_key not in username and search_key != username:
                search_terms = search_key.split()
                qset = reduce(operator.__or__, [
                    Q(title__icontains=search_term) |
                    Q(description__icontains=search_term) |
                    Q(website__name__icontains=search_term)
                    for search_term in search_terms])
                post_list = post_list.filter(qset)
        except:
            pass
        paginator = Paginator(post_list, items_per_page)
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        if len(posts) < 1:
            return render(request, template, context={
                'breadcrumbs': breadcrumbs,
                'error': True,
                'error_msg': 'No posts for requested user found',
                'search': (search_key if search_key else False),
                'page_title': page_title,
                'image_user': True,
            })
        context = {
            'posts': posts,
            'breadcrumbs': breadcrumbs,
            'search': (search_key if search_key else False),
            'page_title': page_title,
            'image_user': True,
        }
        return render(request, template, context=context)
    except Exception as e:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': str(e),
            'search': (search_key if search_key else False),
            'page_title': page_title,
        })


def random_view(request):
    posts = Post.objects.filter(active=True)
    post_ids = [post.pk for post in posts]
    post_id = random.choice(post_ids)
    return redirect(reverse('ic:post_view', kwargs={'post_id': post_id}))


def newest_view(request):
    posts = Post.objects.filter(active=True).order_by('-timestamp')
    return redirect(reverse('ic:post_view', kwargs={'post_id': posts[0].pk}))


def download_post_view(request, post_id):
    template = 'image_collector/post.html'
    index_template = 'image_collector/base_layout.html'
    breadcrumbs = []
    page_title = "Post not found"
    zip_archive = None

    try:
        post = Post.objects.get(pk=post_id)
        page_title = str(post.title)

        zip_name = '%s.zip' % post.id
        zip_path = os.path.join(settings.MEDIA_ROOT, 'zips', zip_name)
        zip_download_name = 'Image Collector - %s.zip' % post.title

        if not os.path.isfile(zip_path):
            zip_archive = zipfile.ZipFile(zip_path, 'w')
            zfill_count = len(str(len(post.images.all())))
            for idx, image in enumerate(post.images.all()):
                filename, file_extension = os.path.splitext(image.file.path)
                image_number = str(idx + 1).zfill(zfill_count)
                image_name = '%s - %s.%s' % (image_number, image.image_id, file_extension.replace('.',''))
                zip_archive.write(image.file.path, image_name)
        else:
            zip_archive = zipfile.ZipFile(zip_path, 'r')
    except Exception as e:
        return render(request, index_template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'page_title': page_title,
            'error_msg': str(e),
        })
    finally:
        if zip_archive:
            zip_archive.close()

    mime_type = mimetypes.guess_type(zip_path)[0]
    response = HttpResponse(open(zip_path, 'rb').read(), content_type=mime_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % zip_download_name
    response['Content-Length'] = os.path.getsize(zip_path)
    return response


def image_view(request, requested_image):
    template = 'image_collector/base_layout.html'
    try:
        image_id, image_ext = requested_image.split('.')
        image = Image.objects.get(image_id=image_id)
        try:
            ext = Extension.objects.get(extension=image_ext)
            mime_type = MimeType.objects.get(extension=ext).mime
        except:
            files_ext = image.file.name.split('.')
            ext = Extension.objects.get(extension=files_ext[-1])
            # mime_type = MimeType.objects.get(extension=ext).mime
            mime_type = mimetypes.guess_type(image.file.name)
        with open(image.file.path, 'rb') as image_file:
            response = HttpResponse(image_file.read(), content_type=mime_type)
            response['Content-Disposition'] = 'filename=%s.%s' % (image_id, image_ext)
    except Exception as e:
        context = {
            'error': True,
            'error_msg': str(e)
        }
        response = render(request, template, context)
    return response


