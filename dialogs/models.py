from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User


class Thread(models.Model):
    participants = models.ManyToManyField(User)
    last_message = models.DateTimeField(null=True, blank=True, db_index=True)

    def get_participants(self):
        return ", ".join(self.participants)

    def get_participants_exclude_author(self, user):
        ret = []
        participants = self.participants.exclude(id=user.id)
        for participant in participants:
            ret.append(participant.username)
        return ", ".join(ret)

class Message(models.Model):
    text = models.TextField()
    sender = models.ForeignKey(User)
    thread = models.ForeignKey(Thread)
    datetime = models.DateTimeField(auto_now_add=True, db_index=True)


def update_last_message_datetime(sender, instance, created, **kwargs):
    """
    Update Thread's last_message field when
    a new message is sent.
    """
    if not created:
        return

    Thread.objects.filter(id=instance.thread.id).update(
        last_message=instance.datetime
    )

post_save.connect(update_last_message_datetime, sender=Message)
