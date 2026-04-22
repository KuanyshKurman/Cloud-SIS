import pdfplumber
import json
import re
import google.generativeai as genai


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
    """
    Извлекает текст из PDF (Streamlit UploadedFile или file-like object).
    Возвращает пустую строку если PDF отсканирован (нет текстового слоя).
    """
    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text.strip()


# =========================
# 2. JSON SANITIZERF
# =========================
def sanitize_json_response(raw: str) -> dict:
    """
    Очищает ответ модели от markdown-обёрток и парсит JSON.
    Устойчив к ```json ... ``` и лишним пробелам.
    """
    # Убираем markdown-блоки ```json ... ``` или ``` ... ```
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Попытка найти JSON-объект внутри текста
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    return {
        "error": "Модель вернула некорректный JSON",
        "raw_output": raw[:500]
    }


# =========================
# 3. GEMINI ANALYSIS
# =========================
def analyze_with_gemini(text: str, api_key: str) -> dict:
    """
    Отправляет текст тендера в Gemini API и возвращает структурированный JSON.
    api_key передаётся явно — нет глобальных зависимостей.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Ограничиваем текст до 30 000 символов (лимит токенов)
    truncated_text = text[:30000]

    prompt = f"""{SYSTEM_PROMPT}

ТЕКСТ ТЕНДЕРА:
{truncated_text}
"""

    try:
        response = model.generate_content(prompt)
        return sanitize_json_response(response.text)

    except Exception as e:
        error_msg = str(e)

        if "ResourceExhausted" in error_msg or "429" in error_msg:
            return {"error": "Превышен лимит запросов Gemini API. Подождите и попробуйте снова."}
        elif "API_KEY_INVALID" in error_msg or "401" in error_msg:
            return {"error": "Неверный API ключ. Проверьте ключ в настройках."}
        else:
            return {"error": f"Ошибка API: {error_msg[:200]}"}


# =========================
# 4. MAIN PIPELINE
# =========================
def process_tender_pdf(pdf_file, api_key: str) -> dict:
    """
    Полный пайплайн: PDF → текст → Gemini → JSON анализ.
    """
    text = extract_text_from_pdf(pdf_file)

    if not text:
        return {
            "error": "Файл является сканом. Пожалуйста, загрузите текстовый PDF или OCR-версию документа."
        }

    return analyze_with_gemini(text, api_key)