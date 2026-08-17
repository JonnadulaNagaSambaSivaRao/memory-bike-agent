# 🧠 Memory-Aware AI Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/AI--Agent-8A2BE2?style=for-the-badge&logo=ai&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/UV-Package_Manager-6E56CF?style=for-the-badge&logo=python&logoColor=white" />
</p>

<p align="center">
  <b>🧠 A persistent memory-aware AI agent with short-term conversation history, long-term user memory, relevant memory retrieval, and automatic conversation summarization.</b>
</p>

<p align="center">
  <i>💬 Remembers conversations • 🧠 Stores important memories • 🔎 Retrieves relevant context • 📝 Summarizes long conversations</i>
</p>

---


---

## 🌟 Project Overview

The **Memory-Aware AI Agent** is an intelligent command-line AI application that can remember important information about the user across conversations.

Unlike a normal chatbot that forgets previous conversations, this agent maintains two different types of memory:

🟢 **Short-Term Memory**  
Keeps recent conversation messages available to the AI.

🔵 **Long-Term Memory**  
Stores important user preferences and information permanently in SQLite.

🟣 **Conversation Summarization**  
When the conversation becomes too large, older messages can be summarized so the agent can continue working without sending the entire conversation history to the LLM.

The agent intelligently combines:

```text
Recent Conversation
        +
Relevant Long-Term Memories
        +
Current User Request
        ↓
       LLM
        ↓
   AI Response
````

---

## 🚀 Key Features

| Feature              | Description                                        |
| -------------------- | -------------------------------------------------- |
| 🧠 Short-Term Memory | Maintains recent conversation history              |
| 💾 Long-Term Memory  | Stores persistent user information                 |
| 🔎 Memory Retrieval  | Retrieves memories relevant to the current request |
| 📝 Summarization     | Compresses older conversation history              |
| 🗄️ SQLite           | Provides persistent local storage                  |
| 🤖 AI Agent          | Uses an LLM to generate responses                  |
| 💻 CLI Interface     | Chat continuously from the terminal                |
| 🔄 Persistent State  | Memories remain available after restarting         |
| 🧹 Memory Management | View or clear stored memories                      |

---

## 🏗️ How It Works

```text
                    👤 USER
                       │
                       ▼
                💬 Current Request
                       │
                       ▼
              🤖 MEMORY-AWARE AGENT
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   🟢 SHORT-TERM              🔵 LONG-TERM
     MEMORY                      MEMORY
          │                         │
          │                  ┌──────┴──────┐
          │                  │             │
          │                  ▼             ▼
          │              🔎 Retrieval   🗄️ SQLite
          │
          └────────────┬────────────┘
                       │
                       ▼
              🧠 CONTEXT BUILDER
                       │
                       ▼
             🤖 LARGE LANGUAGE MODEL
                       │
                       ▼
                  💬 RESPONSE
                       │
                       ▼
              💾 SAVE IMPORTANT
                   MEMORIES
```

---

## 🧠 Memory Architecture

### 🟢 Short-Term Memory

Short-term memory contains the most recent conversation messages.

Example:

```text
User: I prefer Honda bikes.

Agent: Got it! I'll remember that.

User: What bike would you recommend?

Agent: Since you prefer Honda bikes, I would recommend a Honda model.
```

Recent messages provide immediate conversational context.

---

### 🔵 Long-Term Memory

Important information can be stored permanently.

Example:

```text
User Preference:
"I prefer Honda bikes."
```

The information can be stored in:

```text
memory.db
```

After restarting the application:

```text
You: What type of bikes do I prefer?

Agent: You prefer Honda bikes.
```

The agent can remember information from previous sessions.

---

## 📝 Conversation Summarization

Sending the complete conversation history to an LLM can become expensive and inefficient.

This project solves that problem by limiting the amount of conversation sent to the model.

When the conversation becomes too large:

```text
Old Messages
     ↓
📝 Summarization
     ↓
Compact Summary
     ↓
Recent Messages
     +
Relevant Memories
     +
Current Request
     ↓
🤖 LLM
```

This helps control context size while preserving important information.

---

## 🎯 Context Management

The agent does **not** send the entire database or entire conversation to the LLM.

Instead, it builds focused context:

```text
┌───────────────────────────────┐
│      CURRENT REQUEST          │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│      RECENT MESSAGES          │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│     RELEVANT MEMORIES         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       LLM CONTEXT             │
└───────────────┬───────────────┘
                │
                ▼
           🤖 RESPONSE
```

This makes the agent more efficient and memory-aware.

---

## 🗄️ Database

The project uses **SQLite** for persistent memory.

Database file:

```text
memory.db
```

The database stores long-term memories so they remain available even after the application is closed.

Example conceptual data:

```text
┌────┬──────────────────────────────┐
│ ID │ Memory                       │
├────┼──────────────────────────────┤
│ 1  │ User prefers Honda bikes    │
│ 2  │ User likes sports bikes     │
│ 3  │ User prefers blue color     │
└────┴──────────────────────────────┘
```

---

## 📁 Project Structure

```text
memory-bike-agent/
│
├── 🐍 main.py
├── 🤖 agent.py
├── 🧠 memory.py
├── 🗄️ memory.db
├── ⚙️ pyproject.toml
└── 📖 README.md
```

> The exact project structure may vary depending on your implementation.

---

## ⚙️ Requirements

Before running the project, make sure you have:

```text
🐍 Python 3.11+
📦 UV Package Manager
🤖 LLM API Key
💻 Windows / Linux / macOS
```

---

## 📦 Installation

Open PowerShell or your terminal inside the project directory.

### 1️⃣ Create / enter the project

```powershell
cd memory-bike-agent
```

### 2️⃣ Install dependencies

```powershell
uv sync
```

If dependencies have not yet been added, install the required packages according to your project configuration.

---

## 🔐 Environment Variables

Create a `.env` file if your LLM provider requires an API key.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

⚠️ Never commit your real API key to GitHub.

Add `.env` to `.gitignore`:

```gitignore
.env
*.db
__pycache__/
.venv/
```

---

## ▶️ Run the Application

Start the agent using:

```powershell
uv run python main.py
```

You should see something similar to:

```text
============================================================
        🧠 MEMORY-AWARE AI AGENT
============================================================

Agent started successfully!
Type your message and press Enter.

Available commands:
  show memory   → Display saved long-term memories
  clear memory  → Delete all long-term memories
  exit          → Exit the application

============================================================
```

---

## 💬 Example Conversation

```text
You: I prefer Honda bikes.

Agent: Got it! I'll remember that you prefer Honda bikes.

You: I also like sports bikes.

Agent: I'll remember that you like sports bikes.

You: What kind of bike should I consider?

Agent: Since you prefer Honda bikes and like sports bikes,
you may want to consider Honda's sports-oriented models.
```

---

## 🔄 Persistence Test

One of the most important features is persistent memory.

### Session 1

```text
You: I prefer Honda bikes.

Agent: Got it! I'll remember that.
```

Exit:

```text
You: exit
```

Start the application again:

```powershell
uv run python main.py
```

Then ask:

```text
You: What bike brand do I prefer?
```

The agent should be able to use the previously stored long-term memory.

---

## 👀 Show Memory

Inside the application:

```text
You: show memory
```

Example:

```text
============================================================
                 🧠 SAVED MEMORIES
============================================================

1. User prefers Honda bikes.
2. User likes sports bikes.
3. User prefers comfortable motorcycles.

============================================================
```

---

## 🧹 Clear Memory

To remove saved long-term memories:

```text
You: clear memory
```

The application should remove the stored memories according to the implemented memory-management logic.

---

## 🚪 Exit

To close the application:

```text
You: exit
```

or:

```text
You: quit
```

depending on the commands implemented in your application.

---

## 🔥 Why This Project Is Different

A basic chatbot works like:

```text
User
 ↓
LLM
 ↓
Response
```

A memory-aware agent works like:

```text
User
 ↓
Memory Retrieval
 ↓
Recent Conversation
 ↓
Relevant Long-Term Memories
 ↓
Context Management
 ↓
LLM
 ↓
Response
 ↓
Memory Update
```

This allows the application to maintain continuity between conversations.

---

## 🧩 Core Components

### 🤖 Agent

Responsible for:

```text
User Request
     ↓
Understand Request
     ↓
Retrieve Relevant Memory
     ↓
Build Context
     ↓
Call LLM
     ↓
Generate Response
```

### 🧠 Memory Manager

Responsible for:

```text
Save Memory
Retrieve Memory
Search Memory
Delete Memory
Manage Conversation History
```

### 🗄️ SQLite Database

Responsible for persistent storage:

```text
Application
     ↓
Memory Manager
     ↓
SQLite
     ↓
memory.db
```

### 📝 Summarizer

Responsible for reducing large conversation histories:

```text
Large History
     ↓
Summarization
     ↓
Compact Context
```

---

## 📊 Memory Flow

```text
                USER MESSAGE
                     │
                     ▼
             🔎 MEMORY SEARCH
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
   Recent Messages       Long-Term Memory
          │                     │
          └──────────┬──────────┘
                     │
                     ▼
              🧠 CONTEXT
                     │
                     ▼
                🤖 LLM
                     │
                     ▼
                RESPONSE
                     │
                     ▼
             💾 MEMORY UPDATE
```

---

## 🛠️ Technology Stack

<p align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
<img src="https://img.shields.io/badge/LLM-AI-purple?style=for-the-badge" />
<img src="https://img.shields.io/badge/CLI-Terminal-black?style=for-the-badge" />
<img src="https://img.shields.io/badge/UV-6E56CF?style=for-the-badge&logo=python&logoColor=white" />

</p>

---

## 📌 Important Design Principle

The agent should send only the information required for the current request.

Instead of:

```text
❌ Entire conversation
❌ Entire memory database
❌ Unrelated memories
```

It should send:

```text
✅ Recent messages
✅ Relevant memories
✅ Current request
```

This improves:

⚡ Performance
💰 Token efficiency
🎯 Relevance
🧠 Context quality
📈 Scalability

---

## 🧪 Testing Checklist

```text
✅ Start application
✅ Send normal message
✅ Save a user preference
✅ Ask about the preference
✅ Restart application
✅ Verify persistent memory
✅ Display saved memories
✅ Clear memories
✅ Continue conversation
✅ Test large conversation history
✅ Verify summarization
```

---

## 🐛 Troubleshooting

### ❌ Database is locked

If Windows reports:

```text
The process cannot access the file because it is being used by another process.
```

First stop the running application:

```powershell
Ctrl + C
```

Then close any Python processes using the database.

You can check Python processes with:

```powershell
Get-Process python
```

If necessary:

```powershell
Stop-Process -Name python -Force
```

Then try again.

---

### ❌ API Key Not Found

If you see:

```text
GROQ_API_KEY not found
```

check that your `.env` contains:

```env
GROQ_API_KEY=your_api_key_here
```

Also make sure the `.env` file is located in the project directory.

---

### ❌ Dependency Problems

Try:

```powershell
uv sync
```

Then:

```powershell
uv run python main.py
```

---


---

## 🎓 Learning Objectives

This project demonstrates important AI-agent concepts:

```text
🧠 Memory Management
🤖 AI Agents
💬 Conversation History
💾 Persistent Storage
🗄️ SQLite
📝 Summarization
🔎 Context Retrieval
🎯 Context Management
💻 CLI Applications
```

It is especially useful for understanding how modern AI applications can maintain state across multiple interactions.

---

## 🌟 Example Use Cases

### 🏍️ Bike Recommendation Assistant

```text
User preferences
      ↓
Honda
Sports Bikes
Comfortable
      ↓
AI Agent
      ↓
Personalized Recommendation
```

### 🛒 Shopping Assistant

```text
Preferred Brand
Budget
Product Type
      ↓
Persistent Memory
      ↓
Personalized Recommendations
```

### 🎓 Study Assistant

```text
Subject Preferences
Learning Goals
Previous Questions
      ↓
Long-Term Memory
      ↓
Personalized Study Assistance
```

### 💼 Personal Assistant

```text
User Preferences
Tasks
Conversation History
      ↓
Memory
      ↓
Personalized Assistant
```

---

## 🏆 Project Goal

The main goal of this project is to demonstrate how an AI application can become **memory-aware** instead of behaving like a stateless chatbot.

```text
             WITHOUT MEMORY

User → LLM → Response


             WITH MEMORY

User
 ↓
Memory
 ↓
Relevant Context
 ↓
LLM
 ↓
Personalized Response
 ↓
Updated Memory
```

---

## 💡 Final Result

The completed application provides:

<p align="center">

🧠 <b>Memory</b>   •  
💬 <b>Conversation</b>   •  
💾 <b>Persistence</b>   •  
🤖 <b>AI</b>   •  
📝 <b>Summarization</b>

</p>

The result is a CLI-based **Memory-Aware AI Agent** capable of maintaining short-term context, storing long-term memories, retrieving relevant information, and managing large conversations efficiently.

---

<p align="center">
  <b>🧠 Built with Python • 🤖 AI • 💾 SQLite • ⚡ UV</b>
</p>


```
