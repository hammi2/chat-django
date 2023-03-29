from itertools import chain
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View


from .models import (FriendRequest, Message, MessageGroup, MessageRoom, Notification,
                     UserProfile)

# from django.views.generic.base import TemplateView

print("Lets Check this stash")

class HomePageView(View):

    Model = User
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        usr = User.objects.get(id=request.user.id)
        all_usr = User.objects.exclude(id=request.user.id)
        usr_p = UserProfile.objects.filter(user_id=request.user.id).first()
        all_room1 = MessageRoom.objects.filter(first_user=usr_p).all()
        all_room2 = MessageRoom.objects.filter(second_user__in=[usr_p]).all()
        all_rooms = list(chain(all_room1 , all_room2))

        context = {"usr":usr, "all_usr":all_usr, "user_profile":usr_p, "all_rooms":all_rooms}
        return render(request,"index.html", context)

class LoginView(View):

    Model = User
    template_name = "index.html"
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        return render(request,"login.html")
    def post(self,request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username= username, password=password)

        if user is not None:
            login(request ,user)
            return redirect('/home')
        else:
            return redirect('/login')

def Logout(request):

    logout(request)
    return redirect("/login")


def ChatRoom(request,id):
    usr = UserProfile.objects.filter(user_id=request.user.id).first()
    m_room = MessageRoom.objects.filter(group_name=id).first()

    if m_room.one_to_one:
        usr2 = m_room.first_user
        if m_room.first_user == usr:
            usr2 = m_room.second_user.all()[0]
    else:
        usr2 = m_room

    # print(usr2.prof_image)

    # print("------------------MessageRoom-----------------")

    msg = Message.objects.filter(room=m_room).all()
    msgs_room = MessageRoom.objects.filter( Q (first_user=usr)| Q(second_user=usr))
    m_arr = []
    for m in msgs_room:
        messag = Message.objects.select_related("room").filter(room = m).last()
        m_arr.append(messag)
    # print("------------------MessageRoom-----------------")

    all_room1 = MessageRoom.objects.filter(first_user=usr).all()
    all_room2 = MessageRoom.objects.filter(second_user__in=[usr]).all()

    all_rooms = list(chain(all_room1 , all_room2))
    print(all_rooms)

    profiles = UserProfile.objects.exclude(user=request.user)
    user_profile = UserProfile.objects.filter(user=request.user).first()
    user_notifications = Notification.objects.filter(to_user=user_profile).all()
    friend_req = FriendRequest.objects.filter(from_user=user_profile).values_list("to_user", flat=True)
    print(user_notifications)

    # No need for  ("msg",)

    context = { "msg":msg,"usr":usr,"all_usr":usr,"usr2":usr2,"room_name":m_room,"notifications":user_notifications,"all_rooms":all_rooms,
             "msgs_room":msgs_room, "msgs":m_arr, "profiles":profiles, "user_profile":user_profile, "friend_req":friend_req }

    return render(request,"chatroom_index.html", context=context)

class FileUpload(View):

    def post(self, request):
        files = request.FILES.get('files')
        msg_id = request.POST.get('message_id')
        m = Message.objects.filter(id=msg_id).first()
        m.file=files
        m.save()
        return HttpResponse("File Sucessfully added!")


# GROUPS VIEWS BELLOW

def CreateGroup(request):

    g_name = request.POST.get("group_name_form")
    usr = UserProfile.objects.filter(user=request.user).first()
    print(g_name)
    group, Created = MessageGroup.objects.get_or_create(group_admin=usr)
    print(group)
    room = MessageRoom.objects.create(
        group_name=g_name,first_user=usr,one_to_one=False,group=group
        )
    return redirect("/home")

def AddToGroup(request, id):

    g_name = request.POST.get("user_add_group")
    friend  = User.objects.filter(username=g_name).first()
    usr = UserProfile.objects.filter(user=friend).first()
    print(g_name)
    group, Created = MessageGroup.objects.get_or_create(group_admin=usr)
    print(group)
    room = MessageRoom.objects.filter(id=id).first()
    room.second_user.add(usr)
    return redirect("/home")

def RemoveFromGroup(request, id):

    usr = UserProfile.objects.filter(user_id=id).first()
    cur_usr = UserProfile.objects.filter(user=request.user).first()

    cur_usr.friends.remove(usr)
    usr.friends.remove(cur_usr)

    return redirect("/home")

