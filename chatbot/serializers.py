import uuid
from rest_framework import serializers
from .models import Conversation, Message

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'client_id', 'title', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatStreamInputSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(min_length=1, max_length=1000, trim_whitespace=True)

    def validate_message(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Message cannot be empty or whitespace only.")
        return stripped
