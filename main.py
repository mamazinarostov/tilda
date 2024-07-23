from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

def clean_phone_number(phone_number):
    # Убираем все символы, кроме цифр
    cleaned_number = re.sub(r'\D', '', phone_number)
    return cleaned_number

@app.route('/webhook', methods=['POST'])
def webhook():
    phone_number = request.form.get('phone')
    cleaned_number = clean_phone_number(phone_number)
    message = "Ваше сообщение"
    send_whatsapp_message(cleaned_number, message)
    return jsonify({'status': 'success', 'message': 'Message sent successfully'}), 200

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
        print("Message sent successfully:", response.json())
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
