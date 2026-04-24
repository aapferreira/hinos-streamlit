import streamlit as st
from pathlib import Path
import base64

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


def gerar_html_apresentacao(ordem, hinos):
    slides = ""

    for idx, nome in enumerate(ordem, start=1):
        conteudo = hinos[nome].upper().replace("\n", "<br>")

        slides += f"""
        <section class="slide">
            <div class="titulo">{idx}. {nome}</div>
            <div class="conteudo">{conteudo}</div>
        </section>
        """

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ margin:0; overflow:hidden; background:black; color:white; font-family:sans-serif; }}
            .slide {{
                width:100vw;
                height:100vh;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                text-align:center;
                position:absolute;
                top:0;
                left:0;
                opacity:0;
                transition: opacity 0.5s;
            }}
            .slide.active {{ opacity:1; }}
            .titulo {{ font-size:48px; margin-bottom:40px; }}
            .conteudo {{ font-size:36px; line-height:1.6; }}
        </style>
    </head>
    <body>
        {slides}

        <script>
            let index = 0;
            const slides = document.querySelectorAll('.slide');

            function showSlide(i) {{
                slides.forEach(s => s.classList.remove('active'));
                slides[i].classList.add('active');
            }}

            function next() {{
                if(index < slides.length - 1) index++;
                showSlide(index);
            }}

            function prev() {{
                if(index > 0) index--;
                showSlide(index);
            }}

            document.addEventListener('keydown', (e) => {{
                if(e.key === 'ArrowRight' || e.key === 'Enter') next();
                if(e.key === 'ArrowLeft') prev();
            }});

            showSlide(index);
        </script>
    </body>
    </html>
    """

    return html

# -----------------------------
# Estado
# -----------------------------

if "ordem" not in st.session_state:
    st.session_state.ordem = []

# -----------------------------
# Carregamento
# -----------------------------

hinos = carregar_hinos()

# -----------------------------
# UI
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

# -----------------------------
# Ações
# -----------------------------

col1, col2 = st.columns(2)

with col1:
    gerar = st.button("🎤 Preview")

with col2:
    if st.button("📺 Abrir apresentação em nova aba"):
        if not st.session_state.ordem:
            st.error("Selecione pelo menos um hino")
        else:
            html = gerar_html_apresentacao(st.session_state.ordem, hinos)
            b64 = base64.b64encode(html.encode()).decode()
            html = gerar_html_apresentacao(st.session_state.ordem, hinos)

            html = gerar_html_apresentacao(st.session_state.ordem, hinos)

            # Método mais confiável: salvar arquivo HTML e abrir
            file_path = "apresentacao.html"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)

            st.markdown(f'<a href="{file_path}" target="_blank">👉 Clique aqui para abrir a apresentação</a>', unsafe_allow_html=True)

            st.success("Arquivo gerado! Clique no link acima para abrir em nova aba.")

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
