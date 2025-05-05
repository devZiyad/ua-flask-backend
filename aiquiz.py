import json
import os
import random
import logging

from typing import List, Dict, Literal

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# File paths
QUESTION_BANK_EN_FILE: str = "question_bank_en.json"
QUESTION_BANK_AR_FILE: str = "question_bank_ar.json"

# Data type for each question
Question = Dict[str, object]

# Loaded question lists
questions_en: List[Question] = []
questions_ar: List[Question] = []


def init() -> None:
    """Load the full question bank into memory."""
    global questions_en, questions_ar
    questions_en = []
    questions_ar = []

    if not os.path.exists(QUESTION_BANK_EN_FILE):
        logging.error(f"Question bank file '{QUESTION_BANK_EN_FILE}' does not exist.")
        return

    if not os.path.exists(QUESTION_BANK_AR_FILE):
        logging.error(f"Question bank file '{QUESTION_BANK_AR_FILE}' does not exist.")
        return

    try:
        with open(QUESTION_BANK_EN_FILE, "r", encoding="utf-8") as f:
            questions_en = json.load(f)
        logging.info(
            f"Loaded {len(questions_en)} questions from '{QUESTION_BANK_EN_FILE}'"
        )

        with open(QUESTION_BANK_AR_FILE, "r", encoding="utf-8") as f:
            questions_ar = json.load(f)
        logging.info(
            f"Loaded {len(questions_ar)} questions from '{QUESTION_BANK_AR_FILE}'"
        )

    except Exception as e:
        logging.error(f"Failed to load question bank: {e}")


def generate_quiz_questions(
    n: int, language: Literal["ar", "en"]
) -> Dict[str, List[Question]]:
    """Pick n random questions from the loaded question bank."""
    questions = questions_ar if language == "ar" else questions_en

    if not questions:
        logging.error("No questions available in memory.")
        return {"questions": []}

    try:
        selected_questions = random.sample(questions, min(n, len(questions)))
        return {"questions": selected_questions}

    except Exception as e:
        logging.error(f"Error generating quiz: {e}")
        raise
