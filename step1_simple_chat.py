import gradio as gr

def respond(message, history):
    """Simple echo bot - just repeats what you said"""
    return f"You said: {message}"

# Create chat interface
demo = gr.ChatInterface(
    fn=respond,
    title="Simple Chat Interface",
    description="A basic chat interface that echoes your messages"
)

if __name__ == "__main__":
    demo.launch()
