import random
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from .models import Tweet
from django.conf import settings
from django.utils.http import is_safe_url
from .forms import TweetForm
from .serializers import TweetSerializer, TweetActionSerializer,TweetCreateSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
import json
ALLOWED_HOSTS=settings.ALLOWED_HOSTS
# Create your views here.
def tweet_home_pure_django(request,*args,**kwargs):
    #q=Tweet()
    #q.content="here is my tweet"
    #q.author="halima"
    #q.save()
    qs=Tweet.objects.all()
    tweet_list= [x.serialize() for x in qs]
    data={"response":tweet_list}
    print (data)
    return JsonResponse(data, status=200)

@api_view(['GET'])
def tweet_home(request,*args,**kwargs):
    qs=Tweet.objects.all()
    serializer=TweetSerializer(qs, many=True)
    #json.dumps(serializer.data)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def tweet_detail(request, tweet_id,*args,**kwargs):
    qs=Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    obj=qs.first()
    serializer=TweetSerializer(obj)
    return Response(serializer.data, status=200)

@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def tweet_delete(request, tweet_id,*args,**kwargs):
    qs=Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    qs=qs.filter(user=request.user)
    if not qs.exists():
        return Response({"message":"You cannot delete this tweet"}, status=401)
    obj=qs.first()
    obj.delete()
    return Response({"message":"Tweet Removed"}, status=200)


def index(request, *args, **kwargs):
    #print (request.user or None)
    return render(request,'tweet/home.html',{})

@api_view(['POST'])
#@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def Tweet_create_view(request, *args, **kwargs):
    serializer = TweetSerializer(data=request.POST)
    serializer= TweetCreateSerializer(data=request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        print (serializer.data)
        return Response(serializer.data, status=201)
    return Response({}, status=400)


def Tweet_create_view_pure_django(request, *args, **kwargs):
    user=request.user
    if not request.user.is_authenticated:
        user=None
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)

    form= TweetForm(request.POST or None)

    next_url=request.POST.get("next")
    if form.is_valid():
        obj=form.save(commit=False)
        obj.user=user
        obj.save()
        if request.is_ajax():
            print (obj.serialize())
            return JsonResponse(obj.serialize(), status=201)
        if next_url != None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect ('tweets')
    if form.errors:
        if request.is_ajax():
            #print ("heres the error",form.errors)
            return JsonResponse(form.errors,status=400)

        #form=TweetForm()
    return render (request, 'components/form.html', context={'form': form})

@api_view([ 'POST'])
@permission_classes([IsAuthenticated])
def tweet_action(request,*args,**kwargs):

    '''
    is is required.
    Action options are:like, unlike, retweet
    '''
    print (request.data, request.POST)
    serializer=TweetActionSerializer(data=request.data)
    #serializer = TweetCreateSerializer(data=request.POST)
    if serializer.is_valid(raise_exception=True):
        data=serializer.validated_data
        print ('#######',data)
        tweet_id=data.get("id")
        action= data.get("action")
        content=data.get("content")
        qs=Tweet.objects.filter(id=tweet_id)
        if not qs.exists():
            return Response({}, status=404)
        obj=qs.first()
        if action=="like":
            obj.likes.add(request.user)
            serializer=TweetSerializer(obj)
            return Response(serializer.data, status=200)
        elif action =="unlike":
            obj.likes.remove(request.user)
            serializer=TweetSerializer(obj)
            return Response(serializer.data, status=201)

        elif action=="retweet":
            parent_obj=obj
            new_tweet=Tweet.objects.create(user=request.user, parent=parent_obj, content=content)
            serializer=TweetSerializer(new_tweet)
            return Response(serializer.data, status=200)
    return Response({}, status=200)
