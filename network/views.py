from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
import json
from .models import User, Post, Follow, Like


def remove_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post)
    like.delete()
    return JsonResponse({"message": "Like removed!"})


def add_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    newLike = Like(user=user, post=post)
    newLike.save()
    return JsonResponse({"message": "Like added!"})


def index(request):
    # Highest id == most recent post
    all_posts = Post.objects.all().order_by("id").reverse()

    # dango pagination
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    posts_on_page = paginator.get_page(page_number)

    all_likes = Like.objects.all()
    post_liked = []

    # return an empty list if user is NOT signed in
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                post_liked.append(like.post.id)
    except:
        post_liked = []

    context = {
        "all_posts": all_posts,
        "posts_on_page": posts_on_page,
        "post_liked": post_liked
    }
    return render(request, "network/index.html", context)


def new_post(request):
    if request.method == "POST":
        content = request.POST["message"]
        current_user = User.objects.get(pk=request.user.id)
        post = Post(message=content, user=current_user)
        post.save()
        return redirect("index")


def following(request):
    current_user = User.objects.get(pk=request.user.id)
    # Everone Current user is folowing
    people_current_user_is_following = Follow.objects.filter(user=current_user)
    all_posts = Post.objects.all().order_by("id").reverse()
    posts_current_user_is_following = []
    for post in all_posts:
        for person in people_current_user_is_following:
            if person.user_follower == post.user:
                posts_current_user_is_following.append(post)

    # dango pagination
    paginator = Paginator(posts_current_user_is_following, 10)
    page_number = request.GET.get("page")
    posts_on_page = paginator.get_page(page_number)

    all_likes = Like.objects.all()
    post_liked = []
    # return an empty list if user is NOT signed in
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                post_liked.append(like.post.id)
    except:
        post_liked = []

    context = {
        "posts_on_page": posts_on_page,
        "post_liked": post_liked
    }
    return render(request, "network/following.html", context)


def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.message = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change successful", "data": data["content"]})


def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    all_posts = Post.objects.filter(user=user).order_by("-id")

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)

    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    posts_on_page = paginator.get_page(page_number)

    is_following = False
    if request.user.is_authenticated:
        check_follow = followers.filter(
            user=User.objects.get(pk=request.user.id))
        is_following = len(check_follow) != 0

    all_likes = Like.objects.all()
    post_liked = []

    # return an empty list if user is NOT signed in
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                post_liked.append(like.post.id)
    except:
        post_liked = []

    context = {
        "all_posts": all_posts,
        "posts_on_page": posts_on_page,
        "user_name": user.username,
        "following": following,
        "followers": followers,
        "is_following": is_following,
        "current_user": user,
        "post_liked": post_liked
    }
    return render(request, "network/profile.html", context)


def follow(request):
    user_follow = request.POST["user_follow"]
    current_user = User.objects.get(pk=request.user.id)
    user_follow_details = User.objects.get(username=user_follow)
    follow = Follow(user=current_user, user_follower=user_follow_details)
    follow.save()
    user_id = user_follow_details.id
    url = reverse('profile', args=[user_id])
    return redirect(url)


def unfollow(request):
    user_follow = request.POST["user_follow"]
    current_user = User.objects.get(pk=request.user.id)
    user_follow_details = User.objects.get(username=user_follow)
    follow = Follow.objects.get(
        user=current_user, user_follower=user_follow_details)
    follow.delete()
    user_id = user_follow_details.id
    url = reverse('profile', args=[user_id])
    return redirect(url)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
