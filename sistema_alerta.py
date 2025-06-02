#Nome: Larissa Pereira Biusse
#RM: 564068

from email.mime.text import MIMEText
import smtplib
from typing import List, Optional

from twilio.rest import Client

from modelos import ContatoEmergencia, Ocorrencia


class Node:
    """Nó para lista ligada"""

    def __init__(self, data):
        self.data = data
        self.next: Optional['Node'] = None
class LinkedList:
    """Lista ligada personalizada para histórico"""

    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None

    def append(self, data):
        """Adiciona novo nó ao final da lista"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def to_list(self) -> List:
        """Converte a lista ligada para lista Python"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result


class SistemaAlerta:
    """Sistema de envio de alertas por e-mail e SMS"""
    def __init__(self, sistema_emergencia):
        # Lista de contatos para notificação

        self.sistema = sistema_emergencia
        self.contatos = LinkedList() # Referência ao sistema principal

        # Configurações de serviços externos
        self.email_config = {
            'servidor': 'smtp.emergencia.com',
            'porta': 587,
            'usuario': 'alerta@queimadas.com',
            'senha': 'senha_segura'
        }

        self.sms_config = {
            'account_sid': 'ACd025a213f58164a5eac8e653531ec4a1',
            'auth_token': 'cf1462a6e213fd8439c2abb98d9426b2',
            'from_number': '+17755229557'
        }

        self.templates = {
            'email': {
                'alerta': "ALERTA: Foco de incêndio detectado em {regiao} - {local}. Severidade: {severidade}",
                'confirmacao': "CONFIRMAÇÃO: Incêndio em {regiao} foi controlado",
                'alerta_preliminar': "ALERTA PRELIMINAR: Possível foco em {regiao} - {local}"
            },
            'sms': {
                'alerta': "[ALERTA CRÍTICO] Fogo em {regiao}! Severidade: {severidade}. Local: {local}",
                'confirmacao': "[CONTROLE] Incêndio em {regiao} foi controlado",
                'alerta_preliminar': "[ALERTA] Possível fogo em {regiao}. Verificação em andamento"
            }
        }

    def adicionar_contato(self, contato: ContatoEmergencia):
        """Adiciona um novo contato para receber alertas"""
        self.contatos.append(contato)
        self.sistema.historico.append(f"Novo contato adicionado: {contato.nome}")


    def enviar_alertas(self, ocorrencia: Ocorrencia, tipo: str = 'alerta'):
        """Envia alertas para todos os contatos relevantes"""
        # Só envia SMS se a severidade for >= 4
        send_sms = ocorrencia.severidade >= 4

        current = self.contatos.head
        while current:
            contato = current.data
            if ocorrencia.regiao in contato.regioes:
                self._enviar_email(contato, ocorrencia, tipo)
                if send_sms:  # Só envia SMS se atender ao critério
                    self._enviar_sms(contato, ocorrencia, tipo)
            current = current.next


    def _enviar_email(self, contato: ContatoEmergencia, ocorrencia: Ocorrencia, tipo: str):
        """Envia e-mail de alerta"""
        try:
            msg = MIMEText(self.templates['email'][tipo].format(
                regiao=ocorrencia.regiao,
                local=ocorrencia.local,
                severidade=ocorrencia.severidade
            ))
            msg['Subject'] = f"ALERTA DE QUEIMADA - {ocorrencia.regiao}"
            msg['From'] = self.email_config['usuario']
            msg['To'] = contato.email

            with smtplib.SMTP(self.email_config['servidor'], self.email_config['porta']) as server:
                server.starttls()
                server.login(self.email_config['usuario'], self.email_config['senha'])
                server.send_message(msg)

            self.sistema.drone_tracker.registrar("Sistema", f"E-mail enviado para {contato.nome}", ocorrencia.id)
        except Exception as e:
            self.sistema.historico.append(f"Falha ao enviar e-mail para {contato.nome}: {str(e)}")

    def _enviar_sms(self, contato: ContatoEmergencia, ocorrencia: Ocorrencia, tipo: str):
        """Envia SMS de alerta"""

        try:
            client = Client(self.sms_config['account_sid'], self.sms_config['auth_token'])

            message = client.messages.create(
                body=self.templates['sms'][tipo].format(
                    regiao=ocorrencia.regiao,
                    local=ocorrencia.local,
                    severidade=ocorrencia.severidade
                ),
                from_=self.sms_config['from_number'],
                to=contato.telefone
            )

            self.sistema.drone_tracker.registrar("Sistema", f"SMS enviado para {contato.nome}", ocorrencia.id)
        except Exception as e:
            self.sistema.historico.append(f"Falha ao enviar SMS para {contato.nome}: {str(e)}")