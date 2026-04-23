import pdfplumber
import json
import re
from openai import OpenAI


# =========================
# SYSTEM PROMPT (Kazakhstan-specific legal context)
# =========================
SYSTEM_PROMPT = """
Ты — эксперт по тендерам в строительной отрасли Казахстана.

Проанализируй текст тендерной документации и верни ТОЛЬКО JSON без пояснений, 
без markdown-блоков, без текста до или после JSON.

Структура ответа:
{
  "Наличие скрытых штрафов": "...",
  "Сроки выполнения работ": "...",
  "Требуемые категории ГСЛ": "...",
  "Особые требования к материалам": "...",
  "Общий уровень риска": <число от 0 до 100>,
  "Резюме": "..."
}

Правила:
- Сроки ВСЕГДА переводи в рабочие дни
- ГСЛ: указывай уровень (1 / 2 / 3) если упомянут
- Если данных нет — пиши "Не указано"
- ТОЛЬКО JSON, никакого другого текста
"""


# =========================
# 1. PDF TEXT EXTRACTION
# =========================
def extract_text_from_pdf(pdf_file) -> str:
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


# =========================
# 2. JSON SANITIZER
# =========================
def sanitize_json_response(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {"error": "Модель вернула некорректный JSON", "raw_output": raw[:500]}


# =========================
# 3. OPENAI ANALYSIS
# =========================
def analyze_with_openai(text: str, api_key: str) -> dict:
    client = OpenAI(api_key=api_key)
    truncated_text = text[:30000]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"ТЕКСТ ТЕНДЕРА:\n{truncated_text}"}
            ]
        )
        raw = response.choices[0].message.content
        return sanitize_json_response(raw)

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate_limit" in error_msg.lower():
            return {"error": "Превышен лимит запросов OpenAI API. Подождите и попробуйте снова."}
        elif "401" in error_msg or "invalid_api_key" in error_msg.lower():
            return {"error": "Неверный API ключ. Проверьте ключ в настройках."}
        elif "insufficient_quota" in error_msg.lower():
            return {"error": "Закончились средства на OpenAI аккаунте. Пополните баланс на platform.openai.com."}
        else:
            return {"error": f"Ошибка API: {error_msg[:200]}"}


# =========================
# 4. MAIN PIPELINE
# =========================
def process_tender_pdf(pdf_file, api_key: str) -> dict:
    text = extract_text_from_pdf(pdf_file)
    if not text:
        return {"error": "Файл является сканом. Пожалуйста, загрузите текстовый PDF или OCR-версию документа."}
    return analyze_with_openai(text, api_key)