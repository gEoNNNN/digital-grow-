from flask import Flask, request
import requests
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
from chatbot import *


user_states = {}

preferinte_messenger = {
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


app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

def genereaza_prompt_produse_messenger(rezultat, categorie, language_saved):
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
        lista_formatata += f"{idx}. {nume}\n"

    if language_saved == "RO":
        prompt = (
            "Am identificat câteva servicii relevante în urma cererii tale:\n\n"
            f"{lista_formatata}\n"
            "Te rog să alegi exact denumirea serviciului dorit pentru a continua configurarea."
        )
    elif language_saved == "RU":
        prompt = (
            "По вашему запросу найдены следующие релевантные услуги:\n\n"
            f"{lista_formatata}\n"
            "Пожалуйста, укажите точное название нужной услуги, чтобы мы могли продолжить."
        )
    else:
        prompt = (
            "We identified a few relevant services in response to your request:\n\n"
            f"{lista_formatata}\n"
            "Please select the exact name of the desired service to continue configuration."
        )

    return prompt


def build_service_prompt_messenger(categorii_unice, language_saved):
    emoji_list = [
        "💼", "🧠", "📱", "💻", "🛠️", "🎨", "🚀", "🧰", "📈", "📊", "🔧",
        "🖥️", "📦", "🧾", "🌐", "📣", "🤖", "🧑‍💻", "📇", "🗂️", "🖌️", "💡", "📍", "🆕"
    ]
    if language_saved == "RO":
        intro = (
            "Îți pot oferi o gamă variată de servicii IT specializate.\n\n"
            "Te rog alege serviciul dorit din lista de mai jos și răspunde cu denumirea exactă.\n"
            "(Apasă sau scrie exact denumirea serviciului pentru a continua)\n\n"
        )
    elif language_saved == "RU":
        intro = (
            "Я могу предложить вам широкий спектр IT-услуг.\n\n"
            "Пожалуйста, выберите нужный сервис из списка ниже и ответьте с точным названием.\n"
            "(Нажмите или напишите точное название сервиса для продолжения)\n\n"
        )
    else:
        intro = (
            "I can offer you a wide range of IT services.\n\n"
            "Please choose the desired service from the list below and respond with the exact name.\n"
            "(Click or write the exact name of the service to continue)\n\n"
        )

    service_lines = []
    used_emojis = set()
    for categorie in categorii_unice:
        emoji = random.choice(emoji_list)
        while emoji in used_emojis and len(used_emojis) < len(emoji_list):
            emoji = random.choice(emoji_list)
        used_emojis.add(emoji)

        line = f"{emoji} {categorie}"
        service_lines.append(line)

    prompt = intro + "\n".join(service_lines)
    return prompt

def build_service_prompt_2_messenger(categorii_unice, language_saved):
    emoji_list = [
        "💼", "🧠", "📱", "💻", "🛠️", "🎨", "🚀", "🧰", "📈", "📊", "🔧",
        "🖥️", "📦", "🧾", "🌐", "📣", "🤖", "🧑‍💻", "📇", "🗂️", "🖌️", "💡", "📍", "🆕"
    ]
    if language_saved == "RO":
        intro = "Te rog alege serviciul dorit din lista de mai jos și răspunde cu denumirea exactă:\n\n"
    elif language_saved == "RU":
        intro = "Пожалуйста, выберите нужный сервис из списка ниже и ответьте с точным названием:\n\n"
    else:
        intro = "Please choose the desired service from the list below and respond with the exact name:\n\n"

    service_lines = []
    used_emojis = set()
    for categorie in categorii_unice:
        emoji = random.choice(emoji_list)
        while emoji in used_emojis and len(used_emojis) < len(emoji_list):
            emoji = random.choice(emoji_list)
        used_emojis.add(emoji)

        line = f"{emoji} {categorie}"
        service_lines.append(line)

    prompt = intro + "\n".join(service_lines)
    return prompt



def send_language_selection(recipient_id):
    url = f"https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {
            "text": "🌍 Alege limba / Choose your language / Выберите язык:",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "🇷🇴 Română",
                    "payload": "LANG_RO"
                },
                {
                    "content_type": "text",
                    "title": "🇬🇧 English",
                    "payload": "LANG_EN"
                },
                {
                    "content_type": "text",
                    "title": "🇷🇺 Русский",
                    "payload": "LANG_RU"
                }
            ]
        }
    }
    response = requests.post(url, params=params, headers=headers, json=data)
    print("send_language_selection response:", response.status_code, response.text)


def send_message(text, recipient_id):
    max_len = 2000
    url = f"https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}

    for i in range(0, len(text), max_len):
        part = text[i:i + max_len]
        data = {
            "recipient": {"id": recipient_id},
            "message": {"text": part}
        }
        response = requests.post(url, params=params, headers=headers, json=data)
        print("send_message response:", response.status_code, response.text)

def start_check(message_text, sender_id):
    check_language_rag = check_language(message_text)

    if check_language_rag == "RO":
        # language_saved = "RO"
        user_states[sender_id]["language"] = "RO"
        ask_name = (
            "👋 Bun venit la DigitalGrow! 😊\n\n"
            "Te pot ajuta cu:\n"
            "📌 Serviciile disponibile\n"
            "🎯 Alegerea unui serviciu în funcție de preferințele tale\n"
            "🛒 Sau poate dorești direct să achiziționezi unul. 💼✨"
        )

    elif check_language_rag == "RU":
        user_states[sender_id]["language"] = "RU"
        ask_name = (
            "👋 Добро пожаловать в DigitalGrow! 😊\n\n"
            "Я могу помочь вам с:\n"
            "📌 Доступными услугами\n"
            "🎯 Выбором услуги по вашим предпочтениям\n"
            "🛒 Или вы хотите сразу оформить заказ. 💼✨"
        )

    else:
        user_states[sender_id]["language"] = "EN"
        ask_name = (
            "👋 Welcome to DigitalGrow! 😊\n\n"
            "I can help you with:\n"
            "📌 Available services\n"
            "🎯 Choosing a service based on your preferences\n"
            "🛒 Or maybe you’re ready to make a purchase. 💼✨"
        )

    user_states[sender_id]["onboardingStep"] = 1
    
    # print(user_states[sender_id]["onboardingStep"])
    send_message(ask_name,sender_id)
    return

def interests_check(message_text, sender_id):
    language_saved = user_states.get(sender_id, {}).get("language", "RO")

    if user_states[sender_id]["language"] == "RO":
        check = check_interest(message_text)
    elif user_states[sender_id]["language"] == "RU":
        check = check_interest_ru(message_text)
    else:
        check = check_interest_en(message_text)
    
    print("check = ! = " , check)
    if check == "preferinte":
        user_states[sender_id]["onboardingStep"] = 5
        if language_saved == "RO":
            reply = (
                "💰 Haide să alegem un buget potrivit pentru serviciul dorit!\n\n"
                "Alege una dintre opțiunile de mai jos, sau scrie un buget estimativ dacă ai altă preferință:\n\n"
                "🔹 10 000 MDL – Proiect simplu, ideal pentru un început clar și eficient\n"
                "🔸 20 000 MDL – Echilibru între funcționalitate și personalizare\n"
                "🌟 50 000 MDL+ – Soluții avansate, complete, cu funcții extinse și design premium\n\n"
                "✍️ Ne poți scrie direct o altă sumă dacă ai un buget diferit în minte!"
            )
            send_message(reply, sender_id)
            return
        elif language_saved == "RU":
            reply = (
                "💰 Давайте выберем подходящий бюджет для желаемого сервиса!\n\n"
                "Выберите один из вариантов ниже или напишите приблизительную сумму, если у тебя есть другое предпочтение:\n\n"
                "🔹 10 000 MDL – Простой проект, идеально подходит для четкого начала и эффективности\n"
                "🔸 20 000 MDL – Баланс между функциональностью и персонализацией\n"
                "🌟 50 000 MDL+ – Расширенные решения, полные, с расширенными функциями и премиальным дизайном\n\n"
                "✍️ Можешь написать другую сумму, если у тебя другой бюджет!"
            )
            send_message(reply, sender_id)
            return
        else:
            reply = (
                "💰 Let's choose a suitable budget for the desired service!\n\n"
                "Choose one of the options below or write an approximate amount if you have a different preference:\n\n"
                "🔹 10 000 MDL – Simple project, ideal for clear start and efficiency\n"
                "🔸 20 000 MDL – Balance between functionality and personalization\n"
                "🌟 50 000 MDL+ – Advanced solutions, complete, with extended features and premium design\n\n"
                "✍️ You can write a different amount if you have a different budget!"
            )
            send_message(reply, sender_id)
            return

    if "produs_informații" in check or "general" in check:
        user_states[sender_id]["onboardingStep"] = 2
        if language_saved == "RO":
            reply = build_service_prompt_messenger(categorii_unice, language_saved)
        elif language_saved == "RU":
            reply = build_service_prompt_messenger(categorii_unice_ru, language_saved)
        else:
            reply = build_service_prompt_messenger(categorii_unice_en, language_saved)
        print(reply)
        send_message(reply, sender_id)
        return

    elif check == "comandă":
        user_states[sender_id]["onboardingStep"] = 15
        if language_saved == "RO":
            mesaj = (
                "🎉 Mă bucur că vrei să plasezi o comandă!\n\n"
                "📋 Hai să parcurgem împreună câțiva pași simpli pentru a înregistra comanda cu succes. 🚀\n\n"
            )
        elif language_saved == "RU":
            mesaj = (
                "🎉 Мне приятно, что вы хотите сделать заказ!\n\n"
                "📋 Давайте пройдем вместе несколько простых шагов для успешной регистрации заказа. 🚀\n\n"
            )
        else:
            mesaj = (
                "🎉 I'm glad you want to place an order!\n\n"
                "📋 Let's go through a few simple steps to successfully register the order. 🚀\n\n"
            )

        if language_saved == "RO":
            mesaj1 = build_service_prompt_2_messenger(categorii_unice, language_saved)
            mesaj += mesaj1
        elif language_saved == "RU":
            mesaj1 = build_service_prompt_2_messenger(categorii_unice_ru, language_saved)
            mesaj += mesaj1
        else:
            mesaj1 = build_service_prompt_2_messenger(categorii_unice_en, language_saved)
            mesaj += mesaj1

        send_message(mesaj, sender_id)
        return

    else:
        user_states[sender_id]["onboardingStep"] = 1
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris: '{message_text}'.\n\n"
                "Nu spune niciodată „Salut” sau alte introduceri, pentru că deja ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural care:\n"
                "1. Răspunde pe scurt la ce a spus utilizatorul.\n"
                "2. Mesajul să fie scurt, cald, empatic și prietenos (maxim 2-3 propoziții).\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "\n\n❓ Te rugăm să ne spui dacă:\n"
                "👉 vrei să afli mai multe informații despre serviciile disponibile\n"
                "🎯 preferi să alegi un serviciu în funcție de preferințele tale\n"
                "🛒 sau vrei să faci o comandă direct."
            )
            reply = mesaj

        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал: '{message_text}'.\n\n"
                "Не говори никогда «Привет» или другие вступления, потому что мы уже знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что сказал пользователь.\n"
                "2. Сообщение должно быть кратким, теплым, эмпатичным и дружелюбным (максимум 2-3 предложения).\n"
                "Не используй кавычки и не объясняй, что делаешь — только итоговое сообщение."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "\n\n❓ Пожалуйста, скажи, хочешь ли ты:\n"
                "👉 узнать больше информации о доступных услугах\n"
                "🎯 предпочесть услугу по твоим предпочтениям\n"
                "🛒 или сделать заказ напрямую."
            )
            reply = mesaj

        else:
            prompt = (
                f"The user wrote: '{message_text}'.\n\n"
                "Never say greetings like 'Hi' or similar intros, because you already know the user. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. Message should be short, warm, empathetic and friendly (max 2-3 sentences).\n"
                "Do not use quotation marks and do not explain what you do — only the final message."
            )
            messages = [{"role": "system", "content": prompt}]
            message = ask_with_ai(messages).strip()
            message += (
                "\n\n❓ Please let us know:\n"
                "👉 if you want to learn more about the available services\n"
                "🎯 if you'd prefer to choose a service based on your preferences\n"
                "🛒 or if you're ready to place an order directly."
            )
            reply = message

        send_message(reply, sender_id)
        return


def welcome_products(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    mesaj = ""
    prompt_verify = (
        f"Ai o listă de servicii valide: {categorii_unice}\n\n"
        f"Verifică dacă textul următor conține cel puțin un serviciu valid sau o denumire care seamănă suficient (similaritate mare) cu vreuna din serviciile valide.\n\n"
        f'Text de verificat: "{message_text}"\n\n'
        f'Răspunde strict cu "DA" dacă există o potrivire validă sau asemănătoare, altfel răspunde cu "NU".'
    )

    messages = [{"role": "system", "content": prompt_verify}] 
    resp = ask_with_ai(messages , max_tokens=10)

    if language_saved == "RO":
        rezultat = function_check_product(message_text , categorii_unice, "RO")
    elif language_saved == "RU":
        rezultat = function_check_product(message_text , categorii_unice_ru, "RU")
    else:
        rezultat = function_check_product(message_text , categorii_unice_en, "EN")

    if rezultat == "NU":
        lungime_rezultat = 0
    else:
        lungime_rezultat = len(rezultat)


    if lungime_rezultat == 1:
        produs = rezultat[0].get('produs', "") 
        preferinte_messenger["Serviciul_Ales"] = produs
        print("rezultatul =", rezultat)
        print("produs = ", produs)
        detalii = extract_info(produs, language_saved)
        print("detalii ===!!!! ", detalii)
        if detalii:
            descriere = detalii.get("descriere", "N/A")
            beneficii = detalii.get("beneficii", "N/A")
            pret_md = detalii.get("pret_md", "N/A")
            pret_ue = detalii.get("pret_ue", "N/A")

            preferinte_messenger["Pret_MD"] = pret_md
            preferinte_messenger["Pret_UE"] = pret_ue
            # print(preferinte["Pret_MD"])
            # print(preferinte["Pret_UE"])
            pret_reducere = detalii.get("reducere", "N/A")
            preferinte_messenger["reducere"] = pret_reducere
            if language_saved == "RO" or language_saved == "RU":
                preferinte_messenger["country"] = "MD"
            else:
                preferinte_messenger["country"] = "UE"


            if language_saved == "RO":
                # print("tara = ", preferinte["country"])
                user_states[sender_id]["onboardingStep"] = 3
                # print(user_states[sender_id]["onboardingStep"])

                if preferinte_messenger.get("country", "") == "MD":
                    mesaj = (
                        f"✅ Am găsit serviciul tău! Iată toate detaliile despre {produs} 🧩\n\n"
                        f"📌 Descriere:\n{descriere}\n\n"
                        f"🎯 Beneficii:\n{beneficii}\n\n"
                        f"💸 📢 Ține-te bine! Am vești bune pentru tine!\n"
                        f"Acest produs avea prețul de ~{pret_md} MDL~, dar acum este REDUS și îl poți lua cu doar {pret_reducere} MDL! 🤑\n"
                        f"💥 Asta înseamnă că economisești {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                        f"🎯 Preț valabil doar pentru o perioadă limitată!\n\n"
                        "🔄 Dacă vrei detalii despre un alt serviciu, să faci o comandă sau să alegem după preferințe, scrie-mi te rog! 😊"
                    )
                else:
                    mesaj = (
                        f"✅ Am găsit serviciul tău! Iată toate detaliile despre {produs} 🧩\n\n"
                        f"📌 Descriere:\n{descriere}\n\n"
                        f"🎯 Beneficii:\n{beneficii}\n\n"
                        f"🇪🇺 Preț: {pret_ue} MDL\n\n"
                        "🔄 Dacă vrei detalii despre un alt serviciu, să faci o comandă sau să alegem după preferințe, scrie-mi te rog! 😊"
                    )
                

            elif language_saved == "RU":
                user_states[sender_id]["onboardingStep"] = 3
                if preferinte_messenger.get("country", "") == "MD":
                    mesaj = (
                        f"✅ Мы нашли вашу услугу! Вот все детали по {produs} 🧩\n\n"
                        f"📌 Описание:\n{descriere}\n\n"
                        f"🎯 Преимущества:\n{beneficii}\n\n"
                        f"💸 📢 Держитесь! У нас для вас отличные новости!\n"
                        f"Этот продукт раньше стоил ~{pret_md} MDL~, но сейчас его можно получить всего за {pret_reducere} MDL! 🤑\n"
                        f"💥 Это значит, что вы экономите {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                        f"🎯 Цена действует только ограниченное время!\n\n"
                        "🔄 Если хотите узнать детали о другой услуге, оформить заказ или выбрать по предпочтениям, напишите мне, пожалуйста! 😊"
                    )
                else:
                    mesaj = (
                        f"✅ Мы нашли вашу услугу! Вот все детали по {produs} 🧩\n\n"
                        f"📌 Описание:\n{descriere}\n\n"
                        f"🎯 Преимущества:\n{beneficii}\n\n"
                        f"🇪🇺 Цена: {pret_ue} MDL\n\n"
                        "🔄 Если хотите узнать детали о другой услуге, оформить заказ или выбрать по предпочтениям, напишите мне, пожалуйста! 😊"
                    )
            elif language_saved == "EN":
                # print("tara = ", preferinte["country"])
                user_states[sender_id]["onboardingStep"] = 3
                if preferinte_messenger.get("country", "") == "MD":
                    mesaj = (
                        f"✅ We found your service! Here are all the details about {produs} 🧩\n\n"
                        f"📌 Description:\n{descriere}\n\n"
                        f"🎯 Benefits:\n{beneficii}\n\n"
                        f"💸 📢 Hold on! We’ve got great news for you!\n"
                        f"This product used to cost ~{pret_md} MDL~, but now you can get it for only {pret_reducere} MDL! 🤑\n"
                        f"💥 That means you save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                        f"🎯 The price is valid for a limited time only!\n\n"
                        "🔄 If you'd like to see details about a different service, place an order, or choose based on your preferences, just let me know! 😊"
                    )
                else:
                    mesaj = (
                        f"✅ We found your service! Here are all the details about {produs} 🧩\n\n"
                        f"📌 Description:\n{descriere}\n\n"
                        f"🎯 Benefits:\n{beneficii}\n\n"
                        f"🇪🇺 Price: {pret_ue} MDL\n\n"
                        "🔄 If you'd like to see details about a different service, place an order, or choose based on your preferences, just let me know! 😊"
                    )



            preferinte_messenger["Produs_Pentru_Comanda"] = produs

            # return jsonify({"message": mesaj})
            send_message(mesaj, sender_id)
            return
        

    elif lungime_rezultat > 1:
        if language_saved == "RO":
            reply = genereaza_prompt_produse_messenger(rezultat, resp, "RO")
        elif language_saved == "RU":
            reply = genereaza_prompt_produse_messenger(rezultat, resp, "RU")
        elif language_saved == "EN":
            reply = genereaza_prompt_produse_messenger(rezultat, resp, "EN")
        # return jsonify({"message": reply})
        user_states[sender_id]["onboardingStep"] = 2
        send_message(reply, sender_id)
        return
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message_text}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            reply = build_service_prompt_2_messenger(categorii_unice, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал категорию: '{message_text}'.\n\n"
                "Никогда не приветствуй, так как мы уже ведём разговор и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что ты делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            reply = build_service_prompt_2_messenger(categorii_unice_ru, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user wrote the category: '{message_text}'.\n\n"
                "Never say 'Hello' or anything introductory — we are already in a conversation and familiar with each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2-3 sentences.\n"
                "Do not use quotation marks and do not explain what you're doing — just write the final message for the user."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            reply = build_service_prompt_2_messenger(categorii_unice_en, language_saved)
            mesaj = mesaj + reply

            

        # return jsonify({"message": mesaj})
        user_states[sender_id]["onboardingStep"] = 3
        send_message(mesaj, sender_id)
        return
    send_message(mesaj, sender_id)
    return


def chat_general(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    prompt_verify = (
        f"Ai o listă de servicii valide: {categorii_unice}\n\n"
        f"Verifică dacă textul următor conține cel puțin un serviciu valid sau o denumire care seamănă suficient (similaritate mare) cu vreuna din serviciile valide.\n\n"
        f'Text de verificat: "{message_text}"\n\n'
        f'Răspunde strict cu "DA" dacă există o potrivire validă sau asemănătoare, altfel răspunde cu "NU".'
    )

    message = message_text
    messages = [{"role": "system", "content": prompt_verify}] 
    resp = ask_with_ai(messages , max_tokens=10)


    if resp == "DA":
        if language_saved == "RO":  
            rezultat = function_check_product(message_text , categorii_unice, "RO")
        elif language_saved == "RU":
            rezultat = function_check_product(message_text , categorii_unice_ru, "RU")
        elif language_saved == "EN":
            rezultat = function_check_product(message_text , categorii_unice_en, "EN")
        print("rezultat = ", rezultat)


        if rezultat == "NU":
            lungime_rezultat = 0
        else:
            lungime_rezultat = len(rezultat)

        if lungime_rezultat == 1:
            produs = rezultat[0].get('produs', "")
            print("rezultatul =", produs)
            detalii = extract_info(produs, language_saved)            
            if detalii:
                descriere = detalii.get("descriere", "N/A")
                beneficii = detalii.get("beneficii", "N/A")
                pret_md = detalii.get("pret_md", "N/A")
                pret_ue = detalii.get("pret_ue", "N/A")
 

                preferinte_messenger["Pret_MD"] = pret_md
                # print(preferinte["Pret_MD"])
                preferinte_messenger["Pret_UE"] = pret_ue
                # print(preferinte["Pret_UE"])
                pret_reducere = detalii.get("reducere", "N/A")
                preferinte_messenger["reducere"] = pret_reducere

                if language_saved == "RO" or language_saved == "RU":
                    preferinte_messenger["country"] = "MD"
                else:
                    preferinte_messenger["country"] = "UE"
                
                if language_saved == "RO":
                    if preferinte_messenger.get("country", "") == "MD":
                        mesaj = (
                            f"✅ Am găsit serviciul tău! Iată toate detaliile despre {produs} 🧩\n\n"
                            f"📌 Descriere:\n{descriere}\n\n"
                            f"🎯 Beneficii:\n{beneficii}\n\n"
                            f"💸 📢 Ține-te bine! Am vești bune pentru tine!\n"
                            f"Acest produs avea prețul de {pret_md} MDL, dar acum este REDUS și îl poți lua cu doar {pret_reducere} MDL! 🤑\n"
                            f"💥 Asta înseamnă că economisești {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                            f"🎯 Preț valabil doar pentru o perioadă limitată!\n\n"
                            "🔄 Dacă vrei detalii despre un alt serviciu, să faci o comandă sau să alegem după preferințe, scrie-mi te rog! 😊"
                        )
                    else:
                        mesaj = (
                            f"✅ Am găsit serviciul tău! Iată toate detaliile despre {produs} 🧩\n\n"
                            f"📌 Descriere:\n{descriere}\n\n"
                            f"🎯 Beneficii:\n{beneficii}\n\n"
                            f"🇪🇺 Preț: {pret_ue} MDL\n\n"
                            "🔄 Dacă vrei detalii despre un alt serviciu, să faci o comandă sau să alegem după preferințe, scrie-mi te rog! 😊"
                        )

                elif language_saved == "RU":
                    if preferinte_messenger.get("country", "") == "MD":
                        mesaj = (
                            f"✅ Мы нашли вашу услугу! Вот все детали по {produs} 🧩\n\n"
                            f"📌 Описание:\n{descriere}\n\n"
                            f"🎯 Преимущества:\n{beneficii}\n\n"
                            f"💸 📢 Держитесь! У нас для вас отличные новости!\n"
                            f"Этот продукт раньше стоил {pret_md} MDL, но сейчас его можно получить всего за {pret_reducere} MDL! 🤑\n"
                            f"💥 Это значит, что вы экономите {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                            f"🎯 Цена действует только ограниченное время!\n\n"
                            # f"🇪🇺 Цена для Европейского Союза: {pret_ue} MDL\n\n"
                            "🔄 Если хотите узнать детали о другой услуге, оформить заказ или выбрать по предпочтениям, напишите мне, пожалуйста! 😊"
                        )
                    else:
                        mesaj = (
                            f"✅ Мы нашли вашу услугу! Вот все детали по {produs} 🧩\n\n"
                            f"📌 Описание:\n{descriere}\n\n"
                            f"🎯 Преимущества:\n{beneficii}\n\n"
                            f"🇪🇺 Цена: {pret_ue} MDL\n\n"
                            "🔄 Если хотите узнать детали о другой услуге, оформить заказ или выбрать по предпочтениям, напишите мне, пожалуйста! 😊"
                        )
                elif language_saved == "EN":
                    if preferinte_messenger.get("country", "") == "MD":
                        mesaj = (
                            f"✅ We found your service! Here are all the details about {produs} 🧩\n\n"
                            f"📌 Description:\n{descriere}\n\n"
                            f"🎯 Benefits:\n{beneficii}\n\n"
                            f"💸 📢 Great news for you!\n"
                            f"This product used to cost {pret_md} MDL, but now it's available for only {pret_reducere} MDL! 🤑\n"
                            f"💥 That means you save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                            f"🎯 This price is only valid for a limited time!\n\n"
                            "🔄 If you'd like to see details about a different service, place an order, or choose based on your preferences, just let me know! 😊"
                        )
                    else:
                        mesaj = (
                            f"✅ We found your service! Here are all the details about {produs} 🧩\n\n"
                            f"📌 Description:\n{descriere}\n\n"
                            f"🎯 Benefits:\n{beneficii}\n\n"
                            f"🇪🇺 Price: {pret_ue} MDL\n\n"
                            "🔄 If you'd like to see details about a different service, place an order, or choose based on your preferences, just let me know! 😊"
                        )


                # return jsonify({"message": mesaj})
                send_message(mesaj, sender_id)
                return

        elif lungime_rezultat > 1:
            if language_saved == "RO":
                reply = genereaza_prompt_produse_messenger(rezultat, resp, "RO")
            elif language_saved == "RU":
                reply = genereaza_prompt_produse_messenger(rezultat, resp, "RU")
            elif language_saved == "EN":
                reply = genereaza_prompt_produse_messenger(rezultat, resp, "EN")
            # return jsonify({"message": reply})
            send_message(reply, sender_id)
            return
        else:
            if language_saved == "RO":
                prompt = (
                    f"Utilizatorul a scris categoria: '{message_text}'.\n\n"
                    "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                    "Scrie un mesaj politicos, prietenos și natural, care:\n"
                    "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                    "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                    "Nu mai mult de 2-3 propoziții.\n"
                    "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
                )

                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                reply = build_service_prompt_2_messenger(categorii_unice,language_saved)
                mesaj = mesaj + reply
            elif language_saved == "RU":
                prompt = (
                    f"Пользователь написал категорию: '{message_text}'.\n\n"
                    "Никогда не приветствуй, так как мы уже ведём разговор и знакомы. "
                    "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                    "1. Кратко отвечает на то, что написал пользователь.\n"
                    "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                    "Не более 2-3 предложений.\n"
                    "Не используй кавычки и не объясняй, что ты делаешь — пиши только итоговое сообщение."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                reply = build_service_prompt_2_messenger(categorii_unice_ru,language_saved)
                mesaj = mesaj + reply
            elif language_saved == "EN":
                prompt = (
                    f"The user wrote the category: '{message_text}'.\n\n"
                    "Never say 'Hello' or anything introductory — we are already in a conversation and familiar with each other. "
                    "Write a polite, friendly, and natural message that:\n"
                    "1. Briefly responds to what the user said.\n"
                    "2. The message should be short, warm, empathetic, and friendly.\n"
                    "No more than 2-3 sentences.\n"
                    "Do not use quotation marks and do not explain what you're doing — just write the final message for the user."
                )
                messages = [{"role": "system", "content": prompt}]
                mesaj = ask_with_ai(messages).strip()
                reply = build_service_prompt_2_messenger(categorii_unice_en,language_saved)
                mesaj = mesaj + reply
                
            
            # return jsonify({"message": mesaj})
            send_message(mesaj, sender_id)
            return
    elif resp == "NU":
        if language_saved == "RO":
            check = check_interest_pref(message_text)
        elif language_saved == "RU":
            check = check_interest_pref_ru(message_text)
        elif language_saved == "EN":
            check = check_interest_pref_en(message_text)


        if check == "produs_informații" or check == "produs_informatii":
            if language_saved == "RO":
                reply = build_service_prompt_messenger(categorii_unice, language_saved)
            elif language_saved == "RU":
                reply = build_service_prompt_messenger(categorii_unice_ru, language_saved)
            elif language_saved == "EN":
                reply = build_service_prompt_messenger(categorii_unice_en, language_saved)
            # return jsonify({"message": reply})
            user_states[sender_id]["onboardingStep"] = 2
            send_message(reply, sender_id)
            return
        elif check == "comandă" or check == "comanda":
            if language_saved == "RO":
                mesaj = (
                    "🎉 Mǎ bucur că vrei să plasezi o comandă!\n\n"
                    "📋 Hai să parcurgem împreună câțiva pași simpli pentru a înregistra comanda cu succes. 🚀\n\n"
                )
                user_states[sender_id]["onboardingStep"] = 15
            elif language_saved == "RU":
                mesaj = (
                    "🎉 Рад(а), что вы хотите сделать заказ!\n\n"
                    "📋 Давайте вместе пройдем несколько простых шагов, чтобы успешно оформить заказ. 🚀\n\n"
                )
                user_states[sender_id]["onboardingStep"] = 15
            elif language_saved == "EN":
                mesaj = (
                    "🎉 I'm glad you want to place an order!\n\n"
                    "📋 Let's go through a few simple steps together to successfully place the order. 🚀\n\n"
                )
                user_states[sender_id]["onboardingStep"] = 15

            if preferinte_messenger["Produs_Pentru_Comanda"] != "":
                produs = preferinte_messenger.get("Produs_Pentru_Comanda", "")
                if language_saved == "RO":
                    mesaj = f"📦 Doriți să plasați o comandă pentru serviciul {produs}? ✨\nRăspundeți cu Da sau Nu."
                elif language_saved == "RU":
                    mesaj = f"📦 Хотите оформить заказ на услугу {produs}? ✨\nОтветьте Да или Нет."
                elif language_saved == "EN":
                    mesaj = f"📦 Would you like to place an order for the {produs} service? ✨\nPlease reply with Yes or No."
                # return jsonify({"message": mesaj})
                user_states[sender_id]["onboardingStep"] = 20
                send_message(mesaj, sender_id)
                return

            if language_saved == "RO":
                mesaj1 = build_service_prompt_2_messenger(categorii_unice, language_saved)
            elif language_saved == "RU":
                mesaj1 = build_service_prompt_2_messenger(categorii_unice_ru, language_saved)
            elif language_saved == "EN":
                mesaj1 = build_service_prompt_2_messenger(categorii_unice_en, language_saved)


            reply = mesaj + mesaj1
            user_states[sender_id]["onboardingStep"] = 2
            # return jsonify({"message": reply})
            send_message(reply, sender_id)
            return
                
        elif check == "preferinte":
            if language_saved == "RO":
                prompt_buget = (
                    "💰 Haide să alegem un buget potrivit pentru serviciul dorit!\n\n"
                    "Alege una dintre opțiunile de mai jos, sau scrie un buget estimativ dacă ai altă preferință:\n\n"
                    "🔹 10 000 MDL – Proiect simplu, ideal pentru un început clar și eficient\n"
                    "🔸 20 000 MDL – Echilibru între funcționalitate și personalizare\n"
                    "🌟 50 000 MDL+ – Soluții avansate, complete, cu funcții extinse și design premium\n\n"
                    "✍️ Ne poți scrie direct o altă sumă dacă ai un buget diferit în minte!"
                )
            elif language_saved == "RU":
                prompt_buget = (
                    "💰 Давайте выберем подходящий бюджет для желаемой услуги!\n\n"
                    "Выберите один из вариантов ниже или напишите примерный бюджет, если у вас есть другой предпочтительный вариант:\n\n"
                    "🔹 10 000 MDL – Простой проект, идеально подходит для ясного и эффективного старта\n"
                    "🔸 20 000 MDL – Баланс между функциональностью и персонализацией\n"
                    "🌟 50 000 MDL+ – Продвинутые, комплексные решения с расширенными функциями и премиальным дизайном\n\n"
                    "✍️ Вы также можете сразу указать другую сумму, если у вас другой бюджет!"
                )
            elif language_saved == "EN":
                prompt_buget = (
                    "💰 Let's choose a suitable budget for the desired service!\n\n"
                    "Choose one of the options below or write an estimated budget if you have a different preferred option:\n\n"
                    "🔹 10 000 MDL – Simple project, ideal for a clear and efficient start\n"
                    "🔸 20 000 MDL – Balance between functionality and personalization\n"
                    "🌟 50 000 MDL+ – Advanced, comprehensive solutions with extended features and premium design\n\n"
                    "✍️ You can also write a different amount directly if you have another budget in mind!"
                )

            # return jsonify({"message": prompt_buget})
            user_states[sender_id]["onboardingStep"] = 5
            send_message(prompt_buget, sender_id)
            return
        else:
            if language_saved == "RO":
                prompt = (
                    f"Utilizatorul a scris : '{message_text}'.\n\n"
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
                    "\n\n❓ Te rugăm să ne spui dacă:\n"
                    "  🔍 Vrei mai multe informații despre serviciu\n"
                    "  🛒 Vrei să achiziționezi un serviciu\n"
                    "  🛒 Vrei să alegem după preferințe\n"
                )
                reply = mesaj
            elif language_saved == "RU":
                prompt = (
                    f"Пользователь написал: '{message_text}'.\n\n"
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
                    "\n\n❓ Пожалуйста, скажи, что из этого тебе интересно:\n"
                    "  🔍 Хочешь больше информации о сервисе\n"
                    "  🛒 Хочешь приобрести услугу\n"
                    "  🛒 Хочешь выбрать по предпочтениям\n"
                )
                reply = mesaj
            elif language_saved == "EN":
                prompt = (
                    f"The user wrote: '{message_text}'.\n\n"
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
                    "\n\n❓ Please tell me what you're interested in:\n"
                    "  🔍 Want more information about the service\n"
                    "  🛒 Want to purchase the service\n"
                    "  🛒 Want to choose based on preferences\n"
                )
                reply = mesaj

            # return jsonify({"message": reply})
            user_states[sender_id]["onboardingStep"] = 3
            send_message(reply, sender_id)
            return


def criteria_general(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text

    if language_saved == "RO":
        response = check_response(message_text)
    elif language_saved == "RU":
        response = check_response_ru(message_text)
    else:
        response = check_response_en(message_text)

    if response == "general":
        user_states[sender_id]["onboardingStep"] = 2
        if language_saved == "RO":
            reply = build_service_prompt_messenger(categorii_unice, language_saved)
        elif language_saved == "RU":
            reply = build_service_prompt_messenger(categorii_unice_ru, language_saved)
        else:
            reply = build_service_prompt_messenger(categorii_unice_en, language_saved)

    elif response == "preferinte":
        user_states[sender_id]["onboardingStep"] = 5
        if language_saved == "RO":
            reply = (
                "💰 Haide să alegem un buget potrivit pentru serviciul dorit!\n\n"
                "Alege una dintre opțiunile de mai jos, sau scrie un buget estimativ dacă ai altă preferință:\n\n"
                "🔹 10 000 MDL – Proiect simplu, ideal pentru un început clar și eficient\n"
                "🔸 20 000 MDL – Echilibru între funcționalitate și personalizare\n"
                "🌟 50 000 MDL+ – Soluții avansate, complete, cu funcții extinse și design premium\n\n"
                "✍️ Ne poți scrie direct o altă sumă dacă ai un buget diferit în minte!"
            )
        elif language_saved == "RU":
            reply = (
                "💰 Давайте выберем подходящий бюджет для желаемого сервиса!\n\n"
                "Выберите один из вариантов ниже или напишите приблизительную сумму, если у тебя есть другое предпочтение:\n\n"
                "🔹 10 000 MDL – Простой проект, идеально подходит для четкого начала и эффективности\n"
                "🔸 20 000 MDL – Баланс между функциональностью и персонализацией\n"
                "🌟 50 000 MDL+ – Расширенные решения, полные, с расширенными функциями и премиальным дизайном\n\n"
                "✍️ Можешь написать другую сумму, если у тебя другой бюджет!"
            )
        else:
            reply = (
                "💰 Let's choose a suitable budget for the desired service!\n\n"
                "Choose one of the options below or write an approximate amount if you have a different preference:\n\n"
                "🔹 10 000 MDL – Simple project, ideal for clear start and efficiency\n"
                "🔸 20 000 MDL – Balance between functionality and personalization\n"
                "🌟 50 000 MDL+ – Advanced solutions, complete, with extended features and premium design\n\n"
                "✍️ You can write a different amount if you have a different budget!"
            )
    else:
        user_states[sender_id]["onboardingStep"] = 4
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris : '{message_text}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n✍️ Te rugăm să scrii: general sau preferinte pentru a merge mai departe."
            reply = mesaj

        elif language_saved == "RU":
            prompt = (
                f"Utilizatorul a scris : '{message_text}'.\n\n"
                "Не говори никогда „Привет”, всегда начинай с вступительных слов, потому что мы уже общаемся и знакомы. "
                "Пиши политичный, дружелюбный и естественный текст, который:\n"
                "1. Быстро отвечает на то, что сказал пользователь. "
                "2. Краткий, теплый, эмпатичный и дружелюбный. "
                "Не более 2-3 предложений.\n"
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n✍️ Пожалуйста, напишите: общая информация или предпочтения для продолжения."
            reply = mesaj

        else:
            prompt = (
                f"The user wrote: '{message_text}'.\n\n"
                "Never say greetings like 'Hi' or similar intros, because you're already in a conversation and know the user. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. Feels warm, empathetic, and friendly, in no more than 2–3 short sentences.\n"
                "Do not use quotation marks and do not explain what you're doing — write only the final message for the user."
            )
            messages = [{"role": "system", "content": prompt}]
            message = ask_with_ai(messages).strip()
            message += "\n\n✍️ Please write: general or preferences to continue."
            reply = message

    # return jsonify({"message": reply})
    send_message(reply, sender_id)
    return


def budget_general(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text
    budget_c = check_budget(message_text)
    
    if budget_c == "NONE":
        user_states[sender_id]["onboardingStep"] = 5
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message_text}'.\n\n"
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
                "\n\n💬 Apropo, ca să pot veni cu sugestii potrivite, îmi poți spune cam ce buget ai în minte? (în MDL)\n"
                "💸 <2000 MDL – buget mic\n"
                "💶 2000–10 000 MDL – buget mediu\n"
                "💰 10 000–25 000 MDL – buget generos\n"
                "💎 50 000+ MDL – soluții avansate\n"
                "✍️ Sau scrie pur și simplu suma estimativă."
            )
        elif language_saved == "RU":
            prompt = (
                f"Пользователь выбрал категорию: '{message_text}'.\n\n"
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
                "\n\n💬 Кстати, чтобы предложить оптимальные варианты, подскажите, пожалуйста, какой у вас ориентировочный бюджет? (в MDL)\n"
                "💸 <2000 MDL – небольшой бюджет\n"
                "💶 2000–10 000 MDL – средний бюджет\n"
                "💰 10 000–25 000 MDL – щедрый бюджет\n"
                "💎 50 000+ MDL – продвинутые решения\n"
                "✍️ Или просто напишите примерную сумму."
            )
        elif language_saved == "EN":
            prompt = (
                f"The user selected the category: '{message_text}'.\n\n"
                "Never say 'Hi' or use introductory phrases, since we're already in an ongoing conversation. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to the user's input.\n"
                "2. Is warm, empathetic, and friendly – no more than 2–3 sentences.\n"
                "Do not use quotation marks or explain what you're doing — just write the final message for the user."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "\n\n💬 By the way, to offer the most suitable options, could you please let me know your approximate budget? (in MDL)\n"
                "💸 <2000 MDL – small budget\n"
                "💶 2000–10 000 MDL – medium budget\n"
                "💰 10 000–25 000 MDL – generous budget\n"
                "💎 50 000+ MDL – advanced solutions\n"
                "✍️ Or feel free to just write an estimated amount."
            )

        # return jsonify({"message": mesaj})
        send_message(mesaj, sender_id)
        return
    else:
        user_states[sender_id]["onboardingStep"] = 6
        preferinte_messenger["BUDGET"] = budget_c
        if language_saved == "RO":
            mesaj = (
                f"✅ Am notat bugetul tău: {budget_c} MDL.\n\n"
                "🌐 În ce limbă ai prefera să fie oferit serviciul?\n\n"
                "🇷🇴 Română – comunicare completă în limba română\n"
                "🇷🇺 Русский – servicii în limba rusă\n"
                "🇬🇧 English – servicii în limba engleză\n"
                "🌍 Multilingv – combinăm limbile după preferință\n\n"
                "✍️ Te rog scrie limba dorită sau alege 'multilingv' dacă dorești flexibilitate."
            )
        elif language_saved == "RU":
            mesaj = (
                f"✅ Ваш бюджет был зафиксирован: {budget_c} MDL.\n\n"
                "🌐 На каком языке вы предпочитаете получить услугу?\n\n"
                "🇷🇴 Română – полное обслуживание на румынском языке\n"
                "🇷🇺 Русский – полное обслуживание на русском языке\n"
                "🇬🇧 English – полное обслуживание на английском языке\n"
                "🌍 Мультиязычный – комбинируем языки по вашему выбору\n\n"
                "✍️ Пожалуйста, укажите желаемый язык или выберите 'Мультиязычный' для гибкости."
            )
        elif language_saved == "EN":
            mesaj = (
                f"✅ Your budget has been saved: {budget_c} MDL.\n\n"
                "🌐 What language would you prefer the service to be in?\n\n"
                "🇷🇴 Română – full communication in Romanian\n"
                "🇷🇺 Русский – full communication in Russian\n"
                "🇬🇧 English – full communication in English\n"
                "🌍 Multilingual – we can combine languages as needed\n\n"
                "✍️ Please write your preferred language or choose 'Multilingual' for flexibility."
            )

        # return jsonify({"message": mesaj})
        send_message(mesaj, sender_id)
        return



def preference_language_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text

    if language_saved == "RO":
        preference_language = check_preference_language(message_text)
    elif language_saved == "RU":
        preference_language = check_preference_language_ru(message_text)
    else:
        preference_language = check_preference_language_en(message_text)

    if preference_language == "necunoscut":
        user_states[sender_id]["onboardingStep"] = 6
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message_text}'.\n\n"
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
                "\n\n🌍 Ca să-ți ofer informațiile cât mai potrivit, îmi poți spune în ce limbă preferi să fie serviciul?\n\n"
                "🟡 Română – limba română\n"
                "🔵 Rusă – русский язык\n"
                "🟢 Engleză – english\n"
                "🌐 Multilingv – mai multe limbi combinate, după preferințe"
            )
        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал категорию: '{message_text}'.\n\n"
                "Никогда не начинай с «Здравствуйте» или других вводных, так как мы уже ведем диалог и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Должно быть теплым, эмпатичным и дружелюбным – не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что ты делаешь – просто напиши итоговое сообщение для пользователя."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "\n\n🌍 Чтобы дать тебе максимально точную информацию, напиши, пожалуйста, на каком языке тебе удобно общаться:\n\n"
                "🟡 Румынский – limba română\n"
                "🔵 Русский – на русском языке\n"
                "🟢 Английский – english\n"
                "🌐 Мультиязычный – комбинируем языки по твоим предпочтениям"
            )
        elif language_saved == "EN":
            prompt = (
                f"The user wrote the category: '{message_text}'.\n\n"
                "Never start with 'Hello' or any kind of introduction – we're already in a conversation and know each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. Is warm, empathetic, and friendly – no more than 2–3 sentences.\n"
                "Don't use quotation marks or explain what you're doing – just return the final message for the user."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += (
                "\n\n🌍 To offer you the most relevant information, could you tell me your preferred language?\n\n"
                "🟡 Romanian – limba română\n"
                "🔵 Russian – на русском языке\n"
                "🟢 English – full communication in English\n"
                "🌐 Multilingual – a mix of languages based on your preferences"
            )
        
        # return jsonify({"message": mesaj})
        send_message(mesaj, sender_id)
        return
    else:
        user_states[sender_id]["onboardingStep"] = 7
        preferinte_messenger["Limba_Serviciului"] = preference_language
        if language_saved == "RO":
            reply = (
                "💡 Super! Spune-mi, te rog, ce funcționalități ți-ar plăcea să includă serviciul?\n\n"
                "📌 De exemplu: „Platformă de vânzări online cu plată prin card”, „Pagină de prezentare pentru un eveniment”, „Site cu ChatBot Inteligent + CRM” etc.\n\n"
                "✍️ Poți scrie liber ce ai în minte, iar noi îți vom propune opțiuni potrivite."
            )
        elif language_saved == "RU":
            reply = (
                "💡 Супер! Скажите, пожалуйста, какие функциональные возможности вы хотели бы включить в услугу?\n\n"
                "📌 Например: „Платформа для онлайн-продаж с платежной картой”, „Страница для презентации мероприятия”, „Сайт с Интеллектуальным Чатботом + CRM” и т.д.\n\n"
                "✍️ Можете написать, что угодно, и мы предложим вам подходящие варианты."
            )
        elif language_saved == "EN":
            reply = (   
                "💡 Super! Tell me, please, what features would you like to include in the service?\n\n"
                "📌 For example: “Online sales platform with card payment”, “Presentation page for an event”, “Website with Intelligent ChatBot + CRM”, etc.\n\n"
                "✍️ You can write anything you want, and we'll suggest suitable options."
            )
        
        # return jsonify({"message": reply})
        send_message(reply, sender_id)
        return


def filtreaza_servicii_dupa_buget_messenger(servicii_dict, buget_str, language_saved):
    buget = parse_pret(buget_str)
    rezultate = {}
    
    for nume_serviciu, detalii in servicii_dict.items():
        pret_md = parse_pret(detalii.get("pret_md", "0"))
        pret_ue = parse_pret(detalii.get("pret_ue", "0"))
        pret_reducere = parse_pret(detalii.get("reducere", "0"))

        if language_saved == "RO" or language_saved == "RU":
            preferinte_messenger["country"] = "MD"
        else:
            preferinte_messenger["country"] = "UE"

        if preferinte_messenger.get("country", "MD") == "MD":
            if pret_reducere <= buget :
                rezultate[nume_serviciu] = detalii
        else:
            if pret_ue <= buget :
                rezultate[nume_serviciu] = detalii

    return rezultate


def functionalities_check(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text
    preferinte_messenger["Preferintele_Utilizatorului_Cautare"] = message_text
    # print("language_saved = ", language_saved)
    servicii_dict = extract_servicii_dict(language_saved)
    # print("servicii_dict = ", servicii_dict)
    buget = "DA"
    servicii_potrivite = filtreaza_servicii_dupa_buget_messenger(servicii_dict, preferinte_messenger.get("BUDGET", ""),language_saved)
    func111 = check_functionalities_with_ai(message_text, servicii_potrivite)
    if func111 == "NONE":
        buget = "NU"

    length_servicii_potrivite_buget = len(servicii_potrivite)

    if length_servicii_potrivite_buget == 0:
        func = check_functionalities_with_ai(message_text, servicii_dict)

        if func == "NONE":
            if language_saved == "RO":
                prompt = (
                    f"Utilizatorul a scris serviciul: '{message_text}'.\n\n"
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
                    "\n\n❗️ Din ce ai scris, nu am reușit să identific un serviciu potrivit pentru nevoia ta."
                    "\n💬 Te rog să-mi spui mai clar ce funcționalități ți-ar plăcea să aibă – de exemplu: „platformă de vânzare produse online”, „site de prezentare cu 3-5 pagini”, „creare logo” etc."
                    "\n\n🔍 Cu cât mai clar, cu atât mai ușor îți pot recomanda variante potrivite!"
                )
                user_states[sender_id]["onboardingStep"] = 7
                # return jsonify({"message": mesaj})
                send_message(mesaj, sender_id)
                return
            elif language_saved == "RU":
                prompt = (
                    f"Пользователь указал услугу: '{message_text}'.\n\n"
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
                    "\n\n❗️ Из того, что вы написали, я не смог определить подходящую услугу под ваш запрос."
                    "\n💬 Пожалуйста, опишите более конкретно, какие функции или решения вы ищете – например: «онлайн-платформа для продажи товаров», «сайт-презентация на 3–5 страниц», «разработка логотипа» и т.д."
                    "\n\n🔍 Чем точнее описание, тем проще будет подобрать для вас подходящие варианты!"
                )
                # return jsonify({"message": mesaj})
                user_states[sender_id]["onboardingStep"] = 7
                send_message(mesaj, sender_id)
                return
            elif language_saved == "EN":
                prompt = (
                    f"The user wrote the service: '{message_text}'.\n\n"
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
                    "\n\n❗️ From what you wrote, I couldn’t quite identify a specific service that fits your request."
                    "\n💬 Please tell me a bit more clearly what kind of features or solution you're looking for – for example: “online store platform”, “presentation website with 3–5 pages”, “logo creation”, etc."
                    "\n\n🔍 The clearer you are, the better suggestions I can offer!"
                )
                # return jsonify({"message": mesaj})
                user_states[sender_id]["onboardingStep"] = 7
                send_message(mesaj, sender_id)
                return
                
        else:
            if ";" in func:
                splited_func = func.split(";")
                preferinte_messenger["Produs_Pentru_Comanda"] = splited_func
            elif "\n" in func:
                splited_func = func.split("\n")
                preferinte_messenger["Produs_Pentru_Comanda"] = splited_func
            else:
                splited_func = [func]
                preferinte_messenger["Produs_Pentru_Comanda"] = splited_func

            mesaj = ""
            for i in splited_func:
                
                detalii = extract_info(i, language_saved)
                
                if detalii:
                    descriere = detalii.get("descriere", "N/A")
                    beneficii = detalii.get("beneficii", "N/A")
                    pret_md = detalii.get("pret_md", "N/A")
                    pret_ue = detalii.get("pret_ue", "N/A")
                    pret_reducere = detalii.get("reducere", "N/A")
                    # country = preferinte_messenger.get("country", "")

                    if language_saved == "RO" or language_saved == "RU":
                        preferinte_messenger["country"] = "MD"
                        country = "MD"
                    else:
                        preferinte_messenger["country"] = "UE"
                        country = "UE"

                    if language_saved == "RO":
                        if country == "MD":
                            mesaj += (
                                f"✅ Iată toate detaliile despre {i} 🧩\n\n"
                                f"📌 Descriere:\n{descriere}\n\n"
                                f"🎯 Beneficii:\n{beneficii}\n\n"
                                f"💸 📢 Ține-te bine! Am vești bune pentru tine!\n"
                                f"Acest produs avea prețul de {pret_md} MDL, dar acum este REDUS și îl poți lua cu doar {pret_reducere} MDL! 🤑\n"
                                f"💥 Economisești {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                                f"🎯 Preț valabil doar pentru o perioadă limitată!\n\n"
                                # f"{'-'*40}\n"
                            )
                        else:
                            mesaj += (
                                f"✅ Iată toate detaliile despre {i} 🧩\n\n"
                                f"📌 Descriere:\n{descriere}\n\n"
                                f"🎯 Beneficii:\n{beneficii}\n\n"
                                f"🇪🇺 Preț: {pret_ue} MDL\n\n"
                                # f"{'-'*40}\n"
                            )
                    elif language_saved == "RU":
                        if preferinte_messenger.get("country", "") == "MD":
                            mesaj += (
                                f"✅ Вот вся информация о {i} 🧩\n\n"
                                f"📌 Описание:\n{descriere}\n\n"
                                f"🎯 Преимущества:\n{beneficii}\n\n"
                                f"💸 📢 У нас отличные новости для вас!\n"
                                f"Этот продукт раньше стоил {pret_md} MDL, но сейчас он со СКИДКОЙ и доступен всего за {pret_reducere} MDL! 🤑\n"
                                f"💥 Вы экономите {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                                f"🎯 Цена действует только в течение ограниченного времени!\n\n"
                                # f"{'-'*40}\n"
                            )
                        else:
                            mesaj += (
                                f"✅ Вот вся информация о {i} 🧩\n\n"
                                f"📌 Описание:\n{descriere}\n\n"
                                f"🎯 Преимущества:\n{beneficii}\n\n"
                                f"🇪🇺 Цена: {pret_ue} MDL\n\n"
                                # f"{'-'*40}\n"
                            )

                    elif language_saved == "EN":
                        if preferinte_messenger.get("country", "") == "MD":
                            mesaj += (
                                f"✅ Here are all the details about {i} 🧩\n\n"
                                f"📌 Description:\n{descriere}\n\n"
                                f"🎯 Benefits:\n{beneficii}\n\n"
                                f"💸 📢 Great news for you!\n"
                                f"This product used to cost {pret_md} MDL, but now it is AVAILABLE WITH A DISCOUNT for only {pret_reducere} MDL! 🤑\n"
                                f"💥 You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                                f"🎯 The price is valid only for a limited time!\n\n"
                                # f"🇪🇺 Price for the European Union: {pret_ue} MDL\n\n"
                                # f"{'-'*40}\n"
                            )
                        else:
                            mesaj += (
                                f"✅ Here are all the details about {i} 🧩\n\n"
                                f"📌 Description:\n{descriere}\n\n"
                                f"🎯 Benefits:\n{beneficii}\n\n"
                                f"🇪🇺 Price: {pret_ue} MDL\n\n"
                                # f"{'-'*40}\n"
                            )

            if language_saved == "RO":
                if buget == "NU":
                    mesaj += (
                        "❗️ Nu sunt servicii potrivite pentru bugetul ales, dar am găsit unele pe baza funcționalităților alese.\n"
                    )
            elif language_saved == "RU":
                if buget == "NU":
                    mesaj += (
                        "❗️ Не найдено услуг, подходящих для выбранного бюджета, но мы нашли варианты, соответствующие выбранным функциональным возможностям.\n"
                    )
            elif language_saved == "EN":
                if buget == "NU":
                    mesaj += (
                        "❗️ No services suitable for the chosen budget, but we found options that match the selected functional features.\n"
                    )

            if language_saved == "RO":
                mesaj += "\n💬 Dorești să faci o comandă? Răspunde cu DA sau NU\n"
                user_states[sender_id]["onboardingStep"] = 8
            elif language_saved == "RU":
                mesaj += "\n💬 Хотите сделать заказ? Ответьте ДА или НЕТ\n"
                user_states[sender_id]["onboardingStep"] = 8
            elif language_saved == "EN":
                mesaj += "\n💬 Do you want to make an order? Answer with YES or NO\n"
                user_states[sender_id]["onboardingStep"] = 8

    else:
        func = check_functionalities_with_ai(message_text, servicii_potrivite)
        print("func = ", func)
        # func += ("<br><br> Acestea sunt serviciile potrivite pentru bugetul + functionalitatile alese")
        # print("func ======= ", func)
        if func == "NONE":
            func = check_functionalities_with_ai(message_text, servicii_dict)
            if func == "NONE":
                if language_saved == "RO":
                    prompt = (
                        f"Utilizatorul a scris serviciul: '{message_text}'.\n\n"
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
                        "\n\n❗️ Din ce ai scris, nu am reușit să identific un serviciu potrivit pentru nevoia ta."
                        "\n💬 Te rog să-mi spui mai clar ce funcționalități ți-ar plăcea să aibă – de exemplu: „platformă de vânzare produse online”, „site de prezentare cu 3-5 pagini”, „creare logo”."
                        "\n\n🔍 Cu cât mai clar, cu atât mai ușor îți pot recomanda variante potrivite!"
                    )
                    user_states[sender_id]["onboardingStep"] = 7
                elif language_saved == "RU":
                    prompt = (
                        f"Пользователь написал о сервисе: '{message_text}'.\n\n"
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
                        "\n\n❗️ Из того, что вы написали, я не смог определить подходящую услугу для ваших нужд."
                        "\n💬 Пожалуйста, расскажите более подробно, какие функции вы хотели бы видеть — например: «платформа для продажи товаров онлайн», «сайт-визитка с 3-5 страницами», «создание логотипа»."
                        "\n\n🔍 Чем яснее вы выразитесь, тем проще будет подобрать для вас подходящие варианты!"
                    )
                    user_states[sender_id]["onboardingStep"] = 7
                elif language_saved == "EN":
                    prompt = (
                        f"The user wrote about the service: '{message_text}'.\n\n"
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
                        "\n\n❗️ From what you wrote, I couldn't identify a service suitable for your needs."
                        "\n💬 Please tell me more clearly what features you'd like – for example: 'online product sales platform', 'presentation site with 3-5 pages', 'logo creation'."
                        "\n\n🔍 The clearer you are, the easier it will be for me to recommend suitable options!"
                    )
                    user_states[sender_id]["onboardingStep"] = 7
                
                # return jsonify({"message": mesaj})
                send_message(mesaj, sender_id)
                return
            else:
                if ";" in func:
                    splited_func = func.split(";")
                    preferinte_messenger["Produs_Pentru_Comanda"] = splited_func
                elif "\n" in func:
                    splited_func = func.split("\n")
                    preferinte_messenger["Produs_Pentru_Comanda"] = splited_func
                else:
                    splited_func = [func]
                    # if language_saved == "RO":
                    #     splited_func = ["Pachet : Business Smart" , "Site Complex Multilingv (>5 pagini)" , "Magazin Online (E-commerce)"]
                    # elif language_saved == "RU":
                    #     splited_func = ["Пакет: Business Smart" , "Сложный многоязычный сайт (более 5 страниц)" , "Магазин Онлайн (Электронная коммерция)" ]
                    # elif language_saved == "EN":
                    #     splited_func = ["Business Smart" , "Site Complex Multilingual (>5 pages)" , "Online Store (E-commerce)" ]
                    preferinte_messenger["Produs_Pentru_Comanda"] = splited_func

                mesaj = ""
                
                for i in splited_func:
                    detalii = extract_info(i, language_saved)
                    
                    if detalii:
                        descriere = detalii.get("descriere", "N/A")
                        beneficii = detalii.get("beneficii", "N/A")
                        pret_md = detalii.get("pret_md", "N/A")
                        pret_ue = detalii.get("pret_ue", "N/A")
                        pret_reducere = detalii.get("reducere", "N/A")

                        if language_saved == "RO" or language_saved == "RU":
                            preferinte_messenger["country"] = "MD"
                        else:
                            preferinte_messenger["country"] = "UE"

                        if language_saved == "RO":
                            if preferinte_messenger.get("country", "") == "MD":
                                mesaj += (
                                    f"✅ Iată toate detaliile despre {i} 🧩\n\n"
                                    f"📌 Descriere:\n{descriere}\n\n"
                                    f"🎯 Beneficii:\n{beneficii}\n\n"
                                    f"💸 📢 Ține-te bine! Am vești bune pentru tine!\n"
                                    f"Acest produs avea prețul de {pret_md} MDL, dar acum este REDUS și îl poți lua cu doar {pret_reducere} MDL! 🤑\n"
                                    f"💥 Economisești {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                                    f"🎯 Preț valabil doar pentru o perioadă limitată!\n\n"
                                    # f"---------------------------------------------\n"
                                )
                            else:
                                mesaj += (
                                    f"✅ Iată toate detaliile despre {i} 🧩\n\n"
                                    f"📌 Descriere:\n{descriere}\n\n"
                                    f"🎯 Beneficii:\n{beneficii}\n\n"
                                    f"🇪🇺 Preț : {pret_ue} MDL\n\n"
                                )
                        elif language_saved == "RU":
                            if preferinte_messenger.get("country", "") == "MD":
                                mesaj += (
                                    f"✅ Вот вся информация о {i} 🧩\n\n"
                                    f"📌 Описание:\n{descriere}\n\n"
                                    f"🎯 Преимущества:\n{beneficii}\n\n"
                                    f"💸 📢 У нас отличные новости для вас!\n"
                                    f"Этот продукт раньше стоил {pret_md} MDL, но сейчас он со СКИДКОЙ и доступен всего за {pret_reducere} MDL! 🤑\n"
                                    f"💥 Вы экономите {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                                    f"🎯 Цена действует только в течение ограниченного времени!\n\n"
                                    # f"---------------------------------------------\n"
                                )
                            else:
                                mesaj += (
                                    f"✅ Вот вся информация о {i} 🧩\n\n"
                                    f"📌 Описание:\n{descriere}\n\n"
                                    f"🎯 Преимущества:\n{beneficii}\n\n"
                                    f"🇪🇺 Цена : {pret_ue} MDL\n\n"
                                    # f"---------------------------------------------\n"
                                )

                        elif language_saved == "EN":
                            if preferinte_messenger.get("country", "") == "MD":
                                mesaj += (
                                    f"✅ Here are all the details about {i} 🧩\n\n"
                                    f"📌 Description:\n{descriere}\n\n"
                                    f"🎯 Benefits:\n{beneficii}\n\n"
                                    f"💸 📢 Great news for you!\n"
                                    f"This product used to cost {pret_md} MDL, but now it is AVAILABLE WITH A DISCOUNT for only {pret_reducere} MDL! 🤑\n"
                                    f"💥 You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                                    f"🎯 The price is valid only for a limited time!\n\n"
                                    # f"🇪🇺 Price for the European Union: {pret_ue} MDL\n\n"
                                    # f"-----------------------------------------------------\n"
                                )
                            else:
                                mesaj += (
                                    f"✅ Here are all the details about {i}\n\n"
                                    f"Description:\n{descriere}\n\n"
                                    f"Benefits:\n{beneficii}\n\n"
                                    f"Price: {pret_ue} MDL\n\n"
                                    # "-----------------------------------------------------\n"
                                )
                            
                if language_saved == "RO":
                    if buget == "NU":
                        mesaj += (
                            "❗️ Nu sunt servicii potrivite pentru bugetul ales, dar am găsit după funcționalitățile alese.\n"
                        )

                        # mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"

                    

                    mesaj += "\nDorești să faci o comandă? Răspunde cu DA sau NU.\n"
                    user_states[sender_id]["onboardingStep"] = 8
                elif language_saved == "RU":
                    if buget == "NU":
                        mesaj += "❗️ Вот услуги, которые подходят по вашему бюджету и выбранным функциям\n"
                        # mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"

                   
                

                    mesaj += "\n💬 Хотите сделать заказ? Ответьте ДА или НЕТ\n"
                    user_states[sender_id]["onboardingStep"] = 8

                elif language_saved == "EN":
                    if buget == "NU":
                        mesaj += "❗️ No services suitable for the chosen budget, but we found options that match the selected functional features\n"
                        # mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"

                    

                    mesaj += "\n💬 Do you want to make an order? Answer with YES or NO\n"
                    user_states[sender_id]["onboardingStep"] = 8

        else:
            
            if ";" in func:
                splited_func = func.split(";")
                preferinte_messenger["Produs_Pentru_Comanda"] = splited_func
            elif "\n" in func:
                splited_func = func.split("\n")
                preferinte_messenger["Produs_Pentru_Comanda"] = splited_func
            else:
                splited_func = [func]
                # if language_saved == "RO":
                #     splited_func = ["Pachet : Business Smart" , "Site Complex Multilingv (>5 pagini)" , "Magazin Online (E-commerce)"]
                # elif language_saved == "RU":
                #     splited_func = ["Пакет: Business Smart" , "Сложный многоязычный сайт (более 5 страниц)" , "Магазин Онлайн (Электронная коммерция)" ]
                # elif language_saved == "EN":
                #     splited_func = ["Business Smart" , "Site Complex Multilingual (>5 pages)" , "Online Store (E-commerce)" ]
                preferinte_messenger["Produs_Pentru_Comanda"] = splited_func

            mesaj = ""
            for i in splited_func:
                detalii = extract_info(i, language_saved)
                
                if detalii:
                    descriere = detalii.get("descriere", "N/A")
                    beneficii = detalii.get("beneficii", "N/A")
                    pret_md = detalii.get("pret_md", "N/A")
                    pret_ue = detalii.get("pret_ue", "N/A")
                    pret_reducere = detalii.get("reducere", "N/A")

                    if language_saved == "RO" or language_saved == "RU":
                        preferinte_messenger["country"] = "MD"
                    else:
                        preferinte_messenger["country"] = "UE"

                    if language_saved == "RO":
                        if preferinte_messenger.get("country", "") == "MD":
                            mesaj += (
                                f"✅ Iată toate detaliile despre {i} 🧩\n\n"
                                f"📌 Descriere:\n{descriere}\n\n"
                                f"🎯 Beneficii:\n{beneficii}\n\n"
                                f"💸 📢 Ține-te bine! Am vești bune pentru tine!\n"
                                f"Acest produs avea prețul de {pret_md} MDL, dar acum este REDUS și îl poți lua cu doar {pret_reducere} MDL! 🤑\n"
                                f"💥 Economisești {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                                f"🎯 Preț valabil doar pentru o perioadă limitată!\n\n"
                                # "------------------------------------------------------------\n"
                            )
                        else:
                            mesaj += (
                                f"✅ Iată toate detaliile despre {i} 🧩\n\n"
                                f"📌 Descriere:\n{descriere}\n\n"
                                f"🎯 Beneficii:\n{beneficii}\n\n"
                                f"🇪🇺 Preț: {pret_ue} MDL\n\n"
                                # "------------------------------------------------------------\n"
                            )

                    elif language_saved == "RU":
                        if preferinte_messenger.get("country", "") == "MD":
                            mesaj += (
                                f"✅ Вот вся информация о {i} 🧩\n\n"
                                f"📌 Описание:\n{descriere}\n\n"
                                f"🎯 Преимущества:\n{beneficii}\n\n"
                                f"💸 📢 У нас отличные новости для вас!\n"
                                f"Этот продукт раньше стоил {pret_md} MDL, но сейчас он со СКИДКОЙ и доступен всего за {pret_reducere} MDL! 🤑\n"
                                f"💥 Вы экономите {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                                f"🎯 Цена действует только в течение ограниченного времени!\n\n"
                                # "------------------------------------------------------------\n"
                            )
                        else:
                            mesaj += (
                                f"✅ Вот вся информация о {i} 🧩\n\n"
                                f"📌 Описание:\n{descriere}\n\n"
                                f"🎯 Преимущества:\n{beneficii}\n\n"
                                f"🇪🇺 Цена: {pret_ue} MDL\n\n"
                                # "------------------------------------------------------------\n"
                            )

                    elif language_saved == "EN":
                        if preferinte_messenger.get("country", "") == "MD":

                            mesaj += (
                                f"✅ Here are all the details about {i} 🧩\n\n"
                                f"📌 Description:\n{descriere}\n\n"
                                f"🎯 Benefits:\n{beneficii}\n\n"
                                f"💸 📢 Great news for you!\n"
                                f"This product used to cost {pret_md} MDL, but now it is AVAILABLE WITH A DISCOUNT for only {pret_reducere} MDL! 🤑\n"
                                f"💥 You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                                f"🎯 The price is valid only for a limited time!\n\n"
                                # "------------------------------------------------------------\n"
                            )
                        else:
                            mesaj += (
                                f"✅ Here are all the details about {i} 🧩\n\n"
                                f"📌 Description:\n{descriere}\n\n"
                                f"🎯 Benefits:\n{beneficii}\n\n"
                                f"🇪🇺 Price: {pret_ue} MDL\n\n"
                                # "------------------------------------------------------------\n"
                            )
            
            if language_saved == "RO":
                if buget == "NU":
                    mesaj += "❗️ Nu sunt servicii potrivite pentru bugetul ales, dar am găsit după funcționalitățile alese\n"
                    # mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"

                

                mesaj += "\n💬 Dorești să faci o comandă? Răspunde cu DA sau NU\n"
                user_states[sender_id]["onboardingStep"] = 8
            elif language_saved == "RU":
                if buget == "NU":
                    mesaj += "❗️ Вот услуги, которые подходят по вашему бюджету и выбранным функциям\n"
                    # mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"
                

                mesaj += "\n💬 Хотите сделать заказ? Ответьте ДА или НЕТ\n"
                user_states[sender_id]["onboardingStep"] = 8
            elif language_saved == "EN":
                if buget == "NU":
                    mesaj += "❗️ These are the services that match your budget and selected features\n"
                    # mesaj += "<hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0;'><br>"
                
                mesaj += "\n💬 Do you want to make an order? Answer with YES or NO\n"
                user_states[sender_id]["onboardingStep"] = 8


    

    # return jsonify({"message": mesaj})
    send_message(mesaj, sender_id)
    return

def comanda_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text
    resp = check_response_comanda(message_text, language_saved)
    print("resp = ", resp)

    if resp == "DA":
        if preferinte_messenger.get("Produs_Pentru_Comanda", "") != "":
            produse = preferinte_messenger.get("Produs_Pentru_Comanda", "")
            if language_saved == "RO":
                mesaj = "🛍️ Alegeți unul dintre următoarele produse pentru a plasa o comandă: \n\n"
                for idx, produs in enumerate(produse, 1):
                    print("produs = " , idx)
                    mesaj += f"\n{produs}"
            elif language_saved == "RU":
                mesaj = "🛍️ Выберите один из следующих продуктов для размещения заказа: \n\n"
                for idx, produs in enumerate(produse, 1):
                    mesaj += f"\n {produs}"
            elif language_saved == "EN":
                mesaj = "🛍️ Choose one of the following products to place an order: \n\n"
                for idx, produs in enumerate(produse, 1):
                    mesaj += f"\n {produs}"
            # return jsonify({"message": mesaj})
            user_states[sender_id]["onboardingStep"] = 21
            send_message(mesaj, sender_id)
            return

        else:
            if language_saved == "RO":
                mesaj = (
                    "🎉 Mǎ bucur că vrei să plasezi o comandă!\n\n"
                    "📋 Hai să parcurgem împreună câțiva pași simpli pentru a înregistra comanda cu succes. 🚀\n\n"
                )
            elif language_saved == "RU":
                mesaj = (
                    "🎉 Здорово, что вы хотите оформить заказ!\n\n"
                    "📋 Давайте вместе пройдём несколько простых шагов, чтобы успешно зарегистрировать заказ. 🚀\n\n"
                )
            elif language_saved == "EN":
                mesaj = (
                    "🎉 I'm glad you want to place an order!\n\n"
                    "📋 Let's go through a few simple steps together to successfully place the order. 🚀\n\n"
                )

            if language_saved == "RO":
                mesaj1 = build_service_prompt_2_messenger(categorii_unice, language_saved)
            elif language_saved == "RU":
                mesaj1 = build_service_prompt_2_messenger(categorii_unice_ru, language_saved)
            elif language_saved == "EN":
                mesaj1 = build_service_prompt_2_messenger(categorii_unice_en, language_saved)
            mesaj = mesaj + mesaj1

            # rezultat = function_check_product(interests , categorii_unice, "RO")
            # print("rezultat = ", rezultat)
                
        # return jsonify({"message": mesaj})
        send_message(mesaj, sender_id)
        return
    elif resp == "NU":
        if language_saved == "RO":
            mesaj = (
                "🙏 Îți mulțumim pentru răspuns!\n\n"
                "🔄 Dacă vrei detalii despre un alt serviciu, să faci o comandă "
                "sau să alegem un serviciu în funcție de preferințele tale, scrie-mi te rog! 😊"
            )
        elif language_saved == "RU":
            mesaj = (
                "🙏 Спасибо за ответ!\n\n"
                "🔄 Если хотите узнать подробнее о другом сервисе, сделать заказ "
                "или выбрать услугу по вашим предпочтениям, напишите мне, пожалуйста! 😊"
            )
        elif language_saved == "EN":
            mesaj = (
                "🙏 Thank you for your response!\n\n"
                "🔄 If you want to know more about another service, make a purchase, "
                "or choose a service based on your preferences, please write to me! 😊"
            )
        # return jsonify({"message": mesaj})
        user_states[sender_id]["onboardingStep"] = 1
        send_message(mesaj, sender_id)
        return
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris : '{message_text}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n💬 Nu mi-e clar dacă vrei să faci o comandă. Dacă da, te rog răspunde cu DA, iar dacă nu, scrie NU. 😊"

        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал: '{message_text}'.\n\n"
                "Никогда не начинай с «Привет» или вводных фраз, ведь мы уже общаемся и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на сказанное пользователем.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не больше 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n💬 Мне не совсем понятно, хотите ли вы сделать заказ. Если да, пожалуйста, ответьте ДА, если нет — напишите НЕТ. 😊"

        elif language_saved == "EN":
            prompt = (
                f"The user wrote: '{message_text}'.\n\n"
                "Never start with 'Hello' or any introductory phrases since we're already in a conversation and know each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2-3 sentences.\n"
                "Do not use quotation marks or explain what you're doing — just write the final message."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n💬 I'm not sure if you want to place an order. If yes, please reply with YES, otherwise reply with NO. 😊"
        
        # return jsonify({"message": mesaj})
        user_states[sender_id]["onboardingStep"] = 8
        send_message(mesaj, sender_id)
        return

def check_name_surname_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text
    if language_saved == "RO":
        check_sur = check_surname_command_ro(message_text)
    elif language_saved == "RU":
        check_sur = check_surname_command_ru(message_text)
    elif language_saved == "EN":
        check_sur = check_surname_command_en(message_text)

    if check_sur == "DA":
        nume_prenume_corect = extrage_nume_din_text(message_text)
        preferinte_messenger["Nume_Prenume"] = nume_prenume_corect
        print("nume_prenume_corect = ", nume_prenume_corect)
        preferinte_messenger["Nume_Prenume"] = nume_prenume_corect
        if language_saved == "RO":
            reply = (
                "😊 Mulțumim! Ai un nume frumos! 💬\n\n"
                "📞 Te rugăm să ne lași un număr de telefon pentru a putea înregistra comanda.\n\n"
            )
            user_states[sender_id]["onboardingStep"] = 11
            if user_states[sender_id]["language"] == "RO" or user_states[sender_id]["language"] == "RU":
                preferinte_messenger["country"] = "MD"
            else:
                preferinte_messenger["country"] = "UE"

            if preferinte_messenger.get("country") == "MD":
                reply += "Te rugăm să te asiguri că numărul începe cu 0 sau +373. ✅"
            else:
                reply += "Te rugăm să introduci un număr de telefon valid, cu maximum 15 cifre, inclusiv prefixul internațional (ex: +49 pentru Germania). ✅"
        elif language_saved == "RU":
            reply = (
                "😊 Спасибо! У тебя красивое имя! 💬\n\n"
                "📞 Пожалуйста, оставь нам номер телефона для регистрации заказа\n\n"
            )
            user_states[sender_id]["onboardingStep"] = 11
            if user_states[sender_id]["language"] == "RO" or user_states[sender_id]["language"] == "RU":
                preferinte_messenger["country"] = "MD"
            else:
                preferinte_messenger["country"] = "UE"

            if preferinte_messenger.get("country") == "MD":
                reply += "Пожалуйста, убедитесь, что номер начинается с 0 или +373. ✅"
            else:
                reply += "Пожалуйста, введите действительный номер телефона, максимум 15 цифр, включая международный код (например, +49 для Германии). ✅"
        elif language_saved == "EN":
            reply = (
                "😊 Thank you! You have a nice name! 💬\n\n"
                "📞 Please leave us a phone number to register the order\n\n"
            )
            user_states[sender_id]["onboardingStep"] = 11
            if user_states[sender_id]["language"] == "RO" or user_states[sender_id]["language"] == "RU":
                preferinte_messenger["country"] = "MD"
            else:
                preferinte_messenger["country"] = "UE"

            if preferinte_messenger.get("country") == "MD":
                reply += "Please make sure the number starts with 0 or +373. ✅"
            else:
                reply += "Please enter a valid phone number, with a maximum of 15 digits, including the international prefix (e.g., +49 for Germany). ✅"
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
            reply = "📞 Introdu, te rog, doar numele si prenumele – este foarte important pentru a înregistra comanda. Mulțumim ! 🙏😊"
        elif language_saved == "RU":
            reply = "📞 Пожалуйста, введите только имя и фамилию – это очень важно для регистрации заказа. Спасибо! 🙏😊"
        elif language_saved == "EN":
            reply = (
                "📞 Please, enter only name and surname – it is very important for order registration. Thank you! 🙏😊"
            )
        user_states[sender_id]["onboardingStep"] = 10
    
    send_message(reply, sender_id)
    return


def numar_de_telefon_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text
    valid = check_numar(message)

    print("valid = " , valid)
    if valid == "NU":
        if language_saved == "RO":
            prompt = (
                "Nu te saluta pentru ca deja avem o discutie.\n"
                "Acționează ca un asistent prietenos și politicos.\n"
                "Răspunde natural și cald la mesajul clientului.\n"
                f"Mesaj client: \"{message_text}\"\n\n"
                "Răspuns:"
            )

            messages = [{"role": "system", "content": prompt}]
            ai_reply = ask_with_ai(messages, max_tokens=150)
            ai_reply += "\n\n 🙏 Te rog să introduci un număr de telefon valid pentru a putea continua. 📞"
        elif language_saved == "RU":
            prompt = (
                "Не начинай с приветствия, так как разговор уже идет.\n"
                "Веди себя как дружелюбный и вежливый помощник.\n"
                "Ответь тепло и естественно на сообщение клиента.\n"
                f"Сообщение клиента: \"{message_text}\"\n\n"
                "Ответ:"
            )

            messages = [{"role": "system", "content": prompt}]
            ai_reply = ask_with_ai(messages, max_tokens=150)
            ai_reply += "\n'n 🙏 Пожалуйста, укажи корректный номер телефона, чтобы мы могли продолжить. 📞"
        elif language_saved == "EN":
            prompt = (
                "Don't start with greetings, as we're already in an ongoing conversation.\n"
                "Act like a friendly and polite assistant.\n"
                "Reply warmly and naturally to the customer's message.\n"
                f"Customer message: \"{message_text}\"\n\n"
                "Reply:"
            )

            messages = [{"role": "system", "content": prompt}]
            ai_reply = ask_with_ai(messages, max_tokens=150)
            ai_reply += "\n\n 🙏 Please enter a valid phone number so we can proceed. 📞"
            
        # return jsonify({"message": ai_reply})
        send_message(ai_reply, sender_id)
        return

    print(message)
    if language_saved == "RO" or language_saved == "RU":
        preferinte_messenger["country"] = "MD"
    else:
        preferinte_messenger["country"] = "UE"
    if preferinte_messenger.get("country") == "MD":
        nr, status = extrage_si_valideaza_numar(message_text)
    else:
        nr, status = extrage_si_valideaza_numar_en(message_text)

    preferinte_messenger["Numar_Telefon"] = nr
    print(f"valid = {status}")


    if status != "VALID":
        if language_saved == "RO":
            if preferinte_messenger.get("country") == "MD":
                reply = (
                    "⚠️ Hmm, numărul introdus nu pare a fi valid.\n"
                    "Te rog să scrii un număr de telefon care începe cu 0 sau +373. 📞"
                )
            else:
                reply = (
                    "⚠️ Hmm, numărul introdus nu pare a fi valid.\n"
                    "Te rog să scrii un număr de telefon valid, cu maximum 15 cifre, inclusiv prefixul (ex: +49 pentru Germania). 📞"
                )

        elif language_saved == "RU":
            if preferinte_messenger.get("country") == "MD":
                reply = (
                    "⚠️ Хмм, введенный номер телефона не кажется действительным.\n"
                    "Пожалуйста, напишите номер телефона, начинающийся с 0 или +373. 📞"
                )
            else:
                reply = (
                    "⚠️ Хмм, введенный номер телефона не кажется действительным.\n"
                    "Пожалуйста, введите корректный номер телефона, максимум 15 цифр, включая международный код (например, +49 для Германии). 📞"
                )

        elif language_saved == "EN":
            if preferinte_messenger.get("country") == "MD":
                reply = (
                    "⚠️ Hmm, the number you entered doesn't seem to be valid.\n"
                    "Please write a phone number that starts with 0 or +373. 📞"
                )
            else:
                reply = (
                    "⚠️ Hmm, the number you entered doesn't seem to be valid.\n"
                    "Please enter a valid phone number, with a maximum of 15 digits, including the country code (e.g., +49 for Germany). 📞"
                )


    else:
        if language_saved == "RO":
            reply = (
                "✅ Numărul tău a fost salvat cu succes!\n\n"
                "📧 Acum te rog introdu o adresă de email validă pentru a putea trimite confirmarea comenzii și detalii suplimentare."
            )
        elif language_saved == "RU":
            reply = (
                "✅ Номер телефона успешно сохранен!\n\n"
                "📧 Теперь пожалуйста, введите действительный адрес электронной почты для отправки подтверждения заказа и дополнительных деталей."
            )
        elif language_saved == "EN":
            reply = (
                "✅ Your phone number has been successfully saved!\n\n"
                "📧 Now please enter a valid email address so we can send the order confirmation and additional details."
            )
        user_states[sender_id]["onboardingStep"] = 14


    # return jsonify({"message": reply})
    send_message(reply, sender_id)
    return


def afiseaza_produs_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text

    if language_saved == "RO":
        rezultat = function_check_product(message_text , categorii_unice, "RO")
    elif language_saved == "RU":
        rezultat = function_check_product(message_text , categorii_unice_ru, "RU")
    elif language_saved == "EN":
        rezultat = function_check_product(message_text , categorii_unice_en, "EN")

    preferinte_messenger["Serviciul_Ales"] = rezultat[0]['produs']
    print("rezultat = ", rezultat)

    if rezultat == "NU":
        lungime_rezultat = 0
    else:
        lungime_rezultat = len(rezultat)

    if lungime_rezultat == 1:
        produs = rezultat[0]['produs']
        print("rezultatul =", produs)
        detalii = extract_info(produs, language_saved)
        preferinte_messenger["Produs_Pentru_Comanda"] = produs
        preferinte_messenger["Serviciul_Ales"] = produs

        if detalii:
            descriere = detalii.get("descriere", "N/A")
            beneficii = detalii.get("beneficii", "N/A")
            pret_md = detalii.get("pret_md", "N/A")
            pret_ue = detalii.get("pret_ue", "N/A")
            preferinte_messenger["Pret_MD"] = pret_md
            preferinte_messenger["Pret_UE"] = pret_ue

            
            pret_reducere = detalii.get("reducere", "N/A")
            preferinte_messenger["reducere"] = pret_reducere
            if language_saved == "RO" or language_saved == "RU":
                preferinte_messenger["country"] = "MD"
            else:
                preferinte_messenger["country"] = "UE"

            if language_saved == "RO":
                if preferinte_messenger.get("country") == "MD":
                    mesaj = (
                        f"✅ Iată toate detaliile despre {produs} 🧩\n\n"
                        f"📌 Descriere:\n{descriere}\n\n"
                        f"🎯 Beneficii:\n{beneficii}\n\n"
                        f"💸 📢 Ține-te bine! Am vești bune pentru tine!\n"
                        f"Acest produs avea prețul de {pret_md} MDL, dar acum este REDUS și îl poți lua cu doar {pret_reducere} MDL! 🤑\n"
                        f"💥 Economisești {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                        f"🎯 Preț valabil doar pentru o perioadă limitată!\n\n"
                        # f"🇪🇺 Preț pentru Uniunea Europeană: {pret_ue} MDL\n\n"
                        "✅ Dacă dorești acest produs, confirmă cu DA\n"
                        "❌ Dacă vrei să alegi altul, răspunde cu NU"
                    )
                else:
                    mesaj = (
                        f"✅ Iată toate detaliile despre {produs} 🧩\n\n"
                        f"📌 Descriere:\n{descriere}\n\n"
                        f"🎯 Beneficii:\n{beneficii}\n\n"
                        f"🇪🇺 Preț: {pret_ue} MDL\n\n"
                        "✅ Dacă dorești acest produs, confirmă cu DA\n"
                        "❌ Dacă vrei să alegi altul, răspunde cu NU"
                    )
                user_states[sender_id]["onboardingStep"] = 13
                

            elif language_saved == "RU":
                if preferinte_messenger.get("country") == "MD":
                    mesaj = (
                        f"✅ Вот все детали о {produs} 🧩\n\n"
                        f"📌 Описание:\n{descriere}\n\n"
                        f"🎯 Преимущества:\n{beneficii}\n\n"
                        f"💸 📢 У нас отличные новости для вас!\n"
                        f"Этот продукт стоил {pret_md} MDL, но теперь со СКИДКОЙ его можно получить всего за {pret_reducere} MDL! 🤑\n"
                        f"💥 Вы экономите {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                        f"🎯 Цена действует только в течение ограниченного времени!\n\n"
                        # f"🇪🇺 Цена для Европейского Союза: {pret_ue} MDL\n\n"
                        "✅ Если хотите этот продукт, подтвердите с ДА\n"
                        "❌ Если хотите выбрать другой, ответьте с НЕТ"
                    )
                else:
                    mesaj = (
                        f"✅ Вот все детали о {produs} 🧩\n\n"
                        f"📌 Описание:\n{descriere}\n\n"
                        f"🎯 Преимущества:\n{beneficii}\n\n"
                        f"🇪🇺 Цена: {pret_ue} MDL\n\n"
                        "✅ Если хотите этот продукт, подтвердите с ДА\n"
                        "❌ Если хотите выбрать другой, ответьте с НЕТ"
                    )
                user_states[sender_id]["onboardingStep"] = 13

            elif language_saved == "EN":
                if preferinte_messenger.get("country") == "MD":
                    mesaj = (
                        f"✅ Here are all the details about {produs} 🧩\n\n"
                        f"📌 Description:\n{descriere}\n\n"
                        f"🎯 Benefits:\n{beneficii}\n\n"
                        f"💸 📢 Hold on! I have great news for you!\n"
                        f"This product used to cost {pret_md} MDL, but now it’s DISCOUNTED and you can get it for just {pret_reducere} MDL! 🤑\n"
                        f"💥 You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                        f"🎯 Price valid for a limited time only!\n\n"
                        # f"🇪🇺 Price for the European Union: {pret_ue} MDL\n\n"
                        "✅ If you want this product, confirm with YES\n"
                        "❌ If you want to choose another, reply with NO"
                    )
                else:
                    mesaj = (
                        f"✅ Here are all the details about {produs} 🧩\n\n"
                        f"📌 Description:\n{descriere}\n\n"
                        f"🎯 Benefits:\n{beneficii}\n\n"
                        f"🇪🇺 Price: {pret_ue} MDL\n\n"
                        "✅ If you want this product, confirm with YES\n"
                        "❌ If you want to choose another, reply with NO"
                    )
                user_states[sender_id]["onboardingStep"] = 13

            print("mesaj = ", mesaj)
            # return jsonify({"message": mesaj})
            send_message(mesaj, sender_id)
            return

    elif lungime_rezultat > 1:
        
        reply = genereaza_prompt_produse_messenger(rezultat, "OK", language_saved)
        # return jsonify({"message": reply})
        send_message(reply, sender_id)
        return
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message_text}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj +="\n\n"
            reply = build_service_prompt_2_messenger(categorii_unice, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь указал категорию: '{message_text}'.\n\n"
                "Никогда не начинай с приветствий или вводных фраз, так как мы уже ведём разговор и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n"
            reply = build_service_prompt_2_messenger(categorii_unice_ru, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user specified the category: '{message_text}'.\n\n"
                "Never start with greetings or introductory phrases, since we are already having a conversation and are familiar with each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user wrote.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2-3 sentences.\n"
                "Do not use quotation marks and do not explain what you are doing — just write the final message."
            )
            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n"
            reply = build_service_prompt_2_messenger(categorii_unice_en, language_saved)
            mesaj = mesaj + reply

        # return jsonify({"message": mesaj})
        send_message(mesaj, sender_id)
        return

def confirma_produs_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text
    resp = check_response_comanda(message_text, language_saved)
    if resp == "DA":
        if language_saved == "RO":
            mesaj = (
                "✅ Serviciul a fost salvat cu succes!\n\n"
                "📝 Pentru a continua comanda cât mai rapid, te rog scrie numele și prenumele "
            )
        elif language_saved == "RU":
            mesaj = (
                "✅ Заказ успешно сохранен!\n\n"
                "📝 Для продолжения заказа, пожалуйста, напишите имя и фамилию"
            )
        elif language_saved == "EN":
            mesaj = (
                "✅ The service has been successfully saved!\n\n"
                "📝 For the fastest order completion, please write name and surname"
            )
        user_states[sender_id]["onboardingStep"] = 10
        # return jsonify({"message": mesaj})
        send_message(mesaj, sender_id)
        return
    elif resp == "NU":
        if language_saved == "RO":
            mesaj = build_service_prompt_2_messenger(categorii_unice, language_saved)
        elif language_saved == "RU":
            mesaj = build_service_prompt_2_messenger(categorii_unice_ru, language_saved)
        elif language_saved == "EN":
            mesaj = build_service_prompt_2_messenger(categorii_unice_en, language_saved)
        # return jsonify({"message": mesaj})
        user_states[sender_id]["onboardingStep"] = 12
        send_message(mesaj, sender_id)
        return
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message_text}'.\n\n"
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
                "\n\n❓ Te rog spune-mi clar dacă alegi acest produs sau vrei să alegem altul.\n"
                "Răspunde cu DA dacă dorești acest produs, sau NU dacă vrei să căutăm altceva. 😊"
            )
        elif language_saved == "RU":
            prompt = (
                f"Пользователь указал категорию: '{message_text}'.\n\n"
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
                "\n\n❓ Пожалуйста, скажи ясно, выбираешь ли ты этот продукт или хочешь выбрать другой.\n"
                "Ответь ДА, если хочешь этот продукт, или НЕТ, если хочешь поискать что-то другое. 😊"
            )
        elif language_saved == "EN":
            prompt = (
                f"The user specified the category: '{message_text}'.\n\n"
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
                "\n\n❓ Please tell me clearly if you want this product or want to choose another.\n"
                "Reply with YES if you want this product, or NO if you want to choose another. 😊"
            )

    # return jsonify({"message": mesaj})
    send_message(mesaj, sender_id)
    return


def email_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text
    potential_emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', message_text)
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
        email_list = ", ".join(f"{email}" for email in valid_emails)
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

        nume_prenume = preferinte_messenger.get("Nume_Prenume", "").strip()
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
        pret_md_str = str(preferinte_messenger.get("Pret_MD", "0")).replace(" ", "")
        pret_ue_str = str(preferinte_messenger.get("Pret_UE", "0")).replace(" ", "")
        reducere_str = str(preferinte_messenger.get("reducere", "0")).replace(" ", "")

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
        if preferinte_messenger.get("BUDGET", "") != "":
            mesaj_telegram = (
                "🔔 <b><u>Nouă solicitare primită!</u></b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Nume:</b> <i>{preferinte_messenger.get('Nume_Prenume', 'gol')}</i>\n"
                f"📧 <b>Email:</b> <i>{valid_emails[0] if valid_emails else 'gol'}</i>\n"
                f"📞 <b>Telefon:</b> <code>{preferinte_messenger.get('Numar_Telefon', '0')}</code>\n"
                f"🛠️ <b>Serviciu dorit:</b> {preferinte_messenger.get('Serviciul_Ales', 'nimic')}\n"
                f"🌐 <b>Limba dorita:</b> <i>{preferinte_messenger.get('Limba_Serviciului', 'romana')}</i>\n"
                f"💲 <b>Pret MD cu reducere:</b> <i>{preferinte_messenger.get('reducere', '').replace(' ', '') if preferinte_messenger.get('reducere') else '0'}</i>\n"
                f"💲 <b>Pret UE :</b> <i>{pret_ue}</i>\n"
                f"💲 <b>Buget client:</b> <i>{preferinte_messenger.get('BUDGET', '0')}</i>\n"
                f"💬 <b>Mesaj cu preferintele înregistrare din chat:</b> <i>{preferinte_messenger.get('Preferintele_Utilizatorului_Cautare', '')}</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "✅ <b>Verifică și confirmă comanda din sistem!</b>\n"
            )

            if contact_id == "NONE":
                data = {
                    "properties": {
                        "firstname": f"{prenume}",
                        "lastname": f"{nume}",
                        "buget": f"{preferinte_messenger.get('BUDGET', '')}",
                        "phone": f"{preferinte_messenger.get('Numar_Telefon', '')}",
                        "email": f"{valid_emails[0] if valid_emails else ''}",
                        "produs": f"{preferinte_messenger.get('Serviciul_Ales', '')}",
                        "limba_serviciu": f"{preferinte_messenger.get('Limba_Serviciului', '')}",
                        "pret_md": f"{int(preferinte_messenger.get('Pret_MD', '0').replace(' ', '')) if preferinte.get('Pret_MD') else 0}",
                        "pret_ue": f"{int(preferinte_messenger.get('Pret_UE', '0').replace(' ', '')) if preferinte.get('Pret_UE') else 0}",
                        "reducere": f"{preferinte_messenger.get('reducere', '').replace(' ', '') if preferinte.get('reducere') else ''}",
                        "hs_lead_status": "NEW",
                        "preferinte_inregistrare": f"{preferinte_messenger.get('Preferintele_Utilizatorului_Cautare', '')}",
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
                        "buget": f"{preferinte_messenger.get('BUDGET', '')}",
                        "phone": f"{preferinte_messenger.get('Numar_Telefon', '')}",
                        "email": f"{valid_emails[0] if valid_emails else ''}",
                        "produs": f"{preferinte_messenger.get('Serviciul_Ales', '')}",
                        "limba_serviciu": f"{preferinte_messenger.get('Limba_Serviciului', '')}",
                        "pret_md": f"{int(preferinte_messenger.get('Pret_MD', '0').replace(' ', '')) if preferinte.get('Pret_MD') else 0}",
                        "pret_ue": f"{int(preferinte_messenger.get('Pret_UE', '0').replace(' ', '')) if preferinte.get('Pret_UE') else 0}",
                        "reducere": f"{preferinte_messenger.get('reducere', '').replace(' ', '') if preferinte.get('reducere') else ''}",
                        "hs_lead_status": "NEW",
                        "preferinte_inregistrare": f"{preferinte_messenger.get('Preferintele_Utilizatorului_Cautare', '')}",
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
                f"👤 <b>Nume:</b> <i>{preferinte_messenger.get('Nume_Prenume', '')}</i>\n"
                f"📧 <b>Email:</b> <i>{valid_emails[0] if valid_emails else ''}</i>\n"
                f"📞 <b>Telefon:</b> <code>{preferinte_messenger.get('Numar_Telefon', '')}</code>\n"
                f"🛠️ <b>Serviciu dorit:</b> {preferinte_messenger.get('Serviciul_Ales', '')}\n"
                f"💲 <b>Pret MD cu reducere:</b> <i>{preferinte_messenger.get('reducere', '').replace(' ', '')}</i>\n"
                f"💲 <b>Pret UE :</b> <i>{pret_ue}</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "✅ <b>Verifică și confirmă comanda din sistem!</b>\n"
            )

            if contact_id == "NONE":
                data = {
                    "properties": {
                        "firstname": f"{prenume}",
                        "lastname": f"{nume}",
                        "phone": f"{preferinte_messenger.get('Numar_Telefon', '')}",
                        "email": f"{valid_emails[0] if valid_emails else ''}",
                        "produs": f"{preferinte_messenger.get('Serviciul_Ales', '')}",
                        "pret_md": f"{int(preferinte_messenger.get('Pret_MD', '0').replace(' ', ''))}",
                        "pret_ue": f"{int(preferinte_messenger.get('Pret_UE', '0').replace(' ', ''))}",
                        "reducere": f"{preferinte_messenger.get('reducere', '').replace(' ', '')}",
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
                        "phone": f"{preferinte_messenger.get('Numar_Telefon', '')}",
                        "email": f"{valid_emails[0] if valid_emails else ''}",
                        "produs": f"{preferinte_messenger.get('Serviciul_Ales', '')}",
                        "pret_md": f"{int(preferinte_messenger.get('Pret_MD', '0').replace(' ', ''))}",
                        "pret_ue": f"{int(preferinte_messenger.get('Pret_UE', '0').replace(' ', ''))}",
                        "reducere": f"{preferinte_messenger.get('reducere', '').replace(' ', '')}",
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
            user_states[sender_id]["onboardingStep"] = 1
            success_message = (
                "🎉 Comandă înregistrată cu succes!\n"
                "✅ Am notat toate datele importante și totul este pregătit.\n\n"
                "💬 Ce dorești să faci mai departe?\n\n"
                "👉 Plasăm o nouă comandă? 🛒\n"
                "👉 Descoperim alte servicii? 🧰\n"
                "👉 Alegem împreună un serviciu în funcție de preferințele tale? 🎯\n\n"
                "🧭 Spune-mi ce te interesează și te ghidez cu drag! 😊"
            )
            send_message(success_message, sender_id)


        elif language_saved == "RU":
            user_states[sender_id]["onboardingStep"] = 1
            success_message = (
                "🎉 Заказ успешно оформлен!\n"
                "✅ Все важные данные записаны, всё готово.\n\n"
                "💬 Что бы ты хотел сделать дальше?\n\n"
                "👉 Оформим новый заказ? 🛒\n"
                "👉 Посмотрим другие услуги? 🧰\n"
                "👉 Выберем услугу по вашим предпочтениям? 🎯\n\n"
                "🧭 Расскажи, что тебя интересует, и я с радостью помогу! 😊"
            )
            send_message(success_message, sender_id)
        elif language_saved == "EN":
            user_states[sender_id]["onboardingStep"] = 1
            success_message = (
                "🎉 Your order has been successfully placed!\n"
                "✅ All the important details are saved and everything is ready.\n\n"
                "💬 What would you like to do next?\n\n"
                "👉 Place a new order? 🛒\n"
                "👉 Explore other services? 🧰\n"
                "👉 Choose a service based on your preferences? 🎯\n\n"
                "🧭 Let me know what you're interested in and I’ll be happy to help! 😊"
            )
            send_message(success_message, sender_id)
    else:
        if language_saved == "RO":
            mesaj = (
                "😊 Te rog frumos să introduci o adresă de email validă ca să putem continua fără probleme. ✨ Mulțumesc din suflet! 💌"
            )
        elif language_saved == "RU":
            mesaj = (
                "😊 Пожалуйста, введите действительный адрес электронной почты чтобы мы могли продолжить без проблем. ✨ Спасибо от души! 💌"
            )
        elif language_saved == "EN":
            mesaj = (
                "😊 Please enter a valid email address so we can continue without any issues. ✨ Thank you from the bottom of my heart! 💌"
            )
        # return jsonify({"message": mesaj})
        send_message(mesaj, sender_id)
        return


def comanda_inceput_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text
    if language_saved == "RO":
        rezultat = function_check_product(message_text , categorii_unice, "RO")
    elif language_saved == "RU":
        rezultat = function_check_product(message_text , categorii_unice_ru, "RU")
    elif language_saved == "EN":
        rezultat = function_check_product(message_text , categorii_unice_en, "EN")

    print("rezultat = ", rezultat)
    if rezultat == "NU":
        lungime_rezultat = 0
    else:
        lungime_rezultat = len(rezultat)

    if lungime_rezultat == 1:
        produs = rezultat[0]['produs']
        print("rezultatul =", produs)
        detalii = extract_info(produs, language_saved)
        preferinte_messenger["Serviciul_Ales"] = rezultat[0]['produs']
        if detalii:
            descriere = detalii.get("descriere", "N/A")
            beneficii = detalii.get("beneficii", "N/A")
            pret_md = detalii.get("pret_md", "N/A")
            pret_ue = detalii.get("pret_ue", "N/A")

            preferinte_messenger["Pret_MD"] = pret_md
            preferinte_messenger["Pret_UE"] = pret_ue
            pret_reducere = detalii.get("reducere", "N/A")
            preferinte_messenger["reducere"] = pret_reducere

            if language_saved == "RO" or language_saved == "RU":
                preferinte_messenger["country"] = "MD"
            else:
                preferinte_messenger["country"] = "UE"

            if language_saved == "RO":
                if preferinte_messenger.get("country") == "MD":
                    mesaj = (
                        f"✅ Iată toate detaliile despre {produs} 🧩\n\n"
                        f"📌 Descriere:\n{descriere}\n\n"
                        f"🎯 Beneficii:\n{beneficii}\n\n"
                        f"💸 📢 Ține-te bine! Am vești bune pentru tine!\n"
                        f"Acest produs avea prețul de {pret_md} MDL, dar acum este REDUS și îl poți lua cu doar {pret_reducere} MDL! 🤑\n"
                        f"💥 Economisești {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                        f"🎯 Preț valabil doar pentru o perioadă limitată!\n\n"
                        "✅ Dacă dorești acest produs, confirmă cu DA\n"
                        "❌ Dacă vrei să alegi altul, răspunde cu NU"
                    )
                else:
                    mesaj = (
                        f"✅ Iată toate detaliile despre {produs} 🧩\n\n"
                        f"📌 Descriere:\n{descriere}\n\n"
                        f"🎯 Beneficii:\n{beneficii}\n\n"
                        f"🇪🇺 Preț : {pret_ue} MDL\n\n"
                        "✅ Dacă dorești acest produs, confirmă cu DA\n"
                        "❌ Dacă vrei să alegi altul, răspunde cu NU"
                    )
                user_states[sender_id]["onboardingStep"] = 13

            elif language_saved == "RU":
                if preferinte_messenger.get("country") == "MD":
                    mesaj = (
                        f"✅ Вот все детали о {produs} 🧩\n\n"
                        f"📌 Описание:\n{descriere}\n\n"
                        f"🎯 Преимущества:\n{beneficii}\n\n"
                        f"💸 📢 У нас отличные новости для вас!\n"
                        f"Этот продукт стоил {pret_md} MDL, но теперь со СКИДКОЙ его можно получить всего за {pret_reducere} MDL! 🤑\n"
                        f"💥 Вы экономите {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                        f"🎯 Цена действует только в течение ограниченного времени!\n\n"
                        # f"🇪🇺 Цена для Европейского Союза: {pret_ue} MDL\n\n"
                        "✅ Если хотите этот продукт, подтвердите с ДА\n"
                        "❌ Если хотите выбрать другой, ответьте с НЕТ"
                    )
                else:
                    mesaj = (
                        f"✅ Вот все детали о {produs} 🧩\n\n"
                        f"📌 Описание:\n{descriere}\n\n"
                        f"🎯 Преимущества:\n{beneficii}\n\n"
                        f"🇪🇺 Цена : {pret_ue} MDL\n\n"
                        "✅ Если хотите этот продукт, подтвердите с ДА\n"
                        "❌ Если хотите выбрать другой, ответьте с НЕТ"
                    )
                user_states[sender_id]["onboardingStep"] = 13
            elif language_saved == "EN":
                if preferinte_messenger.get("country") == "MD":
                    mesaj = (
                        f"✅ Here are all the details about {produs} 🧩\n\n"
                        f"📌 Description:\n{descriere}\n\n"
                        f"🎯 Benefits:\n{beneficii}\n\n"
                        f"💸 📢 Hold tight! We have great news for you!\n"
                        f"This product used to cost {pret_md} MDL, but now it’s DISCOUNTED and you can get it for just {pret_reducere} MDL! 🤑\n"
                        f"💥 You save {int(pret_md.replace(' ', '')) - int(pret_reducere.replace(' ', ''))} MDL!\n"
                        f"🎯 Price valid only for a limited time!\n\n"
                        "✅ If you want this product, please confirm with YES\n"
                        "❌ If you want to choose another one, reply with NO"
                    )
                else:
                    mesaj = (
                        f"✅ Here are all the details about {produs} 🧩\n\n"
                        f"📌 Description:\n{descriere}\n\n"
                        f"🎯 Benefits:\n{beneficii}\n\n"
                        f"🇪🇺 Price: {pret_ue} MDL\n\n"
                        "✅ If you want this product, please confirm with YES\n"
                        "❌ If you want to choose another one, reply with NO"
                    )
                user_states[sender_id]["onboardingStep"] = 13

            print("mesaj = ", mesaj)
            # return jsonify({"message": mesaj})
            send_message(mesaj, sender_id)
            return

    elif lungime_rezultat > 1:
        
        reply = genereaza_prompt_produse_messenger(rezultat, "OK", language_saved)
        # return jsonify({"message": reply})
        send_message(reply, sender_id)
        return
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message_text}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj +="\n\n"
            reply = build_service_prompt_2_messenger(categorii_unice, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь указал категорию: '{message_text}'.\n\n"
                "Никогда не начинай с приветствий или вводных фраз, так как мы уже ведём разговор и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n'n"
            reply = build_service_prompt_2_messenger(categorii_unice_ru, language_saved)
            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user specified the category: '{message_text}'.\n\n"
                "Never start with greetings or introductory phrases, since we are already having a conversation and are familiar with each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user wrote.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2-3 sentences.\n"
                "Do not use quotation marks and do not explain what you are doing — just write the final message."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n"
            reply = build_service_prompt_2_messenger(categorii_unice_en, language_saved)
            mesaj = mesaj + reply


    # return jsonify({"message": mesaj})
    send_message(mesaj, sender_id)
    return


def produs_intrebare_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    message = message_text
    check_response = check_response_comanda(message, language_saved)


    if check_response == "DA":
        if language_saved == "RO":
            mesaj = (
                "✅ Serviciul a fost salvat cu succes!\n\n"
                "📝 Pentru a continua comanda cât mai rapid, te rog scrie numele și prenumele"
            )
        elif language_saved == "RU":
            mesaj = (
                "✅ Заказ успешно сохранен!\n\n"
                "📝 Для продолжения заказа, пожалуйста, напишите имя и фамилию"
            )
        elif language_saved == "EN":
            mesaj = (
                "✅ The service has been successfully saved!\n\n"
                "📝 For the fastest order completion, please write name and surname"
            )
        user_states[sender_id]["onboardingStep"] = 10
    elif check_response == "NU":
        if language_saved == "RO":
            mesaj = build_service_prompt_2_messenger(categorii_unice, language_saved)
        elif language_saved == "RU":
            mesaj = build_service_prompt_2_messenger(categorii_unice_ru, language_saved)
        elif language_saved == "EN":
            mesaj = build_service_prompt_2_messenger(categorii_unice_en, language_saved)
        # return jsonify({"message": mesaj})
        user_states[sender_id]["onboardingStep"] = 12
        send_message(mesaj, sender_id)
        return
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message_text}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            produs = preferinte_messenger.get("Produs_Pentru_Comanda", "")

            reply = f"\n\n📦 Doriți să plasați o comandă pentru serviciul {produs}? ✨\nRăspundeți cu Da sau Nu."

            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал категорию: '{message_text}'.\n\n"
                "Никогда не приветствуй, так как мы уже ведём разговор и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Кратко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть коротким, тёплым, эмпатичным и дружелюбным.\n"
                "Не более 2-3 предложений.\n"
                "Не используй кавычки и не объясняй, что ты делаешь — пиши только итоговое сообщение."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            produs = preferinte_messenger.get("Produs_Pentru_Comanda", "")

            reply = f"\n\n📦 Хотите оформить заказ на услугу {produs}? ✨\nОтветьте Да или Нет."

            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user wrote the category: '{message_text}'.\n\n"
                "Never say 'Hello' or anything introductory — we are already in a conversation and familiar with each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user said.\n"
                "2. The message should be short, warm, empathetic, and friendly.\n"
                "No more than 2–3 sentences.\n"
                "Do not use quotation marks and do not explain what you're doing — just write the final message for the user."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            produs = preferinte_messenger.get("Produs_Pentru_Comanda", "")

            reply = f"\n\n📦 Would you like to place an order for the {produs} service? ✨\nPlease reply with Yes or No."

            mesaj = mesaj + reply

    # return jsonify({"message": mesaj})
    send_message(mesaj, sender_id)
    return


def selecteaza_produs_messenger(message_text, sender_id):
    language_saved = user_states[sender_id]["language"]
    produsele = preferinte_messenger.get("Produs_Pentru_Comanda", "")
    message = message_text
    
    if language_saved == "RO":
        rezultat = function_check_product(message_text , produsele, language_saved)
    elif language_saved == "RU":
        rezultat = function_check_product(message_text , produsele, language_saved)
    elif language_saved == "EN":
        rezultat = function_check_product(message_text , produsele, language_saved)

    # preferinte["Serviciul_Ales"] = rezultat[0]['produs']
    
    print("produsele = ", produsele)
    print("rezultat = ", rezultat)
    if rezultat == "NU":
        lungime_rezultat = 0
    else:
        lungime_rezultat = len(rezultat)

    if lungime_rezultat == 1:
        produs = rezultat[0]['produs']
        preferinte_messenger["Serviciul_Ales"] = produs
        print("rezultatul =", produs)
        detalii = extract_info(produs, language_saved)            
        pret_md = detalii.get("pret_md", "N/A")
        pret_ue = detalii.get("pret_ue", "N/A")
        pret_reducere = detalii.get("reducere", "N/A")
        preferinte_messenger["reducere"] = pret_reducere
        preferinte_messenger["Pret_MD"] = pret_md
        preferinte_messenger["Pret_UE"] = pret_ue
        preferinte_messenger["Produs_Pentru_Comanda"] = produs
        if language_saved == "RO":
            mesaj = (
                "✅ Serviciul a fost salvat cu succes!\n\n"
                "📝 Pentru a continua comanda cât mai rapid, te rog scrie numele și prenumele "
            )
        elif language_saved == "RU":
            mesaj = (
                "✅ Сервис успешно сохранен!\n\n"
                "📝 Для продолжения заказа, пожалуйста, напишите имя и фамилию "
            )
        elif language_saved == "EN":
            mesaj = (
                "✅ The service has been successfully saved!\n\n"
                "📝 For the fastest order completion, please write name and surname "
            )
        user_states[sender_id]["onboardingStep"] = 10
        # return jsonify({"message": mesaj})
        send_message(mesaj, sender_id)
        return

    elif lungime_rezultat > 1:

        reply = genereaza_prompt_produse_messenger(rezultat , "OK", language_saved)
        # return jsonify({"message": reply})
        send_message(reply, sender_id)
        return
    else:
        if language_saved == "RO":
            prompt = (
                f"Utilizatorul a scris categoria: '{message_text}'.\n\n"
                "Nu spune niciodată „Salut”, gen toate chestiile introductive, pentru că noi deja ducem o discuție și ne cunoaștem. "
                "Scrie un mesaj politicos, prietenos și natural, care:\n"
                "1. Răspunde pe scurt la ceea ce a spus utilizatorul . "
                "2. Mesajul să fie scurt, cald, empatic și prietenos. "
                "Nu mai mult de 2-3 propoziții.\n"
                "Nu folosi ghilimele și nu explica ce faci – scrie doar mesajul final pentru utilizator."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj +="\n\n"
            reply = build_service_prompt_2_messenger(produsele , language_saved)
            mesaj = mesaj + reply
        elif language_saved == "RU":
            prompt = (
                f"Пользователь написал категорию: '{message_text}'.\n\n"
                "Никогда не начинай с «Привет» или других вводных фраз — мы уже ведем диалог и знакомы. "
                "Напиши вежливое, дружелюбное и естественное сообщение, которое:\n"
                "1. Коротко отвечает на то, что написал пользователь.\n"
                "2. Сообщение должно быть тёплым, дружелюбным и эмпатичным. "
                "Не более 2–3 предложений.\n"
                "Не используй кавычки и не объясняй, что ты делаешь — просто напиши готовое сообщение для пользователя."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n"
            reply = build_service_prompt_2_messenger(produsele , language_saved)
            mesaj = mesaj + reply
        elif language_saved == "EN":
            prompt = (
                f"The user wrote the category: '{message_text}'.\n\n"
                "Never start with 'Hello' or any kind of greeting — we’re already in a conversation and know each other. "
                "Write a polite, friendly, and natural message that:\n"
                "1. Briefly responds to what the user wrote.\n"
                "2. Feels warm, empathetic, and friendly. No more than 2–3 sentences.\n"
                "Do not use quotation marks or explain what you’re doing — just write the final message for the user."
            )

            messages = [{"role": "system", "content": prompt}]
            mesaj = ask_with_ai(messages).strip()
            mesaj += "\n\n"
            reply = build_service_prompt_2_messenger(produsele, language_saved)
            mesaj = mesaj + reply
            

    # return jsonify({"message": mesaj})
    send_message(mesaj, sender_id)
    return


def handle_message(message_text,sender_id):
    if sender_id not in user_states:
        user_states[sender_id] = {
            "onboardingStep": 0,
            "language": "",
        }
    step = user_states.get(sender_id, {}).get("onboardingStep", 0)
    print("step ===" , step)

    match step:
        case 0:
            start_check(message_text, sender_id)
        case 1:
            interests_check(message_text, sender_id)
        case 2:
            welcome_products(message_text, sender_id)
        case 3:
            chat_general(message_text, sender_id)
        case 4:
            criteria_general(message_text, sender_id)
        case 5:
            budget_general(message_text, sender_id)
        case 6:
            preference_language_messenger(message_text, sender_id)
        case 7:
            functionalities_check(message_text, sender_id)
        case 8:
            comanda_messenger(message_text, sender_id)
        case 10:
            check_name_surname_messenger(message_text, sender_id)
        case 11:
            numar_de_telefon_messenger(message_text, sender_id)
        case 12:
            afiseaza_produs_messenger(message_text, sender_id)
        case 13:
            confirma_produs_messenger(message_text, sender_id)
        case 14:
            email_messenger(message_text, sender_id)
        case 15:
            comanda_inceput_messenger(message_text, sender_id)
        case 20:
            produs_intrebare_messenger(message_text, sender_id)
        case 21:
            selecteaza_produs_messenger(message_text, sender_id)
        case _:
            # opțional, dacă vrei să faci ceva când nu se potrivește niciun caz
            pass




@app.route("/privacy")
def privacy_policy():
    return render_template("privacy.html")


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Invalid verification token", 403

    elif request.method == 'POST':
        data = request.get_json()
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event['sender']['id']

                # Dacă e mesaj text normal
                message_text = messaging_event.get('message', {}).get('text')
                print(message_text)
                if message_text:
                    # reply = f"AI ZIS: {message_text}"
                    # send_message(sender_id, reply)
                    handle_message(message_text,sender_id)


                # Dacă e postback (ex: Get Started)
                postback = messaging_event.get('postback')
                if postback:
                    payload = postback.get('payload')
                    if payload == 'GET_STARTED_PAYLOAD':
                        if sender_id not in user_states:
                            user_states[sender_id] = {}
                        # send_message(sender_id, message)
                        if not user_states[sender_id].get("language_selection_sent", False):
                            user_states[sender_id]["onboardingStep"] = 0
                            send_language_selection(sender_id)
                            user_states[sender_id]["language_selection_sent"] = True

        return "EVENT_RECEIVED", 200



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port,debug=True, use_reloader=False)
    # app.run(debug=True, use_reloader=False)

