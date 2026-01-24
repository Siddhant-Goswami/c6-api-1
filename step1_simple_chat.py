# ============================================
# STEP 1: Your First Chatbot with Gradio
# ============================================
#
# WHAT YOU'LL LEARN:
# - How to create a chat interface with Gradio
# - How the respond() function works
#
# RUN THIS FILE:
#   python step1_simple_chat.py
#
# Then open: http://127.0.0.1:7860
# ============================================

import gradio as gr
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Connect to Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# This function gets called every time you send a message
def respond(message, history):
    # Save to database
    supabase.table("chat_messages").insert({
        "message": message,
        "reply": f"You said: {message}"
    }).execute()
    
    return f"You said: {message}"

# Create the chat interface
demo = gr.ChatInterface(fn=respond)

# Start the app
demo.launch()