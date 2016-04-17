from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from image_collector.models import Post, Image, ImageUser, Website, MimeType, Extension

items_per_page = '50'


def index_view(request):
    template = 'image_collector/home.html'
    breadcrumbs = []
    search_key = None

    post_list = Post.objects.filter(active=True)
    try:
        search_key = request.GET.get('search')
        post_list = post_list.filter(Q(title__contains=search_key) | Q(description__contains=search_key)).order_by('timestamp')
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

    breadcrumbs.append({
        'name': 'Home',
        'link': reverse('ic:index'),
        'active': True,
    })

    if len(posts) == 0:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': 'No posts found',
            'search': (search_key if search_key else False),
        })

    context = {
        'posts': posts,
        'breadcrumbs': breadcrumbs,
        'search': (search_key if search_key else False),
    }
    print(context)
    return render(request, template, context=context)


def sites_view(request):
    template = 'image_collector/websites.html'
    breadcrumbs = []
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
                'error_msg': 'No websites found'
            })

        objects = []
        for site in sites:
            objects.append({
                'name': site.name,
                'link': reverse('ic:site_view', args=[site.short_name]),
                'notes': site.notes,
                'count': len(Post.objects.filter(website=site, active=True)),
            })

        context = {
            'objects': objects,
            'breadcrumbs': breadcrumbs,
            'grid_title': 'Websites',
            'sites': sites,
        }
        return render(request, template, context=context)
    except Exception as e:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': str(e)
        })


def site_view(request, site):
    template = 'image_collector/website.html'
    breadcrumbs = []
    search_key = None
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
    except Exception as e:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': str(e)
        })

    breadcrumbs.append({
        'name': requested_website.name,
        'active': True,
    })

    post_list = Post.objects.filter(website=requested_website, active=True)
    try:
        search_key = request.GET.get('search')
        post_list = post_list.filter(Q(title__contains=search_key) | Q(description__contains=search_key)).order_by(
            'timestamp')
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
        })
    context = {
        'posts': posts,
        'site': requested_website,
        'breadcrumbs': breadcrumbs,
        'search': (search_key if search_key else False),
    }
    return render(request, template, context=context)


def post_view(request, post_id):
    template = 'image_collector/post.html'
    breadcrumbs = []
    try:
        post = Post.objects.get(pk=post_id)
    except Exception as e:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': str(e)
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
    }
    return render(request, template, context=context)


def users_view(request):
    template = 'image_collector/users.html'
    breadcrumbs = []
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
            })

        objects = []
        for image_user in image_users:
            objects.append({
                'name': image_user.username,
                'link': reverse('ic:user_view', args=[image_user.username]),
                'notes': image_user.notes,
                'count': len(Post.objects.filter(user=image_user, active=True)),
            })

        context = {
            'objects': objects,
            'breadcrumbs': breadcrumbs,
            'grid_title': 'Users',
            'users': image_users,
        }
        return render(request, template, context=context)
    except Exception as e:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': str(e)
        })


def user_view(request, username):
    template = 'image_collector/user.html'
    breadcrumbs = []
    search_key = None
    try:
        image_user = ImageUser.objects.get(username__iexact=username)
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
            post_list = post_list.filter(Q(title__contains=search_key) | Q(description__contains=search_key)).order_by(
                'timestamp')
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
            })
        context = {
            'image_user': image_user,
            'posts': posts,
            'breadcrumbs': breadcrumbs,
            'search': (search_key if search_key else False),
        }
        return render(request, template, context=context)
    except Exception as e:
        return render(request, template, context={
            'breadcrumbs': breadcrumbs,
            'error': True,
            'error_msg': str(e)
        })


def image_view(request, requested_image):
    template = 'image_collector/home.html'
    try:
        image_id, image_ext = requested_image.split('.')
        image = Image.objects.get(image_id=image_id)
        try:
            ext = Extension.objects.get(extension=image_ext)
            mime_type = MimeType.objects.get(extension=ext).mime
        except:
            files_ext = image.file.name.split('.')
            ext = Extension.objects.get(extension=files_ext[-1])
            mime_type = MimeType.objects.get(extension=ext).mime
        with open(image.file.path, 'rb') as image_file:
            response = HttpResponse(image_file.read(), content_type=mime_type)
            response['Content-Disposition'] = 'filename=%s.%s' % (image_id, image_ext)
            return response
    except Exception as e:
        return render(request, template, context={'error': True, 'error_msg': str(e)})


