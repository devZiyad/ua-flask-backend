from anthropic import Anthropic
from typing import List, Dict

import os
import logging


anthropic = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

SUMMARY_FOLDER = "summaries"
DEFAULT_SUMMARY_FILE = "20230926101240991_vcujterl_ad0.txt"  # fallback
DOCUMENT_SUMMARY = None
ACTIVE_SUMMARY_FILE = None  # Tracks the currently loaded summary


def init(summary_filename=None):
    """Initialize chatbot with a given summary file."""
    global DOCUMENT_SUMMARY
    global ACTIVE_SUMMARY_FILE

    if summary_filename is None:
        summary_filename = DEFAULT_SUMMARY_FILE

    summary_path = (
        os.path.join(SUMMARY_FOLDER, summary_filename)
        if not summary_filename.startswith(SUMMARY_FOLDER)
        else summary_filename
    )

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            DOCUMENT_SUMMARY = f.read()
        ACTIVE_SUMMARY_FILE = summary_filename
        logging.info(f"Loaded summarized document for chatbot: {summary_filename}")
    except Exception as e:
        logging.error(f"Failed to load summarized document {summary_filename}: {e}")
        DOCUMENT_SUMMARY = "Summary could not be loaded."
        ACTIVE_SUMMARY_FILE = None


def ask_ai(messages: List[Dict[str, str]], language: str) -> str:
    """Answer based on full conversation messages using Claude."""
    try:
        if DOCUMENT_SUMMARY is None:
            logging.error("Document summary not loaded.")
            return "Error: Document not available for answering."

        if language == "ar":
            logging.info("CHATBOT: selected arabic language")
            system_prompt = (
                f"أنت مساعد ذكي. يجب أن تجيب دائمًا استنادًا فقط إلى المستند الملخّص التالي:\n{DOCUMENT_SUMMARY}\n"
                f"إذا كان السؤال خارج محتوى المستند، يجب أن ترفض بأدب. أجب دائمًا بلغة العربية."
            )
        else:
            logging.info("CHATBOT: selected english language")
            system_prompt = (
                f"You are an assistant that answers strictly based on the following summarized document:\n{DOCUMENT_SUMMARY}\n"
                f"If the question is outside the content, politely refuse. Reply in English only."
            )

        # Claude expects messages in this format
        claude_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages
        ]

        response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=600,
            temperature=0.3,
            system=system_prompt,
            messages=claude_messages,
        )

        return response.content[0].text if response.content else ""

    except Exception as e:
        logging.error(f"Error answering question: {e}")
        raise
