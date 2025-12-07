"""Chat URL configuration."""

from django.urls import path
from chat.views import chat_home, chat_api

app_name = 'chat'

urlpatterns = [
    path('', chat_home, name='chat_home'),
    path('api/chat/', chat_api, name='chat_api'),
]
