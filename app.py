import streamlit as st
from pathlib import Path
import sqlite3
from datetime import date

# Drag-and-drop
try:
    from streamlit_sortables import sort_items
    SORTABLE_AVAILABLE = True
except ImportError:
    SORTABLE_AVAILABLE = False

st.set_page_config(page_title="Hinos", layout="wide")

HINOS_DIR = Path("hinos")
DB_PATH = "hinos.db"

# -----------------------------
# Banco de dados
# -----------------------------

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS hinos (
            nome TEXT PRIMARY KEY,
            contador INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def incrementar_contador(nome):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO hinos (nome, contador) VALUES (?, 0)", (nome,))
    c.execute("UPDATE hinos SET contador = contador + 1 WHERE nome = ?", (nome,))
    conn.commit()
    conn.close()


def carregar_contadores():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nome, contador FROM hinos")
    dados = dict(c.fetchall())
    conn.close()
    return dados

init_db()

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

# -----------------------------
# Carregamento
# -----------------------------

hinos = carregar_hinos()
contadores = carregar_contadores()

# -----------------------------
# MODO NORMAL
# -----------------------------

st.title("📖 Gerador de Hinos")

busca = st.text_input("🔍 Buscar hino")

hinos_filtrados = {
    nome: conteudo for nome, conteudo in hinos.items()
    if busca.lower() in nome.lower()
}

st.subheader("Selecione os hinos")
st.text("Os hinos serão mostrados na ordem em que forem selecionados.\n" \
"A ordem poderá ser reajustada posteriormente.")

# 3 colunas
colunas = st.columns(3)
nomes = list(hinos_filtrados.keys())

for i, nome in enumerate(nomes):
    col = colunas[i % 3]
    contador = contadores.get(nome, 0)

    with col:
        st.checkbox(
            f"{nome} ({contador})",
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

col1 = st.columns(1)[0]

with col1:
    gerar = st.button("🎤 Gerar")

if gerar and st.session_state.ordem:
    for nome in st.session_state.ordem:
        incrementar_contador(nome)

if st.button("🧹 Limpar"):
    st.session_state.ordem = []
    for k in list(st.session_state.keys()):
        if k.startswith("chk_"):
            del st.session_state[k]
    st.rerun()

# -----------------------------
# Preview
# -----------------------------

if gerar:
    if not st.session_state.ordem:
        st.error("⚠️ Nenhum hino selecionado")
    else:
        st.divider()
        st.header(f"📅 {date.today().strftime('%d/%m/%Y')}")
        st.header(f"")

        for idx, nome in enumerate(st.session_state.ordem, start=1):
            conteudo = hinos[nome].upper().replace("\n", "<br>")

            st.markdown(f"""
            <div style='font-size:28px; line-height:1.6;'>
                <!--<b>{idx}. {nome}</b><br><br>-->
                <b>{conteudo}</b>
            </div>
            <br><br><hr><br>
            """, unsafe_allow_html=True)
