import os
from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# Конфигурация с использованием переданных значений
INSTANCE_ID = '1103960944'
API_TOKEN = '557a5f7c1173434086486f390c6ae2290b77f31ba6ca4656aa'

MESSAGE = """🍣 ПОДАРКИ ЗА ОТЗЫВЫ ✍️

Здравствуйте, мы очень сильно благодарим вас за то, что выбираете "Мама Зина"! Хотим предложить вам вкуснейший ролл в подарок при следующем заказе. Для этого нужно оставить отзывы на трёх площадках:

1. 2ГИС

Mamazina
https://2gis.ru/rostov/geo/70000001062267615

2. ЯНДЕКС

https://yandex.ru/profile/26936047750

3. ГРУППА ВКОНТАКТЕ

https://vk.com/topic-207395908_48873636

Отзыв желательно писать с фото, но можно и без 😇
После написания присылайте нам подтверждение в виде скриншота и получайте от нас подарок 🎁

P.S. Так же информируем, что у нас появились "Премиум-роллы" от шеф-повара. Ждём с нетерпением обратной связи! 🥰

С Уважением, Мама Зина!
"""

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        app.logger.info("Request headers: %s", request.headers)
        app.logger.info("Request data: %s", request.data)

        phone_number = None

        if request.content_type == 'application/json':
            data = request.get_json()
            app.logger.info("Received JSON data: %s", data)

            if isinstance(data, dict) and data.get('test') == 'test':
                app.logger.info("Received test request from Tilda")
                return jsonify({'status': 'success', 'message': 'Test request received successfully'}), 200

            if isinstance(data, list):
                phone_numbers = [item.get('Phone') for item in data if isinstance(item, dict) and 'Phone' in item]
            elif isinstance(data, dict):
                phone_numbers = [data.get('Phone')]
            else:
                phone_numbers = []

            app.logger.info("Extracted phone numbers from JSON: %s", phone_numbers)
            if not phone_numbers or not phone_numbers[0]:
                app.logger.error("Phone number not found in the JSON data")
                return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400

            phone_number = phone_numbers[0]
        elif request.content_type == 'application/x-www-form-urlencoded':
            phone_number = request.form.get('Phone')
            app.logger.info("Received form data: %s", request.form)
            if request.form.get('test') == 'test':
                app.logger.info("Received test request from Tilda")
                return jsonify({'status': 'success', 'message': 'Test request received successfully'}), 200

            if not phone_number:
                app.logger.error("Phone number not found in the form data")
                return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400
        elif request.content_type.startswith('multipart/form-data'):
            phone_number = request.form.get('Phone')
            app.logger.info("Received multipart/form-data: %s", request.form)
            if not phone_number:
                app.logger.error("Phone number not found in the multipart form data")
                return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400
        elif request.content_type == 'text/plain':
            data = request.data.decode('utf-8')
            app.logger.info("Received text data: %s", data)
            phone_number_match = re.search(r'Phone:\s*(\+?\d{1,3}[- ]?)?\d{10}', data)
            if phone_number_match:
                phone_number = phone_number_match.group().split(":")[1].strip()
            else:
                app.logger.error("Phone number not found in the text data")
                return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400
        elif request.content_type == 'application/xml':
            data = request.data.decode('utf-8')
            app.logger.info("Received XML data: %s", data)
            phone_number_match = re.search(r'<Phone>(\+?\d{1,3}[- ]?)?\d{10}</Phone>', data)
            if phone_number_match:
                phone_number = phone_number_match.group(0).replace("<Phone>", "").replace("</Phone>", "")
            else:
                app.logger.error("Phone number not found in the XML data")
                return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400
        else:
            app.logger.error("Unsupported Content-Type: %s", request.content_type)
            return jsonify({'status': 'error', 'message': 'Unsupported Content-Type'}), 415

        app.logger.info("Extracted phone number: %s", phone_number)

        cleaned_number = re.sub(r'\D', '', phone_number)
        app.logger.info("Cleaned phone number: %s", cleaned_number)

        if not cleaned_number.startswith('7') or len(cleaned_number) != 11:
            app.logger.error("Invalid phone number format: %s", cleaned_number)
            return jsonify({'status': 'error', 'message': 'Invalid phone number format'}), 400

        send_whatsapp_message(cleaned_number, MESSAGE)
        return jsonify({'status': 'success', 'message': 'Message sent successfully'}), 200

    except Exception as e:
        app.logger.error("An error occurred: %s", e, exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

def send_whatsapp_message(phone_number, message):
    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/sendMessage/{API_TOKEN}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    chat_id = f"{phone_number}@c.us"
    payload = {
        "chatId": chat_id,
        "message": message
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        app.logger.info("Message sent successfully: %s", response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error("Request failed: %s", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
