from twilio.rest import Client
import os
from dotenv import load_dotenv

#

from twilio.rest import Client


def enviar_sms_teste(destino, mensagem):
    # Estas credenciais devem ser removidas após teste
    account_sid = 'ACd025a213f58164a5eac8e653531ec4a1'
    auth_token = 'cf1462a6e213fd8439c2abb98d9426b2'
    twilio_number = '+17755229557'  # Número de teste Twilio

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=mensagem,
            from_=twilio_number,
            to=destino
        )
        return f"SMS enviado! SID: {message.sid}"
    except Exception as e:
        return f"Falha: {str(e)}"


# Exemplo de uso
print(enviar_sms_teste('++18777804236', 'Teste do sistema QueimadasGS'))