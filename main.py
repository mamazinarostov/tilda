from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

def clean_phone_number(phone_number):
    if phone_number:
        # Убираем все символы, кроме цифр
        cleaned_number = re.sub(r'\D', '', phone_number)
        return cleaned_number
    else:
        app.logger.error("Phone number is None")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        phone_number = request.form.get('phone')
        if not phone_number:
            app.logger.error("Phone number not found in the request")
            return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400

        cleaned_number = clean_phone_number(phone_number)
        if not cleaned_number:
            app.logger.error("Failed to clean phone number")
            return jsonify({'status': 'error', 'message': 'Invalid phone number format'}), 400

        message = "Ваше сообщение"
        app.logger.info("Sending message to %s", cleaned_number)
        send_whatsapp_message(cleaned_number, message)
        return jsonify({'status': 'success', 'message': 'Message sent successfully'}), 200
    except Exception as e:
        app.logger.error("An error occurred: %s", e, exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

def send_whatsapp_message(phone_number, message):
    url = "https://api.green-api.com/waInstance1103960944/sendMessage/557a5f7c1173434086486f390c6ae2290b77f31ba6ca4656aa"
    headers = {
        "Authorization": "Bearer 557a5f7c1173434086486f390c6ae2290b77f31ba6ca4656aa",
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
    except requests.exceptions.HTTPError as errh:
        app.logger.error("HTTP Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        app.logger.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        app.logger.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        app.logger.error("Something went wrong: %s", err)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
