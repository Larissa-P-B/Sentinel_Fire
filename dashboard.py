#Nome: Larissa Pereira Biusse
#RM: 564068

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configurações
BACKEND_URL = "http://localhost:5000"
st.set_page_config(
    layout="wide",
    page_title="Sentinel Fire",
    page_icon="🔥"
)

# Inicializa variável de estado para controlar atualizações
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Função para forçar atualização da página
def atualizar_mapa():
    st.session_state.last_update = datetime.now()
    st.rerun()

# Função genérica para chamadas ao backend
def chamar_backend(endpoint, method='get', json_data=None):
    url = f"{BACKEND_URL}/{endpoint}"
    try:
        if method == 'get':
            response = requests.get(url)
        elif method == 'post':
            response = requests.post(url, json=json_data)
        else:
            return None, "Método HTTP não suportado"
        if response.ok:
            return response.json(), None
        else:
            return None, f"Erro: {response.status_code}"
    except Exception as e:
        return None, str(e)

# Funções para buscar dados da API com cache
@st.cache_data(ttl=10)
def fetch_ocorrencias():
    data, erro = chamar_backend("ocorrencias")
    return data["ocorrencias"] if data and "ocorrencias" in data else []

@st.cache_data(ttl=10)
def fetch_historico_drones():
    data, erro = chamar_backend("historico_drones")
    return data if data else {"historico": [], "total_acoes": 0}

# Layout do título com logo
col1, col2 = st.columns([1, 10])
with col1:
    st.image("templates/logo.png", width=120)  # Ajuste na barra invertida para barra normal
with col2:
    st.title("Sentinel Fire Monitoring")

# Sidebar com controles e informações
with st.sidebar:
    st.header("Controles")

    if st.button("🔄 Atualizar Dados", on_click=atualizar_mapa):
        pass

    st.write(f"Última atualização: {st.session_state.last_update.strftime('%H:%M:%S')}")

    if st.button("Simular Ocorrência"):
        _, erro = chamar_backend("simular", method="post", json_data={"quantidade": 1})
        if erro:
            st.error(f"Erro ao simular ocorrência: {erro}")
        else:
            st.success("Ocorrência simulada com sucesso!")
            atualizar_mapa()

    if st.button("Atender Ocorrência"):
        _, erro = chamar_backend("atender", method="post")
        if erro:
            st.error(f"Erro ao atender ocorrência: {erro}")
        else:
            st.success("Ocorrência atendida com sucesso!")
            atualizar_mapa()

    # Mostrar informações resumidas
    data = fetch_ocorrencias()
    df = pd.DataFrame(data)
    if not df.empty:
        st.header("Resumo")
        st.metric("Focos Ativos", len(df[df['status'] == "Fogo ativo"]))
        st.metric("Máxima Severidade", df['severidade'].max())

# Mapa principal com iframe
iframe_src = f"{BACKEND_URL}/mapa?{st.session_state.last_update.timestamp()}"
st.markdown(f"""
<div style="width:100%; height:600px; margin-top:20px;">
    <iframe src="{iframe_src}" width="100%" height="100%" frameborder="0"></iframe>
</div>
""", unsafe_allow_html=True)

# Legenda do mapa
st.markdown("""
**Legenda do Mapa:**
- 🔴 Marcador Vermelho: Fogo ativo
- 🟢 Marcador Verde: Fogo apagado
- 🔵 Marcador Azul: Equipe em ação
""")

# Seção do histórico de drones
st.header("🛸 Histórico de Ações dos Drones")
drones_data = fetch_historico_drones()
df_drones = pd.DataFrame(drones_data.get("historico", []))

if not df_drones.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Ações", drones_data.get("total_acoes", 0))
    with col2:
        if 'acao' in df_drones.columns:
            st.metric("Última Ação", df_drones.iloc[-1]["acao"])
        else:
            st.metric("Última Ação", "N/A")
    st.dataframe(df_drones)
else:
    st.warning("Nenhuma ação de drone registrada")

# Lista de ocorrências detalhada (opcional)
if st.checkbox("Mostrar lista de ocorrências detalhada"):
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("Nenhuma ocorrência ativa no momento")

# Seção de focos apagados
st.header("🔥 Histórico de Focos Apagados")
focos_apagados = [oc for oc in data if oc.get('status') == "Fogo apagado"]
if focos_apagados:
    st.write(f"Total de focos apagados: {len(focos_apagados)}")
    st.dataframe(pd.DataFrame(focos_apagados))
else:
    st.info("Nenhum fogo apagado recentemente")

# Rodapé com última atualização do sistema
st.markdown("---")
st.markdown(f"📅 Última atualização do sistema: {datetime.now().strftime('%H:%M:%S')}")



