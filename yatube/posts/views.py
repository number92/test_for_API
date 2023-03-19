from django.contrib.auth.decorators import login_required
from .models import Post, Group, Follow, User
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm
from .utils import get_paginator
from django.views.decorators.cache import cache_page


@cache_page(60 * 20, key_prefix='index_page')
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
               'post_count': post_count,
               'following': (request.user != author
                             and request.user.is_authenticated
                             and Follow.objects.filter(
                                 user=request.user,
                                 author=author))}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    post_author = post.author
    form = CommentForm(request.POST or None)
    post_comments = post.comments.all()
    title = f'Пост {post.text[:30]}'
    post_count = post.author.posts.count()
    context = {'post': post,
               'post_count': post_count,
               'title': title,
               'author': post_author,
               'form': form,
               'post_comments': post_comments
               }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,)
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
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    context = {'form': form,
               'is_edit': True}
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    context = {'form': form,
               'is_edit': True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post_comment = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post_comment
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    author_post = Post.objects.filter(
        author__following__user=request.user)
    page_obj = get_paginator(request, author_post)
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    if request.user.username != username:
        Follow.objects.get_or_create(
            user=request.user,
            author=get_object_or_404(User, username=username))
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)).delete()
    return redirect('posts:profile', username)
