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

from django.shortcuts import render_to_response, get_object_or_404, render, redirect
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
from dialogs.forms import MessageForm, MessageAPIForm
from dialogs.utils import json_response, send_message, get_messages_info
from dialogs.utils import HttpResponseAjaxError, HttpResponseAjax, login_required_ajax


@require_POST
@csrf_exempt
def send_message_api(request):
    form = MessageAPIForm(request.POST)
    if form.is_valid():
        form.save()
        return json_response({"status": "ok"})
    else:
        return json_response({"status": "error"})


@login_required
def messages_view(request):
    if request.POST:
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('dialogs:chat', kwargs={
                'thread_id' : form.get_thread_id()
            }))
    else:
        form = MessageForm()
    threads = Thread.objects.filter(participants=request.user).order_by("-last_message")

    return render(request, 'private_messages.html', {
        "threads": threads,
        'form' : form,
    })


@login_required
def chat_view(request, thread_id):
    thread = get_object_or_404(
        Thread,
        id=thread_id,
        participants__id=request.user.id
    )
    messages_info = get_messages_info(request.user.id, thread_id)
    messages = thread.message_set.order_by("-datetime")[:30]

    tz = request.COOKIES.get("timezone")
    if tz:
        #timezone.activate(tz)
        pass

    return render(request, 'chat.html', {
        "thread": thread,
        "thread_messages": messages,
        "messages_total": messages_info['total'],
        "messages_sent": messages_info['sent'],
        "messages_received": messages_info['received'],
    })
