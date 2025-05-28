# Importações necessárias para o sistema
import heapq  # Para fila prioritária
from collections import deque  # Para filas de equipes e drones
from dataclasses import dataclass, field  # Para classes de dados
from typing import List, Dict, Optional  # Para type hints
import random  # Para simulação de dados
import threading  # Para processamento paralelo
import time  # Para controle de tempo
import smtplib  # Para envio de e-mails
from email.mime.text import MIMEText  # Para formatação de e-mails
from twilio.rest import Client  # Para envio de SMS
import cv2  # Para processamento de imagens
import numpy as np  # Para manipulação de arrays
from flask import Flask, jsonify, request  # Para API web
from tensorflow.keras import models, layers  # Para modelo de IA


# ==================== Módulo 1: Sistema de Monitoramento (Simulado) ====================

class SensorSimulator:
    """Simula sensores térmicos, de temperatura, umidade e CO2"""

    def __init__(self):
        # Configuração dos sensores com valores normais e de incêndio
        self.sensors = {
            'thermal': {'min': 20, 'max': 50, 'fire_min': 80, 'fire_max': 120},
            'temperature': {'min': 15, 'max': 45, 'fire_min': 60, 'fire_max': 100},
            'humidity': {'min': 20, 'max': 90, 'fire_min': 10, 'fire_max': 30},
            'co2': {'min': 300, 'max': 1000, 'fire_min': 1500, 'fire_max': 5000}
        }

    def generate_sensor_data(self, has_fire=False, size=(224, 224)):
        """Gera dados simulados de todos os sensores"""
        data = {}

        # Gera imagem térmica simulada
        if has_fire:
            # Cria imagem com área de fogo mais quente
            img = np.random.randint(self.sensors['thermal']['min'],
                                    self.sensors['thermal']['max'],
                                    (*size, 3)).astype(np.uint8)
            # Adiciona área de fogo aleatória
            x, y = np.random.randint(50, 150, 2)
            img[x - 20:x + 20, y - 20:y + 20] = np.random.randint(
                self.sensors['thermal']['fire_min'],
                self.sensors['thermal']['fire_max'],
                (40, 40, 3))
            thermal_img = cv2.applyColorMap(img, cv2.COLORMAP_HOT)
        else:
            # Imagem normal sem fogo
            img = np.random.randint(self.sensors['thermal']['min'],
                                    self.sensors['thermal']['max'],
                                    (*size, 3)).astype(np.uint8)
            thermal_img = cv2.applyColorMap(img, cv2.COLORMAP_HOT)

        data['thermal_image'] = thermal_img.tolist()

        # Gera outros dados de sensores
        for sensor in ['temperature', 'humidity', 'co2']:
            if has_fire and random.random() > 0.3:  # 70% de chance de detectar fogo
                data[sensor] = random.randint(
                    self.sensors[sensor]['fire_min'],
                    self.sensors[sensor]['fire_max'])
            else:
                data[sensor] = random.randint(
                    self.sensors[sensor]['min'],
                    self.sensors[sensor]['max'])

        return data


# ==================== Módulo 2: Simulação de Detecção por IA ====================

class FireDetectionModel:
    """Modelo de IA para detecção de focos de incêndio"""

    def __init__(self):
        # Constrói e compila o modelo de IA
        self.model = self.build_model()
        self.model.compile(optimizer='adam',
                           loss='binary_crossentropy',
                           metrics=['accuracy'])

    def build_model(self):
        """Constroi um modelo CNN simples para classificação"""
        model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # Saída binária (fogo ou não)
        ])
        return model

    def predict_fire(self, thermal_image):
        """Faz a predição de fogo em uma imagem térmica"""
        # Pré-processamento da imagem
        img = cv2.resize(thermal_image, (224, 224))
        img = img / 255.0  # Normalização
        img = np.expand_dims(img, axis=0)  # Adiciona dimensão do batch

        # Predição (retorna probabilidade de ser fogo)
        prediction = self.model.predict(img)[0][0]
        return prediction

# ==================== Estruturas de Dados ====================

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


class TreeNode:
    """Nó para árvore binária de regiões"""

    def __init__(self, value):
        self.value = value
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None


class BinarySearchTree:
    """Árvore binária de busca para regiões"""

    def __init__(self):
        self.root: Optional[TreeNode] = None

    def insert(self, value):
        """Insere novo valor na árvore"""
        if not self.root:
            self.root = TreeNode(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node: TreeNode, value):
        """Método auxiliar recursivo para inserção"""
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert_recursive(node.left, value)
        elif value > node.value:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert_recursive(node.right, value)

    def search(self, value) -> bool:
        """Busca um valor na árvore"""
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node: Optional[TreeNode], value) -> bool:
        """Método auxiliar recursivo para busca"""
        if node is None:
            return False
        if node.value == value:
            return True
        elif value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)


class DroneTracker:
    """Rastreamento de atividades dos drones"""
    def __init__(self):
        self.historico = LinkedList()

    def registrar(self, drone_id: str, acao: str, ocorrencia_id: int = None):
        """Registra uma ação no histórico"""
        registro = f"{time.strftime('%H:%M:%S')} - {drone_id}: {acao}"
        if ocorrencia_id:
            registro += f" (Ocorrência {ocorrencia_id})"
        self.historico.append(registro)

    def obter_historico(self) -> List[str]:
        """Retorna o histórico completo"""
        return self.historico.to_list()


@dataclass(order=True)
class Ocorrencia:
    """Classe que usa Heap pela prioridade"""
    prioridade: int # Usado para ordenação no heap
    local: str = field(compare=False)
    severidade: int = field(compare=False) # 1-5
    regiao: str = field(compare=False)
    id: int = field(default_factory=lambda: random.randint(1000, 9999), compare=False)
    status: str = field(default="Pendente", compare=False)
    fogo_confirmado: bool = field(default=False, compare=False)
    fogo_apagado: bool = field(default=False, compare=False)
    tempo_inicio_fogo: float = field(default=0.0, compare=False)

    def __post_init__(self):
        """Configura prioridade baseada na severidade e região"""
        self.prioridade = -self.severidade  # Heap máximo
        if self.regiao in ["Amazônia", "Pantanal"]:
            self.prioridade *= 2 # Prioridade dobrada


@dataclass
class ContatoEmergencia:
    """Contatos para notificação de emergências"""
    nome: str
    email: str
    telefone: str
    tipo: str  # "autoridade" ou "comunidade"
    regioes: List[str]  # Regiões que este contato monitora


class SistemaAlerta:
    """Sistema de envio de alertas por e-mail e SMS"""
    def __init__(self,sistema_emergencia):
        # Lista de contatos para notificação
        self.contatos = LinkedList() # Lista de contatos
        self.sistema = sistema_emergencia  # Armazenamos a referência

        # Configurações de serviços externos E-mail
        self.email_config = {
            'servidor': 'smtp.emergencia.com',
            'porta': 587,
            'usuario': 'alerta@queimadas.com',
            'senha': 'senha_segura'
        }

        # Configuração para SMS (Twilio)
        self.sms_config = {
            'account_sid': 'ACd025a213f58164a5eac8e653531ec4a1',
            'auth_token': 'cf1462a6e213fd8439c2abb98d9426b2',
            'from_number': '+17755229557'
        }



        # Template de mensagens
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


# ==================== Sistema Principal ==============================

class SistemaEmergencia:
    def __init__(self):
        # Heap para ocorrências prioritárias
        self.fila_prioritaria: List[Ocorrencia] = []

        # Fila (deque) para equipes disponíveis
        self.equipes_disponiveis = deque([f"Equipe {i}" for i in range(1, 6)])

        # Fila (deque) para drones disponíveis
        self.drones_disponiveis = deque([f"Drone {i}" for i in range(1, 4)])

        # Pilha para tarefas secundárias
        self.tarefas_pendentes = []

        # Lista ligada para histórico
        self.historico = LinkedList()

        # Árvore binária para regiões monitoradas
        self.regioes = BinarySearchTree()
        for regiao in ["Amazônia", "Pantanal", "Cerrado", "Mata Atlântica"]:
            self.regioes.insert(regiao)

        # Rastreador de drones
        self.drone_tracker = DroneTracker()
        self.drone_em_missao = False
        # Adicionar o sistema de alerta
        self.sistema_alerta = SistemaAlerta(self)

        # Adicionar alguns contatos iniciais
        self._inicializar_contatos_padrao()

    def _inicializar_contatos_padrao(self):
        """Adiciona contatos padrão do sistema"""
        contatos_iniciais = [
            ContatoEmergencia(
                nome="Defesa Civil Nacional",
                email="defesacivil@nacional.gov",
                telefone="+18777804236",
                tipo="autoridade",
                regioes=["Amazônia", "Pantanal", "Cerrado", "Mata Atlântica"]
            ),
            ContatoEmergencia(
                nome="Comunidade Local - Amazônia",
                email="lideranca@amazonia.com",
                telefone="+18777804236",
                tipo="comunidade",
                regioes=["Amazônia"]
            )
        ]

        for contato in contatos_iniciais:
            self.sistema_alerta.adicionar_contato(contato)
    def registrar_ocorrencia(self, local: str, severidade: int, regiao: str) -> Ocorrencia:
        if not self.regioes.search(regiao): # Se região nova, cadastra
            self.regioes.insert(regiao)
            self.historico.append(f"Nova região cadastrada: {regiao}")

        nova_ocorrencia = Ocorrencia(0, local, severidade, regiao)
        heapq.heappush(self.fila_prioritaria, nova_ocorrencia)
        self.historico.append(f"Nova ocorrência ID {nova_ocorrencia.id}")

        # Adiciona tarefa à pilha
        self.tarefas_pendentes.append(f"Gerar relatório para {regiao}")
        return nova_ocorrencia

    def enviar_drone(self, ocorrencia: Ocorrencia) -> Dict:
        """Envia drone para verificar ocorrência"""
        if not self.drones_disponiveis or self.drone_em_missao:
            return {"status": "error", "message": "Nenhum drone disponível"}

        self.drone_em_missao = True
        drone = self.drones_disponiveis.popleft()
        ocorrencia.status = "Em verificação"
        self.drone_tracker.registrar(drone, "Enviado para verificação", ocorrencia.id)

        # Envia alerta preliminar APENAS se severidade >= 4
        if ocorrencia.severidade >= 4:
            self.sistema_alerta.enviar_alertas(ocorrencia, 'alerta_preliminar')

        def simular_missao():
            try:
                time.sleep(1.5) # Simula tempo de voo
                ocorrencia.fogo_confirmado = random.random() > 0.5 # 50% de chance de confirmar

                if ocorrencia.fogo_confirmado:
                    ocorrencia.status = "Fogo ativo"
                    ocorrencia.tempo_inicio_fogo = time.time()
                    # Aumenta a severidade se for confirmado
                    ocorrencia.severidade = max(ocorrencia.severidade, 4) # Garante severidade
                    self.drone_tracker.registrar(drone, "Fogo confirmado", ocorrencia.id)

                    # Envia alerta de confirmação (já verifica severidade >= 4 internamente)
                    self.sistema_alerta.enviar_alertas(ocorrencia, 'alerta')

                    # Processa tarefas da pilha
                    while self.tarefas_pendentes:
                        tarefa = self.tarefas_pendentes.pop()
                        self.historico.append(f"Tarefa concluída: {tarefa}")
                else:
                    ocorrencia.status = "Verificado"
                    self.drone_tracker.registrar(drone, "Nenhum fogo detectado", ocorrencia.id)
            finally:
                # Libera drone após missão
                self.drones_disponiveis.append(drone)
                self.drone_em_missao = False

        # Inicia thread para missão do drone
        threading.Thread(target=simular_missao, daemon=True).start()
        return {"status": "success", "drone": drone}

    def verificar_fogos_apagados(self):
        while True:
            time.sleep(10) # Verifica a cada 10 segundos
            for oc in self.fila_prioritaria:
                if oc.status == "Fogo ativo" and random.random() > 0.7:  # 30% chance de apagar
                    oc.fogo_apagado = True
                    oc.status = "Fogo apagado"
                    oc.severidade = 1
                    self.drone_tracker.registrar("Sistema", f"Fogo apagado na ocorrência {oc.id}")

                    # Envia alerta de confirmação de controle
                    self.sistema_alerta.enviar_alertas(oc, 'confirmacao')


    def verificar_drones_automaticamente(self):
        """Verifica automaticamente se precisa enviar drones"""
        while True:
            time.sleep(2) # Verifica a cada 2 segundos
            if self.drones_disponiveis and self.fila_prioritaria:
                # Filtra ocorrências prioritárias
                ocorrencias = [oc for oc in self.fila_prioritaria
                               if oc.severidade > 3 and oc.status in ["Pendente", "Fogo ativo"]]
                if ocorrencias:
                    # Ordena por severidade e envia drone para a mais grave
                    ocorrencias.sort(key=lambda x: x.severidade, reverse=True)
                    self.enviar_drone(ocorrencias[0])



    def atender_ocorrencia(self) -> Optional[str]:
        """Designa equipe para atender ocorrência"""
        if not self.fila_prioritaria or not self.equipes_disponiveis:
            return None

        ocorrencia = heapq.heappop(self.fila_prioritaria) # Pega ocorrência mais prioritária
        equipe = self.equipes_disponiveis.popleft() # Pega primeira equipe disponível
        ocorrencia.status = "Em atendimento"
        msg = f"{equipe} designada para ocorrência {ocorrencia.id}"
        self.drone_tracker.registrar("Sistema", f"Atendimento iniciado por {equipe}", ocorrencia.id)
        return msg

    def simular_ocorrencias(self, quantidade: int):
        """Simula ocorrências para testes"""
        for _ in range(quantidade):
            self.registrar_ocorrencia(
                local=f"Área {random.randint(1, 100)}",
                severidade=random.randint(1, 5),
                regiao=random.choice(["Amazônia", "Pantanal", "Cerrado"])
            )


# ==================== API Flask ====================

app = Flask(__name__)
sistema = SistemaEmergencia()


# Endpoint raiz
@app.route('/')
def home():
    return "Sistema de Gerenciamento de Queimadas"

# Endpoint para listar ocorrências
@app.route('/ocorrencias', methods=['GET'])
def listar_ocorrencias():
    ocorrencias = [{
        "id": oc.id,
        "local": oc.local,
        "severidade": oc.severidade,
        "regiao": oc.regiao,
        "status": oc.status,
        "fogo_confirmado": oc.fogo_confirmado,
        "fogo_apagado": oc.fogo_apagado,
        "tempo_ativo": f"{(time.time() - oc.tempo_inicio_fogo):.1f}s" if oc.tempo_inicio_fogo > 0 else "Não ativo"
    } for oc in sistema.fila_prioritaria]
    return jsonify({"ocorrencias": ocorrencias})

# Endpoint para histórico geral
@app.route('/historico', methods=['GET'])
def historico():
    return jsonify({"historico": sistema.historico.to_list()})

# Endpoint para histórico de drones
@app.route('/historico_drones', methods=['GET'])
def historico_drones():
    return jsonify({
        "historico": sistema.drone_tracker.obter_historico(),
        "total_acoes": len(sistema.drone_tracker.historico.to_list())
    })

# Endpoint para simular ocorrências (POST)
@app.route('/simular', methods=['POST'])
def simular():
    quantidade = request.json.get('quantidade', 1)
    sistema.simular_ocorrencias(quantidade)
    return jsonify({"status": "success","msg":"Nova ocorrência simulada"})

# Endpoint para atender ocorrência (POST)
@app.route('/atender', methods=['POST'])
def atender():
    resultado = sistema.atender_ocorrencia()
    return jsonify({"resultado": resultado} if resultado else {"error": "Nada para atender"})

# Endpoint para listar contatos
@app.route('/contatos', methods=['GET'])
def listar_contatos():
    contatos = []
    current = sistema.sistema_alerta.contatos.head
    while current:
        contato = current.data
        contatos.append({
            'nome': contato.nome,
            'email': contato.email,
            'telefone': contato.telefone,
            'tipo': contato.tipo,
            'regioes': contato.regioes
        })
        current = current.next
    return jsonify({"contatos": contatos})

# Endpoint para adicionar contato (POST)
@app.route('/contatos/adicionar', methods=['POST'])
def adicionar_contato():
    data = request.json
    try:
        novo_contato = ContatoEmergencia(
            nome=data['nome'],
            email=data['email'],
            telefone=data['telefone'],
            tipo=data['tipo'],
            regioes=data['regioes']
        )
        sistema.sistema_alerta.adicionar_contato(novo_contato)
        return jsonify({"status": "success"})
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Campo faltando: {str(e)}"}), 400

# Endpoint para testar SMS (POST)
@app.route('/testar_sms', methods=['POST'])
def testar_sms():
    data = request.json
    try:
        # Cria uma ocorrência de teste com severidade 4
        ocorrencia_teste = Ocorrencia(
            prioridade=0,
            local=data.get('local', 'Área de Teste'),
            severidade=4,  # Severidade que dispara SMS
            regiao=data.get('regiao', 'Amazônia')
        )

        # Envia alerta
        sistema.sistema_alerta.enviar_alertas(ocorrencia_teste, 'alerta')
        return jsonify({"status": "success", "message": "SMS de teste enviado para contatos da região"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



def iniciar_servicos():
    """Inicia threads de serviços em segundo plano"""
    # Thread para verificação automática de drones
    threading.Thread(target=sistema.verificar_drones_automaticamente, daemon=True).start()
    # Thread para verificação de fogos apagados
    threading.Thread(target=sistema.verificar_fogos_apagados, daemon=True).start()

    # Thread para simulação periódica de ocorrências (apenas para demonstração)
    def simular_ocorrencias_periodicamente():
        while True:
            time.sleep(3)
            sistema.simular_ocorrencias(1)
            print(f"[{time.strftime('%H:%M:%S')}] Nova ocorrência simulada")

    threading.Thread(target=simular_ocorrencias_periodicamente, daemon=True).start()


if __name__ == '__main__':
    print("Iniciando serviços...")
    iniciar_servicos() # Inicia threads de serviço
    print("http://localhost:5000/")
    # Inicia servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)


