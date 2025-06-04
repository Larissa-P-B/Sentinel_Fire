#Nome: Larissa Pereira Biusse
#RM: 564068


# Importações necessárias para o sistema
import heapq  # Para fila prioritária (usada para implementar estruturas de dados como filas de prioridade)
from collections import deque  # Para filas de equipes e drones (estrutura de dados eficiente para filas)

import folium  # Biblioteca para criação de mapas interativos (usada para visualização geográfica)

from mapa_monitoramento import MapaMonitoramento  # Módulo personalizado para monitoramento de mapas
from typing import List, Dict, Optional  # Para type hints (anotações de tipo para melhor legibilidade do código)
import random  # Para simulação de dados aleatórios
import threading  # Para processamento paralelo (permite execução concorrente)
import time  # Para controle de tempo (pausas, medição de tempo, etc.)
from modelos import Ocorrencia, ContatoEmergencia  # Classes personalizadas para modelagem de dados

from sistema_alerta import SistemaAlerta  # Módulo personalizado para sistema de alertas


# ==================== Estruturas de Dados ====================

class Node:
    """Nó para lista ligada (linked list)"""
    def __init__(self, data):
        """Inicializa um novo nó da lista ligada

        Args:
            data: O valor a ser armazenado no nó (qualquer tipo de dado)
        """
        self.data = data  # Armazena o dado/conteúdo do nó
        self.next: Optional['Node'] = None  # Referência para o próximo nó (inicialmente None)


class LinkedList:
    """Lista ligada personalizada para histórico"""
    def __init__(self):
        """Inicializa uma lista ligada vazia"""
        self.head: Optional[Node] = None  # Ponteiro para o primeiro nó
        self.tail: Optional[Node] = None  # Ponteiro para o último nó (otimiza append)

    def append(self, data):
        """Adiciona novo nó ao final da lista

        Args:
            data: Dado a ser armazenado no novo nó

        Complexidade: O(1) - tempo constante devido ao ponteiro tail
        """
        new_node = Node(data)  # Cria novo nó com o dado

        # Caso lista vazia
        if not self.head:
            self.head = new_node  # Novo nó é tanto head quanto tail
            self.tail = new_node
        else:
            # Lista não vazia - adiciona após o tail atual
            self.tail.next = new_node  # Liga último nó ao novo
            self.tail = new_node  # Atualiza tail para o novo nó

    def to_list(self) -> List:
        """Converte a lista ligada para lista Python padrão

        Returns:
            List: Lista Python com todos os elementos na ordem da lista ligada

        Complexidade: O(n) - precisa percorrer todos os nós
        """
        result = []  # Lista Python que será retornada
        current = self.head  # Começa no primeiro nó

        # Percorre todos os nós até chegar no final (None)
        while current:
            result.append(current.data)  # Adiciona dado à lista
            current = current.next  # Avança para próximo nó

        return result


class TreeNode:
    """Nó para árvore binária de regiões

    Representa um nó em uma árvore binária para organização hierárquica de regiões geográficas.
    Cada nó armazena um valor e possui referências para seus filhos esquerdo e direito.
    """

    def __init__(self, value):
        """Inicializa um novo nó da árvore binária

        Args:
            value: O valor/região geográfica a ser armazenado no nó (pode ser string, coordenadas, etc.)
        """
        self.value = value  # Valor principal do nó (dado da região)
        self.left: Optional['TreeNode'] = None  # Subárvore esquerda (menores/região oeste)
        self.right: Optional['TreeNode'] = None  # Subárvore direita (maiores/região leste)



class BinarySearchTree:
    """Árvore binária de busca para regiões

    Implementa uma ABB (Árvore Binária de Busca) para armazenar e organizar regiões geográficas
    de forma eficiente, permitindo operações rápidas de inserção e busca.
    """

    def __init__(self):
        """Inicializa uma árvore vazia"""
        self.root: Optional[TreeNode] = None  # Raiz da árvore (nó inicial)

    def insert(self, value):
        """Insere novo valor na árvore mantendo as propriedades da ABB

        Args:
            value: Valor/região a ser inserido na árvore

        Complexidade:
            - Melhor caso: O(1) - árvore vazia
            - Caso médio: O(log n) - árvore balanceada
            - Pior caso: O(n) - árvore degenerada (lista encadeada)
        """
        if not self.root:
            self.root = TreeNode(value)  # Cria nó raiz se árvore estiver vazia
        else:
            self._insert_recursive(self.root, value)  # Insere recursivamente

    def _insert_recursive(self, node: TreeNode, value):
        """Método auxiliar recursivo para inserção

        Percorre a árvore comparando valores para encontrar a posição correta,
        mantendo a propriedade da ABB (left < parent < right).
        """
        if value < node.value:  # Valor menor -> vai para esquerda
            if node.left is None:
                node.left = TreeNode(value)  # Insere como filho esquerdo
            else:
                self._insert_recursive(node.left, value)  # Continua busca
        elif value > node.value:  # Valor maior -> vai para direita
            if node.right is None:
                node.right = TreeNode(value)  # Insere como filho direito
            else:
                self._insert_recursive(node.right, value)  # Continua busca
        # Se value == node.value, não faz nada (evita duplicatas)

    def search(self, value) -> bool:
        """Busca um valor na árvore
        Args:
            value: Valor a ser buscado

        Returns:
            bool: True se encontrado, False caso contrário

        Complexidade igual à inserção
        """
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node: Optional[TreeNode], value) -> bool:
        """Método auxiliar recursivo para busca

        Percorre a árvore comparando valores até encontrar o alvo
        ou chegar em um nó nulo (valor não encontrado).
        """
        if node is None:  # Caso base: valor não encontrado
            return False
        if node.value == value:  # Valor encontrado
            return True
        elif value < node.value:  # Busca na subárvore esquerda
            return self._search_recursive(node.left, value)
        else:  # Busca na subárvore direita
            return self._search_recursive(node.right, value)



class DroneTracker:
    """Rastreamento de atividades dos drones

    Sistema de registro e monitoramento de todas as ações realizadas por drones
    no sistema de monitoramento, mantendo um histórico completo para auditoria
    e análise posterior.
    """

    def __init__(self):
        """Inicializa o rastreador com histórico vazio"""
        self.historico = LinkedList()  # Usa LinkedList para armazenamento eficiente

    def registrar(self, drone_id: str, acao: str, ocorrencia_id: int = None):
        """Registra uma ação no histórico com timestamp

        Args:
            drone_id: Identificação única do drone
            acao: Descrição da ação realizada (ex: "decolagem", "patrulha")
            ocorrencia_id: ID opcional da ocorrência relacionada (se aplicável)

        Gera um registro com:
        - Timestamp automático
        - Identificação do drone
        - Tipo de ação
        - Ocorrência associada (quando relevante)
        """
        registro = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),  # Data/hora atual
            "drone": drone_id,
            "acao": acao,
            "ocorrencia": ocorrencia_id  # Pode ser None
        }
        self.historico.append(registro)  # Adiciona ao final da lista

    def obter_historico(self) -> List[dict]:
        """Retorna o histórico completo de ações

        Returns:
            List[dict]: Lista de todos registros na ordem cronológica
            Cada registro contém:
            - timestamp: Data/hora da ação
            - drone: ID do drone
            - acao: Tipo de ação
            - ocorrencia: ID relacionado ou None
        """
        return self.historico.to_list()  # Converte LinkedList para lista Python

    def registrar_acao(self, acao: str, local: list, detalhes: str = ""):
        """Método simplificado para registrar ações genéricas

        Args:
            acao: Tipo de ação genérica
            local: Coordenadas [latitude, longitude] onde ocorreu
            detalhes: Informações adicionais (opcional)

        Observação: Este método parece ter parâmetros inconsistentes com
        a implementação atual (não usa o 'local' fornecido)
        """
        self.registrar("Sistema", acao, detalhes)  # Registra como ação do sistema


# ==================== Sistema Principal ==============================



class SistemaEmergencia:
    """Sistema integrado de gerenciamento de emergências"""

    def __init__(self):
        """Inicializa todos os componentes do sistema"""

        # Heap para gerenciamento prioritário de ocorrências
        self.fila_prioritaria: List[Ocorrencia] = []  # Usa heapq para priorização

        # Sistema de monitoramento geográfico
        self.monitoramento = MapaMonitoramento(self)  # Mapa com integração ao sistema

        # Recursos disponíveis (usando deque para FIFO eficiente)
        self.equipes_disponiveis = deque([f"Equipe {i}" for i in range(1, 6)])  # 5 equipes
        self.drones_disponiveis = deque([f"Drone {i}" for i in range(1, 4)])  # 3 drones

        # Pilha para tarefas não urgentes
        self.tarefas_pendentes = []  # LIFO para tarefas secundárias

        # Sistema de registros históricos
        self.historico = LinkedList()  # Lista encadeada para histórico completo

        # Estrutura de organização geográfica
        self.regioes = BinarySearchTree()  # Árvore binária de busca para regiões
        for regiao in ["Amazônia", "Pantanal", "Cerrado",
                       "Mata Atlântica", "Caatinga", "Pampa"]:
            self.regioes.insert(regiao)  # Popula a árvore com biomas brasileiros

        # Rastreador de atividades de drones
        self.drone_tracker = DroneTracker()  # Monitoramento individual de drones
        self.drone_em_missao = False  # Flag de status

        # Subsistema de alertas
        self.sistema_alerta = SistemaAlerta(self)  # Gerenciador de notificações

        # Contatos de emergência padrão
        self._inicializar_contatos_padrao()  # Método privado para configuração inicial

    def _inicializar_contatos_padrao(self):
        """Inicializa os contatos de emergência padrão do sistema

        Adiciona automaticamente contatos essenciais para:
        - Autoridades competentes (cobertura nacional)
        - Lideranças comunitárias (regionais)
        """

        # Lista de contatos pré-configurados
        contatos_iniciais = [
            # Contato de autoridade nacional com ampla cobertura
            ContatoEmergencia(
                nome="Defesa Civil Nacional",
                email="defesacivil@nacional.gov",
                telefone="+1877904236",  # Número fictício
                tipo="autoridade",
                regioes=["Amazônia", "Pantanal", "Cerrado", "Mata Atlântica"]
            ),

            # Contato comunitário específico para a Amazônia
            ContatoEmergencia(
                nome="Comunidade Local - Amazônia",
                email="lideranca@amazonia.com",
                telefone="+18779804236",  # Número fictício
                tipo="comunidade",
                regioes=["Amazônia"]
            )
        ]

        # Adiciona cada contato ao sistema de alerta
        for contato in contatos_iniciais:
            self.sistema_alerta.adicionar_contato(contato)



    def registrar_ocorrencia(self, local: str, severidade: int, regiao: str) -> Ocorrencia:
        """Registra uma nova ocorrência no sistema de emergência"""

        # 1. Gestão de regiões (se região nova, cadastra automaticamente)
        if not self.regioes.search(regiao):
            self.regioes.insert(regiao)  # Adiciona à árvore de regiões
            self.historico.append(f"Nova região cadastrada: {regiao}")  # Audit

        # 2. Cria objeto da ocorrência (ID automático pelo Ocorrencia.__init__)
        nova_ocorrencia = Ocorrencia(
            id=0,  # Valor temporário (geralmente sobrescrito pelo ORM/banco)
            local=local,
            severidade=severidade,
            regiao=regiao
        )

        # 3. Adiciona à fila prioritária (heap)
        heapq.heappush(self.fila_prioritaria, nova_ocorrencia)

        # 4. Registro histórico
        self.historico.append(f"Nova ocorrência ID {nova_ocorrencia.id}")

        # 5. Cria tarefa secundária (relatório)
        self.tarefas_pendentes.append(f"Gerar relatório para {regiao}")

        return nova_ocorrencia

    def enviar_drone(self, ocorrencia: Ocorrencia) -> Dict:
        """Gerencia o envio de drones para verificação de ocorrências com simulação de missão"""

        # 1. Verificação de disponibilidade
        if not self.drones_disponiveis or self.drone_em_missao:
            return {
                "status": "error",
                "message": "Nenhum drone disponível no momento",
                "drone": None
            }

        # 2. Alocação de recursos
        self.drone_em_missao = True  # Bloqueia outros envios
        drone = self.drones_disponiveis.popleft()  # Remove drone da fila
        ocorrencia.status = "Em verificação"  # Atualiza estado

        # 3. Registro no histórico
        self.drone_tracker.registrar(
            drone_id=drone,
            acao="Missão iniciada",
            ocorrencia_id=ocorrencia.id
        )

        # 4. Alerta preliminar para casos graves
        if ocorrencia.severidade >= 4:
            self.sistema_alerta.enviar_alertas(
                ocorrencia=ocorrencia,

            )

        # 5. Função de simulação de missão (executada em thread separada)
        def simular_missao():
            """Simula o processo completo de verificação pelo drone"""
            try:
                # Simula tempo de voo (3 segundos)
                time.sleep(3)

                # 80% de chance de confirmar fogo (para teste)
                ocorrencia.fogo_confirmado = random.random() > 0.2

                if ocorrencia.fogo_confirmado:
                    # Atualiza status e registra confirmação
                    ocorrencia.status = "Fogo ativo"
                    ocorrencia.tempo_inicio_fogo = time.time()

                    # Eleva severidade mínima para 4 (emergência)
                    ocorrencia.severidade = max(ocorrencia.severidade, 4)

                    self.drone_tracker.registrar(
                        drone,
                        "Incêndio confirmado",
                        ocorrencia.id
                    )

                    # Dispara alertas completos
                    self.sistema_alerta.enviar_alertas(
                        ocorrencia,
                        'alerta_confirmado'
                    )

                    # Processa tarefas pendentes (LIFO)
                    while self.tarefas_pendentes:
                        tarefa = self.tarefas_pendentes.pop()
                        self.historico.append(
                            f"Tarefa concluída: {tarefa} "
                            f"para ocorrência {ocorrencia.id}"
                        )
                else:
                    # Caso sem fogo detectado
                    ocorrencia.status = "Verificado"
                    self.drone_tracker.registrar(
                        drone,
                        "Nenhum incêndio detectado",
                        ocorrencia.id
                    )

            finally:
                # 6. Liberação do drone (garantido pelo finally)
                self.drones_disponiveis.append(drone)
                self.drone_em_missao = False
                self.historico.append(
                    f"Drone {drone} retornou à base"
                )

        # Inicia simulação em thread paralela
        threading.Thread(
            target=simular_missao,
            daemon=True
        ).start()

        # 7. Retorno imediato
        return {
            "status": "success",
            "message": f"Drone {drone} despachado com sucesso",
            "drone": drone
        }

    def verificar_fogos_apagados(self):
        # Loop infinito que ficará verificando constantemente
        while True:
            try:
                # Pausa a execução por 10 segundos entre cada verificação
                time.sleep(10)  # Verifica a cada 10 segundos

                # Percorre todas as ocorrências da fila prioritária
                for oc in self.fila_prioritaria:
                    # Verifica se o objeto tem o atributo 'status', se o status é "Fogo ativo"
                    # e se um valor aleatório (entre 0 e 1) for maior que 0.4 (ou seja, 60% de chance)
                    if (hasattr(oc, 'status') and
                            oc.status == "Fogo ativo" and
                            random.random() > 0.4):
                        # Marca que o fogo foi apagado
                        oc.fogo_apagado = True
                        # Atualiza o status da ocorrência para "Fogo apagado"
                        oc.status = "Fogo apagado"
                        # Define a severidade como 1 (mínima, pois o fogo já está apagado)
                        oc.severidade = 1

                        # Registra essa ação no rastreador de drones
                        self.drone_tracker.registrar(
                            drone_id="Sistema",  # Ação realizada pelo sistema automaticamente
                            acao=f"Fogo apagado na ocorrência {oc.id}",  # Mensagem da ação
                            ocorrencia_id=oc.id  # ID da ocorrência tratada
                        )

            # Se ocorrer qualquer erro durante a execução do bloco try
            except Exception as e:
                # Exibe a mensagem de erro
                print(f"Erro na verificação de fogos apagados: {str(e)}")
                # Aguarda 30 segundos antes de tentar novamente
                time.sleep(30)

    def verificar_drones_automaticamente(self):
        """Verifica automaticamente se precisa enviar drones"""

        # Inicia um loop infinito que verifica a cada 5 segundos
        while True:
            time.sleep(5)  # Pausa de 5 segundos entre as verificações

            try:
                # Verifica se há drones disponíveis e se há ocorrências na fila prioritária
                if self.drones_disponiveis and self.fila_prioritaria:

                    # Filtra apenas as ocorrências com severidade alta e status relevante
                    ocorrencias = [oc for oc in self.fila_prioritaria
                                   if hasattr(oc, 'severidade') and
                                   hasattr(oc, 'status') and
                                   oc.severidade > 3 and  # Severidade maior que 3 é considerada alta
                                   oc.status in ["Pendente", "Fogo ativo"]]  # Ocorrências ainda não resolvidas

                    if ocorrencias:
                        # Ordena as ocorrências por severidade (do maior para o menor)
                        ocorrencias.sort(key=lambda x: x.severidade, reverse=True)

                        # Envia um drone para a ocorrência mais grave (primeira da lista)
                        self.enviar_drone(ocorrencias[0])

            except Exception as e:
                # Em caso de erro, imprime a mensagem
                print(f"Erro na verificação automática de drones: {str(e)}")
                # Aguarda 10 segundos antes de tentar novamente
                time.sleep(10)


    def adicionar_marcador(self, lat, lon, cor='red', popup=''):
        # Tenta converter os valores de latitude e longitude para float
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            # Caso não consiga converter (por exemplo, valores inválidos), exibe erro e retorna
            print(f"Coordenadas inválidas: lat={lat}, lon={lon}")
            return

        # Resto do método para criar o marcador
        if cor == 'red':
            # Se a cor for vermelha, cria um marcador com essas coordenadas no mapa
            # A parte "..." deve ser substituída pela criação real do marcador com Folium
            folium.Marker(
                location=[lat, lon],  # Coordenadas do marcador
                popup=popup,  # Texto que aparece ao clicar no marcador
                icon=folium.Icon(color='red')  # Ícone com cor vermelha
            ).add_to(self.mapa)  # Adiciona o marcador ao mapa armazenado em self.mapa

    def atender_ocorrencia(self):
        """Atende a próxima ocorrência na fila prioritária."""

        # Se a fila estiver vazia, não há nada para atender
        if not self.fila_prioritaria:
            return None

        try:
            # Remove a primeira ocorrência da fila (a mais prioritária)
            ocorrencia = self.fila_prioritaria.pop(0)

            # Atualiza o status da ocorrência para indicar que o fogo foi apagado
            ocorrencia.status = "Fogo apagado"
            ocorrencia.fogo_apagado = True
            ocorrencia.tempo_fim_fogo = time.time()  # Marca o tempo em que o fogo foi apagado

            # Cria um dicionário de registro histórico do atendimento
            registro = {
                "tipo": "Atendimento",  # Tipo de ação
                "descricao": f"Fogo apagado em {ocorrencia.regiao}",  # Descrição do evento
                "severidade": ocorrencia.severidade,  # Nível de severidade do incêndio
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),  # Data e hora atual formatada
                "local": ocorrencia.local  # Local onde o fogo foi apagado
            }

            # Adiciona o registro ao histórico do sistema
            self.historico.append(registro)

            # Registra a ação no rastreador de drones (mesmo que feita pela equipe)
            self.drone_tracker.registrar(
                drone_id="Equipe",  # Ação realizada pela equipe (não por drone automático)
                acao="Atendimento",
                ocorrencia_id=ocorrencia.id
            )

            # Retorna uma mensagem com os detalhes do atendimento
            return {
                "mensagem": f"Fogo em {ocorrencia.regiao} foi apagado",
                "detalhes": {
                    "severidade": ocorrencia.severidade,
                    "tempo_ativo": f"{(ocorrencia.tempo_fim_fogo - ocorrencia.tempo_inicio_fogo):.1f}s"
                    if ocorrencia.tempo_inicio_fogo > 0 else "0s",
                    "local": ocorrencia.local
                }
            }

        except Exception as e:
            # Em caso de erro, imprime a mensagem e retorna None
            print(f"Erro ao atender ocorrência: {str(e)}")
            return None

    def simular_ocorrencias(self, quantidade=1):
        """Simula novas ocorrências de incêndio"""

        # Lista de regiões brasileiras onde o incêndio pode ocorrer
        regioes = ["Amazônia", "Cerrado", "Mata Atlântica", "Caatinga", "Pampa"]

        # Gera o número de ocorrências definido pelo parâmetro 'quantidade'
        for _ in range(quantidade):
            try:
                # Gera latitude e longitude dentro dos limites aproximados do Brasil
                lat = random.uniform(-33.75, 5.27)  # Sul ao Norte do Brasil
                lon = random.uniform(-73.99, -34.79)  # Oeste ao Leste do Brasil

                # Cria uma nova ocorrência de incêndio
                nova_ocorrencia = Ocorrencia(
                    prioridade=0,  # A prioridade será ajustada automaticamente no __post_init__
                    local=[lat, lon],  # Coordenadas geográficas da ocorrência
                    severidade=random.randint(1, 5),  # Severidade aleatória de 1 (leve) a 5 (grave)
                    regiao=random.choice(regioes)  # Seleciona uma região aleatória do Brasil
                )

                # Adiciona a nova ocorrência à fila prioritária
                self.fila_prioritaria.append(nova_ocorrencia)

                # Imprime uma mensagem informando que a ocorrência foi simulada
                print(f"Ocorrência {nova_ocorrencia.id} simulada na região {nova_ocorrencia.regiao}")

            except Exception as e:
                # Caso ocorra algum erro durante a simulação, exibe a mensagem de erro
                print(f"Erro ao simular ocorrência: {str(e)}")

        # Observação: Pode ser chamada dentro de uma thread para gerar ocorrências de forma periódica

    def simular_ocorrencias_periodicamente(self):
        """Simula ocorrências periodicamente em segundo plano"""

        # Loop infinito para simular constantemente
        while True:
            try:
                time.sleep(5)  # Espera 5 segundos entre uma simulação e outra

                # Simula uma nova ocorrência de incêndio
                self.simular_ocorrencias(1)

                # Se a fila tiver pelo menos uma ocorrência, pega a mais recente
                if self.fila_prioritaria:
                    ultima_ocorrencia = self.fila_prioritaria[-1]

                    # Cria uma mensagem de log mais informativa com ID, região e severidade
                    log_msg = (
                        f"[{time.strftime('%H:%M:%S')}] "
                        f"Ocorrência simulada - ID: {getattr(ultima_ocorrencia, 'id', 'N/A')} | "
                        f"Região: {getattr(ultima_ocorrencia, 'regiao', 'N/A')} | "
                        f"Severidade: {getattr(ultima_ocorrencia, 'severidade', 'N/A')}"
                    )
                    print(log_msg)
                else:
                    # Caso a fila esteja vazia após a simulação (pouco provável), exibe alerta
                    print(f"[{time.strftime('%H:%M:%S')}] Tentativa de simulação falhou - fila vazia")

            except Exception as e:
                # Se ocorrer algum erro durante a simulação, exibe a mensagem de erro com horário
                print(f"[{time.strftime('%H:%M:%S')}] Erro na simulação periódica: {str(e)}")
                time.sleep(10)  # Espera 10 segundos antes de tentar novamente após erro

    def iniciar_servicos(self):
        """Inicia threads de serviços em segundo plano"""

        # Lista de threads para verificação automática de drones e verificação de fogos apagados
        threads = [
            threading.Thread(
                target=self.verificar_drones_automaticamente,  # Verifica se há drones disponíveis para enviar
                daemon=True,  # Thread daemon: encerra junto com o programa principal
                name="drone_checker"  # Nome da thread para facilitar identificação
            ),
            threading.Thread(
                target=self.verificar_fogos_apagados,  # Verifica se o fogo foi apagado automaticamente
                daemon=True,
                name="fire_checker"
            ),
        ]

        # Cria e inicia uma thread separada para simular ocorrências periodicamente
        threading.Thread(
            target=self.simular_ocorrencias_periodicamente,
            daemon=True,
            name="simulador_ocorrencias"
        ).start()

        # Inicia todas as threads listadas acima
        for t in threads:
            t.start()
            print(f"Iniciada thread {t.name}")  # Mensagem de log indicando que o serviço começou






