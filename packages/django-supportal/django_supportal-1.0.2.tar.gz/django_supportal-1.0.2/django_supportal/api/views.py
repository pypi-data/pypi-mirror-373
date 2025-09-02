import logging
import uuid

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..models import Business, ChatSession, Document
from ..tasks import process_document_task
from .serializers import (
    BusinessSerializer,
    ChatMessageSerializer,
    ChatSessionSerializer,
    DocumentSerializer,
)


logger = logging.getLogger("django_supportal")


class BusinessViewSet(ModelViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        """get documents for business"""
        business = self.get_object()
        documents = business.documents.all()
        serializer = DocumentSerializer(
            instance=documents,
            many=True,
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def chat_sessions(self, request, pk=None):
        """get chat sessions for business"""
        business = self.get_object()
        sessions = business.chat_sessions.all()
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )


class DocumentViewSet(ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(business__owner=self.request.user)

    def perform_create(self, serializer):
        business_id = self.request.data.get("business_id")
        try:
            business = Business.objects.get(id=business_id, owner=self.request.user)
            document = serializer.save(business=business)

            # process document asynchronously
            process_document_task.delay(document.id)

        except Business.DoesNotExist:
            raise ValidationError(_("Business not found"))

    def perform_destroy(self, instance):
        # clean up vector data when document is deleted
        from ..services.vector_service import VectorService

        vector_service = VectorService()
        vector_service.delete_document_chunks(instance.business.id, instance.id)
        instance.delete()


class ChatSessionViewSet(ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(business__owner=self.request.user)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """get messages for chat session"""
        session = self.get_object()
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(
            data=serializer.data,
            status=200,
        )

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """close chat session"""
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response(
            data={
                "status": _("Session closed"),
            },
            status=status.Ok,
        )


@csrf_exempt
def create_chat_session(request, business_id):
    """create new chat session for customer"""
    if request.method == "POST":
        try:
            business = get_object_or_404(
                Business,
                id=business_id,
                is_active=True,
            )

            session_id = str(uuid.uuid4())
            customer_name = request.POST.get("customer_name", "")
            customer_email = request.POST.get("customer_email", "")

            ChatSession.objects.create(
                business=business,
                session_id=session_id,
                customer_name=customer_name,
                customer_email=customer_email,
            )

            return JsonResponse(
                data={
                    "session_id": session_id,
                    "business_name": business.name,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"error creating chat session: {e!s}")
            return JsonResponse(
                data={"error": _("Failed to create chat session")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return JsonResponse(
        data={
            "error": _("Method not allowed"),
        },
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


def chat_interface(request, business_id, session_id):
    """render chat interface"""
    business = get_object_or_404(
        Business,
        id=business_id,
        is_active=True,
    )
    session = get_object_or_404(
        ChatSession,
        business=business,
        session_id=session_id,
    )

    context = {
        "business": business,
        "session": session,
        "websocket_url": f"ws/chat/{business_id}/{session_id}/",
    }

    return render(
        request=request,
        template_name="django_supportal/chat.html",
        context=context,
    )


@login_required
def admin_dashboard(request):
    """admin dashboard for business owners"""
    businesses = Business.objects.filter(owner=request.user)

    context = {
        "businesses": businesses,
    }

    return render(
        request=request,
        template_name="django_supportal/admin_dashboard.html",
        context=context,
    )


def health_check(request):
    """health check endpoint"""
    return JsonResponse(
        data={
            "status": "healthy",
        },
        status=status.HTTP_200_OK,
    )
