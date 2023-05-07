from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from . import models
from . import forms
# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = models.User.objects.get(email=email)
        except:
            messages.error(request, "User does not esixt!")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or Password does not exist!")
            
    context = {'page':page,}
    return render(request, 'accounts/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')



def registerPage(request):
    page='register'
    form = forms.MyUserCreationForm()

    if request.method == "POST":
        form = forms.MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, "Registraion done successfully, Pls login to proceed to the website.")
            return redirect('login')
        else:
            messages.error(request, "Sorry, an error occured during registration, Pls try again.")

    context = {
        'page' : page,
        'form' : form
        }
    return render(request, 'accounts/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    # The previous line is the same as the following commented few lines

    # q = request.GET.get('q') 
    # if request.GET.get('q') != None:
    #     q = request.GET.get('q') 
    # else:
    #     q = ''


    # The search functionality
    rooms = models.Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    
    topics = models.Topic.objects.all()[0:5]
    room_count = rooms.count() 
    room_messages = models.Message.objects.filter(Q(room__name__icontains=q))  

    #  The next one is the same as the above one but the count() method works faster than than the len() method
    # room_count = len(models.Room.objects.all())

    context = {
        'rooms' : rooms,
        'topics' : topics,
        'room_count' : room_count,
        'room_messages' : room_messages,
    }

    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def room(request, pk):
    room = models.Room.objects.get(id=pk)

    # get all messages that spicific to that room.
    room_messages = room.message_set.all().order_by('-created')  
    participants = room.participants.all() 

    if request.method == "POST":
        message = models.Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),
        ) 
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {
        'room' : room,
        'room_messages' : room_messages,
        'participants' : participants,
    }
    return render(request, 'base/room.html', context)
    
    
@login_required(login_url='login')
def userProfile(request, pk):
    user = models.User.objects.get(id=pk)

    # get all rooms that spicific to that user.
    rooms = user.room_set.all() 
    room_messages = user.message_set.all()
    topics = models.Topic.objects.all()

    context = {
        'user' : user,
        'rooms' : rooms,
        'room_messages' : room_messages,
        'topics' : topics,
    }

    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = forms.RoomForm()
    topics = models.Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = models.Topic.objects.get_or_create(name=topic_name)

        models.Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        return redirect('home')
        

    context = {
        'form' : form,
        'topics' : topics,
    }
    return render(request, 'base/room_form.html', context)




@login_required(login_url='login')
def updateRoom(request, pk):
    room = models.Room.objects.get(id=pk)
    form = forms.RoomForm(instance=room)
    topics = models.Topic.objects.all()


    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = models.Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {
        'form' : form,
        'topics' : topics,
        'room' : room,
    }
    return render(request, 'base/room_form.html', context)



@login_required(login_url='login')
def deleteRoom(request, pk):
    room = models.Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!')
    

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    context = {
        'obj' : room,
    }
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = models.Message.objects.get(id=pk)
    message_room = message.room.id
    

    if request.user != message.user:
        return HttpResponse('You are not allowed here!')
    

    if request.method == 'POST':
        message.delete()
        return redirect('room', pk=message_room)

    context = {
        'obj' : message,
    }
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = forms.UserForm(instance=user)

    if request.method == "POST":
        form = forms.UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid:
            form.save()
            return redirect('user-profile', pk=user.id)
        
        
    context = {
        'form' : form,
    }
    return render(request, 'base/update_user.html', context)



def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = models.Topic.objects.filter(name__icontains=q)

    '''
    topics = models.Topic.objects.filter()

    this line is the same as the following one..

    topics = models.Topic.objects.all()

    the filter() method without any filter types inside it is the same as the all() method
    '''

    context = {
        'topics' : topics,
    }

    return render(request, 'base/topics.html', context)



def activityPage(request):
    room_messages = models.Message.objects.all()

    context = {
        'room_messages' : room_messages,
    }

    return render(request, 'base/activity.html', context)