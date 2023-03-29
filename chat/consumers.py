import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.db.models import Q

from .models import (FriendRequest, Message, MessageRoom, Notification,
                     UserProfile)


class ChatConsumer(WebsocketConsumer):

    def connect(self):

        r_id = self.scope['path'].split('socket-server/room_id=')[1]
        # print("------REQUEST--------")
        # # print(r_id[0])
        # print(r_id)
        # print("------REQUEST--------")

        # try:
        #     group_name = MessageRoom.GetGroupName(r_id[0], r_id[1])
        #     print("INTO TRY")
        # except Exception as E:
        #     print("INTO EXCEPT")
        #     print(E)
        group_name = MessageRoom.objects.filter(group_name=r_id).first()

        print(group_name)

        usr_id = self.scope["user"]._wrapped.id
        self.MessageRoomUsers(usr_id, group_name, "Add")

        self.room_group_name = f"chat_{group_name.group_name}"
        print(self.room_group_name)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        self.accept()

    def MessageRoomUsers(self, usr_id, msg_room, action):

        # print(usr_id)
        usr = UserProfile.objects.get(id=usr_id)
        if action == "Add":
            # print("User Joined")
            if usr not in msg_room.users_active.all():
                msg_room.users_active.add(usr)

            room_group_name = f"chat_{msg_room.group_name}"
            m_none = Message.objects.filter(receiver__in=[usr],seen_by_users=None).all()
            m_none_arr = []
            
            if m_none:
                print("Yes there are couple of mesgages with empty seen_by_users")
                for m in m_none:
                    m_none_arr.append(m.id)
                async_to_sync(self.channel_layer.group_send)(
                room_group_name,{
                    "type":"message_seen",
                    "my_user":usr.user.username,
                    "m_none":m_none_arr
                })
                #  nEED TO WORK ON THiS
                # msg = Message.objects.filter(receiver__in=[usr],seen_by_users=None).all().update(seen_by_users=usr)

            else:
                # print(m_none.values("id"))
                print("No All messages are seen.")

        else:
            print("User left")
            msg_room.users_active.remove(usr)

    def message_seen(self, event):
        self.send(
                text_data=json.dumps({
                    'type':'message_seen',
                    'messages_seen':event['m_none'],
                    'username':event['my_user'],
                })
            )


    # def GetGroupName(self, id1, id2):
    #     msg_room = MessageRoom.objects.filter(Q(first_user_id__in=id1,second_user_id__in=id2) | Q(first_user_id__in=id2, second_user_id__in=id1)).first()
    #     return msg_room

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        username = text_data_json['username']

        # try:
        #     room_id = text_data_json['room_id'].split("_")
        # except:
        room_id = text_data_json['room_id']
        rooms = MessageRoom.objects.filter(group_name=room_id).first()
        try:
            msg = text_data_json['typing']
            # msg = 'typing'
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type':'typing_message',
                    'message':msg,
                    'username':username
                }
            )

        except:
            receiver = text_data_json['receiver']
            msg = text_data_json['message']
            msg_id = text_data_json['message_id']

            print("-----------------Room_id-----------------")
            print(room_id)
            print(receiver)
            print("-----------------Room_id-----------------")

            is_group = False
            if not rooms.one_to_one:
                is_group=True

            if not msg_id:
                
                msg_created = self.save_messages(username,receiver,room_id,msg,is_group)
                print(msg_created)
                print(msg)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type':'chat_message',
                        'message':msg,
                        'username':username,
                        'receiver':receiver,
                        'room_id':room_id,
                        'msg_created':msg_created
                    }
                )
            elif msg_id:
                print("editing the message")
                self.edit_message(msg_id, msg)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type':'update_chat_message',
                        'message':msg,
                        'msg_id':msg_id,
                        'receiver':receiver
                    }
                )

    def update_chat_message(self, event):

        msg = event['message']
        msg_id = event['msg_id']
        msg_receiver = event['receiver']
        self.send(
            text_data=json.dumps({
                'type':'update_chat',
                'message':msg,
                'msg_id':msg_id,
                'receiver':msg_receiver
            })
        )

    def chat_message(self, event):

        msg = event['message']
        username = event['username']
        receiver = event['receiver']
        room_id = event['room_id']
        msg_obj = event['msg_created']
        print(room_id)

        if msg_obj.room.one_to_one:
            receiver = UserProfile.objects.get(user_id=receiver)
            seen_by_user = "No"
            if receiver == msg_obj.seen_by_users:
                seen_by_user = "Yes"
        else:
            seen_by_user = "No"
            receiver = msg_obj.room.second_user
        # msg_room = self.GetGroupName(room_id[0], room_id[1])


        self.send(
            text_data=json.dumps({
                'type':'chat',
                'message':msg,
                'messageId':msg_obj.id,
                'username':username,
                "seen":seen_by_user
            })
        )


    def typing_message(self, event):

        msg = event['message']
        username = event['username']
        print("User is typing........")

        self.send(
            text_data=json.dumps({
                'type':'typing_status',
                'message':msg,
                'username':username
            })
        )


    def save_messages(self, username, receiver, room, msg, is_group=False):
        sender = UserProfile.objects.filter(user__username=username).first()
        print("-------VALLUE OF GROUP----------")
        # print(is_group)

        room = MessageRoom.objects.filter(group_name=room).first()
        created = Message.objects.create(sender=sender,room=room,message=msg)

        if not is_group:
            print("------ADDING RECEIVERS--------")
            receiver = UserProfile.objects.filter(user_id=receiver).first()
            created.receiver.add(receiver)
        else:
            print("------ADDING GROUP RECEIVERS--------")
            created.receiver.add(room.first_user)
            for room_user in room.second_user.all():
                print("--------ADDING USERS")
                print(room_user)
                created.receiver.add(room_user)

            # created.save()

        #     room = MessageRoom.GetGroupName(room[0], room[1])

        # WORK OVER HERE!

        # Continue from here

        # created.save()

        msg_obj = Message.objects.get(id=created.id)
        if receiver in room.users_active.all():
            msg_obj.seen_by_users.add(receiver)
            msg_obj.save()
            print("******************Message Seen******************")
        return msg_obj
            # self.MessageRoomUsers(usr_id, group_name, "Add")

    def edit_message(self, msg_id, msg):
        m = Message.objects.filter(id=msg_id).update(message=msg)

    def disconnect(self, close_code):
        # Called when the socket closes
        r_id = self.scope['path'].split('socket-server/room_id=')
        # group_name = MessageRoom.GetGroupName(r_id[0], r_id[1])
        print(f"group leaved :#<20")
        print(r_id)
        group_name = MessageRoom.objects.filter(group_name=r_id[1]).first()
        print("group leaved:#<20")

        usr_id = self.scope["user"]._wrapped.id
        self.MessageRoomUsers(usr_id, group_name, "Remove")


class UserChatConsumer(WebsocketConsumer):

    def connect(self):

        r_id = self.scope['path'].split('/ws/user_chat/room_id=')[1]
        # group_name = self.GetGroupName(r_id[0], r_id[1])
        self.room_group_name = f"notif{r_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        self.accept()
        print(f"connected to the test consumers ---- {self.room_group_name}")


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        from_user = UserProfile.objects.filter(id=text_data_json['from_user']).first()
        to_user =  UserProfile.objects.filter(id=text_data_json['to_user']).first()
        notif_type = text_data_json['type']
        print(text_data_json)

        if notif_type == "friend_request_response":
            f = FriendRequest.objects.filter(from_user=to_user, to_user=from_user).first()
            msgs = f"You have {text_data_json['decision']} this friend request."
            n = Notification.objects.filter(id=int(text_data_json['notification_id'])).update(message=msgs)
            f.status = text_data_json['decision']
            f.save()
            if text_data_json['decision'] == "Accepted":
                to_user.friends.add(from_user)
                from_user.friends.add(to_user)
                # FRIENDS REQUEST ACCEPTED
                print("------------ROOM CREATED------------------")
                msg_created = MessageRoom.objects.create(first_user=from_user)
                # print("------------ROOM CREATED------------------")
                msg_created.second_user.add(to_user)
                # msg_created.second_user.set([to_user])
                # msg_created.save()
            
        elif notif_type == "friend_request_send":
            message = text_data_json['message']
            if not FriendRequest.objects.filter(Q(from_user=from_user, to_user=to_user)|Q(from_user=to_user, to_user=from_user)):
                friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user, message=message)
        elif notif_type == "message_deletion":
            msg_id = text_data_json['msg_id']
            Message.objects.filter(id=msg_id).delete()
            print("-------Mssage deleting Conusmers----------")
            receiver_group_name = f"notif{to_user.user.id}"
            print("-------Mssage deleting Conusmers----------")
            async_to_sync(self.channel_layer.group_send)(
                receiver_group_name,
                {
                    'type':'Remove_message',
                    'msg_id':msg_id,
                }
            )
    
    def Remove_message(self, event):

        self.send(
            text_data=json.dumps({
                'notification_type':'Remove_message',
                'message':event,
            })
        )


    def send_notification(self, event):
        print("-----Notif------")
        print(event)
        print("-----Notif------")
        self.send(
            text_data=json.dumps({
                'type':'notifications',
                'message':event,
            })
        )
