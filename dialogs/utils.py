import json

import redis

from django.http import HttpResponse, HttpResponseRedirect
from django.utils import dateformat

from dialogs.models import Message


class HttpResponseAjax(HttpResponse):
    def __init__(self, status='ok', **kwargs):
        kwargs['status'] = status
        super(HttpResponseAjax, self).__init__(
            content = json.dumps(kwargs),
            content_type = 'application/json',
        )


class HttpResponseAjaxError(HttpResponseAjax):
    def __init__(self, code, message):
        super(HttpResponseAjaxError, self).__init__(
            status = 'error', code = code, message = message
        )


def login_required_ajax(view):
    def view2(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view(request, *args, **kwargs)
        elif request.is_ajax():
            return HttpResponseAjaxError(
                code = "no_auth",
                message = u'Требуется авторизация',
            )
        else:
            redirect('/login/?continue=' + request.get_full_path())
    return view2


def get_messages_info(user_id, thread_id):
    """
    Returns a dict:
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
    This function takes a Python object (a dictionary or a list)
    as an argument and returns an HttpResponse object containing
    the data from the object exported into the JSON format.
    """
    return HttpResponse(json.dumps(obj), content_type="application/json")

def send_message(thread_id,
                 sender_id,
                 message_text,
                 sender_name,
                 pub=False):
    """
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

    print("thread_id")
    print(thread_id)

    message = Message()
    message.text = message_text
    message.thread_id = thread_id
    message.sender_id = sender_id
    message.save()

    thread_id = str(thread_id)
    sender_id = str(sender_id)

    r = redis.StrictRedis()

    if pub:
        r.publish("thread_{}_messages".format(thread_id), json.dumps({
            "timestamp": dateformat.format(message.datetime, 'U'),
            "sender": sender_name,
            "text": message_text,
        }))

    for key in ("total_messages", "from_".format(sender_id)):
        r.hincrby(
            "thread_{}_messages".format(thread_id),
            key,
            1
        )
