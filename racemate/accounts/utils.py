
# accounts/utils.py
import os
from azure.communication.email import EmailClient
from django.conf import settings

def send_azure_otp(target_email, otp_code):
    # Pull credentials from settings.py
    connection_string = settings.AZURE_EMAIL_CONNECTION_STRING
    sender_address = settings.AZURE_EMAIL_SENDER
    
    if not connection_string:
        print("Azure Error: Connection string not found in settings.")
        return False

    try:
        client = EmailClient.from_connection_string(connection_string)
        message = {
            "senderAddress": sender_address,
            "recipients": {"to": [{"address": target_email}]},
            "content": {
                "subject": "Your Racemate Login Code",
                "plainText": f"Your verification code is: {otp_code}",
                "html": f"""
                <html>
                    <body>
                        <h2 style="color: #2c3e50;">Racemate Verification</h2>
                        <p>Use the code below to log in:</p>
                        <h1 style="background: #f4f4f4; padding: 10px; display: inline-block;">{otp_code}</h1>
                    </body>
                </html>
                """
            }
        }
        poller = client.begin_send(message)
        poller.result() # Wait for it to send
        return True
    except Exception as e:
        print(f"Azure Email Error: {e}")
        return False