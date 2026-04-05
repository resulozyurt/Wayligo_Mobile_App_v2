import httpx
from core.config import settings

def send_otp_email(email: str, otp_code: str):
    """
    Resend API kullanarak kullanıcıya 6 haneli doğrulama kodunu gönderir.
    """
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": "Wayligo <onboarding@resend.dev>", # Gerçek domain bağlayana kadar bu kalabilir
        "to": [email],
        "subject": "Wayligo Şifre Sıfırlama Kodu",
        "html": f"""
            <h1>Şifreni mi unuttun?</h1>
            <p>Endişelenme, Wayligo yanında! Şifreni sıfırlamak için aşağıdaki kodu kullanabilirsin:</p>
            <h2 style='color: #4F46E5; letter-spacing: 5px;'>{otp_code}</h2>
            <p>Bu kod 10 dakika geçerlidir.</p>
        """
    }
    
    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload)
        return response.status_code in (200, 201)