from sre_constants import POSSESSIVE_REPEAT_ONE
from openai import OpenAI
from flask import Flask, request, jsonify , redirect, render_template , send_from_directory
from flask_cors import CORS
from openpyxl import Workbook, load_workbook
from datetime import datetime
from thefuzz import fuzz
from thefuzz import process
import pandas as pd
import os
import random
from dotenv import load_dotenv
import openai
import re
from servicii import function_check_product
from logic import extract_info
import unicodedata
from logic import extract_servicii_dict
from email_validator import validate_email, EmailNotValidError
import requests


app = Flask(__name__)
CORS(app)

load_dotenv()

TOKEN = os.getenv("HUBSPOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM = os.getenv("TELEGRAM_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")

HUBSPOT_TOKEN = f"Bearer {TOKEN}"


# Pentru acest proiect am lăsat cheia publică (pentru a fi testată mai repede), dar desigur că nu se face așa!
# Aș fi folosit client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) și aș fi dat export în env la key: export OPENAI_API_KEY="sk-..."

client = OpenAI(
    api_key=f"{OPENAI_API_KEY}",  # pune aici cheia ta reală!
)
df = pd.read_excel('digitalgrow.xlsx')
df_en = pd.read_excel('digitalgrow_en.xlsx')
df_ru = pd.read_excel('digitalgrow_ru.xlsx')
categorii = df['SERVICE']
categorii_ru = df_ru['SERVICE']
categorii_en = df_en['SERVICE']
categorii_unice = list(dict.fromkeys(categorii.dropna().astype(str)))
categorii_unice_ru = list(dict.fromkeys(categorii_ru.dropna().astype(str)))
categorii_unice_en = list(dict.fromkeys(categorii_en.dropna().astype(str)))
preferinte = {
    "pret": "",
    "BUDGET": "",
    "Nume_Prenume": "",
    "Numar_Telefon": "",
    "Serviciul_Ales": "",
    "Limba_Serviciului": "",
    "Preferintele_Utilizatorului_Cautare": "",
    "Produs_Pentru_Comanda": "",
    "country": "",
    "Pret_MD": "",
    "Pret_UE": "",
    "reducere": "",
    "Cantitate": "",
    "Culoare_Aleasa": "",
    "Produs_Ales": "",
    "Pret_Produs": "",
    "Pret_Produs_Extras": "",
    "PRODUS_EXTRAS": "",
    "Trecut_Etapa_Finala": "",
    "Response_Comanda": "",
    "Produsele": [],
    "Culoare": "",
    "Nume": "",
    "Prenume": "",
    "Preferinte_inregistrare": "",
    "Nume_Prenume_Correct": "",
    "Masurare": "",
}
# preferinte["pret"] = ""
# preferinte["BUDGET"] = ""
# preferinte["Nume_Prenume"] = ""
# preferinte["Numar_Telefon"] = ""
# preferinte["Serviciul_Ales"] = ""
# preferinte["Limba_Serviciului"] = ""
# preferinte["Preferintele_Utilizatorului_Cautare"] = ""
# preferinte["Produs_Pentru_Comanda"] = ""
# preferinte["country"] = ""
# preferinte["Pret_MD"] = ""
# preferinte["Pret_UE"] = ""

language_saved = ""

# print(categorii_unice_ru)
def log_message(sender, message):
    # Creează calea absolută către folderul logs ! Pentru a salva log-urile in excel !
    base_dir = os.path.expanduser("../logs")
    os.makedirs(base_dir, exist_ok=True)
    file_path = os.path.join(base_dir, "chat_log1.xlsx")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {"Timestamp": timestamp, "Sender": sender, "Message": message}

    try:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])

        df.to_excel(file_path, index=False)
        print(f"[{timestamp}] [LOGGED] {sender}: {message}")
    except Exception as e:
        print(f"[EROARE] Logarea a eșuat: {e}")


def get_country_by_ip():
    ip_list = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')
    ip = ip_list[0].strip()

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        print("data = ", data.get("countryCode", None))
        return data.get("countryCode", None)  # 'MD' pentru Moldova
    except Exception as e:
        print("GeoIP error:", e)
        return None


def is_fuzzy_comanda(user_text, threshold=90):

    comanda_keywords = [
        # română
        "comand", "cumpăr", "achiziționez", "trimit factură", "factura", "plătesc", "finalizez",
        "trimit date", "pregătiți comanda", "ofertă pentru", "cerere ofertă",
        "cât costă x bucăți", "preț 50 mp", "livrare comandă", "plată", "comanda", "curier", "achizitionez",

        # rusă
        "заказ", "купить", "покупка", "покупаю", "оплата", "оформить заказ", "счет", "выставите счет",
        "отправьте счет", "приобрести", "доставку", "плачу", "готов оплатить", "оплатить", "сделать заказ",

        # engleză
        "order", "order", "buy", "buy",
        "pay", "pay", "the invoice", "invoice", "invoice me", "the contract", "buy", "my order",
        "submit order", "purchase",
        "payment", "order", "payment", "order now", "buying", "delivery", "pay", "confirm purchase"
    ]
        
    user_text = user_text.lower()
    words = user_text.split()

    for keyword in comanda_keywords:
        for word in words:
            if fuzz.token_set_ratio(user_text, keyword) >= threshold:
                return True
        # verificăm și fraze întregi
        if fuzz.partial_ratio(user_text, keyword) >= threshold:
            return True
    return False

def is_fuzzy_preferinte_en(user_text, threshold=85):
    preferinte_keywords = [
        "preference", "preferences", "need", "needs", "requirement", "requirements",
        "custom", "customized", "tailored", "personal", "personalized", "individual",
        "select", "selection", "choose", "chosen", "suitable", "suits", "match", "fit",
        "custom fit", "best fit", "targeted", "recommended", "relevant", "my choice",
        "ideal", "matching", "specific", "adapted", "adjusted", "filtered", "custom option",
        "pick", "option", "setup", "combo", "custom combo", "optimized"
    ]

    user_text = user_text.lower()
    words = user_text.split()

    for keyword in preferinte_keywords:
        for word in words:
            if fuzz.token_set_ratio(user_text, keyword) >= threshold:
                return True
        if fuzz.partial_ratio(user_text, keyword) >= threshold:
            return True
    return False

def is_fuzzy_preferinte_ru(user_text, threshold=85):
    preferinte_keywords = [
        "предпочтения", "предпочтение", "потребности", "персонализированный", "персонализированные", "требования",
        "критерии", "критерий", "подходит", "помощь в выборе", "хочу что-то для себя",
        "выбор", "в зависимости от", "помоги выбрать", "основано на потребностях",
        "перефринте", "перефферинте", "перефринтзе", "выбрать что-то", "что мне подходит",
        "кастом", "индивидуальный", "персонализированный", "подходит мне", "выбирать на основе", "потребностей"
    ]
    
    user_text = user_text.lower()
    words = user_text.split()
    
    for keyword in preferinte_keywords:
        for word in words:
            if fuzz.token_set_ratio(user_text, keyword) >= threshold:
                return True
        if fuzz.partial_ratio(user_text, keyword) >= threshold:
            return True
    return False

def is_fuzzy_preferinte(user_text, threshold=85):
    preferinte_keywords = [
        "preferințe", "preferinte", "nevoi", "personalizat", "personalizate", "cerințe", 
        "criterii", "criterii", "criteriu", "potrivit", "ajutor alegere", "vreau ceva pentru mine", 
        "selectare", "în funcție de", "ajută-mă să aleg", "bazat pe nevoi",
        "prefrinte", "prefferinte", "preferintze", "aleg ceva", "ce mi se potrivește",
        "custom", "tailored", "personalized", "match my needs", "fit for me", "select based on"
    ]
    
    user_text = user_text.lower()
    words = user_text.split()
    
    for keyword in preferinte_keywords:
        for word in words:
            if fuzz.token_set_ratio(user_text, keyword) >= threshold:
                return True
        if fuzz.partial_ratio(user_text, keyword) >= threshold:
            return True
    return False
    
def check_interest_pref_en(interest):
    print(interest)

    if is_fuzzy_preferinte_en(interest):
        return "preferinte"
    
    if is_fuzzy_comanda(interest):
        return "comanda"

    interests_prompt = (
        "Analyze the user's message to accurately determine their intention by choosing one of the following categories:\n\n"

        "1. produs_informatii – when the message expresses interest, curiosity, or a request for information about your services, even if it's vague. This includes:\n"
        "- Any interest in:\n"
        "  - Websites: Landing page, simple website, complex multilingual website, online store\n"
        "  - Branding: Professional logo creation, logo refresh\n"
        "  - Promo materials: T-shirt, cap, pen, business card, planner\n"
        "  - Chatbots: Rule-based, Instagram, Messenger, Telegram, GPT\n"
        "  - CRM, maintenance, service packages (Startup Light, Business Smart, Enterprise Complete)\n"
        "- General inquiries such as:\n"
        "  - 'What services do you offer?'\n"
        "  - 'I'm looking for something related to branding'\n"
        "  - 'I need a chatbot'\n"
        "  - 'Send me the list of offers'\n"
        "  - 'What do you have for CRM?'\n"
        "  - 'How much does a website cost?' (if it doesn’t mention multiple units)\n"
        "  - 'I’d like to see your portfolio'\n"
        "- Even vague phrases like: 'services?', 'offer?', 'branding', 'GPT chatbot'\n"
        "- Vague interest in other products or services:\n"
        "  - 'another service', 'something else', 'alternative option', 'other offer'\n\n"

        "2. comanda – ONLY if there's a clear intention to purchase or collaborate:\n"
        "- Explicit verbs like: 'I want to order', 'ready to buy', 'I’m buying', 'let’s work together', 'send the invoice', 'I’ll pay', 'let’s begin'\n"
        "- Specific quantity requests: 'I want 50 business cards', 'How much for 2 landing pages?'\n"
        "- Requests for contracts or starting a project: 'Send the contract', 'How do we start?', 'We’re going with the Business Smart package'\n\n"

        "3. altceva – only:\n"
        "- Greetings without context ('hello', 'good day')\n"
        "- Thanks without details\n"
        "- Jokes, off-topic, spam\n"
        "- Messages unrelated to services or orders\n\n"

        "IMPORTANT RULES:\n"
        "- Any interest in your services = produs_informatii\n"
        "- Any ambiguity = produs_informatii (better a false positive than missing a potential client)\n"
        "- ONLY clear buying intentions = comanda\n"
        "- Verbs like 'I want', 'I'd like' do NOT count as comanda unless paired with action words (order, pay, etc.)\n\n"

        "EXAMPLES:\n"
        "'What kind of chatbots do you have?' => produs_informatii\n"
        "'I want something for branding' => produs_informatii\n"
        "'We're choosing the Business Smart package' => comanda\n"
        "'Send the invoice for the GPT chatbot' => comanda\n"
        "'Hi there' => altceva\n\n"

        f"Message to analyze: \"{interest}\"\n\n"
        "Respond STRICTLY with only one tag: produs_informatii, comanda, or altceva. No explanations."
    )

    messages = [{"role": "system", "content": interests_prompt}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip().lower()


def check_interest_pref_ru(interest):
    print(interest)

    if is_fuzzy_preferinte_ru(interest):
        return "preferinte"
    
    if is_fuzzy_comanda(interest):
        return "comandă"

    interests_prompt = (
        "Проанализируй сообщение пользователя, чтобы точно определить его намерение, выбрав одну из следующих категорий:\n\n"

        "1. produs_informații – когда сообщение выражает интерес, любопытство или запрос информации о ваших услугах, даже если оно нечеткое. Включает:\n"
        "- Любой интерес к:\n"
        "  - Веб-сайтам: Лендинг, Простой сайт, Сложный мультиязычный сайт, Интернет-магазин\n"
        "  - Брендингу: Профессиональное создание логотипа, Обновление логотипа\n"
        "  - Промо-продукции: Футболка, Бейсболка, Ручка, Визитка, Ежедневник\n"
        "  - Чат-ботам: На правилах, Instagram, Messenger, Telegram, GPT\n"
        "  - CRM, поддержке, пакетам услуг (Startup Light, Business Smart, Enterprise Complete)\n"
        "- Общие запросы типа:\n"
        "  - 'Какие услуги у вас есть?'\n"
        "  - 'Хочу что-то для брендинга'\n"
        "  - 'Мне нужен чат-бот'\n"
        "  - 'Пришлите список предложений'\n"
        "  - 'Что у вас есть для CRM?'\n"
        "  - 'Сколько стоит сайт?' (если не говорится о нескольких штуках)\n"
        "  - 'Хочу посмотреть портфолио'\n"
        "- Даже нечеткие фразы, например: 'услуги?', 'предложение?', 'брендинг', 'чат-бот GPT'\n\n"
        "- Нечеткие фразы, указывающие на интерес к другим продуктам или услугам:\n"
        "  - 'другой сервис', 'что-то еще', 'альтернативный вариант', 'другое предложение'\n\n"

        "2. comandă – ТОЛЬКО если явно выражено намерение купить или сотрудничать:\n"
        "- Явные глаголы: 'хочу заказать', 'готов купить', 'покупаю', 'сотрудничаем', 'начинаем работу', 'счёт', 'оплачиваю', 'начнём'\n"
        "- Конкретные запросы с количеством: 'Хочу 50 визиток', 'Сколько стоит 2 лендинга?'\n"
        "- Запросы на договор, счёт, старт проекта: 'Пришлите договор', 'Как начать?', 'Начинаем с пакета Business Smart'\n\n"

        "3. altceva – только:\n"
        "- Приветствия без контекста ('привет', 'добрый день')\n"
        "- Благодарности без деталей\n"
        "- Шутки, оффтоп, спам\n"
        "- Сообщения без связи с услугами или заказами\n\n"

        "ВАЖНЫЕ ПРАВИЛА:\n"
        "- Любой интерес к вашим услугам = produs_informații\n"
        "- Любая неоднозначность = produs_informații (лучше ложноположительный результат, чем потеря клиента)\n"
        "- ТОЛЬКО чёткие выражения желания купить = comandă\n"
        "- Глаголы типа «хочу», «мне бы» НЕ означают comandă, если не сопровождаются конкретными действиями (заказать, оплатить и т.д.)\n\n"

        "ПРИМЕРЫ:\n"
        "'Какие у вас есть чат-боты?' => produs_informații\n"
        "'Хочу что-то для брендинга' => produs_informații\n"
        "'Выбираю пакет Business Smart' => comandă\n"
        "'Пришлите счёт за чат-бот GPT' => comandă\n"
        "'Здравствуйте' => altceva\n\n"

        f"Сообщение для анализа: \"{interest}\"\n\n"
        "Ответь СТРОГО одним из тегов: produs_informații, comandă, altceva. Без объяснений."
    )

    messages = [{"role": "system", "content": interests_prompt}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip().lower()

def check_interest_pref(interest):
    print(interest)

    if is_fuzzy_preferinte(interest):
        return "preferinte"
    
    if is_fuzzy_comanda(interest):
        return "comandă"

    interests_prompt = (
        "Analizează mesajul utilizatorului pentru a identifica intenția exactă în funcție de următoarele categorii detaliate:\n\n"

        "1. produs_informații – când mesajul arată interes, curiozitate sau cerere de informații despre servicii, chiar dacă este vag. Se clasifică aici:\n"
        "- Orice interes exprimat despre:\n"
        "  - Website-uri: Landing Page, Site Simplu, Site Complex Multilingv, Magazin Online\n"
        "  - Branding: Creare Logo Profesional, Refresh Logo\n"
        "  - Produse promoționale: Maiou, Chipiu, Stilou, Carte de vizită, Agendă\n"
        "  - Chatbot: Rule-Based, Instagram, Messenger, Telegram, GPT\n"
        "  - CRM, mentenanță, pachete (Startup Light, Business Smart, Enterprise Complete)\n"
        "- Cereri generale de tipul:\n"
        "  - 'Ce servicii aveți?'\n"
        "  - 'Aș vrea ceva pentru branding'\n"
        "  - 'Vreau un chatbot'\n"
        "  - 'Trimiteți lista de oferte'\n"
        "  - 'Ce opțiuni aveți pentru CRM?'\n"
        "  - 'Cât costă un site?' (dacă nu cere mai multe bucăți)\n"
        "  - 'Vreau să văd portofoliul'\n"
        "- Chiar și mesaje vagi precum: 'servicii?', 'ofertă?', 'branding', 'chatbot GPT'\n\n"

        "2. comandă - DOAR când există o intenție clar exprimată de achiziție sau colaborare:\n"
        "- Verbe explicite: 'vreau să comand', 'vreau să achiziționez', 'cumpăr', 'să colaborăm', 'să lucrăm împreună', 'factura', 'plătesc', 'să începem'\n"
        "- Mesaje cu număr de bucăți/cerere concretă: 'Vreau 50 cărți de vizită', 'Cât costă 2 landing page-uri?'\n"
        "- Cerere de contract, factură, început de proiect: 'Trimiteți contractul', 'Cum procedăm?', 'Începem cu pachetul Business Smart'\n\n"

        "3. altceva - doar pentru:\n"
        "- Saluturi fără context ('salut', 'bună ziua')\n"
        "- Mulțumiri fără alte informații\n"
        "- Glume, comentarii irelevante, spam\n"
        "- Mesaje fără legătură cu serviciile sau comenzile\n\n"

        "REGULI IMPORTANTE:\n"
        "- Orice interes exprimat despre serviciile tale => produs_informații\n"
        "- Orice ambiguitate => produs_informații (mai bine fals pozitiv decât să pierzi un lead)\n"
        "- Doar când există formulare clare de achiziție/comandă => clasifici ca 'comandă'\n"
        "- Verbe precum „vreau”, „aș dori” NU înseamnă 'comandă' dacă nu sunt urmate de acțiune concretă (comand, colaborez, achiziționez, plătesc, etc.)\n\n"

        "EXEMPLE CLASIFICATE:\n"
        "'Ce chatboturi aveți?' => produs_informații\n"
        "'Aș vrea ceva pentru branding' => produs_informații\n"
        "'Vreau pachetul Business Smart' => comandă\n"
        "'Trimiteți-mi factura pentru chatbot GPT' => comandă\n"
        "'Bună, salut' => altceva\n\n"

        f"Mesaj de analizat: \"{interest}\"\n\n"
        "Răspunde STRICT cu unul dintre tag-uri: produs_informații, comandă, altceva. Fără explicații suplimentare."
    )

    messages = [{"role": "system", "content": interests_prompt}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip().lower()

def check_interest_ru(interest):

    msg = interest.lower()

    general_keywords = ["общая", "информация", "описание", "презентация", "детали", "услуги"]
    preferinte_keywords = ["предпочтения", "персонально", "нужды", "выбор", "помощь", "критерии", "персонализировано", "потребностей"]

    general_score = max([fuzz.partial_ratio(msg, kw) for kw in general_keywords])
    preferinte_score = max([fuzz.partial_ratio(msg, kw) for kw in preferinte_keywords])

    if general_score > preferinte_score and general_score > 70:
        return "general"
    elif preferinte_score > general_score and preferinte_score > 70:
        return "preferinte"

    if is_fuzzy_comanda(interest):
        return "comandă"

    interests_prompt = (
        "Проанализируй сообщение пользователя и определи его точное намерение, выбрав одну из следующих категорий:\n\n"

        "1. produs_informații – когда сообщение выражает интерес, любопытство или запрос информации о ваших услугах, даже если оно написано неясно. Это включает:\n"
        "- Любые упоминания об интересе к:\n"
        "  - Сайтам: Лендинг, Простой сайт, Сложный сайт с мультиязычностью, Интернет-магазин\n"
        "  - Брендингу: Создание логотипа, Обновление логотипа\n"
        "  - Промо-продукции: Майка, Кепка, Ручка, Визитка, Ежедневник\n"
        "  - Чат-ботам: На правилах, для Instagram, Messenger, Telegram, GPT\n"
        "  - CRM, техподдержке, пакетах услуг (Startup Light, Business Smart, Enterprise Complete)\n"
        "- Общие запросы:\n"
        "  - 'Какие услуги вы предлагаете?'\n"
        "  - 'Мне нужно что-то для брендинга'\n"
        "  - 'Хочу чат-бот'\n"
        "  - 'Пришлите список предложений'\n"
        "  - 'Что у вас есть для CRM?'\n"
        "  - 'Сколько стоит сайт?' (если не говорится про несколько штук)\n"
        "  - 'Хочу посмотреть портфолио'\n"
        "- Также нечеткие фразы: 'услуги?', 'предложение?', 'брендинг', 'GPT-бот'\n\n"
        "- Нечеткие фразы, указывающие на интерес к другим продуктам или услугам:\n"
        "  - 'другой сервис', 'что-то еще', 'альтернативный вариант', 'другое предложение'\n\n"

        "2. comandă – ТОЛЬКО если явно выражено намерение купить или сотрудничать:\n"
        "- Прямые глаголы: 'хочу заказать', 'готов купить', 'оплачиваю', 'пришлите счет', 'начнем проект', 'подписать договор'\n"
        "- Конкретные запросы: 'Мне нужно 100 визиток', 'Сколько стоит 2 лендинга?'\n"
        "- Запрос на контракт, счет, начало проекта: 'Пришлите договор', 'С чего начнем?', 'Я выбираю пакет Business Smart'\n\n"

        "3. altceva – только если:\n"
        "- Приветствия без контекста: 'Привет', 'Добрый день'\n"
        "- Благодарности без других деталей\n"
        "- Шутки, оффтоп, спам\n"
        "- Сообщения, не связанные с услугами или заказами\n\n"

        "ВАЖНЫЕ ПРАВИЛА:\n"
        "- Любой интерес к услугам = produs_informații\n"
        "- Любая неоднозначность = produs_informații (лучше ложноположительное срабатывание, чем потерянный клиент)\n"
        "- ТОЛЬКО чёткие выражения желания купить = comandă\n"
        "- Слова типа «хочу», «мне бы» НЕ означают 'comandă', если не сопровождаются чёткими действиями (заказать, оплатить и т.д.)\n\n"

        "ПРИМЕРЫ:\n"
        "'Что за боты у вас есть?' => produs_informații\n"
        "'Хочу что-то для брендинга' => produs_informații\n"
        "'Выбираю пакет Business Smart' => comandă\n"
        "'Пришлите счёт за GPT-бота' => comandă\n"
        "'Добрый день' => altceva\n\n"

        f"Сообщение для анализа: \"{interest}\"\n\n"
        "Ответь СТРОГО одним из следующих тегов: produs_informații, comandă, altceva. Без пояснений."
    )

    messages = [{"role": "system", "content": interests_prompt}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip().lower()


def check_interest(interest):
    msg = interest.lower()

    general_keywords = ["general", "informatii", "prezentare", "descriere", "detalii generale"]
    preferinte_keywords = ["preferinte", "personalizat", "nevoi", "ajutor", "alegere", "criterii"]

    general_score = max([fuzz.partial_ratio(msg, kw) for kw in general_keywords])
    preferinte_score = max([fuzz.partial_ratio(msg, kw) for kw in preferinte_keywords])

    if general_score > preferinte_score and general_score > 70:
        return "general"
    elif preferinte_score > general_score and preferinte_score > 70:
        return "preferinte"


    if is_fuzzy_comanda(interest):
        return "comandă"

    interests_prompt = (
        "Analizează mesajul utilizatorului pentru a identifica intenția exactă în funcție de următoarele categorii detaliate:\n\n"

        "1. produs_informații – când mesajul arată interes, curiozitate sau cerere de informații despre servicii, chiar dacă este vag. Se clasifică aici:\n"
        "- Orice interes exprimat despre:\n"
        "  - Website-uri: Landing Page, Site Simplu, Site Complex Multilingv, Magazin Online\n"
        "  - Branding: Creare Logo Profesional, Refresh Logo\n"
        "  - Produse promoționale: Maiou, Chipiu, Stilou, Carte de vizită, Agendă\n"
        "  - Chatbot: Rule-Based, Instagram, Messenger, Telegram, GPT\n"
        "  - CRM, mentenanță, pachete (Startup Light, Business Smart, Enterprise Complete)\n"
        "- Cereri generale de tipul:\n"
        "  - 'Ce servicii aveți?'\n"
        "  - 'Aș vrea ceva pentru branding'\n"
        "  - 'Vreau un chatbot'\n"
        "  - 'Trimiteți lista de oferte'\n"
        "  - 'Ce opțiuni aveți pentru CRM?'\n"
        "  - 'Cât costă un site?' (dacă nu cere mai multe bucăți)\n"
        "  - 'Vreau să văd portofoliul'\n"
        "- Chiar și mesaje vagi precum: 'servicii?', 'ofertă?', 'branding', 'chatbot GPT'\n\n"

        "2. comandă - DOAR când există o intenție clar exprimată de achiziție sau colaborare:\n"
        "- Verbe explicite: 'vreau să comand', 'vreau să achiziționez', 'cumpăr', 'să colaborăm', 'să lucrăm împreună', 'factura', 'plătesc', 'să începem'\n"
        "- Mesaje cu număr de bucăți/cerere concretă: 'Vreau 50 cărți de vizită', 'Cât costă 2 landing page-uri?'\n"
        "- Cerere de contract, factură, început de proiect: 'Trimiteți contractul', 'Cum procedăm?', 'Începem cu pachetul Business Smart'\n\n"

        "3. altceva - doar pentru:\n"
        "- Saluturi fără context ('salut', 'bună ziua')\n"
        "- Mulțumiri fără alte informații\n"
        "- Glume, comentarii irelevante, spam\n"
        "- Mesaje fără legătură cu serviciile sau comenzile\n\n"

        "REGULI IMPORTANTE:\n"
        "- Orice interes exprimat despre serviciile tale => produs_informații\n"
        "- Orice ambiguitate => produs_informații (mai bine fals pozitiv decât să pierzi un lead)\n"
        "- Doar când există formulare clare de achiziție/comandă => clasifici ca 'comandă'\n"
        "- Verbe precum „vreau”, „aș dori” NU înseamnă 'comandă' dacă nu sunt urmate de acțiune concretă (comand, colaborez, achiziționez, plătesc, etc.)\n\n"

        "EXEMPLE CLASIFICATE:\n"
        "'Ce chatboturi aveți?' => produs_informații\n"
        "'Aș vrea ceva pentru branding' => produs_informații\n"
        "'Vreau pachetul Business Smart' => comandă\n"
        "'Trimiteți-mi factura pentru chatbot GPT' => comandă\n"
        "'Bună, salut' => altceva\n\n"

        f"Mesaj de analizat: \"{interest}\"\n\n"
        "Răspunde STRICT cu unul dintre tag-uri: produs_informații, comandă, altceva. Fără explicații suplimentare."
    )

    messages = [{"role": "system", "content": interests_prompt}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip().lower()

def check_interest_en(interest):
    print(interest)

    msg = interest.lower()

    general_keywords = ["general", "information", "overview", "description", "presentation", "details", "services"]
    preferinte_keywords = ["preferences", "custom", "personalized", "needs", "help", "choice", "criteria", "tailored"]

    general_score = max([fuzz.partial_ratio(msg, kw) for kw in general_keywords])
    preferinte_score = max([fuzz.partial_ratio(msg, kw) for kw in preferinte_keywords])

    if general_score > preferinte_score and general_score > 70:
        return "general"
    elif preferinte_score > general_score and preferinte_score > 85:
        print("PREFFF = == ",preferinte_score)
        return "preferinte"


    if is_fuzzy_comanda(interest):
        return "comandă"

    interests_prompt = (
        "Analyze the user's message to determine their exact intent by choosing one of the following categories:\n\n"

        "1. produs_informații – when the message shows interest, curiosity, or a request for information about your services, even if it's vague. This includes:\n"
        "- Any interest in:\n"
        "  - Websites: Landing Page, Simple Site, Complex Multilingual Site, Online Store\n"
        "  - Branding: Professional Logo Creation, Logo Refresh\n"
        "  - Promo products: Tank Top, Cap, Pen, Business Card, Notebook\n"
        "  - Chatbots: Rule-Based, Instagram, Messenger, Telegram, GPT\n"
        "  - CRM, maintenance, service packages (Startup Light, Business Smart, Enterprise Complete)\n"
        "- General inquiries like:\n"
        "  - 'What services do you offer?'\n"
        "  - 'I'm interested in branding'\n"
        "  - 'I want a chatbot'\n"
        "  - 'Send me your offers'\n"
        "  - 'What CRM options do you have?'\n"
        "  - 'How much does a website cost?' (if not asking for multiple)\n"
        "  - 'Can I see your portfolio?'\n"
        "- Even vague messages like: 'services?', 'offer?', 'branding', 'GPT chatbot'\n\n"

        "2. comandă – ONLY when there's a clearly expressed intent to purchase or collaborate:\n"
        "- Clear verbs like: 'I want to order', 'I'd like to buy', 'I'll pay', 'send me the invoice', 'let's start the project', 'send the contract'\n"
        "- Specific quantity or concrete request: 'I want 50 business cards', 'How much for 2 landing pages?'\n"
        "- Requests for contracts, invoices, or project start: 'Send the contract', 'How do we start?', 'I’ll go with the Business Smart package'\n\n"

        "3. altceva – only if:\n"
        "- Greetings without context: 'hi', 'hello'\n"
        "- Thanks without any other content\n"
        "- Jokes, irrelevant comments, spam\n"
        "- Messages not related to services or orders\n\n"

        "IMPORTANT RULES:\n"
        "- Any interest in your services = produs_informații\n"
        "- Any ambiguity = produs_informații (better to classify as positive than miss a lead)\n"
        "- Only clear purchase or collaboration expressions = comandă\n"
        "- Words like “I want”, “I'd like” do NOT mean comandă unless followed by clear action (buy, pay, order, etc.)\n\n"

        "EXAMPLES:\n"
        "'What chatbots do you offer?' => produs_informații\n"
        "'I'm interested in branding' => produs_informații\n"
        "'I want the Business Smart package' => comandă\n"
        "'Send me the invoice for the GPT bot' => comandă\n"
        "'Hi there!' => altceva\n\n"

        f"Message to analyze: \"{interest}\"\n\n"
        "Reply STRICTLY with one of the following tags: produs_informații, comandă, altceva. No other explanations."
    )

    messages = [{"role": "system", "content": interests_prompt}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip().lower()



# def fuzzy_check_category(user_interest, categorii_unice, threshold=70):

#     best_match, best_score = process.extractOne(user_interest, categorii_unice, scorer=fuzz.token_set_ratio)
#     print("------------------------------------------------")
#     if best_score >= threshold:
#         print("best match = " ,best_match)
#         return best_match

#     # Dacă nu găsește potriviri bune, încearcă să compari fiecare cuvânt din user_interest separat
#     words = user_interest.split()
#     for word in words:
#         best_match, best_score = process.extractOne(word, categorii_unice, scorer=fuzz.token_set_ratio)
#         if best_score >= threshold:
#             return best_match

#     # Nu s-a găsit nimic relevant
#     return "NU"



# def smart_category_prompt(user_interest, categorii_unice):
#     prompt = (
#         "Având în vedere lista de categorii:\n"
#         f"{', '.join(categorii_unice)}\n"
#         f"Utilizatorul a spus: '{user_interest}'\n"
#         "Sugerează cea mai potrivită categorie dintre lista de mai sus. "
#         "Răspunde doar cu numele categoriei, fără alte explicații. "
#         "Dacă niciuna nu se potrivește, răspunde cu NU."
#     )
#     messages = [{"role": "system", "content": prompt}]
#     response = ask_with_ai(messages).strip()

#     if not response or response.upper() == "NU":
#         return "NU"
    
#     if response not in categorii_unice:
#         return "NU"

#     return response


# def check_and_get_category(user_interest, categorii_unice, threshold=70):
#     fuzzy_result = fuzzy_check_category(user_interest, categorii_unice, threshold)

#     if fuzzy_result != "NU":
#         return fuzzy_result

#     ai_result = smart_category_prompt(user_interest, categorii_unice)
#     return ai_result

def genereaza_prompt_produse2(rezultat, categorie, language_saved):
    if not rezultat:
        if language_saved == "RO":
            return "⚠️ Nu am identificat servicii relevante în categoria selectată."
        elif language_saved == "RU":
            return "⚠️ Не удалось найти подходящие услуги в выбранной категории."
        else:
            return "⚠️ We couldn't find relevant services in the selected category."

    lista_formatata = ""
    for i in rezultat:
        lista_formatata += f"<strong>{i}</strong><br />"

    if language_saved == "RO":
        prompt = (
            f"Am identificat câteva servicii relevante în urma cererii tale:<br /><br />"
            f"{lista_formatata}<br />"
            "Te rog să alegi <strong>exact denumirea serviciului dorit</strong> pentru a continua configurarea."
        )
    elif language_saved == "RU":
        prompt = (
            "По вашему запросу найдены следующие релевантные услуги:<br /><br />"
            f"{lista_formatata}<br />"
            "Пожалуйста, укажите <strong>точное название нужной услуги</strong>, чтобы мы могли продолжить."
        )
    else:
        prompt = (
            f"We identified a few relevant services in response to your request:<br /><br />"
            f"{lista_formatata}<br />"
            "Please select the <strong>exact name of the desired service</strong> to continue configuration."
        )

    return prompt


def genereaza_prompt_produse(rezultat, categorie, language_saved):
    print(rezultat)
    if not rezultat:
        if language_saved == "RO":
            return "⚠️ Nu am identificat servicii relevante în categoria selectată."
        elif language_saved == "RU":
            return "⚠️ Не удалось найти подходящие услуги в выбранной категории."
        else:
            return "⚠️ We couldn't find relevant services in the selected category."

    lista_formatata = ""
    for idx, serv in enumerate(rezultat, 1):
        nume = serv['produs'].replace("**", "")
        pret = serv['pret']
        lista_formatata += f"{idx}. <strong>{nume}</strong><br />"

    if language_saved == "RO":
        prompt = (
            f"Am identificat câteva servicii relevante în urma cererii tale:<br /><br />"
            f"{lista_formatata}<br />"
            "Te rog să alegi <strong>exact denumirea serviciului dorit</strong> pentru a continua configurarea."
        )
    elif language_saved == "RU":
        prompt = (
            "По вашему запросу найдены следующие релевантные услуги:<br /><br />"
            f"{lista_formatata}<br />"
            "Пожалуйста, укажите <strong>точное название нужной услуги</strong>, чтобы мы могли продолжить."
        )
    else:
        prompt = (
            f"We identified a few relevant services in response to your request:<br /><br />"
            f"{lista_formatata}<br />"
            "Please select the <strong>exact name of the desired service</strong> to continue configuration."
        )

    return prompt

def check_response_en(message):
    msg = message.lower()

    general_keywords = ["general", "information", "overview", "description", "presentation", "details", "services"]
    preferinte_keywords = ["preferences", "custom", "personalized", "needs", "help", "choice", "criteria", "tailored"]

    general_score = max([fuzz.partial_ratio(msg, kw) for kw in general_keywords])
    preferinte_score = max([fuzz.partial_ratio(msg, kw) for kw in preferinte_keywords])

    if general_score > preferinte_score and general_score > 70:
        return "general"
    elif preferinte_score > general_score and preferinte_score > 70:
        return "preferinte"
    else:
        user_msg = f"""
        Classify the user's intent into ONE of the following three options:
        - general → if they are asking for general information about services
        - preferinte → if they are looking for a personalized service based on their needs
        - altceva → if the message is not relevant for classification, is a random question, or not related to IT services

        Message: "{message}"

        Respond with ONLY one word: general, preferinte, or altceva.
        """

        messages = [
            {"role": "user", "content": user_msg}
        ]

        response = ask_with_ai(messages).strip().lower()

        if response not in ["general", "preferinte", "altceva"]:
            return "altceva"
        
        return response

def check_response_ru(message):
    msg = message.lower()

    general_keywords = ["общая", "информация", "описание", "презентация", "детали", "услуги"]
    preferinte_keywords = ["предпочтения", "персонально", "нужды", "выбор", "помощь", "критерии", "персонализировано", "потребностей"]

    general_score = max([fuzz.partial_ratio(msg, kw) for kw in general_keywords])
    preferinte_score = max([fuzz.partial_ratio(msg, kw) for kw in preferinte_keywords])

    if general_score > preferinte_score and general_score > 70:
        return "general"
    elif preferinte_score > general_score and preferinte_score > 70:
        return "preferinte"
    else:
        user_msg = f"""
        Классифицируй намерение пользователя в ОДНУ из трёх категорий:
        - general → если он хочет общую информацию о наших услугах
        - preferinte → если он хочет индивидуальный или персонализированный сервис под свои нужды
        - altceva → если сообщение не связано с услугами, является вопросом не по теме или просто нерелевантно

        Сообщение: "{message}"

        Ответь ТОЛЬКО одним словом: general, preferinte или altceva.
        """

        messages = [
            {"role": "user", "content": user_msg}
        ]

        response = ask_with_ai(messages).strip().lower()

        if response not in ["general", "preferinte", "altceva"]:
            return "altceva"
        
        return response


def check_response(message):
    msg = message.lower()

    general_keywords = ["general", "informatii", "prezentare", "descriere", "detalii generale"]
    preferinte_keywords = ["preferinte", "personalizat", "nevoi", "ajutor", "alegere", "criterii"]

    general_score = max([fuzz.partial_ratio(msg, kw) for kw in general_keywords])
    preferinte_score = max([fuzz.partial_ratio(msg, kw) for kw in preferinte_keywords])

    if general_score > preferinte_score and general_score > 70:
        return "general"
    elif preferinte_score > general_score and preferinte_score > 70:
        return "preferinte"
    else:
        print("22222222")
        user_msg = f"""
        Clasifică intenția utilizatorului în UNA dintre cele trei opțiuni:
        - general → dacă vrea informații generale despre servicii
        - preferinte → dacă vrea un serviciu personalizat, în funcție de nevoi
        - altceva → dacă mesajul nu e relevant pentru clasificare , daca e o intrebare sau in general nu este legat de servicii IT

        Mesaj: "{message}"

        Răspunde DOAR cu un singur cuvânt: general, preferinte sau altceva.
        """
        messages = [
            {"role": "user", "content": user_msg}
        ]

        response = ask_with_ai(messages).strip().lower()
        
        # fallback în caz de răspuns greșit
        if response not in ["general", "preferinte", "altceva"]:
            return "altceva"
        
        return response
    

def check_language(user_response: str) -> str:
    prompt = (
        f'Utilizatorul a scris: "{user_response}".\n'
        "Trebuie să determini în ce limbă dorește să continue conversația: română (RO), rusă (RU) sau engleză (EN).\n\n"
        "Ia în considerare și expresii vagi, regionale, greșite sau colocviale. De exemplu:\n"
        "- Pentru română: „român”, „moldovenească”, „scrie în limba mea”, „romana fără diacritice”, „scrie normal”, „limba de aici”, „ca acasă”, etc.\n"
        "- Pentru rusă: „русский”, „румынский язык нет”, „по-русски”, „по нашему”, „российский”, „кирилица”, „давай по твоему”, etc.\n"
        "- Pentru engleză: „english”, „engleza”, „speak english”, „angla”, „write in english please”, „in international”, „no romanian”, „not russian”, „universal language”, etc.\n\n"
        "Acceptă și mesaje fără diacritice, cu greșeli, litere în alfabet greșit sau cuvinte mixte.\n\n"
        "Chiar dacă nu există indicii clare despre limba dorită, alege întotdeauna LIMBA cea mai probabilă dintre română (RO), rusă (RU) sau engleză (EN).\n\n"
        "Răspunde STRICT cu una dintre cele trei opțiuni, fără explicații:\n"
        "- RO\n"
        "- RU\n"
        "- EN\n\n"
        "Exemple:\n"
        "\"scrie ca la țară\" -> RO\n"
        "\"давай по-нашему\" -> RU\n"
        "\"romana\" -> RO\n"
        "\"rusa\" -> RU\n"
        "\"english\" -> EN\n"
        "\"angla\" -> EN\n"
        "\"please no russian\" -> EN\n"
        "\"write in my language\" -> EN\n"
        "\"moldoveneasca\" -> RO\n"
        "\"русский\" -> RU\n"
        "\"nu conteaza\" -> RO\n"
        "\"whatever\" -> EN\n"
        "\"ce vrei tu\" -> RO\n"
        "\"who is messi?\" -> EN\n\n"
        "Răspuns final:"
    )

    messages = [{"role": "system", "content": prompt}]
    response = ask_with_ai(messages)
    response = response.strip().upper()
    if response in {"RO", "RU", "EN"}:
        return response
    return "RO"


@app.route("/language", methods=["GET"])
def language():
    message = (
        "🌍 <strong>Alege limba / Choose your language / Выберите язык:</strong><br>"
        "<div style='text-align:center; font-size:1em; margin: 10px 0;'>"
        "🇷🇴 <em>Română</em> | 🇬🇧 <em>English</em> | 🇷🇺 <em>Русский</em>"
        "</div>"
    )
    return jsonify({"ask_name": message})

@app.route('/ip', methods=["POST", "GET"])
def ip():
    ip_list = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')
    user_ip = ip_list[0].strip()

    return jsonify({
        "ip": user_ip,
        "remote_addr": request.remote_addr,
        "x_forwarded_for": request.headers.get('X-Forwarded-For')
    })

@app.route("/start", methods=["GET", "POST"])
def start():
    # print("Start endpoint called", flush=True)
    user_data = request.get_json()
    interest = user_data.get("message", "prieten")
    # ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    # print("ip === ", ip)
    country = get_country_by_ip()
    preferinte["country"] = country
    # preferinte["country"] = country
    # print("country === ", country)
    check_language_rag = check_language(interest)
    if check_language_rag == "RO":
        language_saved = "RO"
        ask_name = (
            '👋 <strong style="font-size: 12;">Bun venit la '
            '<span style="color: #9333ea; text-shadow: 0 0 5px #d8b4fe, 0 0 10px #9333ea;">DigitalGrow</span>!</strong> 😊<br><br>'
            "Te pot ajuta cu:<br>"
            "📌 <strong>Serviciile disponibile</strong><br>"
            "🎯 Alegerea unui serviciu <strong>în funcție de preferințele tale</strong><br>"
            "🛒 Sau poate dorești direct să <strong>achiziționezi unul</strong>. 💼✨<br>"
        )

    elif check_language_rag == "RU":
        language_saved = "RU"
        ask_name = (
            '👋 <strong style="font-size: 12;">Добро пожаловать в '
            '<span style="color: #9333ea; text-shadow: 0 0 5px #d8b4fe, 0 0 10px #9333ea;">DigitalGrow</span>!</strong> 😊<br><br>'
            "Я могу помочь вам с:<br>"
            "📌 <strong>Доступными услугами</strong><br>"
            "🎯 Выбором услуги <strong>по вашим предпочтениям</strong><br>"
            "🛒 Или вы хотите сразу <strong>оформить заказ</strong>. 💼✨<br>"
        )

    else:
        language_saved = "EN"
        ask_name = (
            '👋 <strong style="font-size: 12;">Welcome to '
            '<span style="color: #9333ea; text-shadow: 0 0 5px #d8b4fe, 0 0 10px #9333ea;">DigitalGrow</span>!</strong> 😊<br><br>'
            "I can help you with:<br>"
            "📌 <strong>Available services</strong><br>"
            "🎯 Choosing a service <strong>based on your preferences</strong><br>"
            "🛒 Or maybe you’re ready to <strong>make a purchase</strong>. 💼✨<br>"
        )

    
    

    return jsonify({"ask_name": ask_name, "language": language_saved})

def build_service_prompt(categorii_unice, language_saved):
    emoji_list = [
        "💼", "🧠", "📱", "💻", "🛠️", "🎨", "🚀", "🧰", "📈", "📊", "🔧",
        "🖥️", "📦", "🧾", "🌐", "📣", "🤖", "🧑‍💻", "📇", "🗂️", "🖌️", "💡", "📍", "🆕"
    ]
    if language_saved == "RO":
        intro = (
            "Îți pot oferi o gamă variată de servicii IT specializate. <br><br>"
            "Te rog alege serviciul dorit din lista de mai jos și răspunde cu <strong>denumirea exactă</strong>.<br>\n\n"
            "<em>(Apasă sau scrie exact denumirea serviciului pentru a continua)</em><br><br>\n\n"
        )
    elif language_saved == "RU":
        intro = (
            "Я могу предложить вам широкий спектр IT-услуг. <br><br>"
            "Пожалуйста, выберите нужный сервис из списка ниже и ответьте с <strong>точным названием</strong>.<br>\n\n"
            "<em>(Нажмите или напишите точное название сервиса для продолжения)</em><br><br>\n\n"
        )
    else:
        intro = (   
            "I can offer you a wide range of IT services. <br><br>"
            "Please choose the desired service from the list below and respond with the <strong>exact name</strong>.<br>\n\n"
            "<em>(Click or write the exact name of the service to continue)</em><br><br>\n\n"
        )
    
    service_lines = []
    used_emojis = set()
    for categorie in categorii_unice:
        emoji = random.choice(emoji_list)
        
        # Evită repetițiile excesive dacă e posibil
        while emoji in used_emojis and len(used_emojis) < len(emoji_list):
            emoji = random.choice(emoji_list)
        used_emojis.add(emoji)
        
        line = f"{emoji} <strong>{categorie}</strong>"
        service_lines.append(line)
    
    prompt = intro + "<br>".join(service_lines)
    return prompt

def build_general_or_personal_prompt(language_saved):
    print("language_saved = ", language_saved)
    if language_saved == "RO":
        prompt = (
            "📌 Cum ai dori să continuăm?<br><br>"
            "🔍 Ai vrea să afli <strong>informații generale</strong> despre serviciile noastre?<br>"
            "🎯 Preferi să alegem un serviciu în funcție de <strong> nevoile și preferințele </strong> tale?<br><br>"
            "✍️ Te rugăm să scrii: <strong>general</strong> sau <strong>preferinte</strong> pentru a merge mai departe."
        )
    elif language_saved == "RU":
        prompt = (
            "📌 Как вы хотите продолжить?<br><br>"
            "🔍 Вы хотите узнать <strong>общие сведения</strong> о наших услугах?<br>"
            "🎯 Вы предпочитаете выбрать услугу в зависимости от <strong>ваших потребностей и предпочтений</strong>?<br><br>"
            "✍️ Пожалуйста, напишите: <strong>общая информация</strong> или <strong>предпочтения</strong> для продолжения."
        )
    else:
        prompt = (
            "📌 How would you like to continue?<br><br>"
            "🔍 Do you want to learn <strong>general information</strong> about our services?<br>"
            "🎯 Would you prefer to choose a service based on <strong>your needs and preferences</strong>?<br><br>"
            "✍️ Please write: <strong>general</strong> or <strong>preferences</strong> to continue."
        )
    return prompt

def build_service_prompt_2(categorii_unice, language_saved):
    emoji_list = [
        "💼", "🧠", "📱", "💻", "🛠️", "🎨", "🚀", "🧰", "📈", "📊", "🔧",
        "🖥️", "📦", "🧾", "🌐", "📣", "🤖", "🧑‍💻", "📇", "🗂️", "🖌️", "💡", "📍", "🆕"
    ]
    if language_saved == "RO":
        intro = (
            "<br><br> Te rog alege serviciul dorit din lista de mai jos și răspunde cu <strong>denumirea exactă</strong> : <br><br>"
        )
    elif language_saved == "RU":
        intro = (
            "<br><br> Пожалуйста, выберите нужный сервис из списка ниже и ответьте с <strong>точным названием</strong> : <br><br>"
        )
    else:
        intro = (
            "<br><br> Please choose the desired service from the list below and respond with the <strong>exact name</strong> : <br><br>"
        )

    service_lines = []
    used_emojis = set()
    for categorie in categorii_unice:
        emoji = random.choice(emoji_list)
        
        # Evită repetițiile excesive dacă e posibil
        while emoji in used_emojis and len(used_emojis) < len(emoji_list):
            emoji = random.choice(emoji_list)
        used_emojis.add(emoji)
        
        line = f"{emoji} <strong>{categorie}</strong>"
        service_lines.append(line)
    
    prompt = intro + "<br>".join(service_lines)
    return prompt


def check_budget(user_response: str) -> str:

    raw_numbers = re.findall(r"\d[\d\s]*\d|\d+", user_response)

    cleaned_numbers = []
    for num in raw_numbers:
        # Elimină spațiile din număr (ex: "50 000" → "50000")
        cleaned = num.replace(" ", "")
        if cleaned.isdigit():
            cleaned_numbers.append(int(cleaned))

    if cleaned_numbers:
        return str(max(cleaned_numbers))

    prompt = (
        f"Utilizatorul a spus: \"{user_response}\".\n"
        "Scop: Extrage o valoare numerică aproximativă exprimată în text ca buget (ex: 1200, 5000, 25000).\n\n"
        "Reguli:\n"
        "- Dacă sunt mai multe numere, returnează cel mai relevant (suma principală).\n"
        "- Dacă este exprimat doar în cuvinte (ex: „buget mare”, „peste o mie”), transformă-l într-un număr estimativ (ex: 10000).\n"
        "- Dacă nu există nicio valoare estimabilă, răspunde cu: NONE.\n\n"
        "Exemple:\n"
        "\"cam 3000\" → 3000\n"
        "\"între 5000 și 7000\" → 6000\n"
        "\"buget mare\" → 10000\n"
        "\"приблизительно 10000\" → 10000\n"
        "\"до 2000\" → 2000\n"
        "\"не știu\" → NONE\n"
        "\"depinde\" → NONE\n"
        "\"vreau doar să aflu\" → NONE\n"
    )

    messages = [
        {"role": "system", "content": "Extrage doar un număr (fără text). Dacă nu e clar, răspunde cu NONE."},
        {"role": "user", "content": prompt}
    ]

    try:
        answer = ask_with_ai(messages, temperature=0, max_tokens=10)
        answer = answer.strip().upper()

        if answer != "NONE":
            return answer
        else:
            return "NONE"
    except Exception as e:
        print(f"[EROARE] check_budget failed: {e}")
        return "NONE"


@app.route("/interests", methods=["POST"])
def interests():
    user_data = request.get_json()
    name = user_data.get("name", "prieten")
    language_saved = user_data.get("language", "RO")
    
    if language_saved == "RO":
        check = check_interest(name)
    elif language_saved == "RU":
        check = check_interest_ru(name)
    else:
        check = check_interest_en(name)

    print("check = ", check)

    print(language_saved)



    if check == "preferinte":
        if language_saved == "RO":
            reply = """
            💰 <strong>Haide să alegem un buget potrivit pentru serviciul dorit!</strong><br><br>
            Alege una dintre opțiunile de mai jos, sau scrie un buget estimativ dacă ai altă preferință:<br><br>
            🔹 <strong>10 000 MDL</strong> – Proiect simplu, ideal pentru un început clar și eficient<br>
            🔸 <strong>20 000 MDL</strong> – Echilibru între funcționalitate și personalizare<br>
            🌟 <strong>50 000 MDL+</strong> – Soluții avansate, complete, cu funcții extinse și design premium<br><br>
            ✍️ <em>Ne poți scrie direct o altă sumă dacă ai un buget diferit în minte!</em>
            """
            return jsonify({"ask_interests": reply})
        elif language_saved == "RU":
            reply = """
            💰 <strong>Давайте выберем подходящий бюджет для желаемого сервиса!</strong><br><br>
            Выберите один из вариантов ниже или напишите приблизительную сумму, если у тебя есть другое предпочтение:<br><br>
            🔹 <strong>10 000 MDL</strong> – Простой проект, идеально подходит для четкого начала и эффективности<br>
            🔸 <strong>20 000 MDL</strong> – Баланс между функциональностью и персонализацией<br>
            🌟 <strong>50 000 MDL+</strong> – Расширенные решения, полные, с расширенными функциями и премиальным дизайном<br><br>
            ✍️ <em>Можешь написать другую сумму, если у тебя другой бюджет!</em>
            """
            return jsonify({"ask_interests": reply})
        else:
            reply = """
            💰 <strong>Let's choose a suitable budget for the desired service!</strong><br><br>
            Choose one of the options below or write an approximate amount if you have a different preference:<br><br>
            🔹 <strong>10 000 MDL</strong> – Simple project, ideal for clear start and efficiency<br>
            🔸 <strong>20 000 MDL</strong> – Balance between functionality and personalization<br>
            🌟 <strong>50 000 MDL+</strong> – Advanced solutions, complete, with extended features and premium design<br><br>
            ✍️ <em>You can write a different amount if you have a different budget!</em>
            """
            return jsonify({"ask_interests": reply})

    if "produs_informații" in check or "general" in check:
        if language_saved == "RO":
            reply = build_service_prompt(categorii_unice, language_saved)
        elif language_saved == "RU":
            reply = build_service_prompt(categorii_unice_ru, language_saved)
        else:
            reply = build_service_prompt(categorii_unice_en, language_saved)
        print(reply)
        return jsonify({"ask_interests": reply})

    elif check == "comandă":
        if language_saved == "RO":
            mesaj = (
                "🎉 Mǎ bucur că vrei să plasezi o comandă!<br><br>"
                "📋 Hai să parcurgem împreună câțiva pași simpli pentru a înregistra comanda cu succes. 🚀<br><br>"
            )
        elif language_saved == "RU":
            mesaj = (
                "🎉 Мне приятно, что вы хотите сделать заказ!<br><br>"
                "📋 Давайте пройдем вместе несколько простых шагов для успешной регистрации заказа. 🚀<br><br>"
            )
        else:
            mesaj = (
                "🎉 I'm glad you want to place an order!<br><br>"
                "📋 Let's go through a few simple steps to successfully register the order. 🚀<br><br>"
            )

        
        if language_saved == "RO":
            mesaj1 = build_service_prompt_2(categorii_unice, language_saved)
            mesaj = mesaj + mesaj1
        elif language_saved == "RU":
            mesaj1 = build_service_prompt_2(categorii_unice_ru, language_saved)
            mesaj = mesaj + mesaj1
        else:
            mesaj1 = build_service_prompt_2(categorii_unice_en, language_saved)
            mesaj = mesaj + mesaj1
                
        return jsonify({"ask_interests": mesaj})
    else:
        # print(name)
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris : '{name}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>❓ Te rugăm să ne spui dacă:<br>"
                "👉 vrei să <strong>afli mai multe informații</strong> despre serviciile disponibile<br>"
                "🎯 preferi să <strong>alegi un serviciu în funcție de preferințele tale</strong><br>"
                "🛒 sau vrei să <strong>faci o comandă</strong> direct.<br><br>"
            )
            reply = mesaj
        elif language_saved == "RU":
            prompt = (
                f"Utilizatorul a scris : '{name}'.\n\n"
                "Не говори никогда „Привет”, всегда начинай с вступительных слов, потому что мы уже общаемся и знакомы. "
                "Пиши политичный, дружелюбный и естественный текст, который:\n"
                "1. Быстро отвечает на то, что сказал пользователь. "
                "2. Краткий, теплый, эмпатичный и дружелюбный. "
                "Не более 2-3 предложений.\n"
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>❓ Пожалуйста, скажите, хотите ли вы:<br>"
                "👉 вы хотите <strong>узнать больше информации</strong> о доступных услугах<br>"
                "🎯 предпочитаете <strong>выбрать услугу по вашим предпочтениям</strong><br>"
                "🛒 или вы хотите <strong>сделать заказ</strong> напрямую.<br><br>"
            )
            reply = mesaj
        else:

            prompt = (
                f"The user wrote: '{name}'.\n\n"
                "Never say greetings like 'Hi' or similar intros, because you're already in a conversation and know the user. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. Feels warm, empathetic, and friendly, in no more than 2–3 short sentences.\n"
                "Do not use quotation marks and do not explain what you're doing — write only the final message for the user."
            )
            messages = [{"role": "system", "content": prompt}]
            message = ask_with_ai(messages).strip()
            message += (
                "<br><br>❓ Please let us know:<br>"
                "👉 you want to <strong>learn more about the available services</strong><br>"
                "🎯 you'd prefer to <strong>choose a service based on your preferences</strong><br>"
                "🛒 or you're ready to <strong>place an order</strong> directly.<br><br>"
            )
            reply = message

    return jsonify({"ask_interests": reply})


@app.route("/criteria", methods=["POST"])
def criteria():
    user_data = request.get_json()
    name = user_data.get("name", "prieten")
    message = user_data.get("message", "")
    language_saved = user_data.get("language", "RO")
    if language_saved == "RO":
        response = check_response(message)
    elif language_saved == "RU":
        response = check_response_ru(message)
    else:
        response = check_response_en(message)



    print("response = ", response)
    if response == "general":
        # reply = "general"
        if language_saved == "RO":
            reply = build_service_prompt(categorii_unice, language_saved)
        elif language_saved == "RU":
            reply = build_service_prompt(categorii_unice_ru, language_saved)
        else:
            reply = build_service_prompt(categorii_unice_en, language_saved)

    elif response == "preferinte":
        if language_saved == "RO":
            reply = """
            💰 <strong>Haide să alegem un buget potrivit pentru serviciul dorit!</strong><br><br>
            Alege una dintre opțiunile de mai jos, sau scrie un buget estimativ dacă ai altă preferință:<br><br>
            🔹 <strong>10 000 MDL</strong> – Proiect simplu, ideal pentru un început clar și eficient<br>
            🔸 <strong>20 000 MDL</strong> – Echilibru între funcționalitate și personalizare<br>
            🌟 <strong>50 000 MDL+</strong> – Soluții avansate, complete, cu funcții extinse și design premium<br><br>
            ✍️ <em>Ne poți scrie direct o altă sumă dacă ai un buget diferit în minte!</em>
            """
        elif language_saved == "RU":
            reply = """
            💰 <strong>Давайте выберем подходящий бюджет для желаемого сервиса!</strong><br><br>
            Выберите один из вариантов ниже или напишите приблизительную сумму, если у тебя есть другое предпочтение:<br><br>
            🔹 <strong>10 000 MDL</strong> – Простой проект, идеально подходит для четкого начала и эффективности<br>
            🔸 <strong>20 000 MDL</strong> – Баланс между функциональностью и персонализацией<br>
            🌟 <strong>50 000 MDL+</strong> – Расширенные решения, полные, с расширенными функциями и премиальным дизайном<br><br>
            ✍️ <em>Можешь написать другую сумму, если у тебя другой бюджет!</em>
            """
        else:
            reply = """
            💰 <strong>Let's choose a suitable budget for the desired service!</strong><br><br>
            Choose one of the options below or write an approximate amount if you have a different preference:<br><br>
            🔹 <strong>10 000 MDL</strong> – Simple project, ideal for clear start and efficiency<br>
            🔸 <strong>20 000 MDL</strong> – Balance between functionality and personalization<br>
            🌟 <strong>50 000 MDL+</strong> – Advanced solutions, complete, with extended features and premium design<br><br>
            ✍️ <em>You can write a different amount if you have a different budget!</em>
            """
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris : '{message}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>✍️ Te rugăm să scrii: <strong>general</strong> sau <strong>preferinte</strong> pentru a merge mai departe."  
            )
            reply = mesaj
        elif language_saved == "RU":
            prompt = (
                f"Utilizatorul a scris : '{message}'.\n\n"
                "Не говори никогда „Привет”, всегда начинай с вступительных слов, потому что мы уже общаемся и знакомы. "
                "Пиши политичный, дружелюбный и естественный текст, который:\n"
                "1. Быстро отвечает на то, что сказал пользователь. "
                "2. Краткий, теплый, эмпатичный и дружелюбный. "
                "Не более 2-3 предложений.\n"
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "✍️ Пожалуйста, напишите: <strong>общая информация</strong> или <strong>предпочтения</strong> для продолжения."
            )
            reply = mesaj
        else:
            prompt = (
                f"The user wrote: '{message}'.\n\n"
                "Never say greetings like 'Hi' or similar intros, because you're already in a conversation and know the user. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. Feels warm, empathetic, and friendly, in no more than 2–3 short sentences.\n"
                "Do not use quotation marks and do not explain what you're doing — write only the final message for the user."
            )
            messages = [{"role": "system", "content": prompt}]
            message = ask_with_ai(messages).strip()
            message += (
                "✍️ Please write: <strong>general</strong> or <strong>preferences</strong> to continue."
            )
            reply = message

    return jsonify({"message": reply})


@app.route("/budget", methods=["POST"])
def budget():
    data = request.json
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")
    budget_ = check_budget(message)
    print("budget_ = ", budget_)
    if budget_ == "NONE":
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>💬 Apropo, ca să pot veni cu sugestii potrivite, îmi poți spune cam ce buget ai în minte? (în MDL)"
                "<br>💸 <strong>&lt;2000 MDL</strong> – buget mic<br>"
                "💶 <strong>2000–10 000 MDL</strong> – buget mediu<br>"
                "💰 <strong>10 000–25 000 MDL</strong> – buget generos<br>"
                "💎 <strong>50 000+ MDL</strong> – soluții avansate<br>"
                "✍️ Sau scrie pur și simplu suma estimativă."
            )
        elif language_saved == "RU":
            prompt = (
                f"Пользователь выбрал категорию: '{message}'.\n\n"
                "Никогда не начинай с приветствия или вступительных фраз, потому что мы уже ведем диалог. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко реагирует на выбор пользователя.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2–3 предложений.\n"
                "Не используй кавычки и не объясняй, что ты делаешь — просто напиши финальный текст для пользователя."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>💬 Кстати, чтобы предложить оптимальные варианты, подскажите, пожалуйста, какой у вас ориентировочный бюджет? (в MDL)"
                "<br>💸 <strong>&lt;2000 MDL</strong> – небольшой бюджет<br>"
                "💶 <strong>2000–10 000 MDL</strong> – средний бюджет<br>"
                "💰 <strong>10 000–25 000 MDL</strong> – щедрый бюджет<br>"
                "💎 <strong>50 000+ MDL</strong> – продвинутые решения<br>"
                "✍️ Или просто напишите примерную сумму."
            )
        elif language_saved == "EN":
            prompt = (
                f"The user selected the category: '{message}'.\n\n"
                "Never say 'Hi' or use introductory phrases, since we're already in an ongoing conversation. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to the user's input.\n"
                "2. Is warm, empathetic, and friendly – no more than 2–3 sentences.\n"
                "Do not use quotation marks or explain what you're doing — just write the final message for the user."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>💬 By the way, to offer the most suitable options, could you please let me know your approximate budget? (in MDL)"
                "<br>💸 <strong>&lt;2000 MDL</strong> – small budget<br>"
                "💶 <strong>2000–10 000 MDL</strong> – medium budget<br>"
                "💰 <strong>10 000–25 000 MDL</strong> – generous budget<br>"
                "💎 <strong>50 000+ MDL</strong> – advanced solutions<br>"
                "✍️ Or feel free to just write an estimated amount."
            )

        return jsonify({"message": mesaj})
    else:
        preferinte["BUDGET"] = budget_
        if language_saved == "RO":
            mesaj = (
                f"✅ Am notat bugetul tău: <strong>{budget_} MDL</strong>.<br><br>"
                "🌐 În ce limbă ai prefera să fie oferit serviciul?<br><br>"
                "🇷🇴 <strong>Română</strong> – comunicare completă în limba română<br>"
                "🇷🇺 <strong>Русский</strong> – обслуживание на русском языке<br>"
                "🇬🇧 <strong>English</strong> – full service in English<br>"
                "🌍 <strong>Multilingv</strong> – combinăm limbile după preferință<br><br>"
                "✍️ Te rog scrie limba dorită sau alege <strong>multilingv</strong> dacă dorești flexibilitate."
            )
        elif language_saved == "RU":
            mesaj = (
                f"✅ Ваш бюджет был зафиксирован: <strong>{budget_} MDL</strong>.<br><br>"
                "🌐 На каком языке вы предпочитаете получить услугу?<br><br>"
                "🇷🇴 <strong>Română</strong> – полное обслуживание на румынском языке<br>"
                "🇷🇺 <strong>Русский</strong> – полное обслуживание на русском языке<br>"
                "🇬🇧 <strong>English</strong> – полное обслуживание на английском языке<br>"
                "🌍 <strong>Мультиязычный</strong> – комбинируем языки по вашему выбору<br><br>"
                "✍️ Пожалуйста, укажите желаемый язык или выберите <strong>Мультиязычный</strong> для гибкости."
            )
        elif language_saved == "EN":
            mesaj = (
                f"✅ Your budget has been saved: <strong>{budget_} MDL</strong>.<br><br>"
                "🌐 What language would you prefer the service to be in?<br><br>"
                "🇷🇴 <strong>Română</strong> – full communication in Romanian<br>"
                "🇷🇺 <strong>Русский</strong> – full communication in Russian<br>"
                "🇬🇧 <strong>English</strong> – full communication in English<br>"
                "🌍 <strong>Multilingual</strong> – we can combine languages as needed<br><br>"
                "✍️ Please write your preferred language or choose <strong>Multilingual</strong> for flexibility."
            )

        return jsonify({"message": mesaj})


def normalize_text(text):
    # Fără diacritice + lowercase
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower()


def check_response_comanda(user_message, language_saved):
    if language_saved == "RO":
        prompt = (
            f"Utilizatorul a spus: '{user_message}'\n\n"
            "Clasifică mesajul utilizatorului într-una dintre următoarele categorii, răspunzând cu un singur cuvânt:\n\n"
            "- NU: dacă mesajul exprimă o refuzare, o ezitare sau o lipsă de interes. "
            "Exemple: 'Nu', 'Nu acum', 'Nu sunt sigur', 'Mai târziu', 'Nu am comandat', 'Nu am mai comandat', 'Nu am comandat dar as vrea' etc.\n\n"
            "- DA: dacă mesajul exprimă o intenție clară și pozitivă, cum ar fi o confirmare, o dorință de a merge mai departe, un interes real sau dacă utilizatorul afirmă că a mai comandat de la noi, chiar dacă nu spune explicit că dorește din nou. "
            "Exemple: 'Da', 'Sigur', 'Aș dori', 'Sunt interesat', 'Vreau acel produs', 'Desigur', 'Perfect', 'sunt curios', 'am mai avut comandă', 'am mai comandat de la voi', etc.\n\n"
            "- ALTCEVA: dacă mesajul nu se încadrează în niciuna dintre categoriile de mai sus, de exemplu dacă utilizatorul pune o întrebare nespecifică, schimbă subiectul sau oferă informații fără legătură cu decizia, comanda sau interesul față de produs.\n\n"
        )
    elif language_saved == "RU":
        prompt = (
            f"Пользователь написал: '{user_message}'\n\n"
            "Классифицируй сообщение пользователя в одну из следующих категорий, отвечая одним словом:\n\n"
            "- NU: если сообщение выражает отказ, колебание или отсутствие интереса. "
            "Примеры: 'Нет', 'Не сейчас', 'Я не уверен', 'Позже', 'Я не заказывал', 'Не заказывал, но хотел бы' и т.д.\n\n"
            "- DA: если сообщение выражает явное и положительное намерение, например подтверждение, желание продолжить, реальный интерес, "
            "или если пользователь сообщает, что уже заказывал у нас, даже если не говорит прямо, что хочет снова. "
            "Примеры: 'Да', 'Конечно', 'Я бы хотел', 'Интересно', 'Я хочу этот продукт', 'Идеально', 'Любопытно', 'Я уже заказывал' и т.д.\n\n"
            "- ALTCEVA: если сообщение не подходит ни под одну из вышеуказанных категорий, например, если пользователь задаёт общий вопрос, меняет тему или сообщает не относящуюся к делу информацию.\n\n"
        )
    else:
        prompt = (
            f"The user said: '{user_message}'\n\n"
            "Classify the user's message into one of the following categories, responding with a single word:\n\n"
            "- NU: if the message expresses refusal, hesitation, or lack of interest. "
            "Examples: 'No', 'Not now', 'I'm not sure', 'Later', 'I didn't order', 'I haven't ordered', 'I didn't order but would like to' etc.\n\n"
            "- DA: if the message expresses a clear and positive intention, such as confirmation, willingness to proceed, genuine interest, "
            "or if the user states they have ordered from us before, even if they don't explicitly say they want to order again. "
            "Examples: 'Yes', 'Sure', 'I would like', 'I'm interested', 'I want that product', 'Of course', 'Perfect', 'I'm curious', 'I have ordered before', etc.\n\n"
            "- ALTCEVA: if the message doesn't fit any of the above categories, for example if the user asks a non-specific question, changes the subject, or provides unrelated information.\n\n"
        )
        

    messages = [{"role": "system", "content": prompt}]
    result = ask_with_ai(messages).strip().upper()
    return result


def check_preference_language_en(message: str) -> str:
    msg = message.lower()
    language_keywords = {
        "romana": [
            "romanian", "romana", "română", "limba romana", "in romanian", "rom"
        ],
        "rusa": [
            "russian", "русский", "rusa", "in russian", "russian language", "ru"
        ],
        "engleza": [
            "english", "eng", "engleza", "engleză", "in english", "english language", "en"
        ],
        "multilingv": [
            "multilingual", "multi-language", "mixed languages", "any language", "all languages", 
            "combine languages", "flexible", "multilingv", "more languages", "doesn’t matter"
        ]
    }

    normalized = normalize_text(message)
    tokens = re.findall(r'\b\w+\b', normalized)

    for lang, keywords in language_keywords.items():
        for kw in keywords:
            kw_norm = normalize_text(kw)
            if kw_norm in tokens or kw_norm in normalized:
                return lang

    best_match = "necunoscut"
    best_score = 0
    for lang, keywords in language_keywords.items():
        for kw in keywords:
            score = fuzz.partial_ratio(msg, kw)
            if score > best_score:
                best_score = score
                best_match = lang

    return best_match if best_score > 85 else "necunoscut"


def check_preference_language_ru(message: str) -> str:
    msg = message.lower()
    language_keywords = {
        "romana": [
            "румынский", "на румынском", "румынском", "romana", "română", "limba română", "in romana"
        ],
        "rusa": [
            "русский", "на русском", "по-русски", "по русски", "rusa", "russian", "limba rusă", "рус", "ру"
        ],
        "engleza": [
            "английский", "по-английски", "на английском", "english", "eng", "engleza", "engleză", "limba engleză"
        ],
        "multilingv": [
            "много языков", "все языки", "любой язык", "на любом языке", "смешанные языки", "гибко", 
            "multi-language", "multilingua", "multilingv", "languages combined", "multilingual" , "Мультиязычный"
        ]
    }

    normalized = normalize_text(message)
    tokens = re.findall(r'\b\w+\b', normalized)

    for lang, keywords in language_keywords.items():
        for kw in keywords:
            kw_norm = normalize_text(kw)
            if kw_norm in tokens or kw_norm in normalized:
                return lang

    best_match = "necunoscut"
    best_score = 0
    for lang, keywords in language_keywords.items():
        for kw in keywords:
            score = fuzz.partial_ratio(msg, kw)
            if score > best_score:
                best_score = score
                best_match = lang

    return best_match if best_score > 85 else "necunoscut"


def check_preference_language(message: str) -> str:

    msg = message.lower()
    language_keywords = {
        "romana": [
            "romana", "română", "limba română", "in romana" , "româna", "ромынский", "romanian", "limba romana"
        ],
        "rusa": [
            "rusa", "rusă", "limba rusă", "rusește", "русский", "на русском", "по русски", "russian", "rusă"
        ],
        "engleza": [
            "engleza", "engleză", "limba engleză", "englește", "english", "angla", "in engleza", "eng", "английский", "limba engleza"
        ],
        "multilingv": [
            "multilingv", "mai multe limbi", "toate limbile", "combinat", "flexibil", "multi-language", "multilanguage", 
            "multilingua", "multi limbi", "mix limbi", "multilimba", "orice limba", "indiferent de limba", "orice limbă", 
            "на любом языке", "any language", "languages combined"
        ]
    }

    normalized = normalize_text(message)
    tokens = re.findall(r'\b\w+\b', normalized)

    for lang, keywords in language_keywords.items():
        for kw in keywords:
            kw_norm = normalize_text(kw)
            if kw_norm in tokens or kw_norm in normalized:
                return lang 

    # Fuzzy matching
    best_match = "necunoscut"
    best_score = 0
    for lang, keywords in language_keywords.items():
        for kw in keywords:
            print("kw = ", kw)
            score = fuzz.partial_ratio(msg, kw)
            print("score = ", score)
            if score > best_score:
                best_score = score
                best_match = lang

    if best_score > 85:
        print("best_match = ", best_match)
        return best_match
    else:
        return "necunoscut"


@app.route("/preference_language", methods=["POST"])
def preference_language():
    data = request.json
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")
    if language_saved == "RO":
        preference_language = check_preference_language(message)
    elif language_saved == "RU":
        preference_language = check_preference_language_ru(message)
    else:
        preference_language = check_preference_language_en(message)

    if preference_language == "necunoscut":
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>🌍 <strong>Ca să-ți ofer informațiile cât mai potrivit, îmi poți spune în ce limbă preferi să fie serviciul?</strong><br><br>"
                "🟡 <strong>Romana</strong> – limba română<br>"
                "🔵 <strong>Rusa</strong> – русский язык<br>"
                "🟢 <strong>Engleza</strong> – english<br>"
                "🌐 <strong>Multilingv</strong> – mai multe limbi combinate, după preferințe"
            )
        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал категорию: '{message}'.\n\n"
                "Никогда не начинай с «Здравствуйте» или других вводных, так как мы уже ведем диалог и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Должно быть теплым, эмпатичным и дружелюбным – не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что ты делаешь – просто напиши итоговое сообщение для пользователя."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>🌍 <strong>Чтобы дать тебе максимально точную информацию, напиши, пожалуйста, на каком языке тебе удобно общаться:</strong><br><br>"
                "🟡 <strong>Румынский</strong> – limba română<br>"
                "🔵 <strong>Русский</strong> – на русском языке<br>"
                "🟢 <strong>Английский</strong> – english<br>"
                "🌐 <strong>Мультиязычный</strong> – комбинируем языки по твоим предпочтениям"
            )
        elif language_saved == "EN":
            prompt = (
                f"The user wrote the category: '{message}'.\n\n"
                "Never start with 'Hello' or any kind of introduction – we're already in a conversation and know each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. Is warm, empathetic, and friendly – no more than 2–3 sentences.\n"
                "Don't use quotation marks or explain what you're doing – just return the final message for the user."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>🌍 <strong>To offer you the most relevant information, could you tell me your preferred language?</strong><br><br>"
                "🟡 <strong>Romanian</strong> – limba română<br>"
                "🔵 <strong>Russian</strong> – на русском языке<br>"
                "🟢 <strong>English</strong> – full communication in English<br>"
                "🌐 <strong>Multilingual</strong> – a mix of languages based on your preferences"
            )
        
        return jsonify({"message": mesaj})
    else:

        preferinte["Limba_Serviciului"] = preference_language
        if language_saved == "RO":
            reply = (
                "💡 <strong>Super! Spune-mi, te rog, ce funcționalități ți-ar plăcea să includă serviciul?</strong><br><br>"
                "📌 De exemplu: <em>„Platformă de vânzări online cu plată prin card”</em> sau <em>„Pagină de prezentare pentru un eveniment”</em> , <em>„Site cu ChatBot Inteligent + CRM”</em> etc.<br><br>"
                "✍️ Poți scrie liber ce ai în minte, iar noi îți vom propune opțiuni potrivite."
            )
        elif language_saved == "RU":
            reply = (
                "💡 <strong>Супер! Скажите, пожалуйста, какие функциональные возможности вы хотели бы включить в услугу?</strong><br><br>"
                "📌 Например: <em>„Платформа для онлайн-продаж с платежной картой”</em> или <em>„Страница для презентации мероприятия”</em> , <em>„Сайт с Интеллектуальным Чатботом + CRM”</em> и т.д.<br><br>"
                "✍️ Можете написать, что угодно, и мы предложим вам подходящие варианты."
            )
        elif language_saved == "EN":
            reply = (   
                "💡 <strong>Super! Tell me, please, what features would you like to include in the service?</strong><br><br>"
                "📌 For example: <em>„Online sales platform with card payment”</em> or <em>„Presentation page for an event”</em> , <em>„Website with Intelligent ChatBot + CRM”</em> etc.<br><br>"
                "✍️ You can write anything you want, and we'll suggest suitable options."
            )
        
        return jsonify({"message": reply})

def check_functionalities_with_ai(message, all_descriptions):
    descriptions_text = "\n\n".join(all_descriptions)
    prompt = f"""
    Ești un consultant digital care ajută clienții să găsească serviciile potrivite dintr-o listă de oferte. Ai mai jos o listă de servicii digitale disponibile, fiecare cu nume și descriere. 

    Un utilizator a trimis acest mesaj:
    "{message}"

    Scopul tău este să identifici, din lista de mai jos:
    1. Serviciile care se potrivesc DIRECT cu ceea ce spune utilizatorul (funcționalități, dorințe, scopuri).
    2. Dacă aceste funcționalități sunt ACOPERITE (parțial sau complet) de un pachet, include în rezultat DOAR UN SINGUR PACHET relevant.
    - Alege pachetul care acoperă cele mai multe dintre funcționalitățile potrivite.
    - Nu include pachete care nu au legătură cu cererea utilizatorului.
    - Nu include mai mult de un pachet.

    🔒 REGULI IMPORTANTE:
    - Incearca mereu sa returnezei 2-3 servicii daca este posibil , daca nu returneaza cate trebuie
    - Nu returna pachete decât dacă acoperă CLAR funcționalitățile menționate.
    - Nu inventa funcționalități care nu există în lista de servicii.
    - NU returna nimic dacă potrivirea este vagă sau generală.
    - Fii selectiv și profesionist ca un vânzător real.

    📤 Outputul trebuie să fie:
    - O listă de nume de servicii separate prin `;` (fără ghilimele, explicații sau alte caractere).
    - Fără introduceri, concluzii sau text suplimentar.
    - Dacă nu identifici nimic relevant, returnează exact: `NONE`

    Serviciile disponibile:
    {descriptions_text}
    """
    messages = [{"role": "system", "content": prompt}]
    return ask_with_ai(messages)



def parse_pret(pret_str):
    # Extrage doar cifrele și returnează ca int (ex: '15 000' -> 15000)
    pret_str = str(pret_str)
    pret_clean = re.sub(r"[^\d]", "", pret_str)
    return int(pret_clean) if pret_clean else 0

def filtreaza_servicii_dupa_buget(servicii_dict, buget_str):
    buget = parse_pret(buget_str)
    rezultate = {}
    
    for nume_serviciu, detalii in servicii_dict.items():
        pret_md = parse_pret(detalii.get("pret_md", "0"))
        pret_ue = parse_pret(detalii.get("pret_ue", "0"))
        pret_reducere = parse_pret(detalii.get("reducere", "0"))

        if preferinte.get("country", "MD") == "MD":
            if pret_reducere <= buget :
                rezultate[nume_serviciu] = detalii
        else:
            if pret_ue <= buget :
                rezultate[nume_serviciu] = detalii

    return rezultate


@app.route("/functionalities", methods=["POST"])
def functionalities():
    data = request.json
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")
    preferinte["Preferintele_Utilizatorului_Cautare"] = message;
    print("language_saved = ", language_saved)
    servicii_dict = extract_servicii_dict(language_saved)
    print("servicii_dict = ", servicii_dict)
    buget = "DA"
    servicii_potrivite = filtreaza_servicii_dupa_buget(servicii_dict, preferinte.get("BUDGET", ""))
    func111 = check_functionalities_with_ai(message, servicii_potrivite)
    if func111 == "NONE":
        buget = "NU"

    length_servicii_potrivite_buget = len(servicii_potrivite)
    print("length_servicii_potrivite_buget = ", length_servicii_potrivite_buget)
    if length_servicii_potrivite_buget == 0:
        func = check_functionalities_with_ai(message, servicii_dict)

        if func == "NONE":
            if language_saved == "RO":
                prompt = (
                    f"Utilizatorul a scris serviciul: '{message}'.\n\n"
                    "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                    "Scrie un mesaj politicos, prietenos și natural, care:\n"
                    "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                    "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                    "Nu mai mult de 2-3 propoziții.\n"
                    "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                mesaj += (
                    "<br><br>❗️ Din ce ai scris, nu am reușit să identific un serviciu potrivit pentru nevoia ta."
                    "<br>💬 Te rog să-mi spui mai clar ce funcționalități ți-ar plăcea să aibă – de exemplu: <em>„platformă de vânzare produse online”, „site de prezentare cu 3-5 pagini”, „creare logo”</em> etc."
                    "<br><br>🔍 Cu cât mai clar, cu atât mai ușor îți pot recomanda variante potrivite!"
                )
                return jsonify({"message": mesaj})
            elif language_saved == "RU":
                prompt = (
                    f"Пользователь указал услугу: '{message}'.\n\n"
                    "Никогда не начинай с «Здравствуйте» или других вводных фраз — мы уже ведём диалог и знакомы. "
                    "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                    "1. Кратко отвечает на сообщение пользователя.\n"
                    "2. Будет тёплым, доброжелательным и искренним.\n"
                    "Не более 2–3 предложений.\n"
                    "Не используй кавычки и не объясняй свои действия — просто напиши итоговое сообщение для пользователя."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                mesaj += (
                    "<br><br>❗️ Из того, что вы написали, я не смог определить подходящую услугу под ваш запрос."
                    "<br>💬 Пожалуйста, опишите более конкретно, какие функции или решения вы ищете – например: <em>«онлайн-платформа для продажи товаров», «сайт-презентация на 3–5 страниц», «разработка логотипа»</em> и т.д."
                    "<br><br>🔍 Чем точнее описание, тем проще будет подобрать для вас подходящие варианты!"
                )
                return jsonify({"message": mesaj})
            elif language_saved == "EN":
                prompt = (
                    f"The user wrote the service: '{message}'.\n\n"
                    "Never start with “Hello” or any kind of introduction – we’re already in an ongoing conversation. "
                    "Write a polite, friendly, and natural message that:\n"
                    "1. Briefly responds to what the user said.\n"
                    "2. Sounds warm, kind, and empathetic.\n"
                    "No more than 2–3 short sentences.\n"
                    "Don’t use quotation marks or explain your logic – just write the final message the user will see."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                mesaj += (
                    "<br><br>❗️ From what you wrote, I couldn’t quite identify a specific service that fits your request."
                    "<br>💬 Please tell me a bit more clearly what kind of features or solution you're looking for – for example: <em>“online store platform”, “presentation website with 3–5 pages”, “logo creation”</em>, etc."
                    "<br><br>🔍 The clearer you are, the better suggestions I can offer!"
                )
                return jsonify({"message": mesaj})
                
        else:
            if ";" in func:
                splited_func = func.split(";")
                preferinte["Produs_Pentru_Comanda"] = splited_func
            elif "\n" in func:
                splited_func = func.split("\n")
                preferinte["Produs_Pentru_Comanda"] = splited_func
            else:
                splited_func = [func]
                preferinte["Produs_Pentru_Comanda"] = splited_func

            mesaj = ""
            for i in splited_func:
                
                detalii = extract_info(i, language_saved)
                
                if detalii:
                    descriere = detalii.get("descriere", "N/A")
                    beneficii = detalii.get("beneficii", "N/A")
                    pret_md = detalii.get("pret_md", "N/A")
                    pret_ue = detalii.get("pret_ue", "N/A")
                    pret_reducere = detalii.get("reducere", "N/A")
                    country = preferinte.get("country", "")

                    if language_saved == "RO":
                        if country == "MD":
                            mesaj += (
                                f"✅ Iată toate detaliile despre <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                                f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                                f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                                # f"🇪🇺 <strong>Preț pentru Uniunea Europeană:</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )
                        else:
                            mesaj += (
                                f"✅ Iată toate detaliile despre <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                                # f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                                # f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                # f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                # f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                                f"🇪🇺 <strong>Preț :</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )
                    elif language_saved == "RU":
                        if preferinte.get("country", "") == "MD":
                            mesaj += (
                                f"✅ Вот вся информация о <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                                f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                                f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас он со СКИДКОЙ и доступен всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                                # f"🇪🇺 <strong>Цена для Европейского Союза:</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )
                        else:
                            mesaj += (
                                f"✅ Вот вся информация о <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                                # f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                                # f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас он со СКИДКОЙ и доступен всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                # f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                # f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                                f"🇪🇺 <strong>Цена :</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )

                    elif language_saved == "EN":
                        if preferinte.get("country", "") == "MD":
                            mesaj += (
                                f"✅ Here are all the details about <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                                f"💸 <strong>📢 Great news for you!</strong><br />"
                                f"This product used to cost <s>{pret_md} MDL</s>, but now it is AVAILABLE WITH A DISCOUNT for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                f"💥 <strong>You save {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                f"🎯 <em>The price is valid only for a limited time!</em><br /><br />"
                                # f"🇪🇺 <strong>Price for the European Union:</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )
                        else:
                            mesaj += (
                                f"✅ Here are all the details about <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                                # f"💸 <strong>📢 Great news for you!</strong><br />"
                                # f"This product used to cost <s>{pret_md} MDL</s>, but now it is AVAILABLE WITH A DISCOUNT for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                # f"💥 <strong>You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!</strong><br />"
                                # f"🎯 <em>The price is valid only for a limited time!</em><br /><br />"
                                f"🇪🇺 <strong>Price :</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )

            if language_saved == "RO":
                if buget == "NU":
                    mesaj += (
                        "❗️ <strong>Nu sunt servicii potrivite pentru bugetul ales , dar am gasit dupa functionalitatile alese</strong><br>"
                    )
                    mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"
            elif language_saved == "RU":
                if buget == "NU":
                    mesaj += (
                        "❗️ <strong>Не найдено услуг, подходящих для выбранного бюджета, но мы нашли варианты, соответствующие выбранным функциональным возможностям</strong><br>"
                    )
                    mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"
            elif language_saved == "EN":
                if buget == "NU":
                    mesaj += (
                        "❗️ <strong>No services suitable for the chosen budget, but we found options that match the selected functional features</strong><br>"
                    )
                    mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"
            

            

            if language_saved == "RO":
                mesaj += "<br>💬 <em>Dorești să faci o comandă ? Raspunde cu <strong>DA</strong> sau <strong>NU</strong></em><br>"
            elif language_saved == "RU":
                mesaj += "<br>💬 <em>Хотите сделать заказ? Ответьте <strong>ДА</strong> или <strong>НЕТ</strong></em><br>"
            elif language_saved == "EN":
                mesaj += "<br>💬 <em>Do you want to make an order? Answer with <strong>YES</strong> or <strong>NO</strong></em><br>"


    else:

        func = check_functionalities_with_ai(message, servicii_potrivite)
        print("func = ", func)
        # func += ("<br><br> Acestea sunt serviciile potrivite pentru bugetul + functionalitatile alese")
        # print("func ======= ", func)
        if func == "NONE":
            func = check_functionalities_with_ai(message, servicii_dict)
            if func == "NONE":
                if language_saved == "RO":
                    prompt = (
                        f"Utilizatorul a scris serviciul: '{message}'.\n\n"
                        "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                        "Scrie un mesaj politicos, prietenos și natural, care:\n"
                        "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                        "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                        "Nu mai mult de 2-3 propoziții.\n"
                        "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
                    )
                    messages = [{"role": "system", "content": prompt}]
                    mesaj = ask_with_ai(messages).strip()
                    mesaj += (
                        "<br><br>❗️ Din ce ai scris, nu am reușit să identific un serviciu potrivit pentru nevoia ta."
                        "<br>💬 Te rog să-mi spui mai clar ce funcționalități ți-ar plăcea să aibă – de exemplu: <em>„platformă de vânzare produse online”, „site de prezentare cu 3-5 pagini”, „creare logo”</em>."
                        "<br><br>🔍 Cu cât mai clar, cu atât mai ușor îți pot recomanda variante potrivite!"
                    )
                elif language_saved == "RU":
                    prompt = (
                        f"Пользователь написал о сервисе: '{message}'.\n\n"
                        "Никогда не начинай с «Привет» или вводных фраз, так как мы уже ведём разговор и знакомы друг с другом. "
                        "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                        "1. Кратко отвечает на то, что сказал пользователь.\n"
                        "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                        "Не больше 2-3 предложений.\n"
                        "Не используй кавычки и не объясняй, что ты делаешь — просто напиши итоговое сообщение."
                    )
                    messages = [{"role": "system", "content": prompt}]
                    mesaj = ask_with_ai(messages).strip()
                    mesaj += (
                        "<br><br>❗️ Из того, что вы написали, я не смог определить подходящую услугу для ваших нужд."
                        "<br>💬 Пожалуйста, расскажите более подробно, какие функции вы хотели бы видеть — например: <em>«платформа для продажи товаров онлайн», «сайт-визитка с 3-5 страницами», «создание логотипа»</em>."
                        "<br><br>🔍 Чем яснее вы выразитесь, тем проще будет подобрать для вас подходящие варианты!"
                    )
                elif language_saved == "EN":
                    prompt = (
                        f"The user wrote about the service: '{message}'.\n\n"
                        "Never say 'Hello' or any introductory stuff, since we are already in a conversation and know each other. "
                        "Write a polite, friendly, and natural message that:\n"
                        "1. Briefly responds to what the user said.\n"
                        "2. The message should be short, warm, empathetic, and friendly.\n"
                        "No more than 2-3 sentences.\n"
                        "Do not use quotes or explain what you are doing – just write the final message."
                    )
                    messages = [{"role": "system", "content": prompt}]
                    mesaj = ask_with_ai(messages).strip()
                    mesaj += (
                        "<br><br>❗️ From what you wrote, I couldn't identify a service suitable for your needs."
                        "<br>💬 Please tell me more clearly what features you'd like – for example: <em>'online product sales platform', 'presentation site with 3-5 pages', 'logo creation'</em>."
                        "<br><br>🔍 The clearer you are, the easier it will be for me to recommend suitable options!"
                    )
                
                return jsonify({"message": mesaj})
            else:
                if ";" in func:
                    splited_func = func.split(";")
                    preferinte["Produs_Pentru_Comanda"] = splited_func
                elif "\n" in func:
                    splited_func = func.split("\n")
                    preferinte["Produs_Pentru_Comanda"] = splited_func
                else:
                    splited_func = [func]
                    # if language_saved == "RO":
                    #     splited_func = ["Pachet : Business Smart" , "Site Complex Multilingv (>5 pagini)" , "Magazin Online (E-commerce)"]
                    # elif language_saved == "RU":
                    #     splited_func = ["Пакет: Business Smart" , "Сложный многоязычный сайт (более 5 страниц)" , "Магазин Онлайн (Электронная коммерция)" ]
                    # elif language_saved == "EN":
                    #     splited_func = ["Business Smart" , "Site Complex Multilingual (>5 pages)" , "Online Store (E-commerce)" ]
                    preferinte["Produs_Pentru_Comanda"] = splited_func

                mesaj = ""
                
                for i in splited_func:
                    detalii = extract_info(i, language_saved)
                    
                    if detalii:
                        descriere = detalii.get("descriere", "N/A")
                        beneficii = detalii.get("beneficii", "N/A")
                        pret_md = detalii.get("pret_md", "N/A")
                        pret_ue = detalii.get("pret_ue", "N/A")
                        pret_reducere = detalii.get("reducere", "N/A")

                        if language_saved == "RO":
                            if preferinte.get("country", "") == "MD":
                                mesaj += (
                                    f"✅ Iată toate detaliile despre <strong>{i}</strong> 🧩<br /><br />"
                                    f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                                    f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                                    f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                                    f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                    f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                    f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                                    # f"🇪🇺 <strong>Preț pentru Uniunea Europeană:</strong> {pret_ue} MDL<br /><br />"
                                    f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                                )
                            else:
                                mesaj += (
                                    f"✅ Iată toate detaliile despre <strong>{i}</strong> 🧩<br /><br />"
                                    f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                                    f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                                    # f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                                    # f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                    # f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                    # f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                                    f"🇪🇺 <strong>Preț :</strong> {pret_ue} MDL<br /><br />"
                                    f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                                )
                        elif language_saved == "RU":
                            if preferinte.get("country", "") == "MD":
                                mesaj += (
                                    f"✅ Вот вся информация о <strong>{i}</strong> 🧩<br /><br />"
                                    f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                                    f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                                    f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                                    f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас он со СКИДКОЙ и доступен всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                    f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                    f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                                    # f"🇪🇺 <strong>Цена для Европейского Союза:</strong> {pret_ue} MDL<br /><br />"
                                    f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                                )
                            else:
                                mesaj += (
                                    f"✅ Вот вся информация о <strong>{i}</strong> 🧩<br /><br />"
                                    f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                                    f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                                    # f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                                    # f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас он со СКИДКОЙ и доступен всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                    # f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                    # f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                                    f"🇪🇺 <strong>Цена :</strong> {pret_ue} MDL<br /><br />"
                                    f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                                )

                        elif language_saved == "EN":
                            if preferinte.get("country", "") == "MD":
                                mesaj += (
                                    f"✅ Here are all the details about <strong>{i}</strong> 🧩<br /><br />"
                                    f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                                    f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                                    f"💸 <strong>📢 Great news for you!</strong><br />"
                                    f"This product used to cost <s>{pret_md} MDL</s>, but now it is AVAILABLE WITH A DISCOUNT for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                    f"💥 <strong>You save {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                    f"🎯 <em>The price is valid only for a limited time!</em><br /><br />"
                                    # f"🇪🇺 <strong>Price for the European Union:</strong> {pret_ue} MDL<br /><br />"
                                    f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                                )
                            else:
                                mesaj += (
                                    f"✅ Here are all the details about <strong>{i}</strong> 🧩<br /><br />"
                                    f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                                    f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                                    # f"💸 <strong>📢 Great news for you!</strong><br />"
                                    # f"This product used to cost <s>{pret_md} MDL</s>, but now it is AVAILABLE WITH A DISCOUNT for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                    # f"💥 <strong>You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!</strong><br />"
                                    # f"🎯 <em>The price is valid only for a limited time!</em><br /><br />"
                                    f"🇪🇺 <strong>Price :</strong> {pret_ue} MDL<br /><br />"
                                    f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                                )
                            
                if language_saved == "RO":
                    if buget == "NU":
                        mesaj += (
                            "❗️ <strong>Nu sunt servicii potrivite pentru bugetul ales , dar am gasit dupa functionalitatile alese</strong><br>"
                        )

                        mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"

                    

                    mesaj += "<br>💬 <em>Dorești să faci o comandă ? Raspunde cu <strong>DA</strong> sau <strong>NU</strong></em><br>"
                elif language_saved == "RU":
                    if buget == "NU":
                        mesaj += (
                            "❗️ <strong>Вот услуги, которые подходят по вашему бюджету и выбранным функциям</strong><br>"
                        )
                        mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"

                   
                

                    mesaj += "<br>💬 <em>Хотите сделать заказ? Ответьте <strong>ДА</strong> или <strong>НЕТ</strong></em><br>"

                elif language_saved == "EN":
                    if buget == "NU":
                        mesaj += (
                            "❗️ <strong>No services suitable for the chosen budget, but we found options that match the selected functional features</strong><br>"
                        )
                        mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"

                    

                    mesaj += "<br>💬 <em>Do you want to make an order? Answer with <strong>YES</strong> or <strong>NO</strong></em><br>"

        else:
            
            if ";" in func:
                splited_func = func.split(";")
                preferinte["Produs_Pentru_Comanda"] = splited_func
            elif "\n" in func:
                splited_func = func.split("\n")
                preferinte["Produs_Pentru_Comanda"] = splited_func
            else:
                splited_func = [func]
                # if language_saved == "RO":
                #     splited_func = ["Pachet : Business Smart" , "Site Complex Multilingv (>5 pagini)" , "Magazin Online (E-commerce)"]
                # elif language_saved == "RU":
                #     splited_func = ["Пакет: Business Smart" , "Сложный многоязычный сайт (более 5 страниц)" , "Магазин Онлайн (Электронная коммерция)" ]
                # elif language_saved == "EN":
                #     splited_func = ["Business Smart" , "Site Complex Multilingual (>5 pages)" , "Online Store (E-commerce)" ]
                preferinte["Produs_Pentru_Comanda"] = splited_func

            mesaj = ""
            for i in splited_func:
                detalii = extract_info(i, language_saved)
                
                if detalii:
                    descriere = detalii.get("descriere", "N/A")
                    beneficii = detalii.get("beneficii", "N/A")
                    pret_md = detalii.get("pret_md", "N/A")
                    pret_ue = detalii.get("pret_ue", "N/A")
                    pret_reducere = detalii.get("reducere", "N/A")

                    if language_saved == "RO":
                        if preferinte.get("country", "") == "MD":
                            mesaj += (
                                f"✅ Iată toate detaliile despre <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                                f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                                f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                                # f"🇪🇺 <strong>Preț :</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )
                        else:
                            mesaj += (
                                f"✅ Iată toate detaliile despre <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                                # f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                                # f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                # f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                # f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                                f"🇪🇺 <strong>Preț :</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )

                    elif language_saved == "RU":
                        if preferinte.get("country", "") == "MD":
                            mesaj += (
                                f"✅ Вот вся информация о <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                                f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                                f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас он со СКИДКОЙ и доступен всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                                # f"🇪🇺 <strong>Цена для Европейского Союза:</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )
                        else:
                            mesaj += (
                                f"✅ Вот вся информация о <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                                # f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                                # f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас он со СКИДКОЙ и доступен всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                # f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                # f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                                f"🇪🇺 <strong>Цена :</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )

                    elif language_saved == "EN":
                        if preferinte.get("country", "") == "MD":

                            mesaj += (
                                f"✅ Here are all the details about <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                                f"💸 <strong>📢 Great news for you!</strong><br />"
                                f"This product used to cost <s>{pret_md} MDL</s>, but now it is AVAILABLE WITH A DISCOUNT for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                f"💥 <strong>You save {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                                f"🎯 <em>The price is valid only for a limited time!</em><br /><br />"
                                # f"🇪🇺 <strong>Price for the European Union:</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )
                        else:
                            mesaj += (
                                f"✅ Here are all the details about <strong>{i}</strong> 🧩<br /><br />"
                                f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                                f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                                # f"💸 <strong>📢 Great news for you!</strong><br />"
                                # f"This product used to cost <s>{pret_md} MDL</s>, but now it is AVAILABLE WITH A DISCOUNT for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                                # f"💥 <strong>You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!</strong><br />"
                                # f"🎯 <em>The price is valid only for a limited time!</em><br /><br />"
                                f"🇪🇺 <strong>Price :</strong> {pret_ue} MDL<br /><br />"
                                f"<hr style='border: none; border-top: 1px solid #ccc; margin: 30px 0;'>"
                            )
            
            if language_saved == "RO":
                if buget == "NU":
                    mesaj += (
                        "❗️ <strong>Nu sunt servicii potrivite pentru bugetul ales , dar am gasit dupa functionalitatile alese</strong><br>"
                    )
                    mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"

                

                mesaj += "<br>💬 <em>Dorești să faci o comandă ? Raspunde cu <strong>DA</strong> sau <strong>NU</strong></em><br>"
            elif language_saved == "RU":
                if buget == "NU":
                    mesaj += (
                        "❗️ <strong>Вот услуги, которые подходят по вашему бюджету и выбранным функциям</strong><br>"
                    )
                    mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"
                

                mesaj += "<br>💬 <em>Хотите сделать заказ? Ответьте <strong>ДА</strong> или <strong>НЕТ</strong></em><br>"

            elif language_saved == "EN":
                if buget == "NU":
                    mesaj += (
                        "❗️ <strong>These are the services that match your budget and selected features</strong><br>"
                    )
                    mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"

                mesaj += "<br>💬 <em>Do you want to make an order? Answer with <strong>YES</strong> or <strong>NO</strong></em><br>"


    

    return jsonify({"message": mesaj})



@app.route("/welcome", methods=["POST"])
def welcome():
    data = request.json
    name = data.get("name", "")
    interests = data.get("interests", "")
    language_saved = data.get("language", "RO")
    print("languageeeee ===== ", language_saved)
    mesaj = ""
    prompt_verify = (
        f"Ai o listă de servicii valide: {categorii_unice}\n\n"
        f"Verifică dacă textul următor conține cel puțin un serviciu valid sau o denumire care seamănă suficient (similaritate mare) cu vreuna din serviciile valide.\n\n"
        f'Text de verificat: "{interests}"\n\n'
        f'Răspunde strict cu "DA" dacă există o potrivire validă sau asemănătoare, altfel răspunde cu "NU".'
    )

    messages = [{"role": "system", "content": prompt_verify}] 
    resp = ask_with_ai(messages , max_tokens=10)
    print("RASPUNS = ", resp)


    print("categorii_unice = ", categorii_unice)
    print("\n\n\ncategorii_unice_ru = ", categorii_unice_ru)
    print("\n\n\ncategorii_unice_en = ", categorii_unice_en)

    if language_saved == "RO":
        print("interests ====== ", interests)
        rezultat = function_check_product(interests , categorii_unice, "RO")
    elif language_saved == "RU":
        rezultat = function_check_product(interests , categorii_unice_ru, "RU")
    else:
        rezultat = function_check_product(interests , categorii_unice_en, "EN")

    # print("reezzzzzz = " , rezultat)
    



    if rezultat == "NU":
        lungime_rezultat = 0
    else:
        lungime_rezultat = len(rezultat)

    if lungime_rezultat == 1:
        produs = rezultat[0]['produs']
        preferinte["Serviciul_Ales"] = produs
        print("rezultatul =", rezultat)
        print("produs = ", produs)
        detalii = extract_info(produs, language_saved)
        print("detalii ===!!!! ", detalii)
        if detalii:
            descriere = detalii.get("descriere", "N/A")
            beneficii = detalii.get("beneficii", "N/A")
            pret_md = detalii.get("pret_md", "N/A")
            pret_ue = detalii.get("pret_ue", "N/A")

            preferinte["Pret_MD"] = pret_md
            preferinte["Pret_UE"] = pret_ue
            # print(preferinte["Pret_MD"])
            # print(preferinte["Pret_UE"])
            pret_reducere = detalii.get("reducere", "N/A")
            preferinte["reducere"] = pret_reducere
            if language_saved == "RO":
                # print("tara = ", preferinte["country"])
                if preferinte.get("country", "") == "MD":
                    mesaj = (
                        f"✅ Am găsit serviciul tău! Iată toate detaliile despre <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                        f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                        f"Acest produs avea prețul de <s><strong>{pret_md} MDL</strong></s>, dar acum este <strong>REDUS</strong> și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        f"💥 Asta înseamnă că <strong>economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                        # f"🇪🇺 <strong>Preț (Uniunea Europeană):</strong> {pret_ue} MDL<br /><br />"
                        "🔄 Dacă vrei detalii despre un <strong>alt serviciu</strong>, să faci o <strong>comandă</strong> sau <strong>să alegem după preferințe</strong>, scrie-mi te rog! 😊"
                    )
                else:
                    mesaj = (
                        f"✅ Am găsit serviciul tău! Iată toate detaliile despre <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                        # f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                        # f"Acest produs avea prețul de <s><strong>{pret_md} MDL</strong></s>, dar acum este <strong>REDUS</strong> și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        # f"💥 Asta înseamnă că <strong>economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        # f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                        f"🇪🇺 <strong>Preț :</strong> {pret_ue} MDL<br /><br />"
                        "🔄 Dacă vrei detalii despre un <strong>alt serviciu</strong>, să faci o <strong>comandă</strong> sau <strong>să alegem după preferințe</strong>, scrie-mi te rog! 😊"
                    )

            elif language_saved == "RU":
                if preferinte.get("country", "") == "MD":
                    mesaj = (
                        f"✅ Мы нашли вашу услугу! Вот все детали по <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                        f"💸 <strong>📢 Держитесь! У нас для вас отличные новости!</strong><br />"
                        f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас его можно получить всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        f"💥 Это значит, что вы экономите <strong>{int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL</strong>!<br />"
                        f"🎯 <em>Цена действует только ограниченное время!</em><br /><br />"
                        # f"🇪🇺 <strong>Цена для Европейского Союза:</strong> {pret_ue} MDL<br /><br />"
                        "🔄 Если хотите узнать детали о <strong>другой услуге</strong>, оформить <strong>заказ</strong> или <strong>выбрать по предпочтениям</strong>, напишите мне, пожалуйста! 😊"
                    )
                else:
                    mesaj = (
                        f"✅ Мы нашли вашу услугу! Вот все детали по <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                        # f"💸 <strong>📢 Держитесь! У нас для вас отличные новости!</strong><br />"
                        # f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас его можно получить всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        # f"💥 Это значит, что вы экономите <strong>{int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL</strong>!<br />"
                        # f"🎯 <em>Цена действует только ограниченное время!</em><br /><br />"
                        f"🇪🇺 <strong>Цена :</strong> {pret_ue} MDL<br /><br />"
                        "🔄 Если хотите узнать детали о <strong>другой услуге</strong>, оформить <strong>заказ</strong> или <strong>выбрать по предпочтениям</strong>, напишите мне, пожалуйста! 😊"
                    )
            elif language_saved == "EN":
                # print("tara = ", preferinte["country"])
                if preferinte.get("country", "") == "MD":
                    mesaj = (
                        f"✅ We found your service! Here are all the details about <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                        f"💸 <strong>📢 Hold on! We’ve got great news for you!</strong><br />"
                        f"This product used to cost <s>{pret_md} MDL</s>, but now you can get it for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        f"💥 That means you save <strong>{int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL</strong>!<br />"
                        f"🎯 <em>The price is valid for a limited time only!</em><br /><br />"
                        # f"🇪🇺 <strong>Price:</strong> {pret_ue} MDL<br /><br />"
                        "🔄 If you'd like to see details about a <strong>different service</strong>, place an <strong>order</strong>, or <strong>choose based on your preferences</strong>, just let me know! 😊"
                    )
                else:
                    mesaj = (
                        f"✅ We found your service! Here are all the details about <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                        # f"💸 <strong>📢 Hold on! We’ve got great news for you!</strong><br />"
                        # f"This product used to cost <s>{pret_md} MDL</s>, but now you can get it for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        # f"💥 That means you save <strong>{int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL</strong>!<br />"
                        # f"🎯 <em>The price is valid for a limited time only!</em><br /><br />"
                        f"🇪🇺 <strong>Price:</strong> {pret_ue} MDL<br /><br />"
                        "🔄 If you'd like to see details about a <strong>different service</strong>, place an <strong>order</strong>, or <strong>choose based on your preferences</strong>, just let me know! 😊"
                    )



            preferinte["Produs_Pentru_Comanda"] = produs

            return jsonify({"message": mesaj})

    elif lungime_rezultat > 1:
        if language_saved == "RO":
            reply = genereaza_prompt_produse(rezultat, resp, "RO")
        elif language_saved == "RU":
            reply = genereaza_prompt_produse(rezultat, resp, "RU")
        elif language_saved == "EN":
            reply = genereaza_prompt_produse(rezultat, resp, "EN")
        return jsonify({"message": reply})
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{interests}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            reply = build_service_prompt_2(categorii_unice, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал категорию: '{interests}'.\n\n"
                "Никогда не приветствуй, так как мы уже ведём разговор и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что ты делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            reply = build_service_prompt_2(categorii_unice_ru, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user wrote the category: '{interests}'.\n\n"
                "Never say 'Hello' or anything introductory — we are already in a conversation and familiar with each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2-3 sentences.\n"
                "Do not use quotation marks and do not explain what you're doing — just write the final message for the user."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            reply = build_service_prompt_2(categorii_unice_en, language_saved)
            mesaj = mesaj + reply

            

        return jsonify({"message": mesaj})
        
        

    # categoria_aleasa = check_and_get_category(interests, categorii_unice)
    # print("categoria_aleasa = ", categoria_aleasa)

    # log_message("USER", interests)

    # welcome_msg = generate_welcome_message(name, interests)
    # log_message("AI BOT", welcome_msg)

    return jsonify({"message": mesaj})



@app.route("/produs_intrebare", methods=["POST"])
def produs_intrebare():
    data = request.json
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")
    check_response = check_response_comanda(message, language_saved)


    if check_response == "DA":
        if language_saved == "RO":
            mesaj = (
                "✅ Serviciul a fost salvat cu succes!<br><br>"
                "📝 Pentru a continua comanda cât mai rapid, te rog scrie <strong>numele și prenumele</strong> "
            )
        elif language_saved == "RU":
            mesaj = (
                "✅ Заказ успешно сохранен!<br><br>"
                "📝 Для продолжения заказа, пожалуйста, напишите <strong>имя и фамилию</strong>"
            )
        elif language_saved == "EN":
            mesaj = (
                "✅ The service has been successfully saved!<br><br>"
                "📝 For the fastest order completion, please write <strong>name and surname</strong>"
            )
    elif check_response == "NU":
        if language_saved == "RO":
            mesaj = build_service_prompt_2(categorii_unice, language_saved)
        elif language_saved == "RU":
            mesaj = build_service_prompt_2(categorii_unice_ru, language_saved)
        elif language_saved == "EN":
            mesaj = build_service_prompt_2(categorii_unice_en, language_saved)
        return jsonify({"message": mesaj})
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{interests}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            produs = preferinte.get("Produs_Pentru_Comanda", "")

            reply = f"<br><br>📦 Doriți să plasați o comandă pentru serviciul <strong>{produs}</strong>? ✨<br>Răspundeți cu <strong>Da</strong> sau <strong>Nu</strong>."

            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал категорию: '{interests}'.\n\n"
                "Никогда не приветствуй, так как мы уже ведём разговор и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что ты делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            produs = preferinte.get("Produs_Pentru_Comanda", "")

            reply = f"<br><br>📦 Хотите оформить заказ на услугу <strong>{produs}</strong>? ✨<br>Ответьте <strong>Да</strong> или <strong>Нет</strong>."   

            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user wrote the category: '{interests}'.\n\n"
                "Never say 'Hello' or anything introductory — we are already in a conversation and familiar with each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2–3 sentences.\n"
                "Do not use quotation marks and do not explain what you're doing — just write the final message for the user."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            produs = preferinte.get("Produs_Pentru_Comanda", "")

            reply = f"<br><br>📦 Would you like to place an order for the <strong>{produs}</strong> service? ✨<br>Please reply with <strong>Yes</strong> or <strong>No</strong>."

            mesaj = mesaj + reply

    return jsonify({"message": mesaj})

@app.route("/chat", methods=["POST" , "GET"])
def chat():
    step = request.args.get('step')
    if step == 'feedback':
        return redirect('/feedback')
    data = request.get_json()
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")

    print("mmmmmm = ", message)

    prompt_verify = (
        f"Ai o listă de servicii valide: {categorii_unice}\n\n"
        f"Verifică dacă textul următor conține cel puțin un serviciu valid sau o denumire care seamănă suficient (similaritate mare) cu vreuna din serviciile valide.\n\n"
        f'Text de verificat: "{message}"\n\n'
        f'Răspunde strict cu "DA" dacă există o potrivire validă sau asemănătoare, altfel răspunde cu "NU".'
    )

    messages = [{"role": "system", "content": prompt_verify}] 
    resp = ask_with_ai(messages , max_tokens=10)

    if resp == "DA":
        if language_saved == "RO":  
            rezultat = function_check_product(interests , categorii_unice, "RO")
        elif language_saved == "RU":
            rezultat = function_check_product(interests , categorii_unice_ru, "RU")
        elif language_saved == "EN":
            rezultat = function_check_product(interests , categorii_unice_en, "EN")
        print("rezultat = ", rezultat)

        if rezultat == "NU":
            lungime_rezultat = 0
        else:
            lungime_rezultat = len(rezultat)

        if lungime_rezultat == 1:
            produs = rezultat[0]['produs']
            print("rezultatul =", produs)
            detalii = extract_info(produs, language_saved)            
            if detalii:
                descriere = detalii.get("descriere", "N/A")
                beneficii = detalii.get("beneficii", "N/A")
                pret_md = detalii.get("pret_md", "N/A")
                pret_ue = detalii.get("pret_ue", "N/A")
 

                preferinte["Pret_MD"] = pret_md
                # print(preferinte["Pret_MD"])
                preferinte["Pret_UE"] = pret_ue
                # print(preferinte["Pret_UE"])
                pret_reducere = detalii.get("reducere", "N/A")
                preferinte["reducere"] = pret_reducere

                
                if language_saved == "RO":
                    if preferinte.get("country", "") == "MD":
                        mesaj = (
                            f"✅ Am găsit serviciul tău! Iată toate detaliile despre <strong>{produs}</strong> 🧩<br /><br />"
                            f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                            f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                            f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                            f"Acest produs avea prețul de <s><strong>{pret_md} MDL</strong></s>, dar acum este <strong>REDUS</strong> și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                            f"💥 Asta înseamnă că <strong>economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                            f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                            # f"🇪🇺 <strong>Preț (Uniunea Europeană):</strong> {pret_ue} MDL<br /><br />"
                            "🔄 Dacă vrei detalii despre un <strong>alt serviciu</strong>, să faci o <strong>comandă</strong> sau <strong>să alegem după preferințe</strong>, scrie-mi te rog! 😊"
                        )
                    else:
                        mesaj = (
                            f"✅ Am găsit serviciul tău! Iată toate detaliile despre <strong>{produs}</strong> 🧩<br /><br />"
                            f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                            f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                            # f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                            # f"Acest produs avea prețul de <s><strong>{pret_md} MDL</strong></s>, dar acum este <strong>REDUS</strong> și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                            # f"💥 Asta înseamnă că <strong>economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                            # f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                            f"🇪🇺 <strong>Preț :</strong> {pret_ue} MDL<br /><br />"
                            "🔄 Dacă vrei detalii despre un <strong>alt serviciu</strong>, să faci o <strong>comandă</strong> sau <strong>să alegem după preferințe</strong>, scrie-mi te rog! 😊"
                        )

                elif language_saved == "RU":
                    if preferinte.get("country", "") == "MD":
                        mesaj = (
                            f"✅ Мы нашли вашу услугу! Вот все детали по <strong>{produs}</strong> 🧩<br /><br />"
                            f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                            f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                            f"💸 <strong>📢 Держитесь! У нас для вас отличные новости!</strong><br />"
                            f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас его можно получить всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                            f"💥 Это значит, что вы экономите <strong>{int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL</strong>!<br />"
                            f"🎯 <em>Цена действует только ограниченное время!</em><br /><br />"
                            # f"🇪🇺 <strong>Цена для Европейского Союза:</strong> {pret_ue} MDL<br /><br />"
                            "🔄 Если хотите узнать детали о <strong>другой услуге</strong>, оформить <strong>заказ</strong> или <strong>выбрать по предпочтениям</strong>, напишите мне, пожалуйста! 😊"
                        )
                    else:
                        mesaj = (
                            f"✅ Мы нашли вашу услугу! Вот все детали по <strong>{produs}</strong> 🧩<br /><br />"
                            f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                            f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                            # f"💸 <strong>📢 Держитесь! У нас для вас отличные новости!</strong><br />"
                            # f"Этот продукт раньше стоил <s>{pret_md} MDL</s>, но сейчас его можно получить всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                            # f"💥 Это значит, что вы экономите <strong>{int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL</strong>!<br />"
                            # f"🎯 <em>Цена действует только ограниченное время!</em><br /><br />"
                            f"🇪🇺 <strong>Цена :</strong> {pret_ue} MDL<br /><br />"
                            "🔄 Если хотите узнать детали о <strong>другой услуге</strong>, оформить <strong>заказ</strong> или <strong>выбрать по предпочтениям</strong>, напишите мне, пожалуйста! 😊"
                        )
                elif language_saved == "EN":
                    if preferinte.get("country", "") == "MD":
                        mesaj = (
                            f"✅ We found your service! Here are all the details about <strong>{produs}</strong> 🧩<br /><br />"
                            f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                            f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                            f"💸 <strong>📢 Great news for you!</strong><br />"
                            f"This product used to cost <s>{pret_md} MDL</s>, but now it's available for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                            f"💥 That means you save <strong>{int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL</strong>!<br />"
                            f"🎯 <em>This price is only valid for a limited time!</em><br /><br />"
                            # f"🇪🇺 <strong>Price for the European Union:</strong> {pret_ue} MDL<br /><br />"
                            "🔄 If you'd like to see details about a <strong>different service</strong>, place an <strong>order</strong>, or <strong>choose based on your preferences</strong>, just let me know! 😊"
                        )
                    else:
                        mesaj = (
                            f"✅ We found your service! Here are all the details about <strong>{produs}</strong> 🧩<br /><br />"
                            f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                            f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                            # f"💸 <strong>📢 Great news for you!</strong><br />"
                            # f"This product used to cost <s>{pret_md} MDL</s>, but now it's available for only <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                            # f"💥 That means you save <strong>{int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL</strong>!<br />"
                            # f"🎯 <em>This price is only valid for a limited time!</em><br /><br />"
                            f"🇪🇺 <strong>Price :</strong> {pret_ue} MDL<br /><br />"
                            "🔄 If you'd like to see details about a <strong>different service</strong>, place an <strong>order</strong>, or <strong>choose based on your preferences</strong>, just let me know! 😊"
)


                return jsonify({"message": mesaj})

        elif lungime_rezultat > 1:
            if language_saved == "RO":
                reply = genereaza_prompt_produse(rezultat, resp, "RO")
            elif language_saved == "RU":
                reply = genereaza_prompt_produse(rezultat, resp, "RU")
            elif language_saved == "EN":
                reply = genereaza_prompt_produse(rezultat, resp, "EN")
            return jsonify({"message": reply})
        else:
            if language_saved == "RO":
                prompt = (
                    f"Utilizatorul a scris categoria: '{interests}'.\n\n"
                    "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                    "Scrie un mesaj politicos, prietenos și natural, care:\n"
                    "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                    "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                    "Nu mai mult de 2-3 propoziții.\n"
                    "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
                )

                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                reply = build_service_prompt_2(categorii_unice,language_saved)
                mesaj = mesaj + reply
            elif language_saved == "RU":
                prompt = (
                    f"Пользователь написал категорию: '{interests}'.\n\n"
                    "Никогда не приветствуй, так как мы уже ведём разговор и знакомы. "
                    "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                    "1. Кратко отвечает на то, что написал пользователь.\n"
                    "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                    "Не более 2-3 предложений.\n"
                    "Не используй кавычки и не объясняй, что ты делаешь — пиши только итоговое сообщение."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                reply = build_service_prompt_2(categorii_unice_ru,language_saved)
                mesaj = mesaj + reply
            elif language_saved == "EN":
                prompt = (
                    f"The user wrote the category: '{interests}'.\n\n"
                    "Never say 'Hello' or anything introductory — we are already in a conversation and familiar with each other. "
                    "Write a polite, friendly, and natural message that:\n"
                    "1. Briefly responds to what the user said.\n"
                    "2. The message should be short, warm, empathetic, and friendly.\n"
                    "No more than 2-3 sentences.\n"
                    "Do not use quotation marks and do not explain what you're doing — just write the final message for the user."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                reply = build_service_prompt_2(categorii_unice_en,language_saved)
                mesaj = mesaj + reply
                
            
            return jsonify({"message": mesaj})
    elif resp == "NU":
        if language_saved == "RO":
            check = check_interest_pref(message)
        elif language_saved == "RU":
            check = check_interest_pref_ru(message)
        elif language_saved == "EN":
            check = check_interest_pref_en(message)


        if check == "produs_informații" or check == "produs_informatii":
            if language_saved == "RO":
                reply = build_service_prompt(categorii_unice, language_saved)
            elif language_saved == "RU":
                reply = build_service_prompt(categorii_unice_ru, language_saved)
            elif language_saved == "EN":
                reply = build_service_prompt(categorii_unice_en, language_saved)
            return jsonify({"message": reply})
        elif check == "comandă" or check == "comanda":
            if language_saved == "RO":
                mesaj = (
                    "🎉 Mǎ bucur că vrei să plasezi o comandă!<br><br>"
                    "📋 Hai să parcurgem împreună câțiva pași simpli pentru a înregistra comanda cu succes. 🚀<br><br>"
                )
            elif language_saved == "RU":
                mesaj = (
                    "🎉 Рад(а), что вы хотите сделать заказ!<br><br>"
                    "📋 Давайте вместе пройдем несколько простых шагов, чтобы успешно оформить заказ. 🚀<br><br>"
                )
            elif language_saved == "EN":
                mesaj = (
                    "🎉 I'm glad you want to place an order!<br><br>"
                    "📋 Let's go through a few simple steps together to successfully place the order. 🚀<br><br>"
                )

            if preferinte["Produs_Pentru_Comanda"] != "":
                produs = preferinte.get("Produs_Pentru_Comanda", "")
                if language_saved == "RO":
                    mesaj = f"📦 Doriți să plasați o comandă pentru serviciul <strong>{produs}</strong>? ✨<br>Răspundeți cu <strong>Da</strong> sau <strong>Nu</strong>."
                elif language_saved == "RU":
                    mesaj = f"📦 Хотите оформить заказ на услугу <strong>{produs}</strong>? ✨<br>Ответьте <strong>Да</strong> или <strong>Нет</strong>."
                elif language_saved == "EN":
                    mesaj = f"📦 Would you like to place an order for the <strong>{produs}</strong> service? ✨<br>Please reply with <strong>Yes</strong> or <strong>No</strong>."
                return jsonify({"message": mesaj})

            if language_saved == "RO":
                mesaj1 = build_service_prompt_2(categorii_unice, language_saved)
            elif language_saved == "RU":
                mesaj1 = build_service_prompt_2(categorii_unice_ru, language_saved)
            elif language_saved == "EN":
                mesaj1 = build_service_prompt_2(categorii_unice_en, language_saved)


            reply = mesaj + mesaj1

            return jsonify({"message": reply})
                
        elif check == "preferinte":
            if language_saved == "RO":
                prompt_buget = """
                💰 <strong>Haide să alegem un buget potrivit pentru serviciul dorit!</strong><br><br>
                Alege una dintre opțiunile de mai jos, sau scrie un buget estimativ dacă ai altă preferință:<br><br>
                🔹 <strong>10 000 MDL</strong> – Proiect simplu, ideal pentru un început clar și eficient<br>
                🔸 <strong>20 000 MDL</strong> – Echilibru între funcționalitate și personalizare<br>
                🌟 <strong>50 000 MDL+</strong> – Soluții avansate, complete, cu funcții extinse și design premium<br><br>
                ✍️ <em>Ne poți scrie direct o altă sumă dacă ai un buget diferit în minte!</em>
                """
            elif language_saved == "RU":
                prompt_buget = """
                💰 <strong>Давайте выберем подходящий бюджет для желаемой услуги!</strong><br><br>
                Выберите один из вариантов ниже или напишите примерный бюджет, если у вас есть другой предпочтительный вариант:<br><br>
                🔹 <strong>10 000 MDL</strong> – Простой проект, идеально подходит для ясного и эффективного старта<br>
                🔸 <strong>20 000 MDL</strong> – Баланс между функциональностью и персонализацией<br>
                🌟 <strong>50 000 MDL+</strong> – Продвинутые, комплексные решения с расширенными функциями и премиальным дизайном<br><br>
                ✍️ <em>Вы также можете сразу указать другую сумму, если у вас другой бюджет!</em>
                """
            elif language_saved == "EN":
                prompt_buget = """
                💰 <strong>Let's choose a suitable budget for the desired service!</strong><br><br>
                Choose one of the options below or write an estimated budget if you have a different preferred option:<br><br>
                🔹 <strong>10 000 MDL</strong> – Simple project, ideal for a clear and efficient start<br>
                🔸 <strong>20 000 MDL</strong> – Balance between functionality and personalization<br>
                🌟 <strong>50 000 MDL+</strong> – Advanced, comprehensive solutions with extended features and premium design<br><br>
                """

            return jsonify({"message": prompt_buget})
        else:
            if language_saved == "RO":
                prompt = (
                    f"Utilizatorul a scris : '{message}'.\n\n"
                    "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                    "Scrie un mesaj politicos, prietenos și natural, care:\n"
                    "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                    "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                    "Nu mai mult de 2-3 propoziții.\n"
                    "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                mesaj += (
                    "<br><br>❓ Te rugăm să ne spui dacă:<br>"
                    "&nbsp;&nbsp;🔍 <em>Vrei mai multe informații</em> despre serviciu<br>"
                    "&nbsp;&nbsp;🛒 <em>Vrei să achiziționezi</em> un serviciu<br>"
                    "&nbsp;&nbsp;🛒 <em>Vrei să alegem după preferințe</em><br>"
                    )
                reply = mesaj
            elif language_saved == "RU":
                prompt = (
                    f"Пользователь написал: '{message}'.\n\n"
                    "Никогда не начинай с приветствий или вводных фраз, так как мы уже ведём разговор и знакомы. "
                    "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                    "1. Кратко отвечает на то, что написал пользователь.\n"
                    "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                    "Не более 2-3 предложений.\n"
                    "Не используй кавычки и не объясняй, что ты делаешь — пиши только итоговое сообщение."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                mesaj += (
                    "<br><br>❓ Пожалуйста, скажи, что из этого тебе интересно:<br>"
                    "&nbsp;&nbsp;🔍 <em>Хочешь больше информации</em> о сервисе<br>"
                    "&nbsp;&nbsp;🛒 <em>Хочешь приобрести</em> услугу<br>"
                    "&nbsp;&nbsp;🛒 <em>Хочешь выбрать по предпочтениям</em><br>"
                )
                reply = mesaj
            elif language_saved == "EN":
                prompt = (
                    f"The user wrote: '{message}'.\n\n"
                    "Never start with greetings or introductory phrases, as we are already in a conversation and familiar with each other. "
                    "Write a polite, friendly, and natural message that:\n"
                    "1. Briefly responds to what the user said.\n"
                    "2. The message should be short, warm, empathetic, and friendly.\n"
                    "No more than 2-3 sentences.\n"
                    "Do not use quotation marks and do not explain what you're doing — just write the final message for the user."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                mesaj += (
                    "<br><br>❓ Please tell me what you're interested in:<br>"
                    "&nbsp;&nbsp;🔍 <em>Want more information</em> about the service<br>"
                    "&nbsp;&nbsp;🛒 <em>Want to purchase</em> the service<br>"
                    "&nbsp;&nbsp;🛒 <em>Want to choose based on preferences</em><br>"
                )
                reply = mesaj

            return jsonify({"message": reply})


def check_surname_command_en(command):
    prompt = f"""
    You are a smart automatic validator that STRICTLY REPLIES WITH "YES" or "NO" depending on whether the text contains a valid full name — at least two consecutive words that could represent a person's name (first + last or vice versa), whether real or fictional.

    Rules:
    0. If the text is a question, reply strictly "NO".
    1. Accept any combination of two or more consecutive words that resemble a name (real or fictional).
    2. Do not accept sequences containing emojis, digits, symbols (!, @, #, etc.), or abbreviations like "A.", "B.", etc.
    3. Words can be in any case (uppercase or lowercase).
    4. DO NOT accept single-word names, vague responses, or questions.
    5. Reply STRICTLY with "YES" or "NO", without any explanations.

    Examples of correct names (YES):
    - my name is anna stone
    - I’m igor beton
    - sarah star
    - john marble
    - olga rivera
    - yes, I am jake pepper

    Examples of incorrect (NO):
    - anna
    - stone
    - 😊😊😊
    - 12345
    - what's your name?
    - my name is john!
    - my name!
    - mike99 stone
    - @susan bell
    - andrew 😊 tile

    Text to validate:
    \"\"\"{command}\"\"\"

    Strict answer:
    """

    messages = [{"role": "system", "content": prompt}]

    response1 = ask_with_ai(messages, temperature=0.5, max_tokens=5).strip().upper()

    if response1 == "NO":
        # Second check with lower temperature
        response1 = ask_with_ai(messages, temperature=0.2, max_tokens=5).strip().upper()

    return "DA" if response1 == "YES" else "NU"


def check_surname_command_ru(command):
    prompt = f"""
    Ты — умный автоматический валидатор, который ОТВЕЧАЕТ СТРОГО "ДА" или "НЕТ", если текст содержит корректное полное имя человека, состоящее минимум из двух последовательных слов (имя + фамилия или наоборот), независимо от того, реальные это имена или вымышленные.

    Правила:
    0. Если текст — это вопрос, отвечай СТРОГО "НЕТ".
    1. Принимай любые комбинации из двух или более последовательных слов, которые могут быть именем (не обязательно реальным).
    2. Не принимай последовательности, содержащие эмодзи, цифры, символы (!, @, # и т.п.) или аббревиатуры типа «а.», «б.» и т.д.
    3. Слова могут быть с заглавных или строчных букв.
    4. НЕ принимай неполные имена (только одно слово), расплывчатые ответы или вопросы.
    5. Отвечай СТРОГО "ДА" или "НЕТ", без дополнительных объяснений.

    Примеры корректных (ДА):
    - меня зовут анна гречка
    - моё имя игорь бетон
    - я — оля звезда
    - сергей мрамор
    - инна колос
    - владимир ковёр
    - да, меня зовут паша торт

    Примеры некорректных (НЕТ):
    - анна
    - гречка
    - 😊😊😊
    - 12345
    - как тебя зовут?
    - моё имя иван!
    - меня зовут!
    - саша99 коваль
    - @мария петрова
    - андрей 😊 плитка

    Текст для проверки:
    \"\"\"{command}\"\"\"

    Строгий ответ:
    """

    messages = [{"role": "system", "content": prompt}]

    response1 = ask_with_ai(messages, temperature=0.5, max_tokens=5).strip().upper()

    if response1 == "НЕТ":
        # Повторная проверка с другой температурой
        response1 = ask_with_ai(messages, temperature=0.2, max_tokens=5).strip().upper()

    return "DA" if response1 == "ДА" else "NU"


def check_surname_command_ro(command):
    prompt = f"""
    Ești un validator automat inteligent care răspunde STRICT cu "DA" sau "NU" dacă textul conține un nume complet valid de persoană, format din cel puțin două cuvinte consecutive (prenume + nume sau invers), indiferent dacă acestea sunt nume reale sau inventate.

    Reguli:
    0. Dacă textul este o întrebare, răspunde STRICT "NU".
    1. Acceptă orice combinație de două sau mai multe cuvinte consecutive ce pot forma un nume (nu trebuie să fie neapărat nume reale).
    2. Nu accepta secvențe care conțin emoji, cifre, simboluri (!, @, # etc.) sau abrevieri de tipul „a.”, „b.” etc.
    3. Cuvintele pot fi cu majuscule sau minuscule.
    4. NU accepta nume incomplete (doar un singur cuvânt), răspunsuri vagi sau întrebări.
    5. Răspunde STRICT cu "DA" sau "NU", fără alte explicații.

    Exemple valide (DA):
    - mă numesc ana mamaliga
    - numele meu este gigel beton
    - sunt violeta spartacus
    - brinza daniel
    - ion stan
    - elena cucurigu
    - florin soare
    - dan moldovan
    - da, mă cheamă andrei caramida

    Exemple invalide (NU):
    - daniel
    - popescu
    - 😊😊😊
    - 12345
    - cum te numești?
    - numele meu este ion!
    - mă numesc!
    - ion2 popescu
    - @maria ionescu
    - florin 😊 betișor

    Text de verificat:
    \"\"\"{command}\"\"\"

    Răspuns STRICT:
    """

    messages = [{"role": "system", "content": prompt}]

    response1 = ask_with_ai(messages, temperature=0.5, max_tokens=5).strip().upper()

    if response1 == "NU":
        # Reîncercare cu temperatură diferită pentru robustețe
        response1 = ask_with_ai(messages, temperature=0.2, max_tokens=5).strip().upper()

    return "DA" if response1 == "DA" else "NU"


@app.route("/selecteaza_produs", methods=["POST"])
def selecteaza_produs():
    data = request.get_json()
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")
    produsele = preferinte.get("Produs_Pentru_Comanda", "")
    
    if language_saved == "RO":
        rezultat = function_check_product(message , produsele, language_saved)
    elif language_saved == "RU":
        rezultat = function_check_product(message , produsele, language_saved)
    elif language_saved == "EN":
        rezultat = function_check_product(message , produsele, language_saved)

    # preferinte["Serviciul_Ales"] = rezultat[0]['produs']
    
    print("produsele = ", produsele)
    print("rezultat = ", rezultat)
    if rezultat == "NU":
        lungime_rezultat = 0
    else:
        lungime_rezultat = len(rezultat)

    if lungime_rezultat == 1:
        produs = rezultat[0]['produs']
        preferinte["Serviciul_Ales"] = produs
        print("rezultatul =", produs)
        detalii = extract_info(produs, language_saved)            
        pret_md = detalii.get("pret_md", "N/A")
        pret_ue = detalii.get("pret_ue", "N/A")
        pret_reducere = detalii.get("reducere", "N/A")
        preferinte["reducere"] = pret_reducere
        preferinte["Pret_MD"] = pret_md
        preferinte["Pret_UE"] = pret_ue
        preferinte["Produs_Pentru_Comanda"] = produs
        if language_saved == "RO":
            mesaj = (
                "✅ Serviciul a fost salvat cu succes!<br><br>"
                "📝 Pentru a continua comanda cât mai rapid, te rog scrie <strong>numele și prenumele</strong> "
            )
        elif language_saved == "RU":
            mesaj = (
                "✅ Сервис успешно сохранен!<br><br>"
                "📝 Для продолжения заказа, пожалуйста, напишите <strong>имя и фамилию</strong> "
            )
        elif language_saved == "EN":
            mesaj = (
                "✅ The service has been successfully saved!<br><br>"
                "📝 For the fastest order completion, please write <strong>name and surname</strong> "
            )

        return jsonify({"message": mesaj})

    elif lungime_rezultat > 1:
        reply = genereaza_prompt_produse(rezultat , "OK", language_saved)
        return jsonify({"message": reply})
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{interests}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj +="<br><br>"
            reply = build_service_prompt_2(produsele , language_saved)
            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал категорию: '{interests}'.\n\n"
                "Никогда не начинай с «Привет» или других вводных фраз — мы уже ведем диалог и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Коротко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть тёплым, дружелюбным и эмпатичным. "
                "Не более 2–3 предложений.\n"
                "Не используй кавычки и не объясняй, что ты делаешь — просто напиши готовое сообщение для пользователя."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "<br><br>"
            reply = build_service_prompt_2(produsele , language_saved)
            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user wrote the category: '{interests}'.\n\n"
                "Never start with 'Hello' or any kind of greeting — we’re already in a conversation and know each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user wrote.\n"
                "2. Feels warm, empathetic, and friendly. No more than 2–3 sentences.\n"
                "Do not use quotation marks or explain what you’re doing — just write the final message for the user."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "<br><br>"
            reply = build_service_prompt_2(produsele, language_saved)
            mesaj = mesaj + reply
            

    return jsonify({"message": mesaj})

@app.route("/comanda", methods=["POST"])
def comanda():
    data = request.get_json()
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")


    resp = check_response_comanda(message, language_saved)
    print("resp = ", resp)

    if resp == "DA":
        if preferinte.get("Produs_Pentru_Comanda", "") != "":
            produse = preferinte.get("Produs_Pentru_Comanda", "")
            if language_saved == "RO":
                mesaj = "🛍️ Alegeți unul dintre următoarele produse pentru a plasa o comandă: <br>\n\n"
                for idx, produs in enumerate(produse, 1):
                    mesaj += f"<br> <strong>{produs}</strong>\n"
            elif language_saved == "RU":
                mesaj = "🛍️ Выберите один из следующих продуктов для размещения заказа: <br>\n\n"
                for idx, produs in enumerate(produse, 1):
                    mesaj += f"<br> <strong>{produs}</strong>\n"
            elif language_saved == "EN":
                mesaj = "🛍️ Choose one of the following products to place an order: <br>\n\n"
                for idx, produs in enumerate(produse, 1):
                    mesaj += f"<br> <strong>{produs}</strong>\n"
            return jsonify({"message": mesaj})

        else:
            if language_saved == "RO":
                mesaj = (
                    "🎉 Mǎ bucur că vrei să plasezi o comandă!<br><br>"
                    "📋 Hai să parcurgem împreună câțiva pași simpli pentru a înregistra comanda cu succes. 🚀<br><br>"
                )
            elif language_saved == "RU":
                mesaj = (
                    "🎉 Здорово, что вы хотите оформить заказ!<br><br>"
                    "📋 Давайте вместе пройдём несколько простых шагов, чтобы успешно зарегистрировать заказ. 🚀<br><br>"
                )
            elif language_saved == "EN":
                mesaj = (
                    "🎉 I'm glad you want to place an order!<br><br>"
                    "📋 Let's go through a few simple steps together to successfully place the order. 🚀<br><br>"
                )

            if language_saved == "RO":
                mesaj1 = build_service_prompt_2(categorii_unice, language_saved)
            elif language_saved == "RU":
                mesaj1 = build_service_prompt_2(categorii_unice_ru, language_saved)
            elif language_saved == "EN":
                mesaj1 = build_service_prompt_2(categorii_unice_en, language_saved)
            mesaj = mesaj + mesaj1

            # rezultat = function_check_product(interests , categorii_unice, "RO")
            # print("rezultat = ", rezultat)
                
        return jsonify({"message": mesaj})
    elif resp == "NU":
        if language_saved == "RO":
            mesaj = (
                "🙏 Îți mulțumim pentru răspuns! <br><br>"
                "🔄 Dacă vrei detalii despre un <strong>alt serviciu</strong>, "
                "să faci o <strong>comandă</strong> sau să alegem un serviciu "
                "<strong>în funcție de preferințele tale</strong>, scrie-mi te rog! 😊"
            )
        elif language_saved == "RU":
            mesaj = (
                "🙏 Спасибо за ответ! <br><br>"
                "🔄 Если хотите узнать подробнее о <strong>другом сервисе</strong>, "
                "сделать <strong>заказ</strong> или выбрать услугу "
                "<strong>по вашим предпочтениям</strong>, напишите мне, пожалуйста! 😊"
            )
        elif language_saved == "EN":
            mesaj = (
                "🙏 Thank you for your response! <br><br>"
                "🔄 If you want to know more about <strong>another service</strong>, "
                "make a <strong>purchase</strong>, or choose a service "
                "<strong>based on your preferences</strong>, please write to me! 😊"
            )
        return jsonify({"message": mesaj})
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris : '{message}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "<br><br>💬 Nu mi-e clar dacă vrei să faci o comandă. Dacă da, te rog răspunde cu <strong>DA</strong>, iar dacă nu, scrie <strong>NU</strong>. 😊"

        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал: '{message}'.\n\n"
                "Никогда не начинай с «Привет» или вводных фраз, ведь мы уже общаемся и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на сказанное пользователем.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не больше 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "<br><br>💬 Мне не совсем понятно, хотите ли вы сделать заказ. Если да, пожалуйста, ответьте <strong>ДА</strong>, если нет — напишите <strong>НЕТ</strong>. 😊"

        elif language_saved == "EN":
            prompt = (
                f"The user wrote: '{message}'.\n\n"
                "Never start with 'Hello' or any introductory phrases since we're already in a conversation and know each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2-3 sentences.\n"
                "Do not use quotation marks or explain what you're doing — just write the final message."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "<br><br>💬 I'm not sure if you want to place an order. If yes, please reply with <strong>YES</strong>, otherwise reply with <strong>NO</strong>. 😊"
        
        return jsonify({"message": mesaj})



@app.route("/comanda_inceput", methods=["POST"])
def comanda_inceput():
    data = request.get_json()
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")

    if language_saved == "RO":
        rezultat = function_check_product(message , categorii_unice, "RO")
    elif language_saved == "RU":
        rezultat = function_check_product(message , categorii_unice_ru, "RU")
    elif language_saved == "EN":
        rezultat = function_check_product(message , categorii_unice_en, "EN")

    print("rezultat = ", rezultat)
    if rezultat == "NU":
        lungime_rezultat = 0
    else:
        lungime_rezultat = len(rezultat)

    if lungime_rezultat == 1:
        produs = rezultat[0]['produs']
        print("rezultatul =", produs)
        detalii = extract_info(produs, language_saved)
        preferinte["Serviciul_Ales"] = rezultat[0]['produs']
        if detalii:
            descriere = detalii.get("descriere", "N/A")
            beneficii = detalii.get("beneficii", "N/A")
            pret_md = detalii.get("pret_md", "N/A")
            pret_ue = detalii.get("pret_ue", "N/A")

            preferinte["Pret_MD"] = pret_md
            preferinte["Pret_UE"] = pret_ue
            pret_reducere = detalii.get("reducere", "N/A")
            preferinte["reducere"] = pret_reducere
            if language_saved == "RO":
                if preferinte.get("country") == "MD":
                    mesaj = (
                        f"✅ Iată toate detaliile despre <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                        f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                        f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                        # f"🇪🇺 <strong>Preț pentru Uniunea Europeană:</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>Dacă dorești acest produs, confirmă cu DA</strong><br />"
                        "❌ <strong>Dacă vrei să alegi altul, răspunde cu NU</strong>"
                    )
                else:
                    mesaj = (
                        f"✅ Iată toate detaliile despre <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                        # f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                        # f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        # f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        # f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                        f"🇪🇺 <strong>Preț :</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>Dacă dorești acest produs, confirmă cu DA</strong><br />"
                        "❌ <strong>Dacă vrei să alegi altul, răspunde cu NU</strong>"
                    )

            elif language_saved == "RU":
                if preferinte.get("country") == "MD":
                    mesaj = (
                        f"✅ Вот все детали о <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                        f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                        f"Этот продукт стоил <s>{pret_md} MDL</s>, но теперь со СКИДКОЙ его можно получить всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                        # f"🇪🇺 <strong>Цена для Европейского Союза:</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>Если хотите этот продукт, подтвердите с ДА</strong><br />"
                        "❌ <strong>Если хотите выбрать другой, ответьте с НЕТ</strong>"
                    )
                else:
                    mesaj = (
                        f"✅ Вот все детали о <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                        # f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                        # f"Этот продукт стоил <s>{pret_md} MDL</s>, но теперь со СКИДКОЙ его можно получить всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        # f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        # f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                        f"🇪🇺 <strong>Цена :</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>Если хотите этот продукт, подтвердите с ДА</strong><br />"
                        "❌ <strong>Если хотите выбрать другой, ответьте с НЕТ</strong>"
                    )
            elif language_saved == "EN":
                if preferinte.get("country") == "MD":
                    mesaj = (
                        f"✅ Here are all the details about <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                        f"💸 <strong>📢 Hold tight! We have great news for you!</strong><br />"
                        f"This product used to cost <s>{pret_md} MDL</s>, but now it’s DISCOUNTED and you can get it for just <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        f"💥 <strong>You save {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        f"🎯 <em>Price valid only for a limited time!</em><br /><br />"
                        # f"🇪🇺 <strong>Price for the European Union:</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>If you want this product, please confirm with YES</strong><br />"
                        "❌ <strong>If you want to choose another one, reply with NO</strong>"
                    )
                else:
                    mesaj = (
                        f"✅ Here are all the details about <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                        # f"💸 <strong>📢 Hold tight! We have great news for you!</strong><br />"
                        # f"This product used to cost <s>{pret_md} MDL</s>, but now it’s DISCOUNTED and you can get it for just <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        # f"💥 <strong>You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!</strong><br />"
                        # f"🎯 <em>Price valid only for a limited time!</em><br /><br />"
                        f"🇪🇺 <strong>Price :</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>If you want this product, please confirm with YES</strong><br />"
                        "❌ <strong>If you want to choose another one, reply with NO</strong>"
                    )
                    


            print("mesaj = ", mesaj)
            return jsonify({"message": mesaj})

    elif lungime_rezultat > 1:
        
        reply = genereaza_prompt_produse(rezultat, "OK", language_saved)
        return jsonify({"message": reply})
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{interests}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj +="<br><br>"
            reply = build_service_prompt_2(categorii_unice, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь указал категорию: '{interests}'.\n\n"
                "Никогда не начинай с приветствий или вводных фраз, так как мы уже ведём разговор и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "<br><br>"
            reply = build_service_prompt_2(categorii_unice_ru, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user specified the category: '{interests}'.\n\n"
                "Never start with greetings or introductory phrases, since we are already having a conversation and are familiar with each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user wrote.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2-3 sentences.\n"
                "Do not use quotation marks and do not explain what you are doing — just write the final message."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "<br><br>"
            reply = build_service_prompt_2(categorii_unice_en, language_saved)
            mesaj = mesaj + reply


    return jsonify({"message": mesaj})

@app.route("/afiseaza_produs", methods=["POST"])
def afiseaza_produs():
    data = request.get_json()
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")
    if language_saved == "RO":
        rezultat = function_check_product(message , categorii_unice, "RO")
    elif language_saved == "RU":
        rezultat = function_check_product(message , categorii_unice_ru, "RU")
    elif language_saved == "EN":
        rezultat = function_check_product(message , categorii_unice_en, "EN")

    preferinte["Serviciul_Ales"] = rezultat[0]['produs']
    print("rezultat = ", rezultat)

    if rezultat == "NU":
        lungime_rezultat = 0
    else:
        lungime_rezultat = len(rezultat)

    if lungime_rezultat == 1:
        produs = rezultat[0]['produs']
        print("rezultatul =", produs)
        detalii = extract_info(produs, language_saved)
        preferinte["Produs_Pentru_Comanda"] = produs
        preferinte["Serviciul_Ales"] = produs

        if detalii:
            descriere = detalii.get("descriere", "N/A")
            beneficii = detalii.get("beneficii", "N/A")
            pret_md = detalii.get("pret_md", "N/A")
            pret_ue = detalii.get("pret_ue", "N/A")
            preferinte["Pret_MD"] = pret_md
            preferinte["Pret_UE"] = pret_ue

            
            pret_reducere = detalii.get("reducere", "N/A")
            preferinte["reducere"] = pret_reducere
            
            if language_saved == "RO":
                if preferinte.get("country") == "MD":
                    mesaj = (
                        f"✅ Iată toate detaliile despre <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                        f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                        f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                        # f"🇪🇺 <strong>Preț pentru Uniunea Europeană:</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>Dacă dorești acest produs, confirmă cu DA</strong><br />"
                        "❌ <strong>Dacă vrei să alegi altul, răspunde cu NU</strong>"
                    )
                else:
                    mesaj = (
                        f"✅ Iată toate detaliile despre <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Descriere:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Beneficii:</strong><br />{beneficii}<br /><br />"
                        # f"💸 <strong>📢 Ține-te bine! Am vești bune pentru tine!</strong><br />"
                        # f"Acest produs avea prețul de <s>{pret_md} MDL</s>, dar acum este REDUS și îl poți lua cu doar <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        # f"💥 <strong>Economisești {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        # f"🎯 <em>Preț valabil doar pentru o perioadă limitată!</em><br /><br />"
                        f"🇪🇺 <strong>Preț :</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>Dacă dorești acest produs, confirmă cu DA</strong><br />"
                        "❌ <strong>Dacă vrei să alegi altul, răspunde cu NU</strong>"
                    )

            elif language_saved == "RU":
                if preferinte.get("country") == "MD":
                    mesaj = (
                        f"✅ Вот все детали о <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                        f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                        f"Этот продукт стоил <s>{pret_md} MDL</s>, но теперь со СКИДКОЙ его можно получить всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                        # f"🇪🇺 <strong>Цена для Европейского Союза:</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>Если хотите этот продукт, подтвердите с ДА</strong><br />"
                        "❌ <strong>Если хотите выбрать другой, ответьте с НЕТ</strong>"
                    )
                else:
                    mesaj = (
                        f"✅ Вот все детали о <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Описание:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Преимущества:</strong><br />{beneficii}<br /><br />"
                        # f"💸 <strong>📢 У нас отличные новости для вас!</strong><br />"
                        # f"Этот продукт стоил <s>{pret_md} MDL</s>, но теперь со СКИДКОЙ его можно получить всего за <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        # f"💥 <strong>Вы экономите {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        # f"🎯 <em>Цена действует только в течение ограниченного времени!</em><br /><br />"
                        f"🇪🇺 <strong>Цена :</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>Если хотите этот продукт, подтвердите с ДА</strong><br />"
                        "❌ <strong>Если хотите выбрать другой, ответьте с НЕТ</strong>"
                    )
            elif language_saved == "EN":
                if preferinte.get("country") == "MD":
                    mesaj = (
                        f"✅ Here are all the details about <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                        f"💸 <strong>📢 Hold on! I have great news for you!</strong><br />"
                        f"This product used to cost <s>{pret_md} MDL</s>, but now it’s DISCOUNTED and you can get it for just <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        f"💥 <strong>You save {int(pret_md.replace(" ", "")) - int(pret_reducere.replace(" ", ""))} MDL!</strong><br />"
                        f"🎯 <em>Price valid for a limited time only!</em><br /><br />"
                        # f"🇪🇺 <strong>Price for the European Union:</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>If you want this product, confirm with YES</strong><br />"
                        "❌ <strong>If you want to choose another, reply with NO</strong>"
                    )
                else:
                    mesaj = (
                        f"✅ Here are all the details about <strong>{produs}</strong> 🧩<br /><br />"
                        f"📌 <strong>Description:</strong><br />{descriere}<br /><br />"
                        f"🎯 <strong>Benefits:</strong><br />{beneficii}<br /><br />"
                        # f"💸 <strong>📢 Hold on! I have great news for you!</strong><br />"
                        # f"This product used to cost <s>{pret_md} MDL</s>, but now it’s DISCOUNTED and you can get it for just <strong>{pret_reducere} MDL</strong>! 🤑<br />"
                        # f"💥 <strong>You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!</strong><br />"
                        # f"🎯 <em>Price valid for a limited time only!</em><br /><br />"
                        f"🇪🇺 <strong>Price :</strong> {pret_ue} MDL<br /><br />"
                        "✅ <strong>If you want this product, confirm with YES</strong><br />"
                        "❌ <strong>If you want to choose another, reply with NO</strong>"
                    )

            print("mesaj = ", mesaj)
            return jsonify({"message": mesaj})

    elif lungime_rezultat > 1:
        
        reply = genereaza_prompt_produse(rezultat, "OK", language_saved)
        return jsonify({"message": reply})
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{interests}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj +="<br><br>"
            reply = build_service_prompt_2(categorii_unice, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь указал категорию: '{interests}'.\n\n"
                "Никогда не начинай с приветствий или вводных фраз, так как мы уже ведём разговор и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "<br><br>"
            reply = build_service_prompt_2(categorii_unice_ru, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user specified the category: '{interests}'.\n\n"
                "Never start with greetings or introductory phrases, since we are already having a conversation and are familiar with each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user wrote.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2-3 sentences.\n"
                "Do not use quotation marks and do not explain what you are doing — just write the final message."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "<br><br>"
            reply = build_service_prompt_2(categorii_unice_en, language_saved)
            mesaj = mesaj + reply

        return jsonify({"message": mesaj})

@app.route("/confirma_produs", methods=["POST"])
def confirma_produs():
    data = request.get_json()
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")
    resp = check_response_comanda(message, language_saved)
    if resp == "DA":
        if language_saved == "RO":
            mesaj = (
                "✅ Serviciul a fost salvat cu succes!<br><br>"
                "📝 Pentru a continua comanda cât mai rapid, te rog scrie <strong>numele și prenumele</strong> "
            )
        elif language_saved == "RU":
            mesaj = (
                "✅ Заказ успешно сохранен!<br><br>"
                "📝 Для продолжения заказа, пожалуйста, напишите <strong>имя и фамилию</strong>"
            )
        elif language_saved == "EN":
            mesaj = (
                "✅ The service has been successfully saved!<br><br>"
                "📝 For the fastest order completion, please write <strong>name and surname</strong>"
            )
        return jsonify({"message": mesaj})
    elif resp == "NU":
        if language_saved == "RO":
            mesaj = build_service_prompt_2(categorii_unice, language_saved)
        elif language_saved == "RU":
            mesaj = build_service_prompt_2(categorii_unice_ru, language_saved)
        elif language_saved == "EN":
            mesaj = build_service_prompt_2(categorii_unice_en, language_saved)
        return jsonify({"message": mesaj})
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{interests}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>❓ Te rog spune-mi clar dacă alegi acest produs sau vrei să alegem altul.<br>"
                "Răspunde cu <strong>DA</strong> dacă dorești acest produs, sau <strong>NU</strong> dacă vrei să căutăm altceva. 😊"
            )
        elif language_saved == "RU":
            prompt = (
                f"Пользователь указал категорию: '{interests}'.\n\n"
                "Никогда не начинай с приветствий или вводных фраз, так как мы уже ведём разговор и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что делаешь — пиши только итоговое сообщение."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>❓ Пожалуйста, скажи ясно, выбираешь ли ты этот продукт или хочешь выбрать другой.<br>"
                "Ответь <strong>ДА</strong>, если хочешь этот продукт, или <strong>НЕТ</strong>, если хочешь поискать что-то другое. 😊"
            )
        elif language_saved == "EN":
            prompt = (
                f"The user specified the category: '{interests}'.\n\n"
                "Never start with greetings or introductory phrases, since we are already having a conversation and are familiar with each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user wrote.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2-3 sentences.\n"
                "Do not use quotation marks and do not explain what you are doing — just write the final message."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "<br><br>❓ Please tell me clearly if you want this product or want to choose another.<br>"
                "Reply with <strong>YES</strong> if you want this product, or <strong>NO</strong> if you want to choose another. 😊"
            )

    return jsonify({"message": mesaj})

def extrage_nume_din_text(text):
    prompt = f"""
    Extrage doar numele complet (nume și prenume) din următorul text:
    "{text}"
    
    Returnează doar numele complet cu majuscula pentru ca este nume si prenume, fără explicații sau alte informații.
    """
    messages = [{"role": "system", "content": prompt}]

    response = ask_with_ai(messages , temperature=0.3 , max_tokens=50)

    return response

# @app.route("/comanda_verifica_daca_e_client", methods=["POST"])
# def comanda_etapa_nume_prenume():
#     data = request.get_json()
#     name = data.get("name", "")
#     interests = data.get("interests", "")
#     message = data.get("message", "")
#     # check_sur = check_surname_command_ro(message)

# @app.route("/ai_mai_comandat", methods=["POST"])
# def ai_mai_comandat():
#     data = request.get_json()
#     name = data.get("name", "")
#     interests = data.get("interests", "")
#     message = data.get("message", "")
#     resp = check_response_comanda(message)
#     if resp == "DA":
#         mesaj = (
#             "🤗 Ne bucurăm să te avem din nou alături și îți mulțumim că ești deja clientul nostru!<br><br>"
#             "📝 Pentru a continua comanda cât mai rapid, te rog scrie <strong>numele și prenumele</strong> "
#             "cu care ai făcut comenzile anterioare. Astfel putem verifica mai ușor istoricul tău. 🙌"
#         )
#         return jsonify({"message": mesaj})
#     elif resp == "NU":
        
#         return jsonify({"message": "nu a mai comandat"})
#     else:
#         return jsonify({"message": "altceva"})

@app.route("/check_name_surname", methods=["POST"])
def check_name_surname():
    data = request.get_json()
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")
    if language_saved == "RO":
        check_sur = check_surname_command_ro(message)
    elif language_saved == "RU":
        check_sur = check_surname_command_ru(message)
    elif language_saved == "EN":
        check_sur = check_surname_command_en(message)

    if check_sur == "DA":
        nume_prenume_corect = extrage_nume_din_text(message)
        preferinte["Nume_Prenume"] = nume_prenume_corect
        print("nume_prenume_corect = ", nume_prenume_corect)
        preferinte["Nume_Prenume"] = nume_prenume_corect
        if language_saved == "RO":
            reply = (
                "😊 Mulțumim! Ai un nume frumos! 💬<br><br>"
                "📞 Te rugăm să ne lași un <strong>număr de telefon</strong> pentru a putea <strong>inregistra comanda</strong><br><br>"
            )
            if preferinte.get("country") == "MD":
                reply += "Te rugăm să te asiguri că numărul începe cu <strong>0</strong> sau <strong>+373</strong>. ✅"
            else:
                reply += "Te rugăm să introduci un număr de telefon valid, cu maximum <strong>15 cifre</strong>, inclusiv prefixul internațional (ex: <strong>+49</strong> pentru Germania). ✅"
        elif language_saved == "RU":
            reply = (
                "😊 Спасибо! У тебя красивое имя! 💬<br><br>"
                "📞 Пожалуйста, оставь нам <strong>номер телефона</strong> для регистрации заказа<br><br>"
            )
            if preferinte.get("country") == "MD":
                reply += "Пожалуйста, убедитесь, что номер начинается с <strong>0</strong> или <strong>+373</strong>. ✅"
            else:
                reply += "Пожалуйста, введите действительный номер телефона, максимум <strong>15 цифр</strong>, включая международный код (например, <strong>+49</strong> для Германии). ✅"
        elif language_saved == "EN":
            reply = (
                "😊 Thank you! You have a nice name! 💬<br><br>"
                "📞 Please leave us a <strong>phone number</strong> to register the order<br><br>"
            )
            if preferinte.get("country") == "MD":
                reply += "Please make sure the number starts with <strong>0</strong> or <strong>+373</strong>. ✅"
            else:
                reply += "Please enter a valid phone number, with a maximum of <strong>15 digits</strong>, including the international prefix (e.g., <strong>+49</strong> for Germany). ✅"
    else:
        # prompt_ai = (
        #     f"Nu te saluta niciodata pentru ca deja avem o discutie.\n"
        #     f"Acționează ca un asistent prietenos și politicos.\n"
        #     f"Răspunde la următorul mesaj ca și cum ai fi un agent uman care vrea să ajute clientul.\n"
        #     f"Răspunsul trebuie să fie cald, clar și la obiect. "
        #     f'Mesajul clientului: "{message}"\n\n'
        #     f"Răspuns:"
        # )

        # messages = [{"role": "system", "content": prompt_ai}]
        # reply = ask_with_ai(messages, temperature=0.9 , max_tokens= 150)
        if language_saved == "RO":
            reply = "📞 Introdu, te rog, <strong>doar numele si prenumele</strong> – este foarte important pentru a înregistra comanda. Mulțumim ! 🙏😊"
        elif language_saved == "RU":
            reply = "📞 Пожалуйста, введите <strong>только имя и фамилию</strong> – это очень важно для регистрации заказа. Спасибо! 🙏😊"
        elif language_saved == "EN":
            reply = (
                "📞 Please, enter <strong>only name and surname</strong> – it is very important for order registration. Thank you! 🙏😊"
            )
    
    return jsonify({"message": reply})


def este_numar_valid_local(numar):
    numar = numar.strip()
    if numar.startswith('0') and len(numar) == 9:
        return numar[1] in ['6', '7']
    elif numar.startswith('+373') and len(numar) == 12:
        return numar[4] in ['6', '7']
    elif numar.startswith('373') and len(numar) == 11:
        return numar[3] in ['6', '7']
    else:
        return False

def extrage_si_valideaza_numar_en(text):
    pattern = r'(\+?[()\d\s\-]{6,25})'
    posibile_numere = re.findall(pattern, text)

    for nr in posibile_numere:
        clean = re.sub(r'[^\d+]', '', nr)
        if clean.startswith('+'):
            clean = '+' + re.sub(r'\D', '', clean[1:])
        else:
            clean = re.sub(r'\D', '', clean)

        if 6 <= len(re.sub(r'\D', '', clean)) <= 15:
            return clean, "VALID"

    return None, "INVALID"


def extrage_si_valideaza_numar(text):
    pattern = r'(?<!\d)(\+?373\d{8}|373\d{8}|0\d{8})(?!\d)'
    posibile_numere = re.findall(pattern, text)
    nr = None
    for nr in posibile_numere:
        if este_numar_valid_local(nr):
            return nr , "VALID"
    return nr , "INVALID"

def check_numar(message):
    prompt = (
        "Verifică dacă textul de mai jos conține un număr de telefon, indiferent de format (poate conține spații, paranteze, simboluri, prefix +, etc.).\n"
        "Important este să existe o secvență de cifre care să poată fi considerată un număr de telefon.\n\n"
        f'Text: "{message}"\n\n'
        "RĂSPUNDE STRICT cu:\n"
        "DA – dacă există un număr de telefon în text\n"
        "NU – dacă nu există niciun număr de telefon în text\n\n"
        "Răspunde doar cu DA sau NU. Fără explicații. Fără alte cuvinte."
    )

    messages = [{"role": "system", "content": prompt}]
    response = ask_with_ai(messages, max_tokens=10)
    return response


@app.route("/numar_de_telefon", methods=["POST"])
def numar_de_telefon():
    data = request.get_json()
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")
    valid = check_numar(message)

    print("valid = " , valid)
    if valid == "NU":
        if language_saved == "RO":
            prompt = (
                "Nu te saluta pentru ca deja avem o discutie.\n"
                "Acționează ca un asistent prietenos și politicos.\n"
                "Răspunde natural și cald la mesajul clientului.\n"
                f"Mesaj client: \"{message}\"\n\n"
                "Răspuns:"
            )

            messages = [{"role": "system", "content": prompt}]
            ai_reply = ask_with_ai(messages, max_tokens=150)
            ai_reply += "<br><br> 🙏 Te rog să introduci un număr de telefon valid pentru a putea continua. 📞"
        elif language_saved == "RU":
            prompt = (
                "Не начинай с приветствия, так как разговор уже идет.\n"
                "Веди себя как дружелюбный и вежливый помощник.\n"
                "Ответь тепло и естественно на сообщение клиента.\n"
                f"Сообщение клиента: \"{message}\"\n\n"
                "Ответ:"
            )

            messages = [{"role": "system", "content": prompt}]
            ai_reply = ask_with_ai(messages, max_tokens=150)
            ai_reply += "<br><br> 🙏 Пожалуйста, укажи корректный номер телефона, чтобы мы могли продолжить. 📞"
        elif language_saved == "EN":
            prompt = (
                "Don't start with greetings, as we're already in an ongoing conversation.\n"
                "Act like a friendly and polite assistant.\n"
                "Reply warmly and naturally to the customer's message.\n"
                f"Customer message: \"{message}\"\n\n"
                "Reply:"
            )

            messages = [{"role": "system", "content": prompt}]
            ai_reply = ask_with_ai(messages, max_tokens=150)
            ai_reply += "<br><br> 🙏 Please enter a valid phone number so we can proceed. 📞"
            
        return jsonify({"message": ai_reply})

    print(message)
    if preferinte.get("country") == "MD":
        nr, status = extrage_si_valideaza_numar(message)
    else:
        nr, status = extrage_si_valideaza_numar_en(message)

    preferinte["Numar_Telefon"] = nr
    print(f"valid = {status}")


    if status != "VALID":
        if language_saved == "RO":
            if preferinte.get("country") == "MD":
                reply = (
                    "⚠️ Hmm, numărul introdus nu pare a fi valid.<br>"
                    "Te rog să scrii un număr de telefon care începe cu <strong>0</strong> sau <strong>+373</strong>. 📞"
                )
            else:
                reply = (
                    "⚠️ Hmm, numărul introdus nu pare a fi valid.<br>"
                    "Te rog să scrii un număr de telefon valid, cu maximum <strong>15 cifre</strong>, inclusiv prefixul (ex: <strong>+49</strong> pentru Germania). 📞"
                )

        elif language_saved == "RU":
            if preferinte.get("country") == "MD":
                reply = (
                    "⚠️ Хмм, введенный номер телефона не кажется действительным.<br>"
                    "Пожалуйста, напишите номер телефона, начинающийся с <strong>0</strong> или <strong>+373</strong>. 📞"
                )
            else:
                reply = (
                    "⚠️ Хмм, введенный номер телефона не кажется действительным.<br>"
                    "Пожалуйста, введите корректный номер телефона, максимум <strong>15 цифр</strong>, включая международный код (например, <strong>+49</strong> для Германии). 📞"
                )

        elif language_saved == "EN":
            if preferinte.get("country") == "MD":
                reply = (
                    "⚠️ Hmm, the number you entered doesn't seem to be valid.<br>"
                    "Please write a phone number that starts with <strong>0</strong> or <strong>+373</strong>. 📞"
                )
            else:
                reply = (
                    "⚠️ Hmm, the number you entered doesn't seem to be valid.<br>"
                    "Please enter a valid phone number, with a maximum of <strong>15 digits</strong>, including the country code (e.g., <strong>+49</strong> for Germany). 📞"
                )


    else:
        if language_saved == "RO":
            reply = (
                    "✅ Numărul tău a fost salvat cu succes!<br><br>"
                    "📧 Acum te rog introdu o <strong>adresă de email validă</strong> pentru a putea trimite confirmarea comenzii și detalii suplimentare."
                )
        elif language_saved == "RU":
            reply = (
                "✅ Номер телефона успешно сохранен!<br><br>"
                "📧 Теперь пожалуйста, введите <strong>действительный адрес электронной почты</strong> для отправки подтверждения заказа и дополнительных деталей."
            )
        elif language_saved == "EN":
            reply = (
                "✅ Your phone number has been successfully saved!<br><br>"
                "📧 Now please enter a <strong>valid email address</strong> so we can send the order confirmation and additional details."
            )


    return jsonify({"message": reply})

@app.route("/email", methods=["POST"])
def email():
    data = request.get_json()
    name = data.get("name", "")
    interests = data.get("interests", "")
    message = data.get("message", "")
    language_saved = data.get("language", "RO")

    potential_emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', message)
    valid_emails = []
    for email in potential_emails:
        try:
            valid = validate_email(email)
            valid_email = valid.email
            print(f"Email valid: {valid_email}")
            valid_emails.append(valid_email)
        except EmailNotValidError as e:
            print(f"Email invalid: {email} - {e}")

    if valid_emails:
        email_list = ", ".join(f"<strong>{email}</strong>" for email in valid_emails)
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        EMAIL = valid_emails[0]

        search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"

        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }

        search_body = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "email",
                            "operator": "EQ",
                            "value": EMAIL
                        }
                    ]
                }
            ],
            "properties": ["email"]
        }

        search_response = requests.post(search_url, headers=headers, json=search_body)
        search_data = search_response.json()
        if search_data.get("results"):
            contact_id = search_data["results"][0]["id"]
        else:
            contact_id = "NONE"

        nume_prenume = preferinte.get("Nume_Prenume", "").strip()
        if nume_prenume:
            nume_split = nume_prenume.split(" ")
        else:
            nume_split = []
        nume = nume_split[0]
        prenume = nume_split[1]
        headers = {
            "Authorization": HUBSPOT_TOKEN,
            "Content-Type": "application/json"
        }
        pret_md_str = str(preferinte.get("Pret_MD", "0")).replace(" ", "")
        pret_ue_str = str(preferinte.get("Pret_UE", "0")).replace(" ", "")
        reducere_str = str(preferinte.get("reducere", "0")).replace(" ", "")

        try:
            pret_md = int(pret_md_str)
        except ValueError:
            pret_md = 0  # sau alt fallback

        try:
            pret_ue = int(pret_ue_str)
        except ValueError:
            pret_ue = 0

        # reducere_str = str(preferinte.get("reducere", "0")).replace(" ", "")
        try:
            reducere = int(reducere_str)
        except ValueError:
            reducere = 0

        pret_md_reducere = pret_md - reducere
        pret_ue_reducere = pret_ue - reducere
        # print("preferinte = ", preferinte["Serviciul_Ales"])
        if preferinte.get("BUDGET", "") != "":
            mesaj_telegram = (
                "🔔 <b><u>Nouă solicitare primită!</u></b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Nume:</b> <i>{preferinte.get("Nume_Prenume", "gol")}</i>\n"
                f"📧 <b>Email:</b> <i>{valid_emails[0] if valid_emails else "gol"}</i>\n"
                f"📞 <b>Telefon:</b> <code>{preferinte.get("Numar_Telefon", "0")}</code>\n"
                f"🛠️ <b>Serviciu dorit:</b> {preferinte.get("Serviciul_Ales", "nimic")}\n"
                f"🌐 <b>Limba dorita:</b> <i>{preferinte.get("Limba_Serviciului", "romana")}</i>\n"
                f"💲 <b>Pret MD cu reducere:</b> <i>{preferinte.get("reducere", "").replace(" ", "") if preferinte.get("reducere") else "0"}</i>\n"
                f"💲 <b>Pret UE :</b> <i>{pret_ue}</i>\n"
                f"💲 <b>Buget client:</b> <i>{preferinte.get("BUDGET", "0")}</i>\n"
                f"💬 <b>Mesaj cu preferintele înregistrare din chat:</b> <i>{preferinte.get("Preferintele_Utilizatorului_Cautare", "")}</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "✅ <b>Verifică și confirmă comanda din sistem!</b>\n"
            )

            if contact_id == "NONE":
                data = {
                    "properties": {
                        "firstname": f"{prenume}",
                        "lastname": f"{nume}",
                        "buget": f"{preferinte.get("BUDGET", "")}",
                        "phone": f"{preferinte.get("Numar_Telefon", "")}",
                        "email": f"{valid_emails[0] if valid_emails else ""}",
                        "produs": f"{preferinte.get("Serviciul_Ales", "")}",
                        "limba_serviciu": f"{preferinte.get("Limba_Serviciului", "")}",
                        "pret_md": f"{int(preferinte.get("Pret_MD", "0").replace(" ", "")) if preferinte.get("Pret_MD") else 0}",
                        "pret_ue": f"{int(preferinte.get("Pret_UE", "0").replace(" ", "")) if preferinte.get("Pret_UE") else 0}",
                        "reducere": f"{preferinte.get("reducere", "").replace(" ", "") if preferinte.get("reducere") else ""}",
                        "hs_lead_status": "NEW",
                        "preferinte_inregistrare": f"{preferinte.get("Preferintele_Utilizatorului_Cautare", "")}",
                        # "contract": f"{}"
                    }
                }       

                response_hubspot = requests.post(url, headers=headers, json=data)
                print(response_hubspot.json())

            else:
                update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
                update_body = {
                    "properties": {
                        "firstname": f"{prenume}",
                        "lastname": f"{nume}",
                        "buget": f"{preferinte.get("BUDGET", "")}",
                        "phone": f"{preferinte.get("Numar_Telefon", "")}",
                        "email": f"{valid_emails[0] if valid_emails else ""}",
                        "produs": f"{preferinte.get("Serviciul_Ales", "")}",
                        "limba_serviciu": f"{preferinte.get("Limba_Serviciului", "")}",
                        "pret_md": f"{int(preferinte.get("Pret_MD", "0").replace(" ", "")) if preferinte.get("Pret_MD") else 0}",
                        "pret_ue": f"{int(preferinte.get("Pret_UE", "0").replace(" ", "")) if preferinte.get("Pret_UE") else 0}",
                        "reducere": f"{preferinte.get("reducere", "").replace(" ", "") if preferinte.get("reducere") else ""}",
                        "hs_lead_status": "NEW",
                        "preferinte_inregistrare": f"{preferinte.get("Preferintele_Utilizatorului_Cautare", "")}",
                    }
                }
                update_response = requests.patch(update_url, headers=headers, json=update_body)
                if update_response.status_code == 200:
                    print("✅ Contact actualizat cu succes!")
                else:
                    print("❌ Eroare la actualizare:", update_response.json())
        else:
            mesaj_telegram = (
                "🔔 <b><u>Nouă solicitare primită!</u></b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Nume:</b> <i>{preferinte.get("Nume_Prenume", "")}</i>\n"
                f"📧 <b>Email:</b> <i>{valid_emails[0] if valid_emails else ""}</i>\n"
                f"📞 <b>Telefon:</b> <code>{preferinte.get("Numar_Telefon", "")}</code>\n"
                f"🛠️ <b>Serviciu dorit:</b> {preferinte.get("Serviciul_Ales", "")}\n"
                f"💲 <b>Pret MD cu reducere:</b> <i>{preferinte.get("reducere", "").replace(" ", "")}</i>\n"
                f"💲 <b>Pret UE :</b> <i>{pret_ue}</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "✅ <b>Verifică și confirmă comanda din sistem!</b>\n"
            )

            if contact_id == "NONE":
                data = {
                    "properties": {
                        "firstname": f"{prenume}",
                        "lastname": f"{nume}",
                        "phone": f"{preferinte.get("Numar_Telefon", "")}",
                        "email": f"{valid_emails[0] if valid_emails else ""}",
                        "produs": f"{preferinte.get("Serviciul_Ales", "")}",
                        "pret_md": f"{int(preferinte.get("Pret_MD", "0").replace(" ", ""))}",
                        "pret_ue": f"{int(preferinte.get("Pret_UE", "0").replace(" ", ""))}",
                        "reducere": f"{preferinte.get("reducere", "").replace(" ", "")}",
                        "hs_lead_status": "NEW",
                    }
                }

                response_hubspot = requests.post(url, headers=headers, json=data)
                print(response_hubspot.json())

            else:
                update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
                update_body = {
                    "properties": {
                        "firstname": f"{prenume}",
                        "lastname": f"{nume}",
                        "phone": f"{preferinte.get("Numar_Telefon", "")}",
                        "email": f"{valid_emails[0] if valid_emails else ""}",
                        "produs": f"{preferinte.get("Serviciul_Ales", "")}",
                        "pret_md": f"{int(preferinte.get("Pret_MD", "0").replace(" ", ""))}",
                        "pret_ue": f"{int(preferinte.get("Pret_UE", "0").replace(" ", ""))}",
                        "reducere": f"{preferinte.get("reducere", "").replace(" ", "")}",
                        "hs_lead_status": "NEW",
                    }
                }
                update_response = requests.patch(update_url, headers=headers, json=update_body)
                if update_response.status_code == 200:
                    print("✅ Contact actualizat cu succes!")
                else:
                    print("❌ Eroare la actualizare:", update_response.json())


        url = f"https://api.telegram.org/bot{TELEGRAM}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": mesaj_telegram,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=payload)
        if language_saved == "RO":
            return jsonify({
                "message": """
                    <strong>🎉 Comandă înregistrată cu succes!</strong><br>
                    <em>✅ Am notat toate datele importante și totul este pregătit.</em><br><br>

                    <b>💬 Ce dorești să faci mai departe?</b><br><br>

                    👉 <strong>Plasăm o nouă comandă?</strong> 🛒<br>
                    👉 <strong>Descoperim alte servicii?</strong> 🧰<br>
                    👉 <strong>Alegem împreună un serviciu în funcție de preferințele tale?</strong> 🎯<br><br>

                    🧭 <em>Spune-mi ce te interesează și te ghidez cu drag!</em> 😊
                """
            })
        elif language_saved == "RU":
            return jsonify({
                "message": """
                    <strong>🎉 Заказ успешно оформлен!</strong><br>
                    <em>✅ Все важные данные записаны, всё готово.</em><br><br>

                    <b>💬 Что бы ты хотел сделать дальше?</b><br><br>

                    👉 <strong>Оформим новый заказ?</strong> 🛒<br>
                    👉 <strong>Посмотрим другие услуги?</strong> 🧰<br>
                    👉 <strong>Выберем услугу по вашим предпочтениям?</strong> 🎯<br><br>

                    🧭 <em>Расскажи, что тебя интересует, и я с радостью помогу!</em> 😊
                """
            })
        elif language_saved == "EN":
            return jsonify({
                "message": """
                    <strong>🎉 Your order has been successfully placed!</strong><br>
                    <em>✅ All the important details are saved and everything is ready.</em><br><br>

                    <b>💬 What would you like to do next?</b><br><br>

                    👉 <strong>Place a new order?</strong> 🛒<br>
                    👉 <strong>Explore other services?</strong> 🧰<br>
                    👉 <strong>Choose a service based on your preferences?</strong> 🎯<br><br>

                    🧭 <em>Let me know what you're interested in and I’ll be happy to help!</em> 😊
                """
            })
    else:
        if language_saved == "RO":
            mesaj = (
                "😊 <strong>Te rog frumos să introduci o adresă de email validă</strong> ca să putem continua fără probleme. ✨ Mulțumesc din suflet! 💌"
            )
        elif language_saved == "RU":
            mesaj = (
                "😊 <strong>Пожалуйста, введите действительный адрес электронной почты</strong> чтобы мы могли продолжить без проблем. ✨ Спасибо от души! 💌"
            )
        elif language_saved == "EN":
            mesaj = (
                "😊 <strong>Please enter a valid email address</strong> so we can continue without any issues. ✨ Thank you from the bottom of my heart! 💌"
            )
        return jsonify({"message": mesaj})



def generate_welcome_message(name, interests):
    system_prompt = (
        f"Ești un chatbot inteligent, prietenos și util. Evită să repeți saluturi precum „Salut”, „Bine ai venit” sau numele utilizatorului ({name}) în fiecare mesaj. "
        f"Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
        f"Generează un mesaj foarte scurt și natural, mai scurt de 80 de tokenuri, "
        f"referitor la interesele mele: {interests}. "
        f"Mesajul trebuie să fie cald și încurajator, fără introduceri formale. "
        f"Mesajul trebuie să se termine exact cu: „Cu ce te pot ajuta astăzi?” "
        f"Nu adăuga alte întrebări sau fraze suplimentare. "
        f"Nu saluta, nu repeta numele, doar treci direct la subiect. "
        f"Mereu când ești întrebat de vreo preferință, sfat, alegere sau orice, fă referire la {interests} mele și apoi spune și ceva adițional."
    )
    messages = [{"role": "system", "content": system_prompt}]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.9,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()





def ask_with_ai(messages, temperature=0.9, max_tokens=200):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()


def get_user_info():
    name_prompt = (
        "Generează o întrebare scurtă și prietenoasă prin care să ceri utilizatorului să-și spună numele. "
        "Întrebarea trebuie să înceapă cu un salut simplu, cum ar fi „Salut”, „Bună” sau „Hei”. "
        "Formularea trebuie să fie naturală, clară și fără exagerări. "
        "Evită expresii siropoase sau prea entuziaste (ex: „Ce nume frumos”, „dezvăluie”). "
        "Păstrează un ton prietenos, dar echilibrat. Variază formulările între rulări."
    )
    interests_prompt = (
        "Generează o întrebare naturală și prietenoasă prin care să afli ce interese sau hobby-uri are utilizatorul. "
        "Fii creativ și nu repeta aceeași formulare."
    )

    ask_name = ask_with_ai(name_prompt)
    name = input(ask_name + " ")

    ask_interests = ask_with_ai(interests_prompt)
    interests = input(f"{ask_interests} ")

    return name, interests


def build_messages(name, interests):
    system_prompt = (
        f"Răspunsul să fie mai scurt de 250 de tokenuri. "
        f"Utilizatorul se numește {name} și este interesat de: {interests}. "
        f"Ajută-l să își atingă obiectivele prin răspunsuri precise și relevante. "
        f"Fă referire la {interests} de fiecare dată când îi propui ceva, ține cont de ceea ce îi place. Pe lângă asta, poți adăuga și alte variante. "
        f"Dacă utilizatorul are intenția de a încheia discuția, dacă formulează fraze de adio, atunci încheie discuția elegant. "
        f"Ești un chatbot inteligent, prietenos și util. Evită să repeți saluturi precum „Salut”, „Bine ai venit” sau numele utilizatorului ({name}) în fiecare mesaj. "
        f"Răspunde direct, personalizat, scurt și clar, ca și cum conversația este deja în desfășurare. "
        f"Dacă utilizatorul îți zice că nu mai vrea să audă așa mult despre {interests}, atunci schimbă puțin subiectul. "
        f"Ești un chatbot inteligent, prietenos și util. Pe utilizator îl cheamă {name}, "
        f"și este interesat de: {interests}. Oferă răspunsuri personalizate, scurte și clare. Arată cât mai evident că știi acea persoană și ajut-o să își atingă obiectivele prin răspunsuri clare și bine puse la punct!"
    )
    return [{"role": "system", "content": system_prompt}]


@app.route("/", methods=["GET"])
def home():
    return render_template('website.html')


@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == "POST":
        data = request.get_json()
        emoji = data.get("emoji", "")
        reason = data.get("reason", "")
        language = data.get("language", "")

        print("emoji =", emoji)
        print("reason =", reason)
        print("language =", language)

        # Returnează confirmare
        return jsonify({"status": "success"}), 200
    
    # Pentru GET, poți returna o simplă confirmare sau instrucțiuni
    return jsonify({"message": "Succes"}), 200

    



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

# @app.route("/", defaults={"path": ""})
# @app.route("/<path:path>")
# def serve(path):
#     if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
#         return send_from_directory(app.static_folder, path)
#     else:
#         return send_from_directory(app.static_folder, "index.html")

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))
#     app.run(host="0.0.0.0", port=port,debug=True, use_reloader=False)
