from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import os
from groq import Groq

# Initialize FastAPI app
app = FastAPI(title="AI Chat API", description="FastAPI backend for AI chat")

# Initialize Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Request/Response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to AI Chat API",
        "endpoints": {
            "/chat": "POST - Send a message and get AI response",
            "/docs": "GET - API documentation"
        }
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat endpoint that processes messages and returns AI responses

    Args:
        request: ChatRequest containing message and conversation history

    Returns:
        ChatResponse with AI reply
    """
    # Build messages array
    messages = []

    # Add conversation history
    if request.history:
        for msg in request.history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

    # Add current message
    messages.append({
        "role": "user",
        "content": request.message
    })

    # Call Groq API
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
    )

    # Extract response
    ai_reply = chat_completion.choices[0].message.content

    return ChatResponse(reply=ai_reply)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
