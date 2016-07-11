from django import forms

from django.conf import settings
from django.contrib.auth.models import User
from dialogs.models import Message, Thread
from dialogs.utils import send_message, update_message_status


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
            raise forms.ValidationError(u"Next user's are not exist: {}.".format(", ".join(except_list)))

        if self.user in recipient_list:
            raise forms.ValidationError("You cannot send messages to yourself.")
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
            thread = thread_queryset[0]
        else:
            thread = Thread.objects.create()
            recipient_list.append(self.user)
            print(recipient_list)
            for recipient in recipient_list:
                thread.participants.add(recipient)
            thread.save()

        self.message = Message()
        self.message.text = self.cleaned_data['message_text']
        self.message.thread = thread
        self.message.sender = self.user
        self.message.save()

    def post(self):
        send_message(self.message)

class AbstractMessageAPIForm(forms.Form):
    api_key = forms.CharField(max_length=150)
    thread_id = forms.IntegerField()
    sender_id = forms.IntegerField()

    def clean_api_key(self):
        if self.cleaned_data['api_key'] != settings.API_KEY:
            raise forms.ValidationError("Wrong api key")

    def clean_thread_id(self):
        try:
            self.thread = Thread.objects.get(id=self.cleaned_data['thread_id'])
        except Thread.DoesNotExist:
            raise forms.ValidationError("No such thread")
        return self.thread.id

    def clean_sender_id(self):
        try:
            self.sender = User.objects.get(id=self.cleaned_data['sender_id'])
        except User.DoesNotExist:
            raise forms.ValidationError("No such user")
        self.username = self.sender.username
        return self.sender.id


class UpdateMessageStatusAPIForm(AbstractMessageAPIForm):
    message_id = forms.IntegerField()
    message_status = forms.BooleanField(initial=False, required=False)

    def clean_message_id(self):
        try:
            self.message = Message.objects.get(id=self.cleaned_data['message_id'])
        except Thread.DoesNotExist:
            raise forms.ValidationError("No such message")
        return self.message.id

    def clean(self):
        if (self.sender not in self.thread.participants.all() or
            self.sender == self.message.sender):
            raise forms.ValidationError("Wrong input params")

    def update_status(self):
        self.message.has_read = self.cleaned_data['message_status']
        self.message.save()

    def post(self):
        update_message_status(self.message)



class SendMessageAPIForm(AbstractMessageAPIForm):
    message_text = forms.CharField(max_length=10000)
    message_status = forms.BooleanField(initial=False, required=False)

    def save(self):
        self.message = Message()
        self.message.text = self.cleaned_data['message_text']
        self.message.thread_id = self.cleaned_data['thread_id']
        self.message.sender_id = self.cleaned_data['sender_id']
        self.message.has_read = self.cleaned_data['message_status']
        self.message.save()

    def post(self):
        send_message(self.message)

    def update_status(self):
        pass
