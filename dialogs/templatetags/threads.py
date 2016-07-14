from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def dialog_name(context, thread):
    return thread.get_name_for_current_user(context['user'])

@register.simple_tag(takes_context=True)
def unread_messages_count(context, thread):
    return thread.get_user_unread_messages_count(context['user'])
