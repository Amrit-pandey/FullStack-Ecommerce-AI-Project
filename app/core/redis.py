# Redis client setup & OTP helper functions
import redis.asyncio as redis

from app.core.config import settings

host = settings.redis_host
port = settings.redis_port

redis_client = redis.Redis(host=host, port=port, db=0, decode_responses=True)

async def set_otp(email: str, code: str) -> None:
    """Stores the OTP in Redis with a 5-minute (300s) TTL."""

    key = f"otp:{email}"

    await redis_client.set(name=key, value=code, ex=300)

async def verify_and_delete_otp(email: str, input_code: str) -> bool:
    """Verifies the OTP and deletes it immediately if valid (one-time use)."""

    key = f"otp:{email}"
    stored_code = await redis_client.get(name=key)

    if stored_code is None:
        return False

    if stored_code == input_code:
        await redis_client.delete(key)
        return True

    return False

async def check_and_set_cooldown(email: str, seconds:int = 30) -> bool:
    """
    Checks if a cooldown key exists. 
    If not, sets it for `seconds` and returns True (allowed).
    If it exists, returns False (rate limited).
    """
    email = email.lower()
    
    cooldown_key = f"otp:{email}"
    is_set = await redis_client.set(name=cooldown_key, value=1, ex=seconds, nx=True)
    return bool(is_set)
