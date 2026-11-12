import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

# Configuração da página e tema
st.set_page_config(page_title="Catálogo Completo de Personalizados", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0f111a;
        color: #f0f4f8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #141824;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    .floating-summary {
        position: sticky;
        top: 0;
        background-color: #1c2130;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# Estado da Sessão
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "carrinho_modal" not in st.session_state:
    st.session_state.carrinho_modal = []

# Banco de Imagens e Modelos 3D (Mockup para demonstração)
IMG_PADRAO = "https://www.bing.com/images/search?view=detailV2&ccid=TLmtF1OE&id=7933A9C7F2BCB92C21B98453A4C0E06AD9D02C26&thid=OIP.TLmtF1OECmpE2qk_bbzmBAHaEy&mediaurl=https%3A%2F%2Fi0.wp.com%2Fartesparacanecas.com.br%2Fwp-content%2Fuploads%2F2022%2F12%2FCaneca-Foto-Casal-com-Frase-Melhor-Escolha-mockup-03.jpg%3Fw%3D1780%26ssl%3D1&cdnurl=https%3A%2F%2Fth.bing.com%2Fth%2Fid%2FR.4cb9ad1753840a6a44daa93f6dbce604%3Frik%3DJizQ2WrgwKRThA%26pid%3DImgRaw%26r%3D0&exph=1150&expw=1780&q=imagem+de+canecas+com+estampa&form=IQFRBA&ck=38D682093965CA71632D99331260C4C4&selectedindex=1&ajaxhist=0&ajaxserp=0&vt=0&sim=11"
MODELO_PADRAO = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CoffeeMug/glTF-Binary/CoffeeMug.glb"

CATEGORIAS_SPECS = {
    "Copos Térmicos": (80.00, IMG_PADRAO, MODELO_PADRAO),
    "Camisetas": (55.00, IMG_PADRAO, MODELO_PADRAO),
    "Mateiras": (90.00, IMG_PADRAO, MODELO_PADRAO),
    "Bonés": (35.00, IMG_PADRAO, MODELO_PADRAO),
    "Chaveiros": (15.00, IMG_PADRAO, MODELO_PADRAO),
    "Almofadas": (45.00, IMG_PADRAO, MODELO_PADRAO),
}


def construir_itens_categoria(cat_nome: str, preco_base: float) -> list:
    itens = []
    for i in range(1, 21):
        itens.append({
            "id": f"{cat_nome[:3].lower()}{i}",
            "nome": f"{cat_nome} Modelo {i}",
            "preco": preco_base + (i * 2.5),
            "imagem": IMG_PADRAO,
            "modelo_3d": MODELO_PADRAO
        })
    return itens


CATALOGO = {}
for cat, (preco, img, mod) in CATEGORIAS_SPECS.items():
    CATALOGO[cat] = {
        "destaque": {"nome": f"{cat} em Destaque", "preco": preco, "imagem": img},
        "itens": construir_itens_categoria(cat, preco)
    }


# Lógica do Carrinho
def calcular_promocao(preco_unitario: float, quantidade: int):
    brindes = quantidade // 10
    total = quantidade * preco_unitario
    economia = brindes * preco_unitario
    return total, brindes, economia


def _mesclar_itens(destino: list, item: dict, quantidade: int):
    for item_existente in destino:
        if item_existente["id"] == item["id"]:
            nova_qtd = item_existente["quantidade"] + quantidade
            total, brindes, econ = calcular_promocao(item["preco"], nova_qtd)
            item_existente["quantidade"] = nova_qtd
            item_existente["unidades_gratis"] = brindes
            item_existente["desconto"] = econ
            item_existente["subtotal"] = total
            return

    total, brindes, econ = calcular_promocao(item["preco"], quantidade)
    destino.append({
        "id": item["id"],
        "nome": item["nome"],
        "preco_unitario": item["preco"],
        "quantidade": quantidade,
        "unidades_gratis": brindes,
        "desconto": econ,
        "subtotal": total
    })


def callback_adicionar_modal(item: dict):
    qtd = st.session_state.get(f"qtd_{item['id']}", 1)
    _mesclar_itens(st.session_state.carrinho_modal, item, qtd)
    st.toast(f"{qtd}x {item['nome']} adicionado à seleção!", icon="🛒")


def sincronizar_carrinho_modal():
    if st.session_state.carrinho_modal:
        for item_staged in st.session_state.carrinho_modal:
            item_base = {
                "id": item_staged["id"],
                "nome": item_staged["nome"],
                "preco": item_staged["preco_unitario"]
            }
            _mesclar_itens(st.session_state.carrinho, item_base, item_staged["quantidade"])
        st.session_state.carrinho_modal = []


# Visualizador 3D
def renderizar_visualizador_3d(item: dict, height: int = 250):
    html_code = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"></script>
        <style>
          body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
          .container {{ width: 100%; height: {height}px; position: relative; border-radius: 8px; overflow: hidden; background: #141824; }}
          model-viewer {{ width: 100%; height: 100%; --poster-color: transparent; }}
          .hint {{ position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.7); color: #fff; font-size: 10px; padding: 3px 6px; border-radius: 4px; pointer-events: none; }}
        </style>
      </head>
      <body>
        <div class="container">
          <model-viewer 
            src="{item['modelo_3d']}" 
            poster="{item['imagem']}" 
            alt="{item['nome']}" 
            camera-controls 
            touch-action="pan-y"
            auto-rotate>
            <div class="hint">🔄 Arraste para girar</div>
          </model-viewer>
        </div>
      </body>
    </html>
    """
    components.html(html_code, height=height)


# Modal de Categoria
@st.dialog("Catálogo da Categoria", width="large")
def abrir_modal_categoria(categoria_nome: str):
    st.subheader(f"Modelos Disponíveis: {categoria_nome} (20 opções)")
    st.caption("🔥 Promoção: A cada 10 unidades, ganhe 1 brinde!")

    qtd_modal = sum(i["quantidade"] for i in st.session_state.carrinho_modal)
    brindes_modal = sum(i["unidades_gratis"] for i in st.session_state.carrinho_modal)
    total_modal = sum(i["subtotal"] for i in st.session_state.carrinho_modal)

    col_resumo, col_fechar = st.columns([3, 1])
    with col_resumo:
        brinde_txt = f" | Brindes: {brindes_modal} 🔥" if brindes_modal > 0 else ""
        st.info(f"🛒 Selecionados nesta sessão: {qtd_modal} item(ns){brinde_txt} | Subtotal: R$ {total_modal:.2f}")
    with col_fechar:
        if st.button("✅ Confirmar e Voltar", key=f"fechar_{categoria_nome}", type="primary", use_container_width=True):
            sincronizar_carrinho_modal()
            st.rerun()

    st.divider()

    itens = CATALOGO[categoria_nome]["itens"]
    num_colunas = 4
    for linha_inicio in range(0, len(itens), num_colunas):
        cols = st.columns(num_colunas)
        grupo = itens[linha_inicio:linha_inicio + num_colunas]
        for idx, item in enumerate(grupo):
            with cols[idx]:
                with st.container(border=True):
                    renderizar_visualizador_3d(item)
                    st.markdown(f"**{item['nome']}**")
                    st.write(f"Unitário: R$ {item['preco']:.2f}")

                    qtd = st.number_input("Qtd", min_value=1, max_value=100, value=1, key=f"qtd_{item['id']}")

                    total_item, brindes, eco = calcular_promocao(item["preco"], qtd)
                    if brindes > 0:
                        st.success(f"+{brindes} brinde(s) grátis! (Economia: R$ {eco:.2f})")

                    st.button("🛒 Adicionar", key=f"add_{item['id']}", use_container_width=True,
                              on_click=callback_adicionar_modal, args=(item,))


# Interface Principal
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.title("🏷️")
with col_titulo:
    st.title("Nome da Empresa")
    st.subheader("Catálogo Completo de Produtos Personalizados")

st.divider()

# Barra Lateral (Carrinho e Checkout)
with st.sidebar:
    st.header("🛒 Seu Carrinho")
    if not st.session_state.carrinho:
        st.write("O carrinho está vazio.")
    else:
        total_geral = sum(i["subtotal"] for i in st.session_state.carrinho)
        qtd_total = sum(i["quantidade"] for i in st.session_state.carrinho)
        brindes_totais = sum(i["unidades_gratis"] for i in st.session_state.carrinho)

        st.markdown(f"""
            <div class="floating-summary">
                <h4>Resumo do Pedido</h4>
                <p><b>Total de Itens:</b> {qtd_total}</p>
                <p><b>Brindes Acumulados:</b> {brindes_totais} 🔥</p>
                <h3 style="color: #00FF88;">Subtotal: R$ {total_geral:.2f}</h3>
            </div>
        """, unsafe_allow_html=True)

        st.write("### Itens Selecionados")
        for i, item in enumerate(st.session_state.carrinho):
            col_desc, col_btn = st.columns([4, 1])
            with col_desc:
                info_b = f"(+{item['unidades_gratis']} grátis)" if item['unidades_gratis'] > 0 else ""
                st.write(f"**{item['nome']}**")
                st.write(f"{item['quantidade']}x R$ {item['preco_unitario']:.2f} {info_b} = R$ {item['subtotal']:.2f}")
            with col_btn:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.carrinho.pop(i)
                    st.rerun()
            st.divider()

        st.subheader("💳 Finalização (Pix)")
        if st.button("📲 Finalizar Pedido via WhatsApp", type="primary", use_container_width=True):
            linhas = [f"- {i['quantidade']}x {i['nome']} (R$ {i['subtotal']:.2f})" for i in st.session_state.carrinho]
            msg = f"Olá! Gostaria de confirmar meu pedido:\n\n" + "\n".join(
                linhas) + f"\n\n*Total Geral: R$ {total_geral:.2f}*"
            link = f"https://wa.me/5555996374854?text={urllib.parse.quote(msg)}"
            st.link_button("👉 Clique aqui para enviar no WhatsApp", link)

# Grade de Categorias
st.header("📦 Categorias Disponíveis")
st.caption("Clique em qualquer categoria abaixo para abrir a grade completa com 20 modelos personalizáveis.")

categorias = list(CATALOGO.keys())
num_cols_cat = 3
linhas_cat = [categorias[i:i + num_cols_cat] for i in range(0, len(categorias), num_cols_cat)]

for linha in linhas_cat:
    cols = st.columns(num_cols_cat)
    for idx, cat_nome in enumerate(linha):
        destaque = CATALOGO[cat_nome]["destaque"]
        with cols[idx]:
            with st.container(border=True):
                st.image(destaque["imagem"], use_container_width=True)
                st.subheader(cat_nome)
                st.write(f"A partir de: R$ {destaque['preco']:.2f}")
                if st.button(f"🔍 Ver 20 modelos de {cat_nome}", key=f"btn_cat_{cat_nome}", use_container_width=True):
                    abrir_modal_categoria(cat_nome)

# Botão Voltar ao Topo
st.markdown("""
    <style>
    .btn-top {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #00FF88;
        color: #0f111a;
        padding: 10px 15px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        z-index: 1000;
    }
    </style>
    <a href="#" class="btn-top">↑ Topo</a>
""", unsafe_allow_html=True)
