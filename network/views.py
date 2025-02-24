from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User, Post, Profile, Like

def index(request):
    posts = Post.objects.all().order_by('id').reverse()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {'page_obj': page_obj})

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
    if request.user.is_anonymous:
        return render(request, "network/login.html")
    else:
        return redirect('index')

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
        return redirect('settings', username)
    else:
        if request.user.is_authenticated:
            return redirect(request, 'index')
        else:
            return render(request, "network/register.html")

def profile(request, username):
    # clicking a user profile
    if request.method == 'GET':
        currentuser = request.user
        profileuser = get_object_or_404(User, username=username)
        posts = Post.objects.filter(user=profileuser).order_by('id').reverse()
        follower = Profile.objects.filter(target=profileuser)
        following = Profile.objects.filter(follower=profileuser)
        if request.user.is_anonymous:
            return redirect('login')
        else:
            following_each_other = Profile.objects.filter(follower=currentuser, target=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)
            paginator = Paginator(posts, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'posts': posts.count(),
                'profileuser': profileuser,
                'page_obj': page_obj,
                'follower': follower,
                'totalfollower': totalfollower,
                'following': following,
                'totalfollowing': totalfollowing,
                'followingEachOther': following_each_other
            }

            return render(request, "network/profile.html", context)

    else:
        # clicking follow/unfollow button
        currentuser = request.user
        profileuser = get_object_or_404(User, username=username)
        posts = Post.objects.filter(user=profileuser).order_by('id').reverse()
        following_each_other = Profile.objects.filter(follower=request.user, target=profileuser)
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if not following_each_other:
            follow = Profile.objects.create(target=profileuser, follower=currentuser)
            follow.save()
            follower = Profile.objects.filter(target=profileuser)
            following = Profile.objects.filter(follower=profileuser)
            following_each_other = Profile.objects.filter(follower=request.user, target=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)

            context = {
                'posts': posts.count(),
                'profileuser': profileuser,
                'page_obj': page_obj,
                'follower': follower,
                'following': following,
                'totalfollowing': totalfollowing,
                'totalfollower': totalfollower,
                'followingEachOther': following_each_other
            }

            return render(request, "network/profile.html", context)

        else:
            following_each_other.delete()
            follower = Profile.objects.filter(target=profileuser)
            following = Profile.objects.filter(follower=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)

            context = {
                'posts': posts.count(),
                'profileuser': profileuser,
                'page_obj': page_obj,
                'follower': follower,
                'following': following,
                'totalfollowing': totalfollowing,
                'totalfollower': totalfollower,
                'followingEachOther': following_each_other
            }

            return render(request, "network/profile.html", context)

def newpost(request, username):
    if request.method == 'POST':
        user = get_object_or_404(User, username=username)
        textarea = request.POST["textarea"]
        # if empty return to index
        if not textarea:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        post = Post.objects.create(content=textarea, user=user)
        post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def delete(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.method == 'POST':
        post.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def following(request, username):
    if request.method == 'GET':
        currentuser = get_object_or_404(User, username=username)
        follows = Profile.objects.filter(follower=currentuser)
        posts = Post.objects.all().order_by('id').reverse()
        postlist = []
        for p in posts:
            for follower in follows:
                if follower.target == p.user:
                    postlist.append(p)
        if not follows:
            return render(request, 'network/following.html', {'message': "Opps! You don't follow anybody."})

        paginator = Paginator(postlist, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'network/following.html', {'page_obj':page_obj})

def edit(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(pk=post_id)
        textarea = request.POST["textarea"]
        post.content = textarea
        post.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def settings(request, username):
    user = request.user
    if request.method == 'GET':
        profile = User.objects.get(username=username)
        if request.user.is_anonymous:
            return redirect('login')
        if profile.username == user.username:
            return render(request, 'network/settings.html', {'profile': profile})
        else:
            return redirect("index")
    else:
        profile = User.objects.get(username=username)
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        email_exists = User.objects.filter(email=email)
        profile.first_name = first_name
        profile.last_name = last_name
        if not email_exists or profile.email == email:
            profile.email = email
        else:
            return render(request, "network/settings.html", {'profile': profile, 'message': '*Email already taked.'})


        profile.save()
        return redirect('profile', profile.username)

def likepost(request):
    user = request.user
    if request.method == 'GET':
        #get post id and check if post is in liked model and delete or add if needed
        post_id = request.GET['post_id']
        liked_post = Post.objects.get(pk=post_id)

        if user in liked_post.liked.all() :
            liked_post.liked.remove(user)
            like = Like.objects.get(post=liked_post, user=user)
            like.delete()
        else:
            liked_post.liked.add(user)
            liked_post.save()
            like = Like.objects.get_or_create(post=liked_post, user=user)

        return HttpResponse('success')