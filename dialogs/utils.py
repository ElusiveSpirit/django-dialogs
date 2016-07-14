"""Utils for redis."""
import json
import redis

from django.http import HttpResponse
from django.utils import dateformat
from django.shortcuts import redirect


class HttpResponseAjax(HttpResponse):
    def __init__(self, status='ok', **kwargs):
        kwargs['status'] = status
        super(HttpResponseAjax, self).__init__(
            content=json.dumps(kwargs),
            content_type='application/json',
        )


class HttpResponseAjaxError(HttpResponseAjax):
    def __init__(self, code, message):
        super(HttpResponseAjaxError, self).__init__(
            status='error', code=code, message=message
        )


def login_required_ajax(view):
    def view2(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view(request, *args, **kwargs)
        elif request.is_ajax():
            return HttpResponseAjaxError(
                code="no_auth",
                message=u'Требуется авторизация',
            )
        else:
            return redirect('/login/?continue=' + request.get_full_path())
    return view2


def get_messages_info(user_id, thread_id):
    """
    Returns a dict of message info from redis:
    {
        "total",
        "sent",
        "received"
    }
    """
    user_id = str(user_id)
    thread_id = str(thread_id)
    ret = {}

    r = redis.StrictRedis()

    ret['total'] = r.hget(
        "thread_{}_messages".format(thread_id),
        "total_messages"
    )
    ret['sent'] = r.hget(
        "thread_{}_messages".format(thread_id),
        "from_{}".format(user_id)
    )

    if ret['total']:
        ret['total'] = int(ret['total'])
    else:
        ret['total'] = 0

    if ret['sent']:
        ret['sent'] = int(ret['sent'])
    else:
        ret['sent'] = 0

    ret['received'] = ret['total'] - ret['sent']
    return ret


def json_response(obj):
    """
    A func.

    This function takes a Python object (a dictionary or a list)
    as an argument and returns an HttpResponse object containing
    the data from the object exported into the JSON format.
    """
    return HttpResponse(json.dumps(obj), content_type="application/json")


def clear_users_thread_unread_messages(thread, user):
    """
    Clear user's unread messages in thread in redis channel.

    thread = current thread
    user = who has read messages
    """
    r = redis.StrictRedis()
    r.hset(
        "thread_{}_messages".format(thread.id),
        "user_{}_unread_msg_count".format(user.username),
        0
    )


def update_thread_messages_status(thread, user):
    """
    Make messages in thread read by user.

    thread = current thread
    user = who has read messages
    """
    message_list = thread.get_user_unread_messages(user)
    message_id_list = [message.id for message in message_list[:]]
    message_list.update(has_read=True)

    r = redis.StrictRedis()
    if thread.participants.count() > 2:
        clear_users_thread_unread_messages(thread, user)

    r.publish("thread_{}_messages".format(thread.id), json.dumps({
        "type": "message_status",
        "thread_id": thread.id,
        "message_id_list": message_id_list,
    }))


def send_message(message):
    """
    Send message to redis channel.

    This function takes Thread object id (first argument),
    sender id (second argument), message text (third argument)
    and can also take sender's name.

    It creates a new Message object and increases the
    values stored in Redis that represent the total number
    of messages for the thread and the number of this thread's
    messages sent from this specific user.

    If a sender's name is passed, it also publishes
    the message in the thread's channel in Redis
    (otherwise it is assumed that the message was
    already published in the channel).
    """
    r = redis.StrictRedis()

    r.publish("thread_{}_messages".format(message.thread.id), json.dumps({
        "type": "message",
        "thread_id": message.thread.id,
        "message_id": message.id,
        "timestamp": dateformat.format(message.datetime, 'U'),
        "sender": message.sender.username,
        "text": message.text,
        "has_read": message.has_read,
    }))

    participants = list(message.thread.participants.all())
    participants.remove(message.sender)
    for user in participants:
        r.hincrby(
            "thread_{}_messages".format(message.thread.id),
            "user_{}_unread_msg_count".format(user.username),
            1
        )
