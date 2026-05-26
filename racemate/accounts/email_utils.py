# # accounts/email_utils.py
# from django.template.loader import render_to_string
# from django.conf import settings
# from azure.communication.email import EmailClient


# def send_registration_confirmation(registration, request=None):
#     """
#     Sends an HTML registration confirmation email via Azure Communication Services.
#     Called after a successful registration save.
#     """
#     if not registration.email:
#         return  # No email to send to

#     # Build absolute site URL for the CTA button in the email
#     if request:
#         site_url = request.build_absolute_uri('/').rstrip('/')
#     else:
#         site_url = ''

#     # Render the HTML email template
#     html_body = render_to_string('accounts/registration_confirmation.html', {
#         'registration': registration,
#         'site_url': site_url,
#     })

#     try:
#         client = EmailClient.from_connection_string(settings.AZURE_EMAIL_CONNECTION_STRING)
#         message = {
#             "senderAddress": settings.AZURE_EMAIL_SENDER,
#             "recipients": {
#                 "to": [{"address": registration.email}]
#             },
#             "content": {
#                 "subject": f"Registration Confirmed — {registration.registration_id} | {registration.race.name}",
#                 "html": html_body,
#             },
#         }
#         poller = client.begin_send(message)
#         poller.result()  # Wait for send to complete
#     except Exception as e:
#         # Log but don't crash the registration flow
#         print(f"[EMAIL ERROR] Failed to send confirmation to {registration.email}: {e}")


# accounts/email_utils.py

from django.template.loader import render_to_string
from django.conf import settings
from azure.communication.email import EmailClient


def send_registration_confirmation(registration, request=None):
    """
    Sends an HTML registration confirmation email via Azure Communication Services.
    Called after a successful registration save.
    """
    if not registration.email:
        return  # No email address on record

    # Build absolute site URL for the CTA button in the email
    if request:
        site_url = request.build_absolute_uri('/').rstrip('/')
    else:
        site_url = ''

    # Render the HTML email template
    html_body = render_to_string('accounts/registration_confirmation.html', {
        'registration': registration,
        'site_url': site_url,
    })

    try:
        client = EmailClient.from_connection_string(settings.AZURE_EMAIL_CONNECTION_STRING)
        message = {
            "senderAddress": settings.AZURE_EMAIL_SENDER,
            "recipients": {
                "to": [{"address": registration.email}]
            },
            "content": {
                "subject": (
                    f"Registration Confirmed — "
                    f"{registration.registration_id} | {registration.race.name}"
                ),
                "html": html_body,
            },
        }
        poller = client.begin_send(message)
        poller.result()  # Wait for send to complete

    except Exception as e:
        # Log but don't crash the registration flow
        print(f"[EMAIL ERROR] Failed to send confirmation to {registration.email}: {e}")