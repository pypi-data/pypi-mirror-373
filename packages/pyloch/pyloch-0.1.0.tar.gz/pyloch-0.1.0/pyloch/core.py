import requests
from user_agent import generate_user_agent as ua

def multiply(a, b):
    """دالة بسيطة لضرب رقمين"""
    return a * b


def insta_recovery(username: str):
    """
    محاكاة طلب استرجاع حساب إنستغرام (تعليمي).
    
    Args:
        username (str): اسم المستخدم أو البريد
    
    Returns:
        str: البريد أو النتيجة من السيرفر
    """
    headers = {
        "user-agent": ua(),
        "x-csrftoken": "tb9KuiockmVMmkquEDEiMkqAAplnqswt"
    }
    data = {"email_or_username": username}

    res = requests.post(
        "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/",
        headers=headers,
        data=data
    ).json()

    if res.get("status") == "ok":
        return f"Send Email : {res.get('contact_point', 'Unknown')}"
    else:
        return "An error occurred."