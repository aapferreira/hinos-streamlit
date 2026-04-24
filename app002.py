import streamlit as st
from pathlib import Path

# Para drag-and-drop real
try:
    from streamlit_sortables import sort_items
    SORTABLE_AVAILABLE = True
except ImportError:
    SORTABLE_AVAILABLE = False

# Configuração da página
st.set_page_config(page_title="Hinos", layout="wide")

HINOS_DIR = Path("hinos")

# -----------------------------
# Funções
# -----------------------------

def carregar_hinos():
    hinos = {}
    if not HINOS_DIR.exists():
        return hinos

    for arquivo in sorted(HINOS_DIR.glob("*.txt")):
        with open(arquivo, "r", encoding="latin-1") as f:
            hinos[arquivo.stem] = f.read()
    return hinos

# -----------------------------
# Estado
# -----------------------------

if "selecionados" not in st.session_state:
    st.session_state.selecionados = []

if "ordem" not in st.session_state:
    st.session_state.ordem = []

if "modo" not in st.session_state:
    st.session_state.modo = "normal"  # normal | apresentacao

# -----------------------------
# Carregamento
# -----------------------------

hinos = carregar_hinos()

# -----------------------------
# MODO APRESENTAÇÃO
# -----------------------------

if st.session_state.modo == "apresentacao":
    st.markdown("""
        <style>
        header, footer, .stToolbar {visibility: hidden;}
        .main {padding: 0 !important;}
        </style>
    """, unsafe_allow_html=True)

    for idx, nome in enumerate(st.session_state.ordem, start=1):
        conteudo = hinos[nome].upper().replace("\n", "<br>")

        st.markdown(f"""
        <div style='height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;'>
            <div style='font-size:48px; font-weight:bold; margin-bottom:40px;'>
                {idx}. {nome}
            </div>
            <div style='font-size:36px; line-height:1.6;'>
                {conteudo}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='page-break-after: always;'></div>", unsafe_allow_html=True)

    if st.button("⬅️ Voltar"):
        st.session_state.modo = "normal"
        st.rerun()

    st.stop()

# -----------------------------
# MODO NORMAL
# -----------------------------

st.title("📖 Gerador de Hinos")

# Busca
busca = st.text_input("🔍 Buscar hino")

hinos_filtrados = {
    nome: conteudo for nome, conteudo in hinos.items()
    if busca.lower() in nome.lower()
}

# Seleção
st.subheader("Selecione os hinos")

selecionados = []
for nome in hinos_filtrados:
    if st.checkbox(nome, key=nome):
        selecionados.append(nome)

st.session_state.selecionados = selecionados

# Sincroniza ordem
if set(st.session_state.ordem) != set(selecionados):
    st.session_state.ordem = selecionados.copy()

# -----------------------------
# Drag-and-drop
# -----------------------------

st.subheader("Ordenar hinos (arraste)")

if SORTABLE_AVAILABLE and st.session_state.ordem:
    nova_ordem = sort_items(st.session_state.ordem)
    st.session_state.ordem = nova_ordem
else:
    st.info("Para drag-and-drop real, instale: pip install streamlit-sortables")
    for i, nome in enumerate(st.session_state.ordem):
        col1, col2, col3 = st.columns([6,1,1])

        with col1:
            st.write(f"{i+1}. {nome}")

        with col2:
            if st.button("⬆️", key=f"up_{nome}") and i > 0:
                st.session_state.ordem[i], st.session_state.ordem[i-1] = \
                    st.session_state.ordem[i-1], st.session_state.ordem[i]

        with col3:
            if st.button("⬇️", key=f"down_{nome}") and i < len(st.session_state.ordem)-1:
                st.session_state.ordem[i], st.session_state.ordem[i+1] = \
                    st.session_state.ordem[i+1], st.session_state.ordem[i]

# -----------------------------
# Ações
# -----------------------------

col1, col2, col3 = st.columns(3)

with col1:
    gerar = st.button("🎤 Gerar apresentação")

with col2:
    if st.button("📺 Modo tela cheia"):
        if not st.session_state.ordem:
            st.error("Selecione pelo menos um hino")
        else:
            st.session_state.modo = "apresentacao"
            st.rerun()

with col3:
    if st.button("🧹 Limpar"):
        st.session_state.selecionados = []
        st.session_state.ordem = []
        st.rerun()

# -----------------------------
# Preview normal
# -----------------------------

if gerar:
    if not st.session_state.ordem:
        st.error("⚠️ Nenhum hino selecionado")
    else:
        st.divider()
        st.header("📺 Preview")

        for idx, nome in enumerate(st.session_state.ordem, start=1):
            conteudo = hinos[nome].upper().replace("\n", "<br>")

            st.markdown(f"""
            <div style='font-size:28px; line-height:1.6;'>
                <b>{idx}. {nome}</b><br><br>
                {conteudo}
            </div>
            <br><br><hr><br>
            """, unsafe_allow_html=True)
