# Build Your First AI Chatbot

A step-by-step guide to building a chatbot with Python.

---

## Setup (Do This First!)

### 1. Install the packages

```bash
pip install gradio groq fastapi uvicorn requests supabase python-dotenv
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

### 4. Set up Supabase (Database)

The chatbot saves all conversations to a Supabase database.

1. Go to https://supabase.com
2. Sign up (free tier available)
3. Create a new project
4. Go to Settings → API
5. Copy your **Project URL** and **anon/public key**

6. Set your environment variables:

```bash
export SUPABASE_URL=your_project_url_here
export SUPABASE_KEY=your_anon_key_here
```

**Or create a `.env` file:**
```bash
GROQ_API_KEY=your_key_here
SUPABASE_URL=your_project_url_here
SUPABASE_KEY=your_anon_key_here
```

7. Create the database table:

Go to your Supabase project → SQL Editor and run:

```sql
CREATE TABLE chat_messages (
  id BIGSERIAL PRIMARY KEY,
  message TEXT NOT NULL,
  reply TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
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

**Database Integration:** Every message you send is automatically saved to Supabase in the `chat_messages` table.

---

## Step 2: Add AI

**File:** `step2_gradio_with_groq.py`

Now your chatbot actually thinks! It connects to Groq's AI.

```bash
python step2_gradio_with_groq.py
```

Try asking it questions!

**What you learned:** You can connect to AI APIs with just a few lines of code.

**Database Integration:** Both your messages and the AI's replies are saved to Supabase, creating a complete conversation history.

---

## Step 3: Create Your Own API

**File:** `step3_fastapi_backend.py`

Turn your chatbot into an API that other apps can use.

```bash
python step3_fastapi_backend.py
```

Open http://localhost:8000/docs to see your API!

**What you learned:** FastAPI lets you create APIs easily.

**Database Integration:** The API automatically saves every chat request and response to Supabase, so you can track all API usage and conversations.

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
Step 1: Gradio (echo bot) → Supabase
Step 2: Gradio → Groq AI → Supabase
Step 3: FastAPI → Groq AI → Supabase
Step 4: Gradio → FastAPI → Groq AI → Supabase
```

---

## Database Integration

All steps in this tutorial integrate with **Supabase** to persist chat conversations. Here's how it works:

### What Gets Saved

Every time you send a message, the following data is saved to the `chat_messages` table:
- **message**: Your input message
- **reply**: The AI's response (or echo in Step 1)
- **created_at**: Timestamp (automatically added)

### Viewing Your Data

You can view all saved conversations in your Supabase dashboard:

1. Go to your Supabase project
2. Click on **Table Editor**
3. Select the `chat_messages` table
4. See all your chat history!

### Why Use a Database?

- **Persistent storage**: Conversations survive server restarts
- **Analytics**: Track usage patterns and popular questions
- **History**: Build features like "view past conversations"
- **Debugging**: See exactly what users asked and what the AI responded

### Database Schema

The `chat_messages` table structure:
```sql
- id: Auto-incrementing unique ID
- message: User's input message
- reply: AI's response
- created_at: Timestamp of when the message was saved
```

---

## Quick Fixes

**"Module not found"** → Run: `pip install gradio groq fastapi uvicorn requests supabase python-dotenv`

**"API key error"** → Run: `export GROQ_API_KEY=your_key_here`

**"Connection refused"** → Make sure step3 is running before step4

**"Supabase connection error"** → 
  - Check that `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
  - Make sure you've created the `chat_messages` table in Supabase
  - Verify your Supabase project is active
