import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random
import threading
import time

import cv2
import numpy as np
from flask import Flask, jsonify, request
from tensorflow.keras import models,layers



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


# ==================== Estruturas de Dados ====================

@dataclass(order=True)
class Ocorrencia:
    prioridade: int
    local: str = field(compare=False)
    severidade: int = field(compare=False)
    regiao: str = field(compare=False)
    id: int = field(default_factory=lambda: random.randint(1000, 9999), compare=False)
    status: str = field(default="Pendente", compare=False)
    fogo_confirmado: bool = field(default=False, compare=False)
    fogo_apagado: bool = field(default=False, compare=False)
    tempo_inicio_fogo: float = field(default=0.0, compare=False)

    def __post_init__(self):
        self.prioridade = -self.severidade
        if self.regiao in ["Amazônia", "Pantanal"]:
            self.prioridade *= 2


class DroneTracker:
    def __init__(self):
        self.historico = []

    def registrar(self, drone_id: str, acao: str, ocorrencia_id: int = None):
        registro = f"{time.strftime('%H:%M:%S')} - {drone_id}: {acao}"
        if ocorrencia_id:
            registro += f" (Ocorrência {ocorrencia_id})"
        self.historico.append(registro)

    def obter_historico(self) -> List[str]:
        return self.historico.copy()


# ==================== Sistema Principal ====================

class SistemaEmergencia:
    def __init__(self):
        self.fila_prioritaria = []
        self.drone_tracker = DroneTracker()
        self.equipes_disponiveis = deque([f"Equipe {i}" for i in range(1, 6)])
        self.drones_disponiveis = deque([f"Drone {i}" for i in range(1, 4)])
        self.drone_em_missao = False

    def registrar_ocorrencia(self, local: str, severidade: int, regiao: str) -> Ocorrencia:
        nova_ocorrencia = Ocorrencia(0, local, severidade, regiao)
        heapq.heappush(self.fila_prioritaria, nova_ocorrencia)
        return nova_ocorrencia

    def enviar_drone(self, ocorrencia: Ocorrencia) -> Dict:
        if not self.drones_disponiveis or self.drone_em_missao:
            return {"status": "error", "message": "Nenhum drone disponível"}

        self.drone_em_missao = True
        drone = self.drones_disponiveis.popleft()
        ocorrencia.status = "Em verificação"
        self.drone_tracker.registrar(drone, "Enviado para verificação", ocorrencia.id)

        def simular_missao():
            try:
                time.sleep(1.5)
                ocorrencia.fogo_confirmado = random.random() > 0.5

                if ocorrencia.fogo_confirmado:
                    ocorrencia.status = "Fogo ativo"
                    ocorrencia.tempo_inicio_fogo = time.time()
                    ocorrencia.severidade = max(ocorrencia.severidade, 4)
                    self.drone_tracker.registrar(drone, "Fogo confirmado", ocorrencia.id)
                else:
                    ocorrencia.status = "Verificado"
                    self.drone_tracker.registrar(drone, "Nenhum fogo detectado", ocorrencia.id)
            finally:
                self.drones_disponiveis.append(drone)
                self.drone_em_missao = False

        threading.Thread(target=simular_missao, daemon=True).start()
        return {"status": "success", "drone": drone, "ocorrencia_id": ocorrencia.id}

    def verificar_drones_automaticamente(self):
        while True:
            time.sleep(2)
            if self.drones_disponiveis and self.fila_prioritaria:
                ocorrencias_criticas = [oc for oc in self.fila_prioritaria
                                        if oc.severidade > 3 and oc.status in ["Pendente", "Fogo ativo"]]
                if ocorrencias_criticas:
                    ocorrencias_criticas.sort(key=lambda x: x.severidade, reverse=True)
                    self.enviar_drone(ocorrencias_criticas[0])

    def verificar_fogos_apagados(self):
        """Verifica periodicamente se fogos foram extintos"""
        while True:
            time.sleep(10)  # Verifica a cada 10 segundos
            for oc in self.fila_prioritaria:
                if oc.status == "Fogo ativo" and random.random() > 0.7:  # 30% chance de fogo ser apagado
                    oc.fogo_apagado = True
                    oc.status = "Fogo apagado"
                    oc.severidade = 1  # Reduz severidade após fogo ser apagado
                    self.drone_tracker.registrar("Sistema", f"Fogo apagado na ocorrência {oc.id}")

    def atender_ocorrencia(self) -> Optional[str]:
        if not self.fila_prioritaria or not self.equipes_disponiveis:
            return None

        ocorrencia = heapq.heappop(self.fila_prioritaria)
        equipe = self.equipes_disponiveis.popleft()
        ocorrencia.status = "Em atendimento"
        self.drone_tracker.registrar("Sistema", f"Atendimento iniciado por {equipe}", ocorrencia.id)
        return f"{equipe} designada para ocorrência {ocorrencia.id}"

    def simular_ocorrencias(self, quantidade: int):
        regioes = ["Amazônia", "Pantanal", "Cerrado", "Mata Atlântica"]
        locais = ["Floresta Nacional", "Reserva Biológica", "Parque Estadual"]

        for _ in range(quantidade):
            self.registrar_ocorrencia(
                local=f"{random.choice(locais)} {random.randint(1, 100)}",
                severidade=random.randint(1, 5),
                regiao=random.choice(regioes)
            )


# ==================== API Flask ====================

app = Flask(__name__)
sistema = SistemaEmergencia()


@app.route('/')
def home():
    return "Sistema de Gerenciamento de Queimadas"


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


@app.route('/historico_drones', methods=['GET'])
def historico_drones():
    return jsonify({
        "historico": sistema.drone_tracker.obter_historico(),
        "total_acoes": len(sistema.drone_tracker.historico)
    })


@app.route('/simular', methods=['POST'])
def simular():
    quantidade = request.json.get('quantidade', 1)
    sistema.simular_ocorrencias(quantidade)
    return jsonify({"status": "success"})


@app.route('/atender', methods=['POST'])
def atender():
    resultado = sistema.atender_ocorrencia()
    return jsonify({"resultado": resultado} if resultado else {"error": "Nada para atender"})


def iniciar_servicos():
    threading.Thread(target=sistema.verificar_drones_automaticamente, daemon=True).start()
    threading.Thread(target=sistema.verificar_fogos_apagados, daemon=True).start()
    threading.Thread(target=lambda: [time.sleep(3), sistema.simular_ocorrencias(1)], daemon=True).start()
    threading.Thread(target=simular_ocorrencias_periodicamente, daemon=True).start()
def simular_ocorrencias_periodicamente():
    """Função que simula ocorrências automaticamente em intervalos regulares"""
    while True:
        time.sleep(3)  # Intervalo de 3 segundos
        sistema.simular_ocorrencias(1)
        print(f"[{time.strftime('%H:%M:%S')}] Nova ocorrência simulada")

if __name__ == '__main__':
    print("Iniciando serviços...")
    iniciar_servicos()

    app.run(host='0.0.0.0', port=5000, debug=True)

    # sehna=Testegs21$
    # N7SYZGJTXDJKPFRX8N9KH55E