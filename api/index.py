import os, requests, hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_URL = "https://100067.connect.garena.com"
HEADERS = {"User-Agent": "GarenaMSDK/4.0.39", "Content-Type": "application/x-www-form-urlencoded"}
APP_ID = "100067"
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN", "1380dcb63ab3a077dc05bdf0b25ba4497c403a5b4eae96d7203010eafa6c83a8")

def sha256_hash(s): return hashlib.sha256(s.encode()).hexdigest()

@app.route('/api/call', methods=['POST'])
def handle_api():
    data_in = request.form
    action = data_in.get('action')
    token = data_in.get('token')
    
    try:
        if action == 'refresh':
            r = requests.post(f"{BASE_URL}/oauth/token", data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN, "app_id": APP_ID})
        elif action == 'info':
            r = requests.get(f"{BASE_URL}/game/account_security/bind:get_bind_info", params={"app_id": APP_ID, "access_token": token})
        elif action == 'user_info':
            r = requests.get("https://prod-api.reward.ff.garena.com/redemption/api/auth/inspect_token/", headers={"access-token": token})
        elif action == 'platforms':
            r = requests.get(f"{BASE_URL}/bind/app/platform/info/get", params={"access_token": token})
        elif action == 'send_otp':
            r = requests.post(f"{BASE_URL}/game/account_security/bind:send_otp", data={"app_id": APP_ID, "access_token": token, "email": data_in.get('email'), "locale": "en_PK", "region": "PK"})
        elif action == 'verify_otp':
            r = requests.post(f"{BASE_URL}/game/account_security/bind:verify_otp", data={"app_id": APP_ID, "access_token": token, "email": data_in.get('email'), "otp": data_in.get('otp')})
        elif action == 'verify_id_pass':
            r = requests.post(f"{BASE_URL}/game/account_security/bind:verify_identity", data={"app_id": APP_ID, "access_token": token, "secondary_password": sha256_hash(data_in.get('password'))})
        elif action == 'bind_new':
            r = requests.post(f"{BASE_URL}/game/account_security/bind:create_bind_request", data={"app_id": APP_ID, "access_token": token, "email": data_in.get('email'), "verifier_token": data_in.get('verifier')})
        elif action == 'rebind':
            r = requests.post(f"{BASE_URL}/game/account_security/bind:create_rebind_request", data={"app_id": APP_ID, "access_token": token, "identity_token": data_in.get('identity'), "verifier_token": data_in.get('verifier'), "email": data_in.get('email')})
        elif action == 'unbind':
            r = requests.post(f"{BASE_URL}/game/account_security/bind:unbind_identity", data={"app_id": APP_ID, "access_token": token, "identity_token": data_in.get('identity')})
        elif action == 'cancel':
            r = requests.post(f"{BASE_URL}/game/account_security/bind:cancel_request", data={"app_id": APP_ID, "access_token": token})
        elif action == 'exchange':
            # Chức năng đổi eat_token từ index.js
            eat = data_in.get('eat_token')
            ex_req = requests.get(f"https://api-otrss.garena.com/support/callback/?access_token={eat}", allow_redirects=True)
            new_token = ex_req.url.split('access_token=')[1].split('&')[0]
            return jsonify({"result": 0, "access_token": new_token})
        else: return jsonify({"result": -1, "message": "Thao tác không hợp lệ"})
        
        return jsonify(r.json())
    except Exception as e: return jsonify({"result": -1, "message": str(e)})

# Cần thiết cho Vercel
def handler(request): return app(request)
  2
