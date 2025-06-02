# 🔥 Sentinel Fire – Sistema de Gerenciamento de Queimadas

## Introdução:


O Sentinel Fire é um sistema integrado de monitoramento e combate a 
focos de incêndio florestal, desenvolvido com o objetivo de aumentar a 
eficiência na detecção precoce, monitoramento em tempo real e resposta 
rápida a ocorrências de fogo em áreas florestais. O sistema utiliza 
tecnologias modernas de coleta de dados, visualização geográfica, 
controle remoto por drones e integração de APIs para fornecer uma 
solução completa para órgãos ambientais e equipes de combate a incêndios.


## Objetivos do Projeto:
 
- Detectar e monitorar focos de incêndio florestal em tempo real.

- Fornecer uma interface visual e intuitiva para acompanhamento das ocorrências.

- Controlar remotamente ações de drones que atuam no combate e monitoramento dos incêndios.

- Facilitar a tomada de decisão com informações precisas sobre severidade e status das ocorrências.

- Registrar histórico de ações para análise e melhoria contínua das operações.


## Arquitetura do Sistema
### O Sentinel Fire é composto por três camadas principais:

### 1. Backend:Desenvolvido em Flask (Python), responsável por:

- Gerenciar as ocorrências de incêndio, seu status e severidade.

- Controlar a simulação e atendimento das ocorrências.

- Registrar e disponibilizar histórico das ações dos drones.

- Servir o mapa interativo com os focos de incêndio e equipes em ação.

- Expor uma API REST para consumo do frontend.


## 🌐 URL Base
```
http://localhost:5000/
```

---

## 📄 Endpoints

### `GET /`

* **Descrição**: Página inicial da API.
* **Resposta**:

  ```
  Sentinel Fire
  Sistema de Gerenciamento de Queimadas
  ```

---

### `GET /ocorrencias`

* **Descrição**: Lista todas as ocorrências ativas.
* **Resposta**:

```json
{
  "ocorrencias": [
    {
      "id": 1,
      "local": [latitude, longitude],
      "severidade": 4,
      "regiao": "Amazônia",
      "status": "Fogo ativo",
      "fogo_confirmado": true,
      "fogo_apagado": false,
      "tempo_ativo": "12.3s"
    }
  ]
}
```

---

### `GET /historico`

* **Descrição**: Retorna o histórico de ocorrências resolvidas.

---

### `GET /historico_drones`

* **Descrição**: Retorna as ações realizadas pelos drones.
* **Resposta**:

```json
{
  "historico": [
    {"acao": "Apagar fogo", "local": "...", "timestamp": "..."}
  ],
  "total_acoes": 3
}
```

---

### `POST /simular`

* **Descrição**: Simula novas ocorrências.
* **Corpo JSON**:

```json
{ "quantidade": 1 }
```

---

### `POST /atender`

* **Descrição**: Atende a ocorrência mais urgente.
* **Resposta (sucesso)**:

```json
{
  "status": "success",
  "resultado": "Ocorrência atendida..."
}
```

* **Resposta (erro)**:

```json
{
  "status": "error",
  "message": "Nenhuma ocorrência para atender"
}
```

---

### `GET /contatos`

* **Descrição**: Lista os contatos de emergência cadastrados.

---

### `POST /contatos/adicionar`

* **Descrição**: Adiciona novo contato.
* **Corpo JSON**:

```json
{
  "nome": "Nome",
  "email": "email@exemplo.com",
  "telefone": "000000000",
  "tipo": "Autoridade",
  "regioes": ["Amazônia"]
}
```

---

### `POST /testar_sms`

* **Descrição**: Envia um alerta de teste para contatos da região.
* **Corpo JSON (opcional)**:

```json
{
  "local": "Teste",
  "regiao": "Amazônia"
}
```

---

### `GET /mapa`

* **Descrição**: Retorna mapa interativo com ocorrências.
* 🔴 Fogo ativo
* 🟢 Fogo apagado
* **Resposta**: HTML com mapa interativo (gerado com Folium).

---

## 🔄 Simulação Periódica

O sistema simula automaticamente uma nova ocorrência a cada 5 segundos, em thread separada.

---

## 🚀 Inicialização

Acesse:

* API: [http://localhost:5000/](http://localhost:5000/)
* Mapa: [http://localhost:5000/mapa](http://localhost:5000/mapa)

---


### 2. Frontend: Desenvolvido com Streamlit, oferece:

--- 

🚀 Execução
Execute o painel com:
```bash
#gitbash terminal
streamlit run dashboard.py

#após acessar http://localhost:8501 

```
Certifique-se de que o backend Flask esteja rodando em http://localhost:5000 antes de iniciar o Streamlit.


- Dashboard intuitivo para visualização em tempo real dos focos de incêndio.

- Visualização do mapa interativo com marcadores que indicam fogo ativo, fogo apagado e equipes em ação.

- Controle de simulação, atendimento de ocorrências e atualização dos dados.

- Exibição de métricas importantes como focos ativos, severidade máxima e histórico de ações dos drones.

### 3. Integração e Visualização Geográfica:
- Utiliza o backend para servir um mapa interativo (ex: Folium ou outra biblioteca de mapas), incorporado no frontend via iframe.

- Marcadores coloridos indicam o status das ocorrências para facilitar o entendimento rápido do cenário.

### Funcionalidades Principais: 

**Monitoramento em tempo real**: Atualização automática do mapa com dados das ocorrências e ações dos drones.

**Simulação de incêndios:** Permite simular novas ocorrências para testes e treinamentos.

**Atendimento de ocorrências:** Registrar quando uma ocorrência é atendida e removê-la da lista de focos ativos.

**Histórico de drones:** Visualizar ações realizadas pelos drones, com dados registrados para análise posterior.

**Relatórios e métricas:** Apresentação clara de métricas de focos ativos e severidade dos incêndios.

**Atualização manual:** Botão para atualização dos dados a qualquer momento, garantindo controle pelo usuário.


### Tecnologias Utilizadas:
- Python: Linguagem principal do backend e do frontend.

- Flask: Framework web para criação da API REST e backend.

- Streamlit: Biblioteca para criação do dashboard web interativo.

- Requests: Comunicação HTTP entre frontend e backend.

- Pandas: Manipulação e apresentação de dados tabulares.

- Folium (ou similar): Geração do mapa interativo para visualização dos focos.

## Aplicação de Estruturas de Dados no Projeto (Fila, Pilha, Lista Ligada, Árvore, Heap)

### 1. Heap (Fila Prioritária com Prioridade)Uso: 
**self.fila_prioritaria** (lista usada com heapq para manter ocorrências ordenadas pela severidade/prioridade).

- Local no código:
```
self.fila_prioritaria: List[Ocorrencia] = []
```
Utilizada para armazenar as ocorrências de incêndio de forma que as de maior severidade sejam atendidas primeiro.
Inserção com **heapq.heappush()** no método registrar_ocorrencia.
- Função no sistema:
Gerenciar as ocorrências para atendimento baseado na prioridade, garantindo que os incêndios mais graves sejam tratados primeiro.

### 2. Fila (Deque para Gerenciar Disponibilidade)Uso:

**self.equipes_disponiveis = deque([...])**

**self.drones_disponiveis = deque([...])**

- Local no código:
```python
from collections import deque
...
self.equipes_disponiveis = deque([f"Equipe {i}" for i in range(1, 6)])
self.drones_disponiveis = deque([f"Drone {i}" for i in range(1, 4)])
```
- Função no sistema:
Controlar as equipes e drones disponíveis de forma FIFO — o primeiro que fica disponível será o primeiro a ser usado para atendimento.


### 3. Pilha (Lista Python como Pilha para Tarefas Pendentes)Uso:

**self.tarefas_pendentes** como uma lista Python normal usada como pilha (LIFO).

- Local no código:
```python
self.tarefas_pendentes = []
```
  - Adiciona tarefas com append().

  - Remove tarefas com pop() no método enviar_drone, ao concluir as tarefas da pilha.

- Função no sistema:
Controlar tarefas secundárias relacionadas, como geração de relatórios, processadas na ordem inversa à que foram criadas.

### 4. Lista Ligada (Classe LinkedList e Node para Histórico)Uso:

**self.historico = LinkedList()**

- Classe personalizada para armazenar o histórico de ações de forma encadeada.

- Local no código:

```python
class Node:
...
class LinkedList:
...
self.historico = LinkedList()
```
- Função no sistema:
Registrar o histórico das ações, como registros de ocorrências, tarefas e atendimento, permitindo consulta sequencial do histórico com método to_list().

### 5. Árvore Binária de Busca (Classe BinarySearchTree para Regiões Monitoradas)Uso:

**self.regioes = BinarySearchTree()** para armazenar e buscar regiões monitoradas.

- Local no código:
```python
class TreeNode:
...
class BinarySearchTree:
...
self.regioes = BinarySearchTree()
for regiao in ["Amazônia", "Pantanal", "Cerrado", "Mata Atlântica","Caatinga", "Pampa"]:
    self.regioes.insert(regiao)
```      
- Função no sistema:
Facilitar a busca rápida se uma região já está cadastrada para evitar duplicação e permitir a inserção de novas regiões quando ocorrem ocorrências em áreas novas.



