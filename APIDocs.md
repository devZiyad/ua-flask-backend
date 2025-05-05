# 📋 API Documentation

This document describes the available backend API endpoints used in the Universal Acceptance Educational Website.

---

## 🔄 Common Notes
- All responses are returned in **JSON** format.
- CORS is enabled for frontend access.
- Ensure the backend server is running at `http://127.0.0.1:5000/` or your deployment address.

---

## 📩 `POST /api/subscribe`

Subscribe a user by email and send them a confirmation.

### Request Body (JSON)
```json
{
  "email": "user@مثال.إختبار"
}
```

### Responses
- `200 OK`: Subscription successful and confirmation email sent.
- `400 Bad Request`: Invalid or mixed-script email.
- `409 Conflict`: Email already subscribed.
- `500 Internal Server Error`: Email could not be sent.

---

## 💬 `POST /api/chat`

Send a list of messages and get an AI-generated response based on the summarized TRA document.

### Request Body (JSON)
```json
{
  "language": "ar",  // or "en"
  "messages": [
    { "role": "user", "content": "ما هو القبول الشامل؟" },
    { "role": "assistant", "content": "القبول الشامل هو ..." },
    { "role": "user", "content": "أعطني مثالاً." }
  ]
}
```

### Responses
- `200 OK`: `{ "success": true, "answer": "..." }`
- `400 Bad Request`: Missing or invalid message list/language
- `500 Internal Server Error`: AI communication failed

---

## 🧠 `GET /api/quiz`

Returns a set of AI-generated multiple-choice questions based on the uploaded TRA summaries.

### Query Parameters
- `n` (optional): Number of questions (default is 5)
- `language`: `"ar"` or `"en"`

### Example
```
/api/quiz?n=3&language=en
```

### Response
```json
{
  "success": true,
  "questions": [
    {
      "question": "What is the purpose of the numbering plan?",
      "choices": ["...", "...", "...", "..."],
      "correct_choice_index": 1
    },
    ...
  ]
}
```

---

## ✅ Health Check

To verify the server is running, hit the root:
```
GET /
```
Returns:
```json
{}
```

---

## 🔐 Security Notes

- Do **not** expose this API without rate-limiting and authentication in production.
- Ensure environment variables are managed securely (`.env` file is ignored by Git).
