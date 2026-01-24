# ============================================
# STEP 3: Create Your Own API with FastAPI
# ============================================
#
# WHAT YOU'LL LEARN:
# - How to create an API endpoint
# - How to receive data and send responses
#
# WHY AN API?
# - Other apps can talk to your chatbot
# - You can separate frontend from backend
#
# RUN THIS FILE:
#   python step3_fastapi_backend.py
#
# Then open: http://localhost:8000/docs
# ============================================

from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from groq import Groq
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Create the API
app = FastAPI()

# Connect to Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Connect to Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Define what data we expect to receive
class ChatRequest(BaseModel):
    message: str

# Define what data we'll send back
class ChatResponse(BaseModel):
    reply: str

# Create the /chat endpoint
@app.post("/chat")
def chat(request: ChatRequest):
    # Send message to AI
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": request.message}],
        model="openai/gpt-oss-20b",
    )

    # Get AI's reply
    reply = response.choices[0].message.content
    
    # Save to database
    supabase.table("chat_messages").insert({
        "message": request.message,
        "reply": reply
    }).execute()
    
    # Return AI's reply
    return ChatResponse(reply=reply)

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ============================================
# TRY THIS:
# 1. Run this file
# 2. Open http://localhost:8000/docs
# 3. Click on POST /chat → Try it out
# 4. Enter: {"message": "Hello!"}
# 5. Click Execute and see the AI response!
#
# HOW IT WORKS:
# Someone sends POST request → API receives it → Sends to AI → Returns response
# ============================================
