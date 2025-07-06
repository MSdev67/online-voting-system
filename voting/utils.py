# voting/utils.py
import random
from django.core.cache import cache

def send_otp(phone_number):
    """Generate and store OTP (simulated for development)"""
    otp = str(random.randint(100000, 999999))
    cache.set(f'otp_{phone_number}', otp, timeout=300)  # 5 minutes expiration
    print(f"DEBUG: OTP for {phone_number} is {otp}")  # Remove in production
    return otp