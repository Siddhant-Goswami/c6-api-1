import gradio as gr
import os
from groq import Groq

# Initialize Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def llm_call(message, history):
    """
    Call Groq LLM and return response

    Args:
        message: Current user message
        history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
    """
    # Build messages array from history
    messages = []

    # Add conversation history
    if history:
        for msg in history:
            messages.append(msg)

    # Add current message
    messages.append({
        "role": "user",
        "content": message
    })

    # Call Groq API
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="openai/gpt-oss-20b",
    )

    # Extract and return response
    return chat_completion.choices[0].message.content

# Create chat interface
demo = gr.ChatInterface(
    fn=llm_call,
    title="Groq AI Chat",
    description="Chat interface powered by Groq LLM (openai/gpt-oss-20b)"
)

if __name__ == "__main__":
    demo.launch()
