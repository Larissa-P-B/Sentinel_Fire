# Sistema Integrado de Combate a Queimadas: 
## Funcionalidades:

Este código implementa um sistema tecnológico completo para detecção,
monitoramento e resposta a queimadas, utilizando estruturas de dados eficientes,
IA, drones e automação. 
Abaixo estão as principais funcionalidades:

**Módulo de Monitoramento (SensorSimulator)**
- Simulação de sensores ambientais (térmico, temperatura, umidade, CO²).

- Geração de imagens térmicas simulando focos de incêndio.

- Dados dinâmicos: Valores variam conforme a presença ou ausência de fogo.

**Módulo de Detecção por IA (FireDetectionModel)**

- Rede Neural Convolucional (CNN) para análise de imagens térmicas.
- Classificação binária: Determina se há fogo ou não.
- Processamento em tempo real: Analisa imagens e retorna probabilidade de incêndio.

**Estruturas de Dados para Gestão**

1. **Lista Ligada (LinkedList)**
   
   - Armazena histórico de ações (registros de drones, equipes, alertas).

   - Permite acesso sequencial para relatórios.

2. **Árvore Binária (BinarySearchTree)**
    
   - Regiões monitoradas (Amazônia, Pantanal, Cerrado, etc.).

   - Busca eficiente para verificar se uma área está no sistema.

3. **Heap Prioritário (fila_prioritaria)**

    - Ordena ocorrências por severidade (quanto maior a gravidade, mais rápido é atendido).

    - Prioridade dobrada para regiões críticas (Amazônia, Pantanal).

4. **Fila (deque) para Recursos**

    - Equipes de combate: Gerencia disponibilidade.

    - Drones: Atribui missões de verificação.

5. **Pilha (tarefas_pendentes)**

    - Tarefas secundárias (gerar relatórios, enviar confirmações).

6. **Sistema de Rastreamento (DroneTracker)**

    - Registra todas as ações dos drones (decolagem, confirmação de fogo, retorno).

    - Histórico completo para auditoria e análise.

7. **Sistema de Alerta (SistemaAlerta)**

- Notificações Automáticas 
  - E-mail e SMS para autoridades e comunidades locais.

  - Templates personalizados (alerta crítico, confirmação, aviso preliminar).

- Critérios de Envio

  - SMS apenas para severidade ≥ 4 (emergências graves).

  - Contatos segmentados por região (ex.: Defesa Civil recebe todos os alertas; comunidades locais só da sua área).

8. **Lógica Principal (SistemaEmergencia)**

- Fluxo Automatizado

    - Registro de Ocorrências (com severidade e localização).

    - Priorização via Heap (atendimento das mais graves primeiro).

    - Envio de Drones para confirmação.

    - Alerta Automático se fogo for confirmado.

9. **Atribuição de Equipes para combate.**

- Processos em Segundo Plano

    - Verificação periódica de fogos apagados.

    - Missões automáticas de drones (se severidade alta).

    - Simulação contínua de ocorrências (para testes).


10. **API Flask (Interface Web)**

- Endpoints Disponíveis:


- methods=['GET'] /ocorrencias: Lista todas as ocorrências ativas.
```
{
	"ocorrencias": [
		{
			"fogo_apagado": false,
			"fogo_confirmado": false,
			"id": 9140,
			"local": "Área 39",
			"regiao": "Amazônia",
			"severidade": 5,
			"status": "Verificado",
			"tempo_ativo": "78.3s"
		},
		{
			"fogo_apagado": false,
			"fogo_confirmado": false,
			"id": 7475,
			"local": "Área 2",
			"regiao": "Amazônia",
			"severidade": 5,
			"status": "Verificado",
			"tempo_ativo": "Não ativo"
		},
```

- methods=['GET'] /historico: Mostra o histórico de ações.
```
{
	"historico": [
		"Novo contato adicionado: Defesa Civil Nacional",
		"Novo contato adicionado: Comunidade Local - Amazônia",
		"Nova ocorrência ID 7902",
		"Nova ocorrência ID 9025",
```

- methods=['GET'] /historico_drones: Registros detalhados de drones.
```
{
	"historico": [
		"11:31:54 - Drone 1: Enviado para verificação (Ocorrência 9025)",
		"11:31:56 - Drone 1: Nenhum fogo detectado (Ocorrência 9025)",
		"11:31:59 - Drone 2: Enviado para verificação (Ocorrência 9140)",
		"11:32:01 - Drone 2: Fogo confirmado (Ocorrência 9140)",
		"11:32:02 - Drone 3: Enviado para verificação (Ocorrência 9140)",
		"11:32:04 - Drone 3: Nenhum fogo detectado (Ocorrência 9140)",
		"11:32:04 - Drone 1: Enviado para verificação (Ocorrência 7475)",
		"11:32:06 - Drone 1: Nenhum fogo detectado (Ocorrência 7475)",
		"11:32:08 - Drone 2: Enviado para verificação (Ocorrência 8292)",
		"11:32:10 - Drone 2: Fogo confirmado (Ocorrência 8292)",
```

- methods=['POST'] /simular: Gera ocorrências de teste.
```
{
	"msg": "Nova ocorrência simulada",
	"status": "success"
}
```

- methods=['POST'] /atender: Designa equipes para atendimento.
```
{
	"resultado": "Equipe 1 designada para ocorrência 6892"
}
```

- methods=['GET'] /contatos: Gerencia lista de contatos para alertas.
```
{
	"contatos": [
		{
			"email": "defesacivil@nacional.gov",
			"nome": "Defesa Civil Nacional",
			"regioes": [
				"Amazônia",
				"Pantanal",
				"Cerrado",
				"Mata Atlântica"
			],
			"telefone": "+18777804236",
			"tipo": "autoridade"
		},
		{
			"email": "lideranca@amazonia.com",
			"nome": "Comunidade Local - Amazônia",
			"regioes": [
				"Amazônia"
			],
			"telefone": "+18777804236",
			"tipo": "comunidade"
		}
	]
}
```

- methods=['POST'] /testar_sms: Dispara SMS de teste.
```
{
	"message": "SMS de teste enviado para contatos da região",
	"status": "success"
}
```

8. **Funcionalidades Adicionais**

- Threads em paralelo: Processamento assíncrono (drones, alertas, simulações).

- Integração com serviços externos:

- SMTP (envio de e-mails).

- Twilio API (envio de SMS).

- Dashboard via Flask: Visualização em tempo real.

### **Tecnologias Utilizadas**

Python (POO, estruturas de dados).
    
TensorFlow/Keras (IA para detecção de fogo).
    
OpenCV (processamento de imagens térmicas).
    
Flask (API REST).
    
Twilio (SMS).
    
SMTPLib (e-mails).

Objetivo Principal:

### **Automatizar o combate a queimadas com:**

✔ Resposta rápida (drones + equipes).

✔ Previsão inteligente (dados históricos + IA).

✔ Fiscalização eficiente (rastreamento + relatórios).

Este sistema é escalável e pode ser integrado a satélites, bancos de dados climáticos e órgãos governamentais.