import os
import fitz  # PyMuPDF
import hashlib
import json
import time
import logging
import re

from typing import List, Optional, Dict, Any, Literal
from anthropic import Anthropic

# Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# Anthropic Claude setup
claude = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# Folders and files
PDF_FOLDER = "tra_documents"
SUMMARY_FOLDER = "summaries"
QUESTION_BANK_EN_FILE = "question_bank_en.json"
QUESTION_BANK_AR_FILE = "question_bank_ar.json"
METADATA_FILE = "pdf_metadata.json"

# Settings
CHUNK_SIZE = 2000
DELAY_BETWEEN_REQUESTS = 1  # seconds
QUESTIONS_PER_DOCUMENT = 5


def ensure_directories() -> None:
    os.makedirs(SUMMARY_FOLDER, exist_ok=True)


def calculate_file_hash(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "".join(page.get_text() for page in doc)


def split_text_into_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def summarize_chunk(chunk: str) -> str:
    try:
        response = claude.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=700,
            temperature=0.3,
            system="Summarize the following text clearly and neutrally in English.",
            messages=[{"role": "user", "content": chunk}],
        )
        return response.content[0].text.strip() if response.content else ""
    except Exception as e:
        logging.error(f"Error summarizing chunk: {e}")
        return ""


def generate_mcq_questions(
    summary_text: str, n: int, language: Literal["ar", "en"]
) -> List[Dict[str, Any]]:
    try:
        if language != "ar":
            language = "en"

        if language == "ar":
            system_prompt = (
                f"استنادًا فقط إلى المستند الملخّص التالي:\n{summary_text}\n"
                f"أنشئ {n} أسئلة اختبار متعددة الخيارات."
                f"يجب أن يحتوي كل سؤال على أربعة اختيارات: اختيار صحيح وثلاثة خاطئة."
                f"نسق الناتج بدقة كمصفوفة JSON حيث يحتوي كل عنصر على المفاتيح التالية:"
                f"'question'، 'choices' (مصفوفة من 4 سلاسل نصية)، و 'correct_choice_index' (من 0 إلى 3)."
            )
        else:
            system_prompt = (
                f"Based only on the following summarized document:\n{summary_text}\n"
                f"Generate {n} multiple-choice quiz questions."
                f"Each question must have exactly 4 choices: 1 correct and 3 wrong."
                f"Format the output strictly as a JSON array where each item has keys:"
                f"'question', 'choices' (array of 4 strings), and 'correct_choice_index' (0-3)."
            )

        response = claude.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.5,
            system=system_prompt,
            messages=[],
        )

        raw_output = response.content[0].text.strip() if response.content else ""
        raw_output = re.sub(r"^```(?:json)?\\s*", "", raw_output)
        raw_output = re.sub(r"\\s*```$", "", raw_output)

        return json.loads(raw_output)

    except Exception as e:
        logging.error(f"Error generating MCQ questions: {e}")
        return []


def summarize_pdf(pdf_path: str) -> Optional[str]:
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    summary_path = os.path.join(SUMMARY_FOLDER, f"{filename}.txt")
    hash_path = os.path.join(SUMMARY_FOLDER, f"{filename}.hash")

    current_hash = calculate_file_hash(pdf_path)
    saved_hash = load_saved_hash(hash_path)

    if os.path.exists(summary_path) and saved_hash == current_hash:
        logging.info(f"No changes detected in {filename}. Skipping summarization.")
        return summary_path

    logging.info(f"Summarizing {filename}...")
    try:
        full_text = extract_text_from_pdf(pdf_path)
        chunks = split_text_into_chunks(full_text)
        logging.info(f"Total {len(chunks)} chunks created for {filename}.")

        all_summaries = [summarize_chunk(chunk) for chunk in chunks if chunk]
        time.sleep(DELAY_BETWEEN_REQUESTS)

        final_summary = "\n\n".join(all_summaries)

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(final_summary)

        save_hash(current_hash, hash_path)
        return summary_path

    except Exception as e:
        logging.error(f"Failed to summarize {filename}: {e}")
        return None


def save_hash(hash_value: str, hash_path: str) -> None:
    with open(hash_path, "w") as f:
        f.write(hash_value)


def load_saved_hash(hash_path: str) -> Optional[str]:
    if os.path.exists(hash_path):
        with open(hash_path, "r") as f:
            return f.read().strip()
    return None


def load_pdf_metadata() -> Dict[str, Any]:
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_pdf_metadata(metadata: Dict[str, Any]) -> None:
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def generate_summary_and_questions() -> None:
    ensure_directories()

    pdf_metadata = load_pdf_metadata()
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

    if not pdf_files:
        logging.error(f"No PDF files found in {PDF_FOLDER}. Nothing to process.")
        return

    all_questions_en, all_questions_ar = [], []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        current_hash = calculate_file_hash(pdf_path)

        metadata_entry = pdf_metadata.get(pdf_file)

        if metadata_entry and metadata_entry.get("hash") == current_hash:
            logging.info(f"No changes detected in {pdf_file}. Skipping summarization.")
        else:
            summarize_pdf(pdf_path)
            pdf_metadata[pdf_file] = {
                "hash": current_hash,
                "summary_ready": True,
                "questions_en_ready": False,
                "questions_ar_ready": False,
            }

        summary_path = os.path.join(
            SUMMARY_FOLDER, f"{os.path.splitext(pdf_file)[0]}.txt"
        )

        if not os.path.exists(summary_path):
            logging.error(
                f"Summary file missing for {pdf_file}. Skipping questions generation."
            )
            continue

        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_text = f.read()

            if not pdf_metadata[pdf_file].get("questions_en_ready"):
                logging.info(f"Generating EN questions for {pdf_file}...")
                questions_en = generate_mcq_questions(
                    summary_text, QUESTIONS_PER_DOCUMENT, "en"
                )
                if questions_en:
                    all_questions_en.extend(questions_en)
                    pdf_metadata[pdf_file]["questions_en_ready"] = True

            if not pdf_metadata[pdf_file].get("questions_ar_ready"):
                logging.info(f"Generating AR questions for {pdf_file}...")
                questions_ar = generate_mcq_questions(
                    summary_text, QUESTIONS_PER_DOCUMENT, "ar"
                )
                if questions_ar:
                    all_questions_ar.extend(questions_ar)
                    pdf_metadata[pdf_file]["questions_ar_ready"] = True

        except Exception as e:
            logging.error(f"Failed to generate questions for {pdf_file}: {e}")

    if all_questions_en:
        with open(QUESTION_BANK_EN_FILE, "w", encoding="utf-8") as f:
            json.dump(all_questions_en, f, ensure_ascii=False, indent=2)
        logging.info(
            f"English question bank saved to {QUESTION_BANK_EN_FILE}. Total questions: {len(all_questions_en)}"
        )

    if all_questions_ar:
        with open(QUESTION_BANK_AR_FILE, "w", encoding="utf-8") as f:
            json.dump(all_questions_ar, f, ensure_ascii=False, indent=2)
        logging.info(
            f"Arabic question bank saved to {QUESTION_BANK_AR_FILE}. Total questions: {len(all_questions_ar)}"
        )

    if not all_questions_en and not all_questions_ar:
        logging.warning("No questions generated.")

    save_pdf_metadata(pdf_metadata)
