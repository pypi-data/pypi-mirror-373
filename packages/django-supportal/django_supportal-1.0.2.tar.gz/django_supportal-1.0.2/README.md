# 🧠 Django Supportal – AI-Powered Business Support Chat APIs for django projects

**Django Supportal** is an intelligent, AI-powered customer support system built with **Django**, **Django Channels**, and **OpenAI API**.  
It provides APIs for businesses to upload their internal documents, and a smart assistant will handle customer inquiries via live chat – powered by a Retrieval-Augmented Generation (RAG) system.

---

## Contribution

I'd be really happy to see you join the development of this project!
Whether it's sharing ideas, reporting bugs, or writing some code — your contributions are truly appreciated ❤️

---

## 🚀 Features

- ✅ Real-time chat via **Django Channels (WebSockets)**
- 📎 Businesses can upload **PDF, DOCX, or TXT documents**
- 🤖 Uses **OpenAI GPT models** to provide intelligent responses
- 📚 Implements **RAG (Retrieval-Augmented Generation)** to process custom business knowledge
- 🔒 Secured communication and Redis-based event layer

---

## 🧠 How it Works (RAG Architecture)

Supportal uses a **Retrieval-Augmented Generation (RAG)** approach to enable AI to answer business-specific questions:

1. **Document Upload:**  
   Businesses upload documents such as FAQs, product guides, manuals, or policies.

2. **Chunking & Embedding:**  
   Uploaded documents are:
   - Split into smaller text chunks
   - Converted into **vector embeddings** using OpenAI's `text-embedding` models

3. **Vector Storage:**  
   Embeddings are stored in a **vector database** (like FAISS) for fast similarity search.

4. **Chat Inference:**
   - When a customer sends a message, it's embedded and compared against stored chunks.
   - The most relevant chunks are selected as **context**.
   - The context is fed into OpenAI's **chat completion API** along with the user's question.
   - A tailored, relevant answer is generated based on actual business documents.

> This allows Supportal to **answer domain-specific questions accurately**, beyond what a generic AI model can do.

---

## 🛠️ Tech Stack

- **Backend:** Django + Django Channels
- **Realtime Layer:** Redis (via `channels_redis`)
- **AI Engine:** OpenAI API (GPT + Embeddings)
- **Vector DB:** FAISS (in-memory vector search)

---

## 📦 Getting Started

### 🔧 Prerequisites

- Django
- Channels
- Celery
- Redis
- OpenAI API key

### 🧪 Installation

#### 1. Install the package

```bash
pip install django-supportal
```

#### 2. Add to your Django project

Add `django_supportal` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_supportal',
    'channels',
    'rest_framework',
]
```

#### 3. Include URLs in your main `urls.py`

```python
from django.urls import path, include

urlpatterns = [
    # ... your other URL patterns
    path('supportal/', include('django_supportal.urls')),
]
```

#### 4. Configure settings

Add the following configuration to your `settings.py`:

```python
# Supportal Configuration
SUPPORTAL_SETTINGS = {
    "OPENAI_API_KEY": "your-openai-api-key-here",
    "OPENAI_MODEL": "gpt-3.5-turbo",  # or "gpt-4"
    "OPENAI_EMBEDDING_MODEL": "text-embedding-ada-002",
    "MAX_TOKENS": 1000,
    "TEMPERATURE": 0.7,
    "CHUNK_SIZE": 1000,
    "CHUNK_OVERLAP": 200,
    "TOP_K_RESULTS": 5,
    "VECTOR_DB_PATH": "vector_db/",
    "ALLOWED_FILE_TYPES": ["pdf", "docx", "txt"],
    "MAX_FILE_SIZE": 10 * 1024 * 1024,  # 10MB
    "REDIS_URL": "redis://localhost:6379/0",
    "CELERY_BROKER_URL": "redis://localhost:6379/0",
    "ENABLE_LOGGING": True,
    "LOG_LEVEL": "INFO",
}

# Channel Layers (for WebSocket support)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Celery Configuration
CELERY_BROKER_URL = SUPPORTAL_SETTINGS["CELERY_BROKER_URL"]
CELERY_RESULT_BACKEND = SUPPORTAL_SETTINGS["CELERY_BROKER_URL"]
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
```

#### 5. Configure WebSocket Routes

**This is a crucial step for real-time chat functionality!** You need to configure your ASGI application to handle WebSocket connections.

Create or update your project's `asgi.py` file:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

# Import your main URLs and Supportal WebSocket routes
from django_supportal.websocket.ws_routes import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

# Get the Django ASGI application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
```

**Alternative: Include WebSocket routes in your main routing**

If you have other WebSocket consumers, you can combine them:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

# Import your main URLs and Supportal WebSocket routes
from django_supportal.websocket.ws_routes import websocket_urlpatterns

# Your custom WebSocket routes (if any)
custom_websocket_urlpatterns = [
    # Add your custom WebSocket routes here
    # re_path(r"ws/custom/$", YourCustomConsumer.as_asgi()),
]

# Combine all WebSocket routes
all_websocket_urlpatterns = websocket_urlpatterns + custom_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            all_websocket_urlpatterns
        )
    ),
})
```

#### 6. Update your `settings.py` for ASGI

Make sure your Django settings include the ASGI application:

```python
# Add this to your settings.py
ASGI_APPLICATION = "your_project.asgi.application"
```

#### 7. Run migrations

```bash
python manage.py migrate
```

#### 8. Start required services

Make sure you have Redis running:

```bash
# Install Redis (if not already installed)
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server

# Start Redis
redis-server
```

#### 9. Start Celery worker (in a separate terminal)

```bash
celery -A your_project_name worker --loglevel=info
```

#### 10. Run your Django server with ASGI

```bash
# For development with ASGI support
python -m uvicorn your_project.asgi:application --reload

# Or using Daphne
daphne your_project.asgi:application

# Or using the standard Django server (limited WebSocket support)
python manage.py runserver
```

### 🔌 WebSocket Connection Details

Once configured, your WebSocket endpoint will be available at:

```
ws://your-domain/ws/chat/{business_id}/{session_id}/
```

**Parameters:**
- `business_id`: The ID of the business (integer)
- `session_id`: The chat session identifier (string)

**Example JavaScript connection:**

```javascript
// Connect to WebSocket
const socket = new WebSocket(`ws://localhost:8000/ws/chat/${businessId}/${sessionId}/`);

// Send a message
socket.send(JSON.stringify({
    message: "Hello, I need help with my order",
    type: "user"
}));

// Listen for messages
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Received:', data.message);
    console.log('From:', data.sender);
    console.log('Timestamp:', data.timestamp);
};

// Handle connection events
socket.onopen = function(e) {
    console.log('WebSocket connection established');
};

socket.onclose = function(e) {
    console.log('WebSocket connection closed');
};

socket.onerror = function(e) {
    console.error('WebSocket error:', e);
};
```

**Message Format:**

```javascript
// User message
{
    "message": "Your question here",
    "type": "user"
}

// System message
{
    "message": "System notification",
    "type": "system"
}
```

**Response Format:**

```javascript
{
    "message": "AI response content",
    "sender": "assistant", // or "user", "system"
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 🎯 Available URLs

After installation, the following URLs will be available:

- **Admin Dashboard:** `http://localhost:8000/supportal/admin-dashboard/`
- **API Endpoints:** `http://localhost:8000/supportal/api/`
  - Businesses: `/supportal/api/businesses/`
  - Documents: `/supportal/api/documents/`
  - Chat Sessions: `/supportal/api/chat-sessions/`
- **Chat Interface:** `http://localhost:8000/supportal/chats/{business_id}/{session_id}/`
- **Health Check:** `http://localhost:8000/supportal/health/`
- **WebSocket Endpoint:** `ws://localhost:8000/ws/chat/{business_id}/{session_id}/`

### 🔧 Environment Variables

For production, use environment variables:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export REDIS_URL="redis://your-redis-host:6379/0"
export CELERY_BROKER_URL="redis://your-redis-host:6379/0"
```

### 🚨 Common WebSocket Issues

**1. WebSocket connection fails:**
- Make sure you're using an ASGI server (uvicorn, daphne, or hypercorn)
- Check that your ASGI configuration is correct
- Verify that `CHANNEL_LAYERS` is configured in settings

**2. Messages not being received:**
- Ensure Redis is running and accessible
- Check that the business_id and session_id are valid
- Verify the message format is correct JSON

**3. CORS issues in development:**
- Add CORS headers to your ASGI application
- Use a CORS middleware for WebSocket connections

**4. Production deployment:**
- Use Redis as the channel layer backend instead of InMemoryChannelLayer
- Configure proper SSL/TLS for secure WebSocket connections (wss://)

> 📖 **For detailed WebSocket configuration, see [WEBSOCKET_SETUP.md](./WEBSOCKET_SETUP.md)**

## 📄 License
This project is licensed under the **MIT License** – see the [LICENSE](./LICENSE) file for details.