
import streamlit as st
import os
from pathlib import Path

# Diretório dos hinos
HINOS_DIR = Path("hinos")

# Função para carregar hinos
def carregar_hinos():
    hinos = {}
    if not HINOS_DIR.exists():
        return hinos

    for arquivo in sorted(HINOS_DIR.glob("*.txt")):
        nome = arquivo.stem
        with open(arquivo, "r", encoding="latin-1") as f:
            conteudo = f.read()
        hinos[nome] = conteudo
    return hinos

# Inicializa estado
if "selecionados" not in st.session_state:
    st.session_state.selecionados = []

if "ordem" not in st.session_state:
    st.session_state.ordem = []

# Carrega dados
hinos = carregar_hinos()
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
    if st.checkbox(nome, key=f"chk_{nome}"):
        selecionados.append(nome)

# Atualiza session_state
st.session_state.selecionados = selecionados

# Inicializa ordem se necessário
if set(st.session_state.ordem) != set(selecionados):
    st.session_state.ordem = selecionados.copy()

# Reordenação
st.subheader("Ordenar hinos")

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

# Botões
col1, col2 = st.columns(2)

with col1:
    gerar = st.button("🎤 Gerar apresentação")

with col2:
    if st.button("🧹 Limpar seleção"):
        st.session_state.selecionados = []
        st.session_state.ordem = []
        st.experimental_rerun()

# Validação
if gerar:
    if not st.session_state.ordem:
        st.error("⚠️ Nenhum hino selecionado")
    else:
        st.divider()
        st.header("📺 Apresentação")

        for idx, nome in enumerate(st.session_state.ordem, start=1):
            conteudo = hinos[nome].upper().replace("\n", "<br>")

            st.markdown(f"""
            <div style='font-size:28px; line-height:1.6;'>
                <b>{idx}. {nome}</b><br><br>
                {conteudo}
            </div>
            <br><br><hr><br>
            """, unsafe_allow_html=True)
