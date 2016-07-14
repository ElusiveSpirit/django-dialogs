"""Django models."""
import redis

from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User

r = redis.StrictRedis()


class Thread(models.Model):
    """Thread model that actual is a dialog."""

    name = models.TextField(blank=True)
    participants = models.ManyToManyField(User)
    last_message = models.DateTimeField(null=True, blank=True, db_index=True)

    def get_participants_list_usernames(self):
        ret = []
        participants = self.participants.all()[:]
        for participant in participants:
            ret.append(participant.username)
        return ret

    def get_name_for_current_user(self, user):
        if self.name:
            return self.name
        participant_list = self.get_participants_list_usernames()
        participant_list.remove(user.username)
        return ", ".join(participant_list)

    def get_total_messages(self):
        """
        Code to peek up info from redis.

        return r.hget(
            "thread_{}_messages".format(str(self.pk)),
            "total_messages"
        )
        """
        return self.message_set.count()

    def get_user_unread_messages(self, user):
        return self.message_set.filter(has_read=False).exclude(sender=user)

    def get_unread_messages_count(self):
        return self.message_set.filter(has_read=False).count()

    def get_user_unread_messages_count(self, user):
        if self.participants.count() == 2:
            return self.message_set.filter(
                has_read=False
            ).exclude(sender=user).count()
        else:
            count = r.hget(
                "thread_{}_messages".format(str(self.pk)),
                "user_{}_unread_msg_count".format(user.username)
            )
            if count is None:
                r.hset(
                    "thread_{}_messages".format(str(self.pk)),
                    "user_{}_unread_msg_count".format(user.username),
                    0
                )
                count = self.get_unread_messages_count()
            else:
                count = int(count)
            return count

    def __str__(self):
        """Returns string list with all participants"""
        if self.name:
            return self.name
        return ", ".join(self.get_participants_list_usernames())


class Message(models.Model):
    text = models.TextField()
    sender = models.ForeignKey(User)
    thread = models.ForeignKey(Thread)
    datetime = models.DateTimeField(auto_now_add=True, db_index=True)
    has_read = models.BooleanField(default=False)


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
