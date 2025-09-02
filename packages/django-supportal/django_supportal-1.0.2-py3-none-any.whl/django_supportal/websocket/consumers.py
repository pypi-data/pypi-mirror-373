import json
import logging

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_supportal.models import Business, ChatMessage, ChatSession
from django_supportal.services.ai_service import AIService
from django_supportal.services.vector_service import VectorService


logger = logging.getLogger("django_supportal")


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business_id = None
        self.session_id = None
        self.room_group_name = None
        self.ai_service = None
        self.vector_service = None

    async def connect(self):
        try:
            self.business_id = self.scope["url_route"]["kwargs"]["business_id"]
            self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
            self.room_group_name = f"chat_{self.business_id}_{self.session_id}"

            # Initialize services
            self.ai_service = AIService()
            self.vector_service = VectorService()

            # join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await sync_to_async(Business.objects.get)(id=self.business_id)
            await sync_to_async(ChatSession.objects.get)(
                session_id=self.session_id, business_id=self.business_id
            )
            await self.accept()

            # Send a welcome message
            await self.send(
                text_data=json.dumps(
                    {
                        "message": f"Connected to chat for business {self.business_id}, session {self.session_id}",
                        "sender": "system",
                    }
                )
            )

        except Exception as e:
            logger.error(f"Error in connect: {e}")
            # Still accept the connection but log the error
            await self.accept()
            await self.send(
                text_data=json.dumps(
                    {"error": f"Connection error: {e!s}", "sender": "system"}
                )
            )

    async def disconnect(self, close_code):
        # leave room group
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data):
        try:
            # Check if text_data is empty or whitespace
            if not text_data or not text_data.strip():
                logger.warning("Received empty or whitespace-only message")
                await self.send(
                    text_data=json.dumps({"error": str(_("Empty message received"))})
                )
                return

            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            message_type = text_data_json.get("type", "user")

            if message_type == "user":
                await self.handle_user_message(message)
            elif message_type == "system":
                await self.handle_system_message(message)

        except json.JSONDecodeError as e:
            logger.error(
                f"JSON decode error in websocket receive: {e!s}, text_data: {text_data}"
            )
            await self.send(
                text_data=json.dumps({"error": str(_("Invalid message format"))})
            )
        except KeyError as e:
            logger.error(f"Missing key in websocket message: {e!s}")
            await self.send(
                text_data=json.dumps(
                    {"error": str(_("Missing required field in message"))}
                )
            )
        except Exception as e:
            logger.error(f"error in websocket receive: {e!s}")
            await self.send(
                text_data=json.dumps({"error": str(_("Failed to process message"))})
            )

    async def handle_user_message(self, message):
        """handle user message and generate ai response"""
        try:
            # Get the session object
            session = await sync_to_async(ChatSession.objects.get)(
                session_id=self.session_id, business_id=self.business_id
            )

            # Save user message to database
            await sync_to_async(ChatMessage.objects.create)(
                session=session,
                message_type=ChatMessage.ChatMessageMessageTypesEnum.USER,
                content=message,
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "message": message,
                        "sender": "user",
                        "timestamp": str(timezone.now()),
                    }
                )
            )

            # Get conversation history for context
            conversation_history = await self.get_conversation_history(session)

            # Get relevant context from vector search
            context = await self.get_relevant_context(message)

            # Generate AI response
            response_message = await self.ai_service.generate_response(
                messages=conversation_history, context=context
            )

            # Save assistant response to database
            await sync_to_async(ChatMessage.objects.create)(
                session=session,
                message_type=ChatMessage.ChatMessageMessageTypesEnum.ASSISTANT,
                content=response_message,
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "message": response_message,
                        "sender": "assistant",
                        "timestamp": str(timezone.now()),
                    }
                )
            )

        except Exception as e:
            logger.error(f"error handling user message: {e!s}")
            await self.send_error_message(
                str(_("sorry, I encountered an error processing your message"))
            )

    async def get_conversation_history(self, session):
        """get conversation history for AI context"""
        try:
            # Get recent messages (last 10 messages to avoid token limits)
            messages = await sync_to_async(list)(
                ChatMessage.objects.filter(session=session)
                .order_by("-created_at")[:10]
                .values("message_type", "content")
            )

            # Convert to OpenAI format and reverse order (oldest first)
            conversation = []
            for msg in reversed(messages):
                # Convert message_type to string to avoid JSON serialization issues
                message_type = str(msg["message_type"])
                if message_type == "USER":
                    conversation.append({"role": "user", "content": msg["content"]})
                elif message_type == "ASSISTANT":
                    conversation.append(
                        {"role": "assistant", "content": msg["content"]}
                    )

            return conversation
        except Exception as e:
            logger.error(f"error getting conversation history: {e!s}")
            return []

    async def get_relevant_context(self, user_message):
        """get relevant context from vector search"""
        try:
            # Generate embedding for user message
            query_embedding = await sync_to_async(self.ai_service.generate_embedding)(
                user_message
            )

            if not query_embedding:
                return ""

            # Search for similar chunks
            similar_chunks = await sync_to_async(
                self.vector_service.search_similar_chunks
            )(
                business_id=self.business_id,
                query_embedding=query_embedding,
                top_k=3,  # Get top 3 most relevant chunks
            )

            # Combine chunks into context
            context = await sync_to_async(self.vector_service.get_context_from_chunks)(
                similar_chunks
            )
            return context

        except Exception as e:
            logger.error(f"error getting relevant context: {e!s}")
            return ""

    async def handle_system_message(self, message):
        """handle system messages"""
        try:
            # Get the session object
            session = await sync_to_async(ChatSession.objects.get)(
                session_id=self.session_id, business_id=self.business_id
            )

            # Save system message to database
            await sync_to_async(ChatMessage.objects.create)(
                session=session,
                message_type=ChatMessage.ChatMessageMessageTypesEnum.SYSTEM,
                content=message,
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "message": f"System message: {message}",
                        "sender": "system",
                        "timestamp": str(timezone.now()),
                    }
                )
            )
        except Exception as e:
            logger.error(f"error handling system message: {e!s}")
            await self.send_error_message(
                str(_("sorry, I encountered an error processing the system message"))
            )

    async def send_error_message(self, error_message):
        """send error message to client"""
        await self.send(
            text_data=json.dumps(
                {
                    "error": error_message,
                    "sender": "system",
                }
            )
        )
