import urllib.parse
import streamlit as st

st.set_page_config(page_title="Catálogo e Pedidos", layout="wide")

# Estilo personalizado com imagem de fundo temática de gráfica/personalizados
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(15, 17, 26, 0.86), rgba(15, 17, 26, 0.90)),
                          url("https://images.unsplash.com/photo-1562577309-4932fdd64cd1?auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #FFFFFF;
    }
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }
    [data-testid="stSidebar"] {
        background-color: rgba(20, 24, 36, 0.92);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(28, 33, 48, 0.85);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# Base de imagens temáticas da internet por categoria
IMG_COPOS = [
    "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1577937927133-66ef06acdf18?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1570784332176-fdd73da66f03?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1589365278144-c9e705f843ba?auto=format&fit=crop&w=500&q=80",
]

IMG_CAMISAS = [
    "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1562157873-818bc0726f68?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1503341504253-dff4815485f1?auto=format&fit=crop&w=500&q=80",
]

IMG_MATEIRAS = [
    "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=500&q=80",
]

COPOS_SPECS = [
    ("Copo Térmico 473ml Preto Fosco", 80.00),
    ("Copo Térmico 473ml Branco Neve", 80.00),
    ("Caneca Térmica 700ml Inox Escovado", 110.00),
    ("Copo Térmico 473ml Azul Marinho", 85.00),
    ("Copo Térmico 473ml Amarelo Vibrante", 85.00),
    ("Copo Térmico 473ml Verde Militar", 85.00),
    ("Copo Térmico 473ml Vermelho Rubi", 85.00),
    ("Copo Térmico 473ml Rosa Quartz", 85.00),
    ("Copo Térmico 473ml Laranja Neon", 85.00),
    ("Copo Térmico 473ml Roxo Ametista", 85.00),
    ("Caneca Choppeira 500ml Preto", 95.00),
    ("Caneca Choppeira 500ml Branca", 95.00),
    ("Caneca Cerâmica 325ml Branca Sublimada", 45.00),
    ("Caneca Cerâmica 325ml Alça Preta", 50.00),
    ("Caneca Cerâmica Mágica Preta 325ml", 55.00),
    ("Caneca Polímero Infantil 320ml", 38.00),
    ("Garrafa Térmica Squeeze 600ml Preta", 90.00),
    ("Garrafa Térmica Squeeze 600ml Inox", 95.00),
    ("Copo Cuia Térmica Chimarrão 350ml", 75.00),
    ("Caneca Esmaltada Retrô 370ml", 60.00),
]

CAMISAS_SPECS = [
    ("Camisa Algodão Branca Personalizada", 60.00),
    ("Camisa Algodão Preta Personalizada", 65.00),
    ("Camisa Dry-Fit Esportiva Branca", 55.00),
    ("Camisa Dry-Fit Esportiva Preta", 58.00),
    ("Camisa Poliéster Sublimação Total", 50.00),
    ("Camisa Algodão Azul Marinho", 65.00),
    ("Camisa Algodão Cinza Mescla", 62.00),
    ("Camisa Algodão Vermelha", 65.00),
    ("Camisa Algodão Verde Bandeira", 65.00),
    ("Camisa Algodão Amarela Ouro", 65.00),
    ("Camisa Polo Piquet Preta Bordada/Estampada", 85.00),
    ("Camisa Polo Piquet Branca Personalizada", 80.00),
    ("Camisa Manga Longa UV50+ Branca", 75.00),
    ("Camisa Manga Longa UV50+ Preta", 78.00),
    ("Baby Look Algodão Branca Feminina", 58.00),
    ("Baby Look Algodão Preta Feminina", 62.00),
    ("Camiseta Infantil Algodão Branca", 45.00),
    ("Camiseta Infantil Algodão Colorida", 48.00),
    ("Regata Dry-Fit Treino Personalizada", 50.00),
    ("Camisa Uniforme Empresarial Reforçada", 70.00),
]

MATEIRAS_SPECS = [
    ("Mateira Couro Legítimo Marrom Café", 120.00),
    ("Mateira Couro Sintético Preta Clássica", 90.00),
    ("Kit Chimarrão Completo Couro Legítimo", 180.00),
    ("Mateira Couro Caramelo Artesanal", 130.00),
    ("Mateira Couro Pinhão com Porta-Erva", 145.00),
    ("Mateira Compacta 1 Litro Preta", 85.00),
    ("Mateira Compacta 1 Litro Marrom", 85.00),
    ("Mateira Luxo Costura Trançada", 160.00),
    ("Mateira Rústica Gravação a Laser", 150.00),
    ("Mateira Sintética Azul Marinho", 95.00),
    ("Mateira Sintética Vermelha", 95.00),
    ("Mateira Sintética Rosa", 95.00),
    ("Mateira Sintética Verde Musgo", 95.00),
    ("Mateira Bolsa Térmica Chimarrão", 110.00),
    ("Mateira Couro Preto com Alça Ombro", 135.00),
    ("Mateira Couro Havana Especial", 140.00),
    ("Kit Mateira + Cuia + Bomba Inox", 210.00),
    ("Mateira Grande 1.8L para Térmica", 155.00),
    ("Mateira Minimalista Couro Nobuck", 145.00),
    ("Mateira Personalizada Brasão/Nome", 165.00),
]

def _construir_itens(prefixo: str, specs: list, imagens: list) -> list:
    itens = []
    for idx, (nome, preco) in enumerate(specs[:20], start=1):
        img_principal = imagens[(idx - 1) % len(imagens)]
        img_lateral = imagens[idx % len(imagens)]
        img_verso = imagens[(idx + 1) % len(imagens)]
        itens.append({
            "id": f"{prefixo}_{idx}",
            "nome": nome,
            "preco": preco,
            "imagem": img_principal,
            "vistas": {
                "Frente": img_principal,
                "Lateral": img_lateral,
                "Verso": img_verso
            }
        })
    return itens

CATALOGO = {
    "Copos": {
        "destaque": {"nome": "Copo Térmico Personalizado", "preco": 38.00, "imagem": IMG_COPOS[0]},
        "itens": _construir_itens("copo", COPOS_SPECS, IMG_COPOS),
    },
    "Camisas": {
        "destaque": {"nome": "Camisa Estampada Personalizada", "preco": 45.00, "imagem": IMG_CAMISAS[0]},
        "itens": _construir_itens("cam", CAMISAS_SPECS, IMG_CAMISAS),
    },
    "Mateiras": {
        "destaque": {"nome": "Mateira em Couro", "preco": 85.00, "imagem": IMG_MATEIRAS[0]},
        "itens": _construir_itens("mat", MATEIRAS_SPECS, IMG_MATEIRAS),
    },
}

def calcular_preco_com_desconto(preco_unitario: float, quantidade: int):
    brindes = quantidade // 10
    total = quantidade * preco_unitario
    economia = brindes * preco_unitario
    return total, brindes, economia

def adicionar_ao_carrinho(item: dict, quantidade: int):
    for item_carrinho in st.session_state.carrinho:
        if item_carrinho["id"] == item["id"]:
            nova_qtd = item_carrinho["quantidade"] + quantidade
            total, brindes, econ = calcular_preco_com_desconto(item["preco"], nova_qtd)
            item_carrinho["quantidade"] = nova_qtd
            item_carrinho["unidades_gratis"] = brindes
            item_carrinho["desconto"] = econ
            item_carrinho["subtotal"] = total
            return

    total, brindes, econ = calcular_preco_com_desconto(item["preco"], quantidade)
    st.session_state.carrinho.append({
        "id": item["id"],
        "nome": item["nome"],
        "preco_unitario": item["preco"],
        "quantidade": quantidade,
        "unidades_gratis": brindes,
        "desconto": econ,
        "subtotal": total,
    })

@st.dialog("Catálogo da Categoria", width="large")
def abrir_modal_categoria(categoria_nome: str):
    st.subheader(f"Modelos Disponíveis: {categoria_nome} (20 opções)")
    st.caption("Promoção: A cada 10 unidades, você ganha +1 unidade de brinde 🔥!")
    st.divider()

    itens = CATALOGO[categoria_nome]["itens"]
    num_colunas = 4
    
    for linha_inicio in range(0, len(itens), num_colunas):
        cols = st.columns(num_colunas)
        grupo = itens[linha_inicio:linha_inicio + num_colunas]
        
        for idx, item in enumerate(grupo):
            with cols[idx]:
                with st.container(border=True):
                    st.image(item["imagem"], use_container_width=True)
                    st.markdown(f"**{item['nome']}**")
                    st.write(f"Unitário: **R$ {item['preco']:.2f}**")
                    
                    with st.expander("🔍 Zoom e Ângulos"):
                        angulo = st.radio("Ângulo:", ["Frente", "Lateral", "Verso"], horizontal=True, key=f"ang_{item['id']}")
                        zoom = st.slider("Zoom (%)", min_value=100, max_value=250, value=140, step=10, key=f"zoom_{item['id']}")
                        img_url = item["vistas"][angulo]
                        st.markdown(f"""
                        <div style="overflow:auto; max-height:240px; border-radius:8px; border:1px solid #444;">
                            <img src="{img_url}" style="width:{zoom}%; max-width:none; display:block;" />
                        </div>
                        """, unsafe_allow_html=True)

                    qtd = st.number_input("Quantidade", min_value=1, max_value=100, value=1, step=1, key=f"qtd_{item['id']}")
                    
                    total_item, brindes, economia = calcular_preco_com_desconto(item["preco"], qtd)
                    foguinhos = "🔥" * brindes if brindes > 0 else ""
                    st.markdown(f"**Total: R$ {total_item:.2f}** {foguinhos}")
                    
                    if brindes > 0:
                        st.success(f"{foguinhos} +{brindes} brinde(s) grátis! (Economia: R$ {economia:.2f})")
                    
                    if st.button("🛒 Adicionar", key=f"add_{item['id']}", use_container_width=True):
                        adicionar_ao_carrinho(item, qtd)
                        st.toast(f"{qtd}x {item['nome']} adicionado(s)!")
                        st.rerun()

col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("### [LOGO]")
with col2:
    st.title("Nome da Empresa")
    st.subheader("Catálogo de Produtos Personalizados")

st.divider()

with st.sidebar:
    st.header("🛒 Resumo do Pedido")
    if not st.session_state.carrinho:
        st.write("O carrinho está vazio.")
    else:
        total_parcial = sum(item["subtotal"] for item in st.session_state.carrinho)
        total_itens = sum(item["quantidade"] for item in st.session_state.carrinho)
        total_brindes = sum(item["unidades_gratis"] for item in st.session_state.carrinho)
        st.write(f"**Itens pagos:** {total_itens}")
        if total_brindes > 0:
            st.write(f"**Brindes ganhos:** {total_brindes} {'🔥' * total_brindes}")
        st.write(f"**Total Parcial:** R$ {total_parcial:.2f}")

st.header("Produtos Disponíveis")
st.caption("Clique em uma categoria para abrir a grade flutuante com 20 modelos.")

categorias = list(CATALOGO.keys())
cols_cat = st.columns(len(categorias))

for idx, cat_nome in enumerate(categorias):
    destaque = CATALOGO[cat_nome]["destaque"]
    with cols_cat[idx]:
        with st.container(border=True):
            st.image(destaque["imagem"], use_container_width=True)
            st.subheader(destaque["nome"])
            st.write(f"**A partir de:** R$ {destaque['preco']:.2f}")
            if st.button(f"🔍 Ver opções de {cat_nome} (20 modelos)", key=f"btn_cat_{cat_nome}", use_container_width=True):
                abrir_modal_categoria(cat_nome)

st.divider()

st.header("Finalização do Pedido")
if st.session_state.carrinho:
    st.write("### Itens Selecionados:")
    for i, item in enumerate(st.session_state.carrinho):
        col_item, col_acoes = st.columns([4, 1])
        with col_item:
            foguinhos_item = "🔥" * item["unidades_gratis"]
            info_extra = f" ({foguinhos_item} +{item['unidades_gratis']} grátis - Economia: R$ {item['desconto']:.2f})" if item["unidades_gratis"] > 0 else ""
            st.write(f"**{i+1}. {item['nome']}** | Qtd: `{item['quantidade']}x` (R$ {item['preco_unitario']:.2f}/un) — **Subtotal: R$ {item['subtotal']:.2f}**{info_extra}")
        with col_acoes:
            if st.button("Remover", key=f"remove_{item['id']}"):
                st.session_state.carrinho.pop(i)
                st.rerun()

    total_final = sum(item["subtotal"] for item in st.session_state.carrinho)
    economia_total = sum(item["desconto"] for item in st.session_state.carrinho)
    brindes_totais = sum(item["unidades_gratis"] for item in st.session_state.carrinho)

    st.subheader(f"Total Geral: R$ {total_final:.2f}")
    if brindes_totais > 0:
        st.info(f"{'🔥' * brindes_totais} Você ganhou {brindes_totais} unidade(s) de brinde! Economia total: R$ {economia_total:.2f}")
    st.success(f"Pedido pronto para envio! Valor total: R$ {total_final:.2f}")

    st.divider()
    st.markdown("### 💳 Opções de Pagamento Seguras")
    st.info("Aceitamos Pix e Cartões.")
    st.subheader("🔑 Pagamento via Pix")
    st.info("Chave Pix: **SUA-CHAVE-PIX-AQUI**")

    linhas_pedido = []
    for item in st.session_state.carrinho:
        bonus_txt = f" + {item['unidades_gratis']} brinde(s) 🔥" if item["unidades_gratis"] > 0 else ""
        linhas_pedido.append(f"- {item['quantidade']}x {item['nome']}{bonus_txt} (R$ {item['subtotal']:.2f})")
    
    itens_texto = "\n".join(linhas_pedido)
    mensagem = f"Olá! Gostaria de confirmar o pedido:\n{itens_texto}\n\nTotal Geral: R$ {total_final:.2f}\nComprovante em anexo."
    mensagem_codificada = urllib.parse.quote(mensagem)
    link_whatsapp = f"https://wa.me/5555996374854?text={mensagem_codificada}"
    
    st.link_button("📲 Finalizar Pedido no WhatsApp", link_whatsapp)
else:
    st.write("Seu carrinho está vazio.")

