import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List, Dict
import random
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras import layers, models
from flask import Flask, jsonify, request
import threading
import time


# ==================== Módulo 1: Sistema de Monitoramento (Simulado) ====================

class SensorSimulator:
    """Simula sensores térmicos, de temperatura, umidade e CO2"""

    def __init__(self):
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
            img = np.random.randint(self.sensors['thermal']['min'],
                                    self.sensors['thermal']['max'],
                                    (*size, 3)).astype(np.uint8)
            # Adiciona área de fogo
            x, y = np.random.randint(50, 150, 2)
            img[x - 20:x + 20, y - 20:y + 20] = np.random.randint(
                self.sensors['thermal']['fire_min'],
                self.sensors['thermal']['fire_max'],
                (40, 40, 3))
            thermal_img = cv2.applyColorMap(img, cv2.COLORMAP_HOT)
        else:
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


# ==================== Módulo 2: Detecção por IA ====================

class FireDetectionModel:
    """Modelo de IA para detecção de focos de incêndio"""

    def __init__(self):
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
            layers.Dense(1, activation='sigmoid')
        ])
        return model

    def predict_fire(self, thermal_image):
        """Faz a predição de fogo em uma imagem térmica"""
        # Pré-processamento
        img = cv2.resize(thermal_image, (224, 224))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        # Predição
        prediction = self.model.predict(img)[0][0]
        return prediction


# ==================== Módulo 3: Sistema de Gerenciamento de Emergências ====================

@dataclass(order=True)
class Ocorrencia:
    """Classe que representa uma ocorrência de queimada"""
    prioridade: int
    local: str = field(compare=False)
    severidade: int = field(compare=False)
    regiao: str = field(compare=False)
    status: str = field(default="Pendente", compare=False)
    id: int = field(default_factory=lambda: random.randint(1000, 9999), compare=False)
    latitude: float = field(default=0.0, compare=False)
    longitude: float = field(default=0.0, compare=False)
    status: str = field(default="Pendente",compare=False)  # Valores possíveis: Pendente, Em verificação, Fogo confirmado, Em atendimento, Concluído
    fogo_confirmado: str = field(default=False, compare=False)

    def __post_init__(self):
        """Define a prioridade com base na severidade e região crítica"""
        # Prioridade maior para severidades mais altas
        self.prioridade = -self.severidade  # Usamos negativo para max heap
        if self.regiao in ["Amazônia", "Pantanal"]:  # Regiões mais críticas
            self.prioridade *= 2


# Adicione esta classe para rastrear ações dos drones
class DroneTracker:
    def __init__(self):
        self.historico_drones = LinkedList()

    def registrar_acao(self, drone_id: str, acao: str, ocorrencia_id: int = None):
        registro = f"Drone {drone_id}: {acao}"
        if ocorrencia_id:
            registro += f" (Ocorrência ID {ocorrencia_id})"
        self.historico_drones.append(registro)

    def obter_historico(self) -> List[str]:
        return self.historico_drones.to_list()

class SistemaEmergencia:
    """Sistema principal de gerenciamento de emergências"""

    def __init__(self):
        self.fila_prioritaria: List[Ocorrencia] = []  # Heap de ocorrências
        self.historico = LinkedList()  # Lista ligada para histórico
        self.equipes_disponiveis = deque()  # Fila de equipes disponíveis
        self.tarefas_pendentes = []  # Pilha de tarefas secundárias
        self.regioes = BinarySearchTree()  # Árvore para organizar regiões
        self.drones_disponiveis = deque()  # Fila de drones disponíveis
        self.drone_tracker = DroneTracker()
        self.drone_em_missao = False

        # Inicializa recursos
        self.inicializar_recursos()

        # Modelo de IA
        self.fire_model = FireDetectionModel()

        # Simulador de sensores
        self.sensor_simulator = SensorSimulator()

    def inicializar_recursos(self):
        """Inicializa equipes e drones"""
        for i in range(1, 6):
            self.equipes_disponiveis.append(f"Equipe {i}")

        for i in range(1, 4):
            self.drones_disponiveis.append(f"Drone {i}")

        # Cadastra algumas regiões iniciais
        regioes_iniciais = ["Amazônia", "Pantanal", "Cerrado", "Mata Atlântica", "Caatinga", "Pampa"]
        for regiao in regioes_iniciais:
            self.regioes.insert(regiao)

    def registrar_ocorrencia(self, local: str, severidade: int, regiao: str, lat: float, lon: float) -> Ocorrencia:
        """Registra uma nova ocorrência no sistema"""
        if not self.regioes.search(regiao):
            self.regioes.insert(regiao)
            self.historico.append(f"Nova região cadastrada: {regiao}")

        # Calcula a prioridade inicial baseada na severidade
        prioridade = -severidade  # Usamos negativo para max heap
        if regiao in ["Amazônia", "Pantanal"]:  # Regiões mais críticas
            prioridade *= 2

        nova_ocorrencia = Ocorrencia(
            prioridade=prioridade,  # Agora passando a prioridade explicitamente
            local=local,
            severidade=severidade,
            regiao=regiao,
            latitude=lat,
            longitude=lon
        )

        heapq.heappush(self.fila_prioritaria, nova_ocorrencia)
        self.historico.append(
            f"Nova ocorrência registrada: ID {nova_ocorrencia.id} em {local} (Severidade: {severidade})")

        return nova_ocorrencia

    def finalizar_atendimentos_automaticamente(self):
        """Finaliza atendimentos após 6 segundos automaticamente"""
        while True:
            time.sleep(6)
            for ocorrencia in self.fila_prioritaria:
                if ocorrencia.status == "Em atendimento":
                    ocorrencia.status = "Concluído"
                    ocorrencia.fogo_confirmado = False  # Resetar ao concluir
                    equipe_liberada = f"Equipe {random.randint(1, 5)}"
                    self.equipes_disponiveis.append(equipe_liberada)
                    self.historico.append(
                        f"Atendimento automático concluído para ocorrência {ocorrencia.id}. {equipe_liberada} liberada.")
    def enviar_drone_para_verificacao(self, ocorrencia: Ocorrencia) -> Dict:
        if not self.drones_disponiveis or self.drone_em_missao:
            return {"status": "error", "message": "Nenhum drone disponível"}

        self.drone_em_missao = True
        drone = self.drones_disponiveis.popleft()
        ocorrencia.status = "Em verificação"

        # Registrar no histórico
        self.drone_tracker.registrar_acao(drone, f"Enviado para ocorrência {ocorrencia.id}", ocorrencia.id)
        self.historico.append(
            f"{drone} enviado para verificar ocorrência ID {ocorrencia.id} (Severidade: {ocorrencia.severidade})")

        # Simular missão (agora mais rápida para permitir redirecionamento)
        def simular_missao():

            try:
                time.sleep(1.5)
                has_fire = random.random() > 0.5
                sensor_data = self.sensor_simulator.generate_sensor_data(has_fire)

                thermal_img = np.array(sensor_data['thermal_image'], dtype=np.uint8)
                fire_prob = self.fire_model.predict_fire(thermal_img)
                confirmed_fire = fire_prob > 0.7

                    # Atualizar status e flag de fogo confirmado
                ocorrencia.fogo_confirmado = confirmed_fire  # Definindo o novo campo
                if confirmed_fire:
                    ocorrencia.severidade = max(ocorrencia.severidade, 4)
                    ocorrencia.status = "Fogo confirmado"
                    self.historico.append(f"Fogo confirmado na ocorrência {ocorrencia.id}")
                else:
                    ocorrencia.status = "Verificado - sem fogo"

            finally:
                # Liberar drone independente do resultado
                self.drones_disponiveis.append(drone)
                self.drone_em_missao = False
                self.drone_tracker.registrar_acao(drone, f"Retornou da ocorrência {ocorrencia.id}", ocorrencia.id)

        threading.Thread(target=simular_missao, daemon=True).start()

        return {
            "status": "success",
            "drone": drone,
            "ocorrencia_id": ocorrencia.id,
            "message": "Drone enviado para verificação. Resultados em breve."
        }
    def verificar_e_enviar_drones(self):
        """Verifica ocorrências críticas e envia drones automaticamente"""
        while True:
            time.sleep(2)  # Verifica a cada 2 segundos

            # Verifica se há drones disponíveis e ocorrências críticas
            if self.drones_disponiveis and self.fila_prioritaria:
                # Faz uma cópia da fila prioritária para não modificar a original durante a iteração
                ocorrencias_criticas = [oc for oc in self.fila_prioritaria
                                        if oc.severidade > 3 and oc.status == "Pendente"]

                if ocorrencias_criticas:
                    # Ordena por severidade (maior primeiro)
                    ocorrencias_criticas.sort(key=lambda x: x.severidade, reverse=True)
                    # Envia drone para a ocorrência mais crítica
                    ocorrencia = ocorrencias_criticas[0]
                    resultado = self.enviar_drone_para_verificacao(ocorrencia)

                    # Se não há drones disponíveis após envio, espera liberação
                    if not self.drones_disponiveis:
                        continue


                    # Atualiza status se fogo for confirmado
                    if resultado.get('fire_confirmed', False):
                        ocorrencia.severidade = max(ocorrencia.severidade, 4)  # Garante severidade mínima de 4
                        self.historico.append(
                            f"Fogo confirmado na ocorrência {ocorrencia.id} - Severidade aumentada para {ocorrencia.severidade}")

    def atender_ocorrencia(self) -> Optional[str]:
        """Atende a ocorrência de maior prioridade"""
        if not self.fila_prioritaria:
            self.historico.append("Tentativa de atendimento sem ocorrências pendentes")
            return None

        if not self.equipes_disponiveis:
            self.historico.append("Nenhuma equipe disponível para atendimento")
            return None

        ocorrencia = heapq.heappop(self.fila_prioritaria)
        equipe = self.equipes_disponiveis.popleft()

        ocorrencia.status = "Em atendimento"
        mensagem = f"{equipe} designada para ocorrência ID {ocorrencia.id} em {ocorrencia.local}"
        self.historico.append(mensagem)

        # Adiciona tarefas secundárias à pilha
        self.tarefas_pendentes.append(f"Atualizar status da ocorrência {ocorrencia.id}")
        self.tarefas_pendentes.append(f"Gerar relatório para {ocorrencia.regiao}")

        return mensagem

    def finalizar_atendimento(self, id_ocorrencia: int) -> str:
        """Finaliza o atendimento de uma ocorrência"""
        # Processa tarefas pendentes da pilha
        while self.tarefas_pendentes:
            tarefa = self.tarefas_pendentes.pop()
            self.historico.append(f"Tarefa concluída: {tarefa}")

        # Simula liberação de equipe
        equipe_liberada = f"Equipe {random.randint(1, 5)}"
        self.equipes_disponiveis.append(equipe_liberada)

        mensagem = f"Atendimento da ocorrência {id_ocorrencia} finalizado. {equipe_liberada} disponível."
        self.historico.append(mensagem)
        return mensagem

    def simular_ocorrencias(self, quantidade: int):
        """Simula a criação de ocorrências aleatórias"""
        regioes = ["Amazônia", "Pantanal", "Cerrado", "Mata Atlântica", "Caatinga", "Pampa"]
        locais = ["Floresta Nacional", "Reserva Biológica", "Parque Estadual", "Área de Preservação"]

        for i in range(quantidade):
            local = f"{random.choice(locais)} {random.randint(1, 100)}"
            severidade = random.randint(1, 5)
            regiao = random.choice(regioes)
            lat = random.uniform(-33.0, 5.0)  # Latitude aproximada do Brasil
            lon = random.uniform(-74.0, -34.0)  # Longitude aproximada do Brasil

            self.registrar_ocorrencia(local, severidade, regiao, lat, lon)

    def gerar_relatorio(self, regiao: str = None) -> List[str]:
        """Gera relatório de ocorrências por região"""
        relatorio = []

        if regiao:
            ocorrencias_regiao = [oc for oc in self.fila_prioritaria if oc.regiao == regiao]
            relatorio.append(f"Relatório para região {regiao}:")
            relatorio.append(f"Ocorrências pendentes: {len(ocorrencias_regiao)}")
            if ocorrencias_regiao:
                avg_severity = sum(oc.severidade for oc in ocorrencias_regiao) / len(ocorrencias_regiao)
                relatorio.append(f"Severidade média: {avg_severity:.1f}")
                active_fires = sum(1 for oc in ocorrencias_regiao if oc.severidade >= 3)
                relatorio.append(f"Focos ativos: {active_fires}")
            else:
                relatorio.append("Nenhuma ocorrência")
        else:
            relatorio.append("Relatório geral:")
            regioes = self.regioes.inorder_traversal()
            for reg in regioes:
                ocorrencias_reg = [oc for oc in self.fila_prioritaria if oc.regiao == reg]
                relatorio.append(f"{reg}: {len(ocorrencias_reg)} ocorrências")

        return relatorio

    def exibir_historico(self) -> List[str]:
        """Retorna o histórico de ações"""
        return self.historico.to_list()


class Node:
    """Nó para lista ligada e árvore binária"""

    def __init__(self, data):
        self.data = data
        self.next: Optional[Node] = None


class LinkedList:
    """Implementação de lista ligada para histórico"""

    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def to_list(self) -> List[str]:
        """Converte a lista ligada para lista Python"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result


class TreeNode:
    """Nó para árvore binária de busca"""

    def __init__(self, value):
        self.value = value
        self.left: Optional[TreeNode] = None
        self.right: Optional[TreeNode] = None


class BinarySearchTree:
    """Árvore binária de busca para organizar regiões"""

    def __init__(self):
        self.root: Optional[TreeNode] = None

    def insert(self, value):
        if not self.root:
            self.root = TreeNode(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node: TreeNode, value):
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
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node: Optional[TreeNode], value) -> bool:
        if node is None:
            return False
        if node.value == value:
            return True
        elif value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)

    def inorder_traversal(self) -> List[str]:
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node: Optional[TreeNode], result: List[str]):
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.value)
            self._inorder_recursive(node.right, result)


# ==================== API Backend ====================

app = Flask(__name__)
sistema = SistemaEmergencia()


@app.route('/')
def home():
    return "Sistema Autônomo de Prevenção, Detecção e Combate a Queimadas"


@app.route('/simular_ocorrencias', methods=['POST'])
def simular_ocorrencias():
    quantidade = request.json.get('quantidade', 1)
    sistema.simular_ocorrencias(quantidade)
    return jsonify({"status": "success", "message": f"{quantidade} ocorrências simuladas"})


@app.route('/registrar_ocorrencia', methods=['POST'])
def registrar_ocorrencia():
    data = request.json
    ocorrencia = sistema.registrar_ocorrencia(
        local=data['local'],
        severidade=data['severidade'],
        regiao=data['regiao'],
        lat=data.get('latitude', 0),
        lon=data.get('longitude', 0)
    )
    return jsonify({
        "status": "success",
        "ocorrencia": {
            "id": ocorrencia.id,
            "local": ocorrencia.local,
            "severidade": ocorrencia.severidade,
            "regiao": ocorrencia.regiao,
            "status": ocorrencia.status
        }
    })


@app.route('/verificar_ocorrencia/<int:ocorrencia_id>', methods=['GET'])
def verificar_ocorrencia(ocorrencia_id):
    # Busca em todas as ocorrências, não apenas na fila prioritária
    ocorrencia = None
    for oc in sistema.fila_prioritaria + [oc for oc in sistema.historico.to_list() if isinstance(oc, Ocorrencia)]:
        if getattr(oc, 'id', None) == ocorrencia_id:
            ocorrencia = oc
            break

    if not ocorrencia:
        return jsonify({
            "status": "error",
            "message": f"Ocorrência ID {ocorrencia_id} não encontrada",
            "ocorrencias_disponiveis": [oc.id for oc in sistema.fila_prioritaria]
        }), 404

    resultado = sistema.enviar_drone_para_verificacao(ocorrencia)
    return jsonify(resultado)

@app.route('/atender_ocorrencia', methods=['POST'])
def atender_ocorrencia():
    resultado = sistema.atender_ocorrencia()
    if not resultado:
        return jsonify({"status": "error", "message": "Nenhuma ocorrência ou equipe disponível"}), 400
    return jsonify({"status": "success", "message": resultado})


@app.route('/finalizar_atendimento/<int:ocorrencia_id>', methods=['POST'])
def finalizar_atendimento(ocorrencia_id):
    resultado = sistema.finalizar_atendimento(ocorrencia_id)
    return jsonify({"status": "success", "message": resultado})

@app.route('/listar_ocorrencias', methods=['GET'])
def listar_ocorrencias():
    ocorrencias = []
    for oc in sistema.fila_prioritaria:
        ocorrencias.append({
            "id": oc.id,
            "local": oc.local,
            "severidade": oc.severidade,
            "regiao": oc.regiao,
            "status": oc.status,
            "fogo_confirmado": oc.fogo_confirmado,
        })
    return jsonify({
        "status": "success",
        "ocorrencias": ocorrencias,
        "total": len(ocorrencias)
    })

@app.route('/relatorio', methods=['GET'])
def relatorio():
    regiao = request.args.get('regiao')
    relatorio = sistema.gerar_relatorio(regiao)
    return jsonify({"status": "success", "relatorio": relatorio})


@app.route('/historico', methods=['GET'])
def historico():
    historico = sistema.exibir_historico()
    return jsonify({"status": "success", "historico": historico})

# Adicione esta nova rota no Flask
@app.route('/historico_drones', methods=['GET'])
def historico_drones():
    historico = sistema.drone_tracker.obter_historico()
    return jsonify({
        "status": "success",
        "total_acoes": len(historico),
        "historico_drones": historico
    })


def run_simulator():
    """Função para simular ocorrências automaticamente"""
    # Inicia o verificador de drones em uma thread separada
    drone_checker_thread = threading.Thread(target=sistema.verificar_e_enviar_drones, daemon=True)
    drone_checker_thread.start()

    # Inicia o finalizador automático de atendimentos
    finalizador_thread = threading.Thread(target=sistema.finalizar_atendimentos_automaticamente, daemon=True)
    finalizador_thread.start()

    while True:
        time.sleep(3)  # Simula uma nova ocorrência a cada 3 segundos
        sistema.simular_ocorrencias(1)
        print("Nova ocorrência simulada")

if __name__ == '__main__':
    # Inicia o simulador em uma thread separada
    simulator_thread = threading.Thread(target=run_simulator, daemon=True)
    simulator_thread.start()

    # Inicia a API Flask
    app.run(host='0.0.0.0', port=5000, debug=True)