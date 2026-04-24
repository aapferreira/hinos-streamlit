import streamlit as st
from pathlib import Path

# Drag-and-drop
try:
    from streamlit_sortables import sort_items
    SORTABLE_AVAILABLE = True
except ImportError:
    SORTABLE_AVAILABLE = False

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
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()
        except UnicodeDecodeError:
            with open(arquivo, "r", encoding="latin-1") as f:
                conteudo = f.read()
        hinos[arquivo.stem] = conteudo
    return hinos


def toggle_hino(nome):
    marcado = st.session_state.get(f"chk_{nome}", False)

    if marcado:
        if nome not in st.session_state.ordem:
            st.session_state.ordem.append(nome)
    else:
        if nome in st.session_state.ordem:
            st.session_state.ordem.remove(nome)

# -----------------------------
# Estado
# -----------------------------

if "ordem" not in st.session_state:
    st.session_state.ordem = []

if "modo" not in st.session_state:
    st.session_state.modo = "normal"

if "slide_atual" not in st.session_state:
    st.session_state.slide_atual = 0

# -----------------------------
# Carregamento
# -----------------------------

hinos = carregar_hinos()

# -----------------------------
# MODO APRESENTAÇÃO (CORRIGIDO)
# -----------------------------

if st.session_state.modo == "apresentacao":

    st.markdown("""
        <style>
        header, footer, .stToolbar {visibility: hidden;}
        .main {padding: 0 !important;}
        </style>
    """, unsafe_allow_html=True)

    total = len(st.session_state.ordem)

    if total == 0:
        st.warning("Nenhum hino selecionado")
        st.stop()

    idx = st.session_state.slide_atual
    nome = st.session_state.ordem[idx]

    conteudo = hinos[nome].upper().replace("\n", "<br>")

    st.markdown(f"""
    <div style='height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;'>
        <div style='font-size:48px; font-weight:bold; margin-bottom:40px;'>
            {idx+1}. {nome}
        </div>
        <div style='font-size:36px; line-height:1.6;'>
            {conteudo}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col1:
        if st.button("⬅️ Anterior") and idx > 0:
            st.session_state.slide_atual -= 1
            st.rerun()

    with col2:
        st.markdown(f"<div style='text-align:center'>{idx+1} / {total}</div>", unsafe_allow_html=True)

    with col3:
        if st.button("Próximo ➡️") and idx < total - 1:
            st.session_state.slide_atual += 1
            st.rerun()

    if st.button("❌ Sair"):
        st.session_state.modo = "normal"
        st.session_state.slide_atual = 0
        st.rerun()

    st.stop()

# -----------------------------
# MODO NORMAL
# -----------------------------

st.title("📖 Gerador de Hinos")

busca = st.text_input("🔍 Buscar hino")

hinos_filtrados = {
    nome: conteudo for nome, conteudo in hinos.items()
    if busca.lower() in nome.lower()
}

st.subheader("Selecione os hinos (ordem = ordem de clique)")

for nome in hinos_filtrados:
    st.checkbox(
        nome,
        key=f"chk_{nome}",
        value=(nome in st.session_state.ordem),
        on_change=toggle_hino,
        args=(nome,)
    )

# -----------------------------
# Ordenação
# -----------------------------

st.subheader("Ajustar ordem (opcional)")

if SORTABLE_AVAILABLE and st.session_state.ordem:
    st.session_state.ordem = sort_items(st.session_state.ordem)
else:
    st.caption("Instale streamlit-sortables para arrastar")

# -----------------------------
# Ações
# -----------------------------

col1, col2 = st.columns(2)

with col1:
    gerar = st.button("🎤 Preview")

with col2:
    if st.button("📺 Modo tela cheia"):
        if not st.session_state.ordem:
            st.error("Selecione pelo menos um hino")
        else:
            st.session_state.modo = "apresentacao"
            st.session_state.slide_atual = 0
            st.rerun()

if st.button("🧹 Limpar"):
    st.session_state.ordem = []
    for k in list(st.session_state.keys()):
        if k.startswith("chk_"):
            st.session_state[k] = False
    st.rerun()

# -----------------------------
# Preview
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
