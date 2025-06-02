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

# Variável de estado para controlar atualizações
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Função para forçar atualização
def atualizar_mapa():
    st.session_state.last_update = datetime.now()
    st.rerun()

# Funções para buscar dados da API
@st.cache_data(ttl=10)
def fetch_ocorrencias():
    try:
        response = requests.get(f"{BACKEND_URL}/ocorrencias")
        return response.json()["ocorrencias"] if response.ok else []
    except:
        return []

@st.cache_data(ttl=10)
def fetch_historico_drones():
    try:
        response = requests.get(f"{BACKEND_URL}/historico_drones")
        return response.json() if response.ok else {"historico": [], "total_acoes": 0}
    except:
        return {"historico": [], "total_acoes": 0}

# Layout do título com logo
col1, col2 = st.columns([1, 10])
with col1:
    st.image("templates\logo.png", width=120 )# Você pode substituir por seu próprio logo
with col2:
    st.title("Sentinel Fire Monitoring")


# Sidebar com controles e informações
with st.sidebar:
    st.header("Controles")

    # Botão para atualizar o mapa
    if st.button("🔄 Atualizar Dados", on_click=atualizar_mapa):
        pass

    st.write(f"Última atualização: {st.session_state.last_update.strftime('%H:%M:%S')}")

    if st.button("Simular Ocorrência"):
        try:
            response = requests.post(f"{BACKEND_URL}/simular", json={"quantidade": 1})
            if response.ok:
                st.success("Ocorrência simulada com sucesso!")
                atualizar_mapa()
            else:
                st.error("Erro ao simular ocorrência")
        except:
            st.error("Não foi possível conectar ao servidor")

    if st.button("Atender Ocorrência"):
        try:
            response = requests.post(f"{BACKEND_URL}/atender")
            if response.ok:
                st.success("Ocorrência atendida com sucesso!")
                atualizar_mapa()
            else:
                st.error("Nenhuma ocorrência para atender")
        except:
            st.error("Não foi possível conectar ao servidor")

    # Mostrar informações resumidas
    data = fetch_ocorrencias()
    df = pd.DataFrame(data)
    if not df.empty:
        st.header("Resumo")
        st.metric("Focos Ativos", len(df[df['status'] == "Fogo ativo"]))
        st.metric("Máxima Severidade", df['severidade'].max())

# Mapa principal
st.markdown(f"""
<div style="width:100%; height:600px; margin-top:20px;">
    <iframe src="{BACKEND_URL}/mapa?{st.session_state.last_update.timestamp()}" 
            width="100%" height="100%"></iframe>
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
df_drones = pd.DataFrame(drones_data["historico"])

st.write("Última linha do DataFrame:", df_drones.iloc[-1] if not df_drones.empty else "DataFrame vazio")
st.write("Dados recebidos do histórico:", drones_data["historico"])
drones_data = fetch_historico_drones()
if not df_drones.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Ações", drones_data["total_acoes"])
    with col2:
        if 'acao' in df_drones.columns:
            st.metric("Última Ação", df_drones.iloc[-1]["acao"])
        else:
            st.metric("Última Ação", "N/A")
    st.dataframe(df_drones)
else:
    st.warning("Nenhuma ação de drone registrada")

# Lista de ocorrências (opcional)
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

# Rodapé
st.markdown("---")
st.markdown(f"📅 Última atualização do sistema: {datetime.now().strftime('%H:%M:%S')}")

#streamlit run dashboard.py


