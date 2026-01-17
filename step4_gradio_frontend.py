import gradio as gr
import requests

# FastAPI backend URL
API_URL = "http://localhost:8000/chat"

def chat_with_api(message, history):
    """
    Send message to FastAPI backend and return response

    Args:
        message: Current user message
        history: List of previous messages in Gradio format

    Returns:
        AI response string
    """
    # Convert Gradio history format to API format
    api_history = []
    if history:
        for msg in history:
            # Gradio messages are dicts with 'role' and 'content'
            api_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Prepare request payload
    payload = {
        "message": message,
        "history": api_history
    }

    try:
        # Send POST request to FastAPI
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()

        # Extract reply from response
        data = response.json()
        return data["reply"]

    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to backend API. Make sure FastAPI server is running on http://localhost:8000"
    except requests.exceptions.HTTPError as e:
        return f"Error: API request failed with status {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create chat interface
demo = gr.ChatInterface(
    fn=chat_with_api,
    title="AI Chat (via FastAPI)",
    description="Gradio frontend → FastAPI backend → Groq AI"
)

if __name__ == "__main__":
    demo.launch()
