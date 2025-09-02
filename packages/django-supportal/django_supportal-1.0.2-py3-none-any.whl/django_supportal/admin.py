from django.contrib import admin, messages

from .models import Business, ChatMessage, ChatSession, Document, VectorChunk
from .tasks import process_document_task


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "owner",
        "created_at",
        "is_active",
    ]
    list_filter = [
        "is_active",
        "created_at",
    ]
    search_fields = [
        "name",
        "owner__username",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    actions = ["process_all_documents"]

    def process_all_documents(self, request, queryset):
        """Admin action to process all documents for selected businesses"""
        total_count = 0
        for business in queryset:
            unprocessed_docs = business.documents.filter(processed=False)
            count = 0
            for document in unprocessed_docs:
                try:
                    process_document_task.delay(document.id)
                    count += 1
                except Exception as e:
                    messages.error(
                        request,
                        f"Failed to queue document '{document.title}' for processing: {e!s}",
                    )
            total_count += count

            if count > 0:
                messages.success(
                    request,
                    f"Queued {count} document(s) for processing from business '{business.name}'.",
                )

        if total_count > 0:
            messages.success(
                request,
                f"Successfully queued {total_count} document(s) for processing across all selected businesses.",
            )
        else:
            messages.warning(
                request,
                "No documents were queued for processing (all documents may already be processed).",
            )

    process_all_documents.short_description = (
        "Process all documents for selected businesses"
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "business",
        "processed",
        "created_at",
    ]
    list_filter = [
        "processed",
        "created_at",
        "business",
    ]
    search_fields = [
        "title",
        "business__name",
    ]
    readonly_fields = [
        "processed",
        "created_at",
        "updated_at",
    ]
    actions = ["process_documents", "reprocess_documents"]

    def save_model(self, request, obj, form, change):
        """Override save_model to trigger document processing for new documents"""
        super().save_model(request, obj, form, change)

        # Only trigger processing for new documents (not updates)
        if not change:
            try:
                process_document_task.delay(obj.id)
                messages.success(
                    request, f"Document '{obj.title}' has been queued for processing."
                )
            except Exception as e:
                messages.error(
                    request,
                    f"Failed to queue document '{obj.title}' for processing: {e!s}",
                )

    def process_documents(self, request, queryset):
        """Admin action to process selected documents"""
        count = 0
        for document in queryset:
            if not document.processed:
                try:
                    process_document_task.delay(document.id)
                    count += 1
                except Exception as e:
                    messages.error(
                        request,
                        f"Failed to queue document '{document.title}' for processing: {e!s}",
                    )

        if count > 0:
            messages.success(
                request, f"Successfully queued {count} document(s) for processing."
            )
        else:
            messages.warning(
                request,
                "No documents were queued for processing (all selected documents may already be processed).",
            )

    process_documents.short_description = "Process selected documents"

    def reprocess_documents(self, request, queryset):
        """Admin action to reprocess selected documents"""
        count = 0
        for document in queryset:
            try:
                # Reset processed status
                document.processed = False
                document.save()

                # Queue for processing
                process_document_task.delay(document.id)
                count += 1
            except Exception as e:
                messages.error(
                    request,
                    f"Failed to queue document '{document.title}' for reprocessing: {e!s}",
                )

        if count > 0:
            messages.success(
                request, f"Successfully queued {count} document(s) for reprocessing."
            )

    reprocess_documents.short_description = "Reprocess selected documents"


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = [
        "session_id",
        "business",
        "customer_name",
        "created_at",
        "is_active",
    ]
    list_filter = [
        "is_active",
        "created_at",
        "business",
    ]
    search_fields = [
        "session_id",
        "customer_name",
        "customer_email",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        "session",
        "message_type",
        "content_preview",
        "created_at",
    ]
    list_filter = [
        "message_type",
        "created_at",
    ]
    search_fields = [
        "content",
        "session__session_id",
    ]
    readonly_fields = [
        "created_at",
    ]

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "content"


@admin.register(VectorChunk)
class VectorChunkAdmin(admin.ModelAdmin):
    list_display = [
        "document",
        "chunk_index",
        "content_preview",
        "created_at",
    ]
    list_filter = [
        "created_at",
        "document__business",
    ]
    search_fields = [
        "content",
        "document__title",
    ]
    readonly_fields = [
        "created_at",
    ]

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "content"


# Global admin actions
@admin.action(description="Reprocess all documents")
def reprocess_all_documents(modeladmin, request, queryset):
    """Global admin action to reprocess all documents"""
    from .models import Document

    all_documents = Document.objects.all()
    count = 0

    for document in all_documents:
        try:
            # Reset processed status
            document.processed = False
            document.save()

            # Queue for processing
            process_document_task.delay(document.id)
            count += 1
        except Exception as e:
            messages.error(
                request,
                f"Failed to queue document '{document.title}' for reprocessing: {e!s}",
            )

    if count > 0:
        messages.success(
            request, f"Successfully queued {count} document(s) for reprocessing."
        )
    else:
        messages.warning(request, "No documents were queued for reprocessing.")


# Register global actions
admin.site.add_action(reprocess_all_documents)
