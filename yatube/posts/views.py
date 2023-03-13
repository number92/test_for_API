from django.contrib.auth.decorators import login_required
from .models import Post, Group, User
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from .utils import get_paginator


def index(request):
    template = 'posts/index.html'
    title = "Последние обновления на сайте"
    post_list = Post.objects.all()
    context = {'title': title,
               'post_list': post_list,
               'page_obj': get_paginator(request, post_list)
               }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    title = f"Записи сообщества {slug}"
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {'title': title,
               'group': group,
               'post_list': post_list,
               'page_obj': get_paginator(request, post_list)}
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    post_count = post_list.count()
    context = {'author': author,
               'page_obj': get_paginator(request, post_list),
               'post_count': post_count}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    title = f'Пост {post.text[:30]}'
    post_count = post.author.posts.count()
    context = {'post': post,
               'post_count': post_count,
               'title': title}
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
        else:
            return render(request, template, {'form': form})
    else:
        return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            post.save()
            return redirect('posts:post_detail', post.pk)
        else:
            is_edit = True
            context = {'form': form,
                       'is_edit': is_edit}
            return render(request, template, context)
    else:
        is_edit = True
        form = PostForm(instance=post)
        context = {'form': form,
                   'is_edit': is_edit}
        return render(request, template, context)
