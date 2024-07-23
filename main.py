from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    phone_number = request.form.get('phone')
    message = "Ваше сообщение"
    send_whatsapp_message(phone_number, message)
    return 'OK', 200

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
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
