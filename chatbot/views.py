import json
import uuid
import logging
from django.db import transaction
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, ChatStreamInputSerializer
from .rate_limiter import check_rate_limit
from .retrieval import retrieve_approved_information
from .context import build_conversation_context
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)

def get_validated_client_id(request) -> uuid.UUID:
    client_id_header = request.headers.get('X-Client-ID') or request.META.get('HTTP_X_CLIENT_ID')
    if not client_id_header:
        return None
    try:
        return uuid.UUID(str(client_id_header).strip())
    except (ValueError, TypeError):
        return None


class ChatStreamView(APIView):
    """
    POST /api/v1/chat/stream/
    Streams AI response over Server-Sent Events (SSE).
    Follows FR-024 to FR-030, FR-034, FR-035.
    """
    def post(self, request, *args, **kwargs):
        client_id = get_validated_client_id(request)
        if not client_id:
            return Response(
                {"error": {"code": "INVALID_CLIENT_ID", "message": "A valid UUID X-Client-ID header is required."}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Rate Limiting check (FR-035)
        is_allowed, retry_after = check_rate_limit(str(client_id), request)
        if not is_allowed:
            resp = Response(
                {"error": {"code": "RATE_LIMIT_EXCEEDED", "message": f"Rate limit reached. Please wait {retry_after}s before retrying."}},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
            resp['Retry-After'] = str(retry_after)
            return resp

        # Input Validation (FR-014)
        serializer = ChatStreamInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": {"code": "INVALID_INPUT", "message": serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data
        conversation_id = validated_data.get('conversation_id')
        user_message_text = validated_data['message']

        # Conversation retrieval or creation (FR-017, FR-024)
        with transaction.atomic():
            if conversation_id:
                try:
                    conversation = Conversation.objects.select_for_update().get(id=conversation_id, client_id=client_id)
                except Conversation.DoesNotExist:
                    return Response(
                        {"error": {"code": "NOT_FOUND", "message": "Conversation not found or access denied."}},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                title = user_message_text[:40]
                conversation = Conversation.objects.create(client_id=client_id, title=title)

            # If title is default, update with first message preview
            if conversation.title in ("New Conversation", "Untitled Chat"):
                conversation.title = user_message_text[:40]
                conversation.save(update_fields=['title'])

            # Store user message (FR-018)
            user_msg = Message.objects.create(
                conversation=conversation,
                role='user',
                content=user_message_text,
                status='complete'
            )

            # Create placeholder assistant message record
            assistant_msg = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content='',
                status='incomplete'
            )

        # Knowledge retrieval & context building (FR-022, FR-023, FR-033)
        retrieved_info = retrieve_approved_information(user_message_text)
        context_turns = build_conversation_context(conversation, user_message_text, retrieved_info)

        # Event stream generator
        def event_stream():
            accumulated_chunks = []
            service = GeminiService()
            terminal_event_sent = False

            try:
                for token in service.stream_chat_response(context_turns):
                    accumulated_chunks.append(token)
                    payload = json.dumps({"text": token})
                    yield f"event: token\ndata: {payload}\n\n"

                # Stream completed successfully
                full_content = "".join(accumulated_chunks)
                with transaction.atomic():
                    assistant_msg.content = full_content
                    assistant_msg.status = 'complete'
                    assistant_msg.save(update_fields=['content', 'status'])
                    conversation.save(update_fields=['updated_at'])

                done_payload = json.dumps({
                    "conversation_id": str(conversation.id),
                    "message_id": assistant_msg.id
                })
                terminal_event_sent = True
                yield f"event: done\ndata: {done_payload}\n\n"

            except (GeneratorExit, BrokenPipeError, ConnectionResetError):
                # Client disconnected or aborted request (FR-030)
                logger.info("Client disconnected from SSE stream.")
                full_content = "".join(accumulated_chunks)
                with transaction.atomic():
                    if full_content:
                        assistant_msg.content = full_content
                        assistant_msg.status = 'incomplete'
                        assistant_msg.save(update_fields=['content', 'status'])
                    else:
                        # Clean up empty assistant record if aborted before first token
                        assistant_msg.delete()
                return

            except Exception as e:
                # Genuine server or external API failure
                logger.error(f"Streaming error in chat: {type(e).__name__}: {e}")
                full_content = "".join(accumulated_chunks)
                with transaction.atomic():
                    if full_content:
                        assistant_msg.content = full_content
                        assistant_msg.status = 'incomplete'
                    else:
                        assistant_msg.content = "KAI is temporarily unavailable. Please retry."
                        assistant_msg.status = 'error'
                    assistant_msg.save(update_fields=['content', 'status'])

                if not terminal_event_sent:
                    error_payload = json.dumps({
                        "code": "SERVICE_UNAVAILABLE",
                        "message": "KAI is temporarily unavailable. Please retry."
                    })
                    yield f"event: error\ndata: {error_payload}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class ConversationListView(APIView):
    """
    GET /api/v1/conversations/
    List all conversations belonging to the client (X-Client-ID), ordered by -updated_at.
    FR-019, FR-024.
    """
    def get(self, request, *args, **kwargs):
        client_id = get_validated_client_id(request)
        if not client_id:
            return Response(
                {"error": {"code": "INVALID_CLIENT_ID", "message": "Valid UUID X-Client-ID header required."}},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversations = Conversation.objects.filter(client_id=client_id).order_by('-updated_at')
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConversationMessagesView(APIView):
    """
    GET /api/v1/conversations/{id}/messages/
    Load messages in chronological order; 404 if not owned by client.
    FR-020, FR-024.
    """
    def get(self, request, id, *args, **kwargs):
        client_id = get_validated_client_id(request)
        if not client_id:
            return Response(
                {"error": {"code": "INVALID_CLIENT_ID", "message": "Valid UUID X-Client-ID header required."}},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = get_object_or_404(Conversation, id=id, client_id=client_id)
        messages = conversation.messages.all().order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConversationDetailView(APIView):
    """
    DELETE /api/v1/conversations/{id}/
    Deletes conversation and cascades to its messages; returns 204.
    FR-021, NFR-010.
    """
    def delete(self, request, id, *args, **kwargs):
        client_id = get_validated_client_id(request)
        if not client_id:
            return Response(
                {"error": {"code": "INVALID_CLIENT_ID", "message": "Valid UUID X-Client-ID header required."}},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = get_object_or_404(Conversation, id=id, client_id=client_id)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConversationClearView(APIView):
    """
    POST /api/v1/conversations/{id}/clear/
    Removes all messages, keeps the conversation record; returns 204.
    FR-021.
    """
    def post(self, request, id, *args, **kwargs):
        client_id = get_validated_client_id(request)
        if not client_id:
            return Response(
                {"error": {"code": "INVALID_CLIENT_ID", "message": "Valid UUID X-Client-ID header required."}},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = get_object_or_404(Conversation, id=id, client_id=client_id)
        conversation.messages.all().delete()
        conversation.save(update_fields=['updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)
