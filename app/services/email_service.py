import logging
import os
import smtplib
from email.message import EmailMessage

import resend
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# resend.api_key = os.getenv("RESEND_API_KEY")

MAILTRAP_HOST= os.getenv("MAILTRAP_HOST")
MAILTRAP_PORT= os.getenv("MAILTRAP_PORT")
MAILTRAP_USERNAME= os.getenv("MAILTRAP_USERNAME")
MAILTRAP_PASSWORD= os.getenv("MAILTRAP_PASSWORD")
MAIL_FROM= os.getenv("MAIL_FROM")

async def send_otp_email(to_email: str, otp_code: str) -> None:
    """Sends a 6-digit OTP code to the specified email using Mailtraps's async client."""

    message = EmailMessage()

    message["Subject"] = f"{otp_code} is your verification code"
    message["From"] = MAIL_FROM
    message["To"] = to_email

    message.set_content(
        f"""
        Your OTP is: {otp_code}

        This OTP will expire in 5 minutes.
        """
    )

    with smtplib.SMTP( MAILTRAP_HOST, int(MAILTRAP_PORT) ) as smtp:
        smtp.starttls()
        smtp.login( MAILTRAP_USERNAME, MAILTRAP_PASSWORD )

        try:
           smtp.send_message(message)
        except Exception as e:
            logger.error(f"Failed to send OTP email to {to_email}: {e}")
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Please try again later.",
        )
            
    
    # html_content = f"""
    # <div style="font-family: Arial, sans-serif; padding: 20px;">
    #     <h2>Your Verification Code</h2>
    #     <p>Your login OTP code is:</p>
    #     <h1 style="letter-spacing: 4px; color: #4F46E5;">{otp_code}</h1>
    #     <p>This code will expire in <strong>5 minutes</strong>.</p>
    #     <p>If you did not request this, please ignore this email.</p>
    # </div>
    # """

    # params: resend.Emails.SendParams = {
    #     "from": "onboarding@resend.dev",
    #     "to": [to_email],
    #     "subject": f"{otp_code} is your verification code",
    #     "html": html_content,
    # }

    # try:
    #     await resend.Emails.send_async(params)
    # except Exception as e:
    #     logger.error(f"Failed to send OTP email to {to_email}: {e}")
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Failed to send OTP email. Please try again later.",
    #     )