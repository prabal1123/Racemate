import os
from azure.communication.email import EmailClient

def send_otp_email(target_email, otp_code):
    # It's best to use environment variables for security
    connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING", "your_fallback_string_here")
    
    try:
        client = EmailClient.from_connection_string(connection_string)
        message = {
            "senderAddress": "DoNotReply@e816a3a8-f533-4231-ad0c-fa6a80537e32.azurecomm.net",
            "recipients": {"to": [{"address": target_email}]},
            "content": {
                "subject": f"Your Racemate Login Code",
                "plainText": f"Your OTP is {otp_code}",
                "html": f"<html><body><h1>Your OTP is {otp_code}</h1></body></html>"
            }
        }
        poller = client.begin_send(message)
        poller.result()
        return True
    except Exception as ex:
        print(f"Error sending email: {ex}")
        return False