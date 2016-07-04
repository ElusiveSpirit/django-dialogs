from django.conf.urls import url
from . import views

app_name = 'dialogs'
urlpatterns = [
    url(r'^send_message/$', views.send_message_view, name='send-message'),
    url(r'^send_message_api/(?P<thread_id>\d+)/$', views.send_message_api_view, name='send-message-api'),
    url(r'^chat/(?P<thread_id>\d+)/$', views.chat_view, name='chat'),
    url(r'^$', views.messages_view, name='messages'),
]
