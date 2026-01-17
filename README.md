# Build Your First AI Chatbot

A step-by-step guide to building a chatbot with Python.

---

## Setup (Do This First!)

### 1. Install the packages

```bash
pip install gradio groq fastapi uvicorn requests
```

### 2. Get your Groq API key

1. Go to https://console.groq.com
2. Sign up (it's free)
3. Click "API Keys" → "Create API Key"
4. Copy your key

### 3. Set your API key

```bash
export GROQ_API_KEY=your_key_here
```

---

## Step 1: Hello Gradio

**File:** `step1_simple_chat.py`

This creates a simple chat interface that echoes your messages.

```bash
python step1_simple_chat.py
```

Open http://127.0.0.1:7860 and try typing something!

**What you learned:** Gradio makes it easy to create chat interfaces.

---

## Step 2: Add AI

**File:** `step2_gradio_with_groq.py`

Now your chatbot actually thinks! It connects to Groq's AI.

```bash
python step2_gradio_with_groq.py
```

Try asking it questions!

**What you learned:** You can connect to AI APIs with just a few lines of code.

---

## Step 3: Create Your Own API

**File:** `step3_fastapi_backend.py`

Turn your chatbot into an API that other apps can use.

```bash
python step3_fastapi_backend.py
```

Open http://localhost:8000/docs to see your API!

**What you learned:** FastAPI lets you create APIs easily.

---

## Step 4: Connect Frontend to Backend

**Files:** `step3_fastapi_backend.py` + `step4_gradio_frontend.py`

Run both together to see how real apps work.

**Terminal 1:**
```bash
python step3_fastapi_backend.py
```

**Terminal 2:**
```bash
python step4_gradio_frontend.py
```

**What you learned:** Real apps have separate frontend and backend.

---

## What You Built

```
Step 1: Gradio (echo bot)
Step 2: Gradio → Groq AI
Step 3: FastAPI → Groq AI
Step 4: Gradio → FastAPI → Groq AI
```

---

## Quick Fixes

**"Module not found"** → Run: `pip install gradio groq fastapi uvicorn requests`

**"API key error"** → Run: `export GROQ_API_KEY=your_key_here`

**"Connection refused"** → Make sure step3 is running before step4
