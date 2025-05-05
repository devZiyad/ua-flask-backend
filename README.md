# 🛠️ Backend Setup Guide

## 📚 Project Description

This is a **sanitized public version** of the backend for the **Universal Acceptance Educational Website**.  
The original private repository included sensitive credentials such as:
- SMTP server details (IP, username, and password)
- AI provider API keys (Anthropic/OpenAI)

These credentials were removed in this version for security reasons.

---

## 🔧 Features

This Flask-based backend provides:
- 📩 Arabic/International email subscription with confirmation
- 🤖 Claude-powered AI chatbot that answers based on uploaded TRA PDFs
- 🧠 AI-generated educational quizzes from regulatory content
- 🇸🇦 Full support for Arabic language and UTF-8 email addresses 

Built with **Python 3.10+**, Flask, and Claude API.

---

## 📦 Prerequisites

- Python 3.10 or newer
- `pip`
- Git
- A Gmail or SMTP account for sending confirmation emails
- Claude API key via [Anthropic](https://www.anthropic.com/)

---

## 🚀 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/devZiyad/dotbh-hackathon-backend.git
cd dotbh-hackathon-backend
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> Includes `flask`, `flask-cors`, `python-dotenv`, `pymupdf`, `email-validator`, `idna`, and `anthropic`.

---

## 🛠️ Running the Server

```bash
flask run
```

Server will start at:  
👉 `http://127.0.0.1:5000/`

---

## 📋 API Reference

API endpoint documentation is available in [`APIDocs.md`](./APIDocs.md)

---

## 🧪 Development Notes

- ✅ Email validation supports Arabic (IDNA2008 + mailbox rules)
- 🧠 AI chatbot loads summarized PDF data on startup
- 📄 Quiz questions are generated dynamically per document
- 🌐 CORS enabled for frontend integration
- 📁 Summaries and metadata are auto-generated at runtime and ignored in Git

---

## 🛡️ Security Reminder

Do **not** commit any of the following:
- `.env` files containing secrets
- `subscribers.txt`
- Claude/OpenAI API keys
- SMTP credentials
