from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView

from .models import Category, Post, Comments
from .forms import CreatePost, ProfileForm, CommentForm, RegistrationForm
from .services import (
    annotate_and_sort_posts,
    filter_posts_by_publication,
    get_select_related,
    paginate
)


User = get_user_model()


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    page_obj = paginate(get_select_related(
        filter_posts_by_publication(
            annotate_and_sort_posts(category.posts.all())
        )
    ), request)
    return render(
        request,
        'blog/category.html',
        {
            'page_obj': page_obj,
            'category': category,
        }
    )


def post_detail(request, post_id):
    post = get_object_or_404(get_select_related(Post.objects), pk=post_id)
    if request.user != post.author:
        post = get_object_or_404(
            get_select_related(
                filter_posts_by_publication(Post.objects)
            ),
            pk=post_id
        )
    comments = post.comments.select_related('author')
    form = CommentForm()
    return render(
        request,
        'blog/detail.html',
        {'post': post, 'form': form, 'comments': comments},
    )


def index(request):
    page_obj = paginate(get_select_related(
        filter_posts_by_publication(
            annotate_and_sort_posts(Post.objects.all())
        )
    ), request)
    return render(
        request,
        'blog/index.html',
        {'page_obj': page_obj}
    )


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = get_select_related(
        annotate_and_sort_posts(profile.posts.all())
    )
    if request.user != profile:
        post_list = filter_posts_by_publication(post_list)
    page_obj = paginate(post_list, request)
    return render(request, 'blog/profile.html',
                  {'profile': profile, 'page_obj': page_obj})


@login_required
def create_post(request):
    form = CreatePost(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_profile(request):
    user = request.user
    form = ProfileForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.pk)
    form = CreatePost(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.pk)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author and not request.user.is_staff:
        return redirect('blog:post_detail', post_id=post.pk)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', {'post': post})


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comments, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        comment = form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html',
                  {'post': comment.post, 'form': form, 'comment': comment})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request, 'blog/comment.html',
        {'post': post, 'form': form, 'comments': post.comments.all()}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comments, pk=comment_id, post_id=post_id)
    if request.user != comment.author and not request.user.is_staff:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html',
                  {'post': comment.post, 'comment': comment})


class UserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    model = User
    form_class = RegistrationForm

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return redirect('blog:profile', username=self.object.username)
