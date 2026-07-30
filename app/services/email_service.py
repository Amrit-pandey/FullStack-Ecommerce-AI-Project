import logging
import os

import resend
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

resend.api_key = os.getenv("RESEND_API_KEY")

async def send_otp_email(to_email: str, otp_code: str) -> None:
    """Sends a 6-digit OTP code to the specified email using Resend's async client."""
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Your Verification Code</h2>
        <p>Your login OTP code is:</p>
        <h1 style="letter-spacing: 4px; color: #4F46E5;">{otp_code}</h1>
        <p>This code will expire in <strong>5 minutes</strong>.</p>
        <p>If you did not request this, please ignore this email.</p>
    </div>
    """

    params: resend.Emails.SendParams = {
        "from": "onboarding@resend.dev",
        "to": [to_email],
        "subject": f"{otp_code} is your verification code",
        "html": html_content,
    }

    try:
        await resend.Emails.send_async(params)
    except Exception as e:
        logger.error(f"Failed to send OTP email to {to_email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Please try again later.",
        )