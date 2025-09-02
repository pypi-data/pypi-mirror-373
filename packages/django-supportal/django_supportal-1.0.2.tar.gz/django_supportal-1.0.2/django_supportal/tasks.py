import logging

from celery import shared_task

from .models import Document, VectorChunk
from .services.ai_service import AIService
from .services.document_processor import DocumentProcessor
from .services.vector_service import VectorService


logger = logging.getLogger("django_supportal")


@shared_task
def process_document_task(document_id: int):
    """process uploaded document and create vector embeddings"""
    try:
        logger.info(f"Starting to process document {document_id}")
        document = Document.objects.get(id=document_id)
        logger.info(
            f"Found document: {document.title} for business {document.business.id}"
        )

        # Check if document is already processed
        if document.processed:
            logger.info(f"Document {document_id} is already processed, skipping")
            return

        # extract text from document
        processor = DocumentProcessor()
        file_extension = document.file.name.split(".")[-1].lower()
        logger.info(f"Extracting text from {file_extension} file: {document.file.path}")
        text = processor.extract_text(document.file.path, file_extension)

        if not text:
            logger.error(f"no text extracted from document {document_id}")
            return

        logger.info(f"Extracted {len(text)} characters from document {document_id}")

        # preprocess and chunk text
        preprocessed_text = processor.preprocess_text(text)
        chunks = processor.chunk_text(preprocessed_text)
        logger.info(f"Created {len(chunks)} chunks from document {document_id}")

        # generate embeddings
        ai_service = AIService()
        chunks_data = []

        for chunk_text, chunk_index in chunks:
            logger.info(
                f"Generating embedding for chunk {chunk_index} of document {document_id}"
            )
            embedding = ai_service.generate_embedding(chunk_text)
            if embedding:
                chunks_data.append(
                    {
                        "content": chunk_text,
                        "chunk_index": chunk_index,
                        "embedding": embedding,
                    }
                )
            else:
                logger.warning(f"Failed to generate embedding for chunk {chunk_index}")

        logger.info(
            f"Generated {len(chunks_data)} embeddings for document {document_id}"
        )

        # Clear existing chunks for this document
        VectorChunk.objects.filter(document=document).delete()
        logger.info(f"Cleared existing chunks for document {document_id}")

        # save chunks to database
        for chunk_data in chunks_data:
            VectorChunk.objects.create(
                document=document,
                chunk_index=chunk_data["chunk_index"],
                content=chunk_data["content"],
                embedding=chunk_data["embedding"],
            )

        logger.info(
            f"Saved {len(chunks_data)} chunks to database for document {document_id}"
        )

        # add to vector index
        vector_service = VectorService()
        logger.info(f"Created vector service instance for document {document_id}")

        # Test the vector service
        vector_service.create_index(document.business.id)
        logger.info(
            f"Index initialized for business {document.business.id}, ntotal: {vector_service.index.ntotal if vector_service.index else 'None'}"
        )

        vector_service.add_document_chunks(document, chunks_data)

        # mark document as processed
        document.content = preprocessed_text
        document.processed = True
        document.save()

        logger.info(
            f"successfully processed document {document_id} with {len(chunks_data)} chunks"
        )

    except Document.DoesNotExist:
        logger.error(f"document {document_id} not found")
    except Exception as e:
        logger.error(f"error processing document {document_id}: {e!s}")
        # Try to get the document to mark it as failed
        try:
            document = Document.objects.get(id=document_id)
            document.processed = False
            document.save()
        except:
            pass


@shared_task
def cleanup_old_chat_sessions():
    """clean up old inactive chat sessions"""
    from datetime import datetime, timedelta

    from .models import ChatSession

    try:
        # remove sessions older than 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        old_sessions = ChatSession.objects.filter(
            created_at__lt=cutoff_date, is_active=False
        )

        count = old_sessions.count()
        old_sessions.delete()

        logger.info(f"cleaned up {count} old chat sessions")

    except Exception as e:
        logger.error(f"error cleaning up old chat sessions: {e!s}")
