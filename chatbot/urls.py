from django.urls import path
from .views import (
    ChatStreamView,
    ConversationListView,
    ConversationMessagesView,
    ConversationDetailView,
    ConversationClearView,
)

urlpatterns = [
    path('chat/stream/', ChatStreamView.as_view(), name='chat-stream'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:id>/messages/', ConversationMessagesView.as_view(), name='conversation-messages'),
    path('conversations/<uuid:id>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:id>/clear/', ConversationClearView.as_view(), name='conversation-clear'),
]
