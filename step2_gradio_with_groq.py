# ============================================
# STEP 2: Connect Your Chatbot to AI (GroqCloud)
# ============================================
#
# WHAT YOU'LL LEARN:
# - How to connect to GroqCloud's API
# - How to send messages and get AI responses
#
# BEFORE RUNNING:
# 1. Get your free API key from: https://console.groq.com
# 2. Set it in your terminal:
#    export GROQ_API_KEY=your_key_here
#
# RUN THIS FILE:
#   python step2_gradio_with_groq.py
# ============================================

import gradio as gr
import os
from dotenv import load_dotenv
from groq import Groq
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Connect to Groq using your API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Connect to Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def respond(message, history):
    # Build the conversation history for the AI
    messages = []

    # Add all previous messages
    for msg in history:
        messages.append(msg)

    # Add the new message from user
    messages.append({"role": "user", "content": message})

    # Send to AI and get response
    response = client.chat.completions.create(
        messages=messages,
        model="openai/gpt-oss-20b",
    )

    # Get the AI's reply
    reply = response.choices[0].message.content
    
    # Save to database
    supabase.table("chat_messages").insert({
        "message": message,
        "reply": reply
    }).execute()
    
    # Return the AI's reply
    return reply

# Create and launch the chat interface
demo = gr.ChatInterface(fn=respond)
demo.launch()
