from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('role', 'content', 'status', 'created_at')
    can_delete = True

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_id', 'title', 'created_at', 'updated_at')
    search_fields = ('id', 'client_id', 'title')
    inlines = [MessageInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'status', 'created_at')
    list_filter = ('role', 'status')
    search_fields = ('content', 'conversation__id')
    readonly_fields = ('created_at',)
