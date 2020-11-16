from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
import json

from .models import User, Follow, Post, Like


def index(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    try:
        page = int(request.GET['page'])
    except:
        page = 1

    offset = (page - 1) * 10
    data = Post.objects.all()
    total_posts = data.count()
    posts = data.order_by('-date')[offset:offset+10]
    return render(request, "network/index.html", {
        'posts': [post.format(user=request.user) for post in posts],
        'total_posts': total_posts,
        'pages': int(total_posts / 10) + 1,
        'current': page,
        'loop_times': range(1, int(total_posts / 10) + 2)
    })


@csrf_exempt
@login_required
def new_post(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=400)

    body = json.loads(request.body)
    if body.get('content') is None or body.get('content').strip() == '':
        return JsonResponse({'error': 'Post content is empty.'}, status=400)

    content = body.get('content')
    post = Post(user=request.user, content=content)
    post.save()
    return JsonResponse({'post': post.format(request.user)})


@csrf_exempt
@login_required
def edit_post(request, post_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=400)

    body = json.loads(request.body)
    if body.get('content') is None or body.get('content').strip() == '':
        return JsonResponse({'error': 'Post content is empty.'}, status=400)

    content = body.get('content')
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
        post.content = content
        post.save()
        return JsonResponse({'message': 'Post has been edited successfully.'})
    except:
        return JsonResponse({'error': 'You do not have permission to edit this post.'}, status=401)


@csrf_exempt
@login_required
def toggle_like(request, post_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=400)

    body = json.loads(request.body)
    if body.get('liked') is None:
        return JsonResponse({'error': 'No operation found.'}, status=400)

    try:
        post = Post(user=request.user, pk=post_id)
    except:
        return JsonResponse({'error': 'No post found.'}, status=401)

    liked = body.get('liked')
    if liked:
        if Like.objects.filter(user=request.user, post=post).exists():
            return JsonResponse({'message': 'No operation needed.'})
        else:
            Like(user=request.user, post=post).save()
            return JsonResponse({'message': 'Done.'})
    else:
        try:
            Like.objects.get(user=request.user, post=post).delete()
            return JsonResponse({'message': 'Done.'})
        except:
            return JsonResponse({'error': 'Something unexpected happened.'}, status=400)


def user(request, username):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    try:
        page = int(request.GET['page'])
    except:
        page = 1

    offset = (page - 1) * 10
    try:
        user = User.objects.get(username=username)
        data = Post.objects.filter(user=user)
        total_posts = data.count()
        posts = data.order_by('-date')[offset:offset + 10]
        response = {
            'posts': [post.format(request.user) for post in posts],
            'followings': Follow.objects.filter(follower=user).count(),
            'followers': Follow.objects.filter(user=user).count(),
            'profile': user.username,
            'profileid': user.id,
            'total_posts': total_posts,
            'pages': int(total_posts / 10) + 1,
            'current': page,
            'loop_times': range(1, int(total_posts / 10) + 2)
        }
        if request.user.is_authenticated:
            response['am_i_following'] = Follow.objects.filter(
                user=user, follower=request.user).exists()
        return render(request, 'network/profile.html', response)
    except Exception as e:
        print(e)
        return HttpResponse('User not found.')


@csrf_exempt
@login_required
def follow(request, user_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=400)

    body = json.loads(request.body)
    if body.get('follow') is None:
        return JsonResponse({'error': 'No operation found.'}, status=400)

    follow = body.get('follow')
    try:
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse({'error': 'User not found.'}, status=400)

    if request.user == user:
        return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)

    if follow:
        if Follow.objects.filter(user=user, follower=request.user).exists():
            return JsonResponse({'message': 'No operation needed.'})
        else:
            Follow(user=user, follower=request.user).save()
            return JsonResponse({'message': 'Done.'})
    else:
        try:
            Follow.objects.get(user=user, follower=request.user).delete()
            return JsonResponse({'message': 'Done.'})
        except:
            return JsonResponse({'error': 'Something unexpected happened.'}, status=400)


@login_required
def following(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    try:
        page = int(request.GET['page'])
    except:
        page = 1

    offset = (page - 1) * 10
    users = []
    for f in Follow.objects.filter(follower=request.user):
        users.append(f.user)

    data = Post.objects.filter(user__in=users)
    total_posts = data.count()
    posts = data.order_by('-date')[offset:offset+10]
    return render(request, 'network/following.html', {
        'posts': [post.format(request.user) for post in posts],
        'total_posts': total_posts,
        'pages': int(total_posts / 10) + 1,
        'current': page,
        'loop_times': range(1, int(total_posts / 10) + 2)
    })


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
