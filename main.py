from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        app.logger.info("Request headers: %s", request.headers)
        app.logger.info("Request form data: %s", request.form)
        app.logger.info("Request data: %s", request.data)

        # Обработка тестового запроса от Tilda
        if request.form.get('test') == 'test':
            app.logger.info("Received test request from Tilda")
            return jsonify({'status': 'success', 'message': 'Test request received successfully'}), 200

        phone_number = request.form.get('phone')
        app.logger.info("Received phone number: %s", phone_number)
        if not phone_number:
            app.logger.error("Phone number not found in the request")
            return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400
        
        cleaned_number = re.sub(r'\D', '', phone_number)
        message = "Ваше сообщение"
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
    except requests.exceptions.RequestException as e:
        app.logger.error("Request failed: %s", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
