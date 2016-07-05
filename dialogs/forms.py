from django import forms

from django.conf import settings
from django.contrib.auth.models import User
from dialogs.models import Message, Thread
from dialogs.utils import send_message


class MessageForm(forms.Form):
    recipient_name = forms.CharField(max_length=300,
        widget=forms.TextInput(attrs={'placeholder': 'Пользователи'}))
    message_text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Сообщение'}), max_length=10000)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MessageForm, self).__init__(*args, **kwargs)

    def clean_recipient_name(self):
        names = self.cleaned_data["recipient_name"]
        names = names.replace(" ", "")
        names = names.split(',')
        recipient_list = []
        except_list = []
        for name in names:
            try:
                recipient_list.append(User.objects.get(username=name))
            except User.DoesNotExist:
                except_list.append(name)
        if len(except_list) > 0:
            raise forms.ValidationrError(u"Next user's are not exist: {}.".format(", ".join(except_list)))

        if self.user in recipient_list:
            raise forms.ValidationrError("You cannot send messages to yourself.")
        return recipient_list

    def get_thread_id(self):
        return self.thread.id

    def save(self):
        recipient_list = self.cleaned_data['recipient_name']
        thread_queryset = Thread.objects.filter(
            participants=self.user
        )

        for recipient in recipient_list:
            thread_queryset = thread_queryset.filter(
                participants=recipient
            )

        if thread_queryset.exists():
            self.thread = thread_queryset[0]
        else:
            self.thread = Thread.objects.create()
            recipient_list.append(self.user)
            print(recipient_list)
            for recipient in recipient_list:
                self.thread.participants.add(recipient)

        send_message(
            self.thread.id,
            self.user.id,
            self.cleaned_data['message_text'],
            self.user.username,
            True
        )

class MessageAPIForm(forms.Form):
    api_key = forms.CharField(max_length=150)
    thread_id = forms.IntegerField()
    sender_id = forms.IntegerField()
    message_text = forms.CharField(max_length=10000)
    message_status = forms.BooleanField(initial=False, required=False)

    def clean_api_key(self):
        if self.cleaned_data['api_key'] != settings.API_KEY:
            raise forms.ValidationrError("Wrong api key")

    def clean_thread_id(self):
        try:
            thread = Thread.objects.get(id=self.cleaned_data['thread_id'])
        except Thread.DoesNotExist:
            raise forms.ValidationrError("No such thread")
        return thread.id

    def clean_sender_id(self):
        try:
            sender = User.objects.get(id=self.cleaned_data['sender_id'])
        except User.DoesNotExist:
            raise forms.ValidationrError("No such user")
        self.username = sender.username
        return sender.id

    def save(self):
        send_message(
            self.cleaned_data['thread_id'],
            self.cleaned_data['sender_id'],
            self.cleaned_data['message_text'],
            self.username,
            True
        )

    def update_status(self):
        pass
