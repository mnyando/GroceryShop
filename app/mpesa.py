import requests
from requests.auth import HTTPBasicAuth
import datetime
import base64
import json

def format_phone_number(phone):
    """Formats phone number to 2547XXXXXXXX or 2541XXXXXXXX."""
    phone = phone.strip().replace(" ", "").replace("+", "")
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("7") or phone.startswith("1"):
        phone = "254" + phone
    return phone

def get_mpesa_token(consumer_key, consumer_secret):
    """Requests OAuth access token from Safaricom Daraja API."""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret), timeout=10)
        if response.status_code == 200:
            return response.json().get("access_token"), None
        else:
            return None, f"Token request failed with status {response.status_code}: {response.text}"
    except Exception as e:
        return None, f"Token request exception: {e}"

def trigger_stk_push(phone, amount, consumer_key, consumer_secret, shortcode, passkey, callback_url):
    """Triggers a Lipa Na M-Pesa Online STK Push transaction."""
    # Format phone
    formatted_phone = format_phone_number(phone)
    # Cast amount to integer (Daraja Sandbox usually expects integers for test amounts)
    amount_int = int(round(float(amount)))
    if amount_int < 1:
        amount_int = 1 # Minimum 1 KSh

    # Fetch token
    token, err = get_mpesa_token(consumer_key, consumer_secret)
    if err:
        return False, err

    # Prepare parameters
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password_string = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(password_string.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount_int,
        "PartyA": formatted_phone,
        "PartyB": shortcode,
        "PhoneNumber": formatted_phone,
        "CallBackURL": callback_url,
        "AccountReference": "MAMAMBOGA",
        "TransactionDesc": "Grocery Payment"
    }

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_data = response.json()
        if response.status_code == 200 and res_data.get("ResponseCode") == "0":
            return True, res_data
        else:
            msg = res_data.get("errorMessage") or res_data.get("CustomerMessage") or f"Status {response.status_code}"
            return False, msg
    except Exception as e:
        return False, f"STK push request exception: {e}"
