# API Foundations Tutorial - Progressive Implementation

This tutorial builds a complete AI chat system in 4 progressive steps:

## Prerequisites

1. **Python 3.8+** installed
2. **Groq API Key** - Get yours at [console.groq.com](https://console.groq.com)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Export API Key via CLI:

```bash
export GROQ_API_KEY=your_api_key_here
```

---

## Step 1: Simple Gradio Chat Interface

**File:** `step1_simple_chat.py`

A basic chat interface that echoes your messages (no AI).

**Run:**
```bash
python step1_simple_chat.py
```

**What you'll see:**
- A chat interface opens in your browser
- Type a message → it echoes back "You said: [your message]"

**Learning:**
- Basic Gradio ChatInterface setup
- Understanding the `respond(message, history)` function signature

---

## Step 2: Connect Gradio to Groq API

**File:** `step2_gradio_with_groq.py`

Gradio interface directly connected to Groq LLM.

**Architecture:**
```
User → Gradio → Groq API → Response
```

**Run:**
```bash
python step2_gradio_with_groq.py
```

**What you'll see:**
- Chat interface with real AI responses
- Using Groq's llama-3.3-70b-versatile model
- Conversation history is maintained

**Learning:**
- Using the Groq Python SDK
- Building message history for context
- Direct API integration in frontend

---

## Step 3: Create FastAPI Backend

**File:** `step3_fastapi_backend.py`

A standalone API server that handles chat requests.

**Run:**
```bash
python step3_fastapi_backend.py
```

Or using uvicorn directly:
```bash
uvicorn step3_fastapi_backend:app --reload
```

**Test the API:**

1. **Open API docs:** http://localhost:8000/docs

2. **Test with curl:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain APIs in one sentence",
    "history": []
  }'
```

**Endpoints:**
- `GET /` - Welcome message
- `POST /chat` - Send message, get AI response

**Learning:**
- FastAPI app structure
- Pydantic models for request/response validation
- Creating REST endpoints
- API documentation with Swagger UI

---

## Step 4: Complete System (Gradio Frontend + FastAPI Backend)

**File:** `step4_gradio_frontend.py`

Gradio frontend that communicates with FastAPI backend.

**Architecture:**
```
User → Gradio → FastAPI → Groq API → Response
```

**Run (requires 2 terminals):**

**Terminal 1 - Start Backend:**
```bash
python step3_fastapi_backend.py
```

**Terminal 2 - Start Frontend:**
```bash
python step4_gradio_frontend.py
```

**What you'll see:**
- Gradio chat interface
- Messages go through your FastAPI backend
- Backend handles all AI communication

**Learning:**
- Separation of frontend and backend
- Making HTTP requests from Gradio
- Error handling for API calls
- Converting between different message formats

---

## Architecture Comparison

### Step 2 (Direct):
```
┌──────────┐
│  Gradio  │
└────┬─────┘
     │
     ▼
┌──────────┐
│ Groq API │
└──────────┘
```

### Step 4 (API Architecture):
```
┌──────────┐      ┌─────────┐      ┌──────────┐
│  Gradio  │─────→│ FastAPI │─────→│ Groq API │
│ Frontend │      │ Backend │      └──────────┘
└──────────┘      └─────────┘
```

---

## Key Concepts

### 1. **Progressive Enhancement**
- Start simple (echo bot)
- Add AI (direct connection)
- Add structure (API layer)
- Final: Production-ready architecture

### 2. **Separation of Concerns**
- **Frontend (Gradio):** User interface
- **Backend (FastAPI):** Business logic, API calls
- **External API (Groq):** AI processing

### 3. **Why Use FastAPI as Middleware?**

**Benefits:**
- ✅ Multiple frontends can use one backend
- ✅ Backend can switch AI providers without changing frontend
- ✅ Add authentication, rate limiting, logging in one place
- ✅ Teams can work independently (frontend/backend)
- ✅ Can cache responses, add queuing, etc.

**When Direct Connection (Step 2) is OK:**
- Small personal projects
- Prototypes/demos
- No need for multi-client support

---

## Troubleshooting

### "Cannot connect to backend API"
- Make sure FastAPI server is running (`python step3_fastapi_backend.py`)
- Check it's running on port 8000: http://localhost:8000
- Verify both terminals are running for Step 4

### "API Key Error"
- Ensure `.env` file exists with `GROQ_API_KEY=...`
- Or export the environment variable
- Restart your script after adding the key

### "Module not found"
- Run `pip install -r requirements.txt`
- Make sure you're in the correct directory

---

## Next Steps

1. **Add streaming responses** - See Groq's streaming API
2. **Add database** - Save conversation history
3. **Add authentication** - Protect your API
4. **Add multiple models** - Let users choose AI models
5. **Deploy** - Put it on a server (Heroku, Railway, etc.)

---

## File Overview

```
.
├── step1_simple_chat.py          # Basic Gradio (no AI)
├── step2_gradio_with_groq.py     # Gradio + Groq (direct)
├── step3_fastapi_backend.py      # FastAPI backend only
├── step4_gradio_frontend.py      # Gradio → FastAPI
├── requirements.txt              # Dependencies
├── .env                          # API keys (create this)
└── TUTORIAL.md                   # This file
```

---

## Learning Path

1. **Run Step 1** → Understand Gradio basics
2. **Run Step 2** → See AI integration
3. **Run Step 3** → Test API with docs/curl
4. **Run Step 4** → See complete architecture

**Time estimate:** 30-60 minutes total

---

## Code Highlights

### Gradio ChatInterface Signature

```python
def respond(message, history):
    # message: str - current user message
    # history: list - previous messages [{"role": "user/assistant", "content": "..."}]
    return "response string"
```

### FastAPI Request/Response Models

```python
class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    reply: str
```

### Groq API Call

```python
chat_completion = client.chat.completions.create(
    messages=messages,
    model="llama-3.3-70b-versatile",
)
response = chat_completion.choices[0].message.content
```

---

## Questions?

- Gradio docs: https://gradio.app
- FastAPI docs: https://fastapi.tiangolo.com
- Groq docs: https://console.groq.com/docs

**Happy coding! 🚀**
