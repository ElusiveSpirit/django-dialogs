import pytz

from django.shortcuts import render_to_response, get_object_or_404, render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.models import User

from dialogs.models import Thread, Message

from dialogs.forms import MessageForm, SendMessageAPIForm
from dialogs.forms import UpdateMessageStatusAPIForm

from dialogs.utils import json_response, get_messages_info
from dialogs.utils import clear_users_thread_unread_messages


@require_POST
@csrf_exempt
def send_message_api(request):
    form = SendMessageAPIForm(request.POST)
    if form.is_valid():
        if 'message_status' in form.changed_data:
            form.update_status()
        else:
            form.save()
            form.post()
        return json_response({"status": "ok"})
    else:
        return json_response({"status": "error"})


@require_POST
@csrf_exempt
def update_message_status_api(request):
    form = UpdateMessageStatusAPIForm(request.POST)
    if form.is_valid():
        form.update_status_and_post()
        return json_response({"status": "ok"})
    else:
        return json_response({"status": "error"})


@login_required
def messages_view(request):
    if request.POST:
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            form.post()
            return redirect(reverse('dialogs:chat', kwargs={
                'thread_id': form.get_thread_id()
            }))
    else:
        form = MessageForm()
    thread_list = Thread.objects.filter(
        participants=request.user).order_by("-last_message")

    unread_messages = 0
    for thread in thread_list:
        thread.unread_messages_count = thread.get_user_unread_messages_count(
            request.user)
        unread_messages += thread.unread_messages_count

    return render(request, 'private_messages.html', {
        "thread_list": thread_list,
        'form': form,
        'unread_messages': unread_messages,
    })


@login_required
def chat_view(request, thread_id):
    thread = get_object_or_404(
        Thread,
        id=thread_id,
        participants__id=request.user.id
    )
    messages_info = get_messages_info(request.user.id, thread_id)
    messages = thread.message_set.order_by("-datetime")[:]

    tz = request.COOKIES.get("timezone")
    if tz:
        timezone.activate(pytz.timezone(tz))

    clear_users_thread_unread_messages(thread, request.user)

    return render(request, 'chat.html', {
        "thread": thread,
        "thread_messages": messages,
        "messages_total": messages_info['total'],
        "messages_sent": messages_info['sent'],
        "messages_received": messages_info['received'],
    })
