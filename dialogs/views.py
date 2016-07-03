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
