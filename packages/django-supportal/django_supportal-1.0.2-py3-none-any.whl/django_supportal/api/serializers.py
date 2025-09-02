from rest_framework import serializers

from ..models import Business, ChatMessage, ChatSession, Document


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file",
            "processed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "processed",
            "created_at",
            "updated_at",
        ]

    def validate_file(self, value):
        from ..settings import SUPPORTAL_SETTINGS

        # check file size
        if value.size > SUPPORTAL_SETTINGS["MAX_FILE_SIZE"]:
            raise serializers.ValidationError("file size too large")

        # check file extension
        file_extension = value.name.split(".")[-1].lower()
        if file_extension not in SUPPORTAL_SETTINGS["ALLOWED_FILE_TYPES"]:
            raise serializers.ValidationError(
                f"unsupported file type: {file_extension}"
            )

        return value


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = [
            "id",
            "session_id",
            "customer_name",
            "customer_email",
            "created_at",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "message_type",
            "content",
            "created_at",
            "metadata",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]
