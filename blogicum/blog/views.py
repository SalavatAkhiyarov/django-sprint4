from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import CreateView

from .models import Category, Post, Comments
from .forms import CreatePost, ProfileForm, CommentForm, CustomUserCreationForm

User = get_user_model()


def get_select_related(queryset):
    return queryset.select_related(
        'author',
        'location',
        'category',
    )


def filter_posts_by_publication(queryset):
    return queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_select_related(
        filter_posts_by_publication(
            category.posts.all().annotate(
                comment_count=Count('comments')).order_by('-pub_date')
        )
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'blog/category.html',
        {
            'page_obj': page_obj,
            'category': category,
        }
    )


def post_detail(request, pk):
    post = Post.objects.filter(pk=pk).first()
    if not post or (not post.is_published and request.user != post.author):
        raise Http404
    comments = Comments.objects.filter(post=post)
    form = CommentForm()
    return render(
        request,
        'blog/detail.html',
        {'post': post, 'form': form, 'comments': comments},
    )


def index(request):
    post_list = get_select_related(
        filter_posts_by_publication(
            Post.objects.annotate(
                comment_count=Count('comments')).order_by('-pub_date')
        )
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'blog/index.html',
        {'page_obj': page_obj}
    )


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile).annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/profile.html',
                  {'profile': profile, 'page_obj': page_obj})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = CreatePost(request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
        else:
            return render(request, 'blog/create.html', {'form': form})
    else:
        form = CreatePost()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=user.username)
    else:
        form = ProfileForm(instance=user)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('blog:post_detail', pk=post.pk)
    if request.method == 'POST':
        form = CreatePost(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = CreatePost(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author and not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', {'post': post})


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comments, pk=comment_id, post=post)
    if comment.author != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', pk=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html',
                  {'post': post, 'form': form, 'comment': comment})


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', pk=pk)
    else:
        form = CommentForm()
    return render(
        request, 'blog/comment.html',
        {'post': post, 'form': form, 'comments': post.comments.all()}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comments, pk=comment_id, post=post)
    if request.user != comment.author and not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html',
                  {'post': post, 'comment': comment})


class UserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    model = User
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return redirect('blog:profile', username=self.object.username)
