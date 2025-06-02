#Nome: Larissa Pereira Biusse
#RM: 564068

# Importações necessárias para o sistema
import heapq  # Para fila prioritária
from collections import deque  # Para filas de equipes e drones

import folium

from mapa_monitoramento import MapaMonitoramento
from typing import List, Dict, Optional  # Para type hints
import random  # Para simulação de dados
import threading  # Para processamento paralelo
import time  # Para controle de tempo
from modelos import Ocorrencia, ContatoEmergencia

from sistema_alerta import SistemaAlerta


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
        registro = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "drone": drone_id,
            "acao": acao,
            "ocorrencia": ocorrencia_id
        }
        self.historico.append(registro)

    def obter_historico(self) -> List[dict]:
        """Retorna o histórico completo"""
        return self.historico.to_list()

    def registrar_acao(self, acao: str, local: list, detalhes: str = ""):
        """Método alternativo para registrar ações genéricas"""
        self.registrar("Sistema", acao, detalhes)


# ==================== Sistema Principal ==============================

class SistemaEmergencia:
    def __init__(self):
        # Heap para ocorrências prioritárias


        self.fila_prioritaria: List[Ocorrencia] = []
        self.monitoramento = MapaMonitoramento(self)
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
        for regiao in ["Amazônia", "Pantanal", "Cerrado", "Mata Atlântica","Caatinga", "Pampa"]:
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
                time.sleep(3) # Simula tempo de voo
                ocorrencia.fogo_confirmado = random.random() > 0.2 # 95% de chance de confirmar

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
            try:
                time.sleep(10)  # Verifica a cada 10 segundos
                for oc in self.fila_prioritaria:
                    if (hasattr(oc, 'status') and
                            oc.status == "Fogo ativo" and
                            random.random() > 0.4):
                        oc.fogo_apagado = True
                        oc.status = "Fogo apagado"
                        oc.severidade = 1
                        self.drone_tracker.registrar(
                            drone_id="Sistema",
                            acao=f"Fogo apagado na ocorrência {oc.id}",
                            ocorrencia_id=oc.id
                        )
            except Exception as e:
                print(f"Erro na verificação de fogos apagados: {str(e)}")
                time.sleep(30)  # Long wait before retry


    def verificar_drones_automaticamente(self):
        """Verifica automaticamente se precisa enviar drones"""
        while True:
            time.sleep(5)
            try:
                if self.drones_disponiveis and self.fila_prioritaria:
                    # Filtra ocorrências prioritárias
                    ocorrencias = [oc for oc in self.fila_prioritaria
                                   if hasattr(oc, 'severidade') and
                                   hasattr(oc, 'status') and
                                   oc.severidade > 3 and
                                   oc.status in ["Pendente", "Fogo ativo"]]

                    if ocorrencias:
                        # Ordena por severidade e envia drone para a mais grave
                        ocorrencias.sort(key=lambda x: x.severidade, reverse=True)
                        self.enviar_drone(ocorrencias[0])
            except Exception as e:
                print(f"Erro na verificação automática de drones: {str(e)}")
                time.sleep(10)  # Espera mais tempo antes de tentar novamente
    def adicionar_marcador(self, lat, lon, cor='red', popup=''):
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            print(f"Coordenadas inválidas: lat={lat}, lon={lon}")
            return

        # Resto do método para criar o marcador
        if cor == 'red':
            folium.Marker(...).add_to(self.mapa)
        # ...

    def atender_ocorrencia(self):
        """Atende a próxima ocorrência na fila prioritária."""
        if not self.fila_prioritaria:
            return None

        try:
            # Obtém e remove a primeira ocorrência
            ocorrencia = self.fila_prioritaria.pop(0)

            # Atualiza os status da ocorrência
            ocorrencia.status = "Fogo apagado"
            ocorrencia.fogo_apagado = True
            ocorrencia.tempo_fim_fogo = time.time()

            # Cria o registro histórico
            registro = {
                "tipo": "Atendimento",
                "descricao": f"Fogo apagado em {ocorrencia.regiao}",
                "severidade": ocorrencia.severidade,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "local": ocorrencia.local
            }

            # Adiciona ao histórico
            self.historico.append(registro)

            # Registra ação do drone
            self.drone_tracker.registrar(
                drone_id="Equipe",
                acao="Atendimento",
                ocorrencia_id=ocorrencia.id
            )

            return {
                "mensagem": f"Fogo em {ocorrencia.regiao} foi apagado",
                "detalhes": {
                    "severidade": ocorrencia.severidade,
                    "tempo_ativo": f"{(ocorrencia.tempo_fim_fogo - ocorrencia.tempo_inicio_fogo):.1f}s" if ocorrencia.tempo_inicio_fogo > 0 else "0s",
                    "local": ocorrencia.local
                }
            }
        except Exception as e:
            print(f"Erro ao atender ocorrência: {str(e)}")
            return None

    def simular_ocorrencias(self, quantidade=1):
        """Simula novas ocorrências de incêndio"""
        regioes = ["Amazônia", "Cerrado", "Mata Atlântica", "Caatinga", "Pampa"]

        for _ in range(quantidade):
            try:
                # Gera coordenadas dentro do território brasileiro
                lat = random.uniform(-33.75, 5.27)
                lon = random.uniform(-73.99, -34.79)

                nova_ocorrencia = Ocorrencia(
                    prioridade=0,  # Será calculada no __post_init__
                    local=[lat, lon],
                    severidade=random.randint(1, 5),
                    regiao=random.choice(regioes)
                )

                self.fila_prioritaria.append(nova_ocorrencia)
                print(f"Ocorrência {nova_ocorrencia.id} simulada na região {nova_ocorrencia.regiao}")

            except Exception as e:
                print(f"Erro ao simular ocorrência: {str(e)}")
            # Thread para simulação periódica de ocorrências (apenas para demonstração)

    def simular_ocorrencias_periodicamente(self):
        """Simula ocorrências periodicamente em segundo plano"""
        while True:
            try:
                time.sleep(5)  # Espera 5 segundos entre simulações
                self.simular_ocorrencias(1)

                # Log mais informativo
                if self.fila_prioritaria:
                    ultima_ocorrencia = self.fila_prioritaria[-1]
                    log_msg = (
                        f"[{time.strftime('%H:%M:%S')}] "
                        f"Ocorrência simulada - ID: {getattr(ultima_ocorrencia, 'id', 'N/A')} | "
                        f"Região: {getattr(ultima_ocorrencia, 'regiao', 'N/A')} | "
                        f"Severidade: {getattr(ultima_ocorrencia, 'severidade', 'N/A')}"
                    )
                    print(log_msg)
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Tentativa de simulação falhou - fila vazia")

            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Erro na simulação periódica: {str(e)}")
                time.sleep(10)  # Espera mais tempo antes de tentar novamente em caso de erro

    def iniciar_servicos(self):

        """Inicia threads de serviços em segundo plano"""
        threads = [
            threading.Thread(target=self.verificar_drones_automaticamente, daemon=True, name="drone_checker"),
            threading.Thread(target=self.verificar_fogos_apagados, daemon=True, name="fire_checker"),

        ]
        # Thread para simulação periódica
        threading.Thread(
            target=self.simular_ocorrencias_periodicamente,
            daemon=True,
            name="simulador_ocorrencias"
        ).start()

        for t in threads:
            t.start()
            print(f"Iniciada thread {t.name}")





