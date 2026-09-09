from azure.communication.email import EmailClient

connection_string = "endpoint=https://ts-com.india.communication.azure.com/;accesskey=2La23dvQrrAGRo9xiQVyapOz0mMreNgTPdIgxIjl3OD…"

client = EmailClient.from_connection_string(connection_string)

message = {

    "senderAddress": "DoNotReply@e816a3a8-f533-4231-ad0c-fa6a80537e32.azurecomm.net",

    "recipients": {

        "to": [{"address": "mrprabalpratap23@gmail.com"}]

    },

    "content": {

        "subject": "Test Email",

        "plainText": "Hello! This is a test.",

    }

}

poller = client.begin_send(message)

result = poller.result()

print("Sent! Message ID:", result.message_id)
