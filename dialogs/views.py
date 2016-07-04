"""
from django.shortcuts import render

from dialogs.forms import SendMessageForm
from dialogs.utils import HttpResponseAjaxError, HttpResponseAjax, login_required_ajax

@login_required_ajax
def send_message_api(request):
    form = SendMessageForm(request.POST)
    if form.is_valid():
        form.send_message()
        return HttpResponseAjax(status='ok')
    else:
        return HttpResponseAjaxError(
            code = 'send_message_error',
            message = form.errors,
        )
"""
import json

import redis

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from dialogs.models import Thread, Message
from dialogs.utils import json_response, send_message

@login_required
def send_message_view(request):
    if not request.method == "POST":
        return HttpResponse("Please use POST.")

    message_text = request.POST.get("message")

    if not message_text:
        return HttpResponse("No message found.")

    if len(message_text) > 10000:
        return HttpResponse("The message is too long.")

    recipient_names = request.POST.get("recipient_name")
    recipient_names = recipient_names.replace(" ", "")
    recipient_names = recipient_names.split(',')
    recipient_list = []
    try:
        for name in recipient_names:
            recipient_list.append(User.objects.get(username=name))
    except User.DoesNotExist:
        return HttpResponse("No such user.")

    if request.user in recipient_list:
        return HttpResponse("You cannot send messages to yourself.")

    thread_queryset = Thread.objects.filter(
        participants=request.user
    )

    for recipient in recipient_list:
        thread_queryset = thread_queryset.filter(
            participants=recipient
        )

    if thread_queryset.exists():
        thread = thread_queryset[0]
    else:
        thread = Thread.objects.create()
        recipient_list.append(request.user)
        for recipient in recipient_list:
            thread.participants.add(recipient)

    send_message(
        thread.id,
        request.user.id,
        message_text,
        request.user.username,
        True
    )

    return HttpResponseRedirect(
        reverse('dialogs:messages')
    )


@csrf_exempt
def send_message_api_view(request, thread_id):
    if not request.method == "POST":
        return json_response({"error": "Please use POST."})

    api_key = request.POST.get("api_key")

    if api_key != settings.API_KEY:
        return json_response({"error": "Please pass a correct API key."})

    try:
        thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist:
        return json_response({"error": "No such thread."})

    try:
        sender = User.objects.get(id=request.POST.get("sender_id"))
    except User.DoesNotExist:
        return json_response({"error": "No such user."})

    message_text = request.POST.get("message")

    if not message_text:
        return json_response({"error": "No message found."})

    if len(message_text) > 10000:
        return json_response({"error": "The message is too long."})

    send_message(
        thread.id,
        sender.id,
        message_text,
        sender.username
    )

    return json_response({"status": "ok"})


@login_required
def messages_view(request):
    threads = Thread.objects.filter(
        participants=request.user
    ).order_by("-last_message")

    if not threads:
        return render_to_response('private_messages.html',
                                  {},
                                  context_instance=RequestContext(request))

    r = redis.StrictRedis()

    user_id = str(request.user.id)

    for thread in threads:
        thread.partners = thread.get_participants_exclude_author(request.user)

        thread.total_messages = r.hget(
            "".join(["thread_", str(thread.id), "_messages"]),
            "total_messages"
        )

    return render_to_response('private_messages.html',
                              {
                                  "threads": threads,
                              },
                              context_instance=RequestContext(request))

@login_required
def chat_view(request, thread_id):
    thread = get_object_or_404(
        Thread,
        id=thread_id,
        participants__id=request.user.id
    )

    messages = thread.message_set.order_by("-datetime")[:100]

    user_id = str(request.user.id)

    r = redis.StrictRedis()

    messages_total = r.hget(
        "".join(["thread_", thread_id, "_messages"]),
        "total_messages"
    )

    messages_sent = r.hget(
        "".join(["thread_", thread_id, "_messages"]),
        "".join(["from_", user_id])
    )

    if messages_total:
        messages_total = int(messages_total)
    else:
        messages_total = 0

    if messages_sent:
        messages_sent = int(messages_sent)
    else:
        messages_sent = 0

    messages_received = messages_total-messages_sent

    partners = thread.get_participants_exclude_author(request.user)

    tz = request.COOKIES.get("timezone")
    if tz:
        #timezone.activate(tz)
        pass

    return render_to_response('chat.html',
                              {
                                  "thread_id": thread_id,
                                  "thread_messages": messages,
                                  "messages_total": messages_total,
                                  "messages_sent": messages_sent,
                                  "messages_received": messages_received,
                                  "partners": partners,
                              },
                              context_instance=RequestContext(request))
