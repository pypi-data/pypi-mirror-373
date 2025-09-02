import os

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from .settings import SUPPORTAL_SETTINGS


class Business(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Name"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
    )
    owner = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name=_("Owner"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
    )

    class Meta:
        verbose_name = _("Business")
        verbose_name_plural = _("Businesses")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def active_chat_sessions_count(self):
        """Return the count of active chat sessions for this business."""
        return self.chat_sessions.filter(is_active=True).count()


class Document(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("Business"),
    )
    title = models.CharField(
        max_length=255,
    )
    file = models.FileField(
        upload_to="documents/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=SUPPORTAL_SETTINGS["ALLOWED_FILE_TYPES"]
            )
        ],
        help_text=_("Your business documents to help ai answer"),
        verbose_name=_("File"),
    )
    content = models.TextField(
        blank=True,
        verbose_name=_("Content"),
    )
    processed = models.BooleanField(
        default=False,
        verbose_name=_("Processed"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.title

    def trigger_processing(self):
        """Trigger document processing task"""
        from .tasks import process_document_task

        try:
            process_document_task.delay(self.id)
            return True
        except Exception:
            return False

    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


class ChatSession(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
        verbose_name=_("Business"),
    )
    session_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Session ID"),
    )
    customer_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Customer Name"),
    )
    customer_email = models.EmailField(
        blank=True,
        verbose_name=_("Customer Email"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
    )

    def __str__(self) -> str:
        return f"{self.business.name} - {self.session_id}"

    class Meta:
        verbose_name = _("Chat Session")
        verbose_name_plural = _("Chat Sessions")
        ordering = ["created_at"]


class ChatMessage(models.Model):
    class ChatMessageMessageTypesEnum(models.TextChoices):
        USER = "USER", _("User")
        ASSISTANT = "ASSISTANT", _("Assistant")
        SYSTEM = "SYSTEM", _("System")

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("Session"),
    )
    message_type = models.CharField(
        max_length=20,
        choices=ChatMessageMessageTypesEnum.choices,
        verbose_name=_("Message Type"),
    )
    content = models.TextField(
        verbose_name=_("Content"),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Metadata"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )

    def __str__(self) -> str:
        return f"{self.session.session_id} - {self.message_type}: {self.content[:50]}"

    class Meta:
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")
        ordering = ["created_at"]


class VectorChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
        verbose_name=_("Document"),
    )
    chunk_index = models.IntegerField(
        verbose_name=_("Chunk Index"),
    )
    content = models.TextField(
        verbose_name=_("Content"),
    )
    embedding = models.JSONField(
        verbose_name=_("Embedding"),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Metadata"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )

    def __str__(self) -> str:
        return f"{self.document.title} - chunk {self.chunk_index}"

    class Meta:
        verbose_name = _("Vector Chunk")
        verbose_name_plural = _("Vector Chunks")
        constraints = (
            UniqueConstraint(
                name="unique_document_chunk_index",
                fields=[
                    "document",
                    "chunk_index",
                ],
                violation_error_message="A document can not have same chunk indexes",
            ),
        )
