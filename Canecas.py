import urllib.parse
import streamlit as st

st.set_page_config(page_title="Catálogo e Pedidos", layout="wide")

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

CATALOGO = {
    "Copos": {
        "destaque": {
            "nome": "Copo Térmico Personalizado",
            "preco": 80.00,
            "imagem": "https://picsum.photos/200/200?random=1",
        },
        "itens": [
            {
                "id": "copo_1",
                "nome": "Copo Térmico 473ml Preto",
                "preco": 80.00,
                "imagem": "https://picsum.photos/200/200?random=11",
            },
            {
                "id": "copo_2",
                "nome": "Copo Térmico 473ml Branco",
                "preco": 80.00,
                "imagem": "https://picsum.photos/200/200?random=12",
            },
            {
                "id": "copo_3",
                "nome": "Caneca Térmica 700ml Inox",
                "preco": 110.00,
                "imagem": "https://picsum.photos/200/200?random=13",
            },
        ],
    },
    "Camisas": {
        "destaque": {
            "nome": "Camisa Estampada Algodão",
            "preco": 60.00,
            "imagem": "https://picsum.photos/200/200?random=2",
        },
        "itens": [
            {
                "id": "cam_1",
                "nome": "Camisa Algodão Branca Personalizada",
                "preco": 60.00,
                "imagem": "https://picsum.photos/200/200?random=21",
            },
            {
                "id": "cam_2",
                "nome": "Camisa Algodão Preta Personalizada",
                "preco": 65.00,
                "imagem": "https://picsum.photos/200/200?random=22",
            },
            {
                "id": "cam_3",
                "nome": "Camisa Dry-Fit Esportiva",
                "preco": 55.00,
                "imagem": "https://picsum.photos/200/200?random=23",
            },
        ],
    },
    "Mateiras": {
        "destaque": {
            "nome": "Mateira em Couro",
            "preco": 120.00,
            "imagem": "https://picsum.photos/200/200?random=3",
        },
        "itens": [
            {
                "id": "mat_1",
                "nome": "Mateira Couro Legítimo Marrom",
                "preco": 120.00,
                "imagem": "https://picsum.photos/200/200?random=31",
            },
            {
                "id": "mat_2",
                "nome": "Mateira Couro Sintético Preta",
                "preco": 90.00,
                "imagem": "https://picsum.photos/200/200?random=32",
            },
            {
                "id": "mat_3",
                "nome": "Kit Chimarrão Completo Couro",
                "preco": 180.00,
                "imagem": "https://picsum.photos/200/200?random=33",
            },
        ],
    },
}


def calcular_preco_com_desconto(preco_unitario: float, quantidade: int):
    unidades_gratis = quantidade // 11
    unidades_pagas = quantidade - unidades_gratis
    total = unidades_pagas * preco_unitario
    desconto_aplicado = unidades_gratis * preco_unitario
    return total, unidades_gratis, desconto_aplicado


def adicionar_ao_carrinho(item: dict, quantidade: int):
    for item_carrinho in st.session_state.carrinho:
        if item_carrinho["id"] == item["id"]:
            nova_qtd = item_carrinho["quantidade"] + quantidade
            total, gratis, desc = calcular_preco_com_desconto(
                item["preco"], nova_qtd
            )
            item_carrinho["quantidade"] = nova_qtd
            item_carrinho["unidades_gratis"] = gratis
            item_carrinho["desconto"] = desc
            item_carrinho["subtotal"] = total
            return

    total, gratis, desc = calcular_preco_com_desconto(item["preco"], quantidade)
    st.session_state.carrinho.append({
        "id": item["id"],
        "nome": item["nome"],
        "preco_unitario": item["preco"],
        "quantidade": quantidade,
        "unidades_gratis": gratis,
        "desconto": desc,
        "subtotal": total,
    })


@st.dialog("Catálogo da Categoria", width="large")
def abrir_modal_categoria(categoria_nome: str):
    st.subheader(f"Modelos Disponíveis: {categoria_nome}")
    st.caption("Promoção: A cada 10 unidades, a 11ª é grátis!")
    st.divider()

    itens = CATALOGO[categoria_nome]["itens"]
    cols = st.columns(len(itens))

    for idx, item in enumerate(itens):
        with cols[idx]:
            st.image(item["imagem"], use_container_width=True)
            st.markdown(f"**{item['nome']}**")
            st.write(f"Unitário: R$ {item['preco']:.2f}")

            qtd = st.number_input(
                "Quantidade",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                key=f"qtd_{item['id']}",
            )

            total_item, gratis, desconto = calcular_preco_com_desconto(
                item["preco"], qtd
            )

            st.markdown(f"**Total: R$ {total_item:.2f}**")
            if gratis > 0:
                st.success(f"🎁 +{gratis} grátis! (Economia: R$ {desconto:.2f})")

            if st.button(
                "🛒 Adicionar ao Carrinho",
                key=f"add_{item['id']}",
                use_container_width=True,
            ):
                adicionar_ao_carrinho(item, qtd)
                st.toast(f"{qtd}x {item['nome']} adicionado(s)!")
                st.rerun()


col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("### [LOGO]")
with col2:
    st.title("Nome da Empresa")
    st.subheader("Catálogo de Produtos")

st.divider()

with st.sidebar:
    st.image(
        "https://media.giphy.com/media/3o7TKMtpxxHOGTdzJC/giphy.gif",
        caption="Seu assistente!",
        width=150,
    )
    st.header("🛒 Resumo do Pedido")

    if not st.session_state.carrinho:
        st.write("O carrinho está vazio.")
    else:
        total_parcial = sum(item["subtotal"] for item in st.session_state.carrinho)
        total_itens = sum(item["quantidade"] for item in st.session_state.carrinho)
        st.write(f"**Itens no carrinho:** {total_itens}")
        st.write(f"**Total Parcial:** R$ {total_parcial:.2f}")

st.header("Produtos Disponíveis")
st.caption("Clique em uma categoria para ver modelos e quantidades.")

categorias = list(CATALOGO.keys())
cols_cat = st.columns(len(categorias))

for idx, cat_nome in enumerate(categorias):
    destaque = CATALOGO[cat_nome]["destaque"]
    with cols_cat[idx]:
        with st.container(border=True):
            st.image(destaque["imagem"], use_container_width=True)
            st.subheader(destaque["nome"])
            st.write(f"**A partir de:** R$ {destaque['preco']:.2f}")
            if st.button(
                f"🔍 Ver opções de {cat_nome}",
                key=f"btn_cat_{cat_nome}",
                use_container_width=True,
            ):
                abrir_modal_categoria(cat_nome)

st.divider()

st.header("Finalização do Pedido")

if st.session_state.carrinho:
    st.write("### Itens Selecionados:")

    for i, item in enumerate(st.session_state.carrinho):
        col_item, col_acoes = st.columns([4, 1])
        with col_item:
            info_extra = (
                f" (Inclui {item['unidades_gratis']} grátis - Economia: R$"
                f" {item['desconto']:.2f})"
                if item["unidades_gratis"] > 0
                else ""
            )
            st.write(
                f"**{i+1}. {item['nome']}** | Qtd: `{item['quantidade']}x` "
                f"(R$ {item['preco_unitario']:.2f}/un) — **Subtotal: R$ {item['subtotal']:.2f}**{info_extra}"
            )
        with col_acoes:
            if st.button("Remover", key=f"remove_{item['id']}"):
                st.session_state.carrinho.pop(i)
                st.rerun()

    total_final = sum(item["subtotal"] for item in st.session_state.carrinho)
    economia_total = sum(item["desconto"] for item in st.session_state.carrinho)

    st.subheader(f"Total Geral: R$ {total_final:.2f}")
    if economia_total > 0:
        st.info(f"Economia total com descontos: R$ {economia_total:.2f}")
    st.success(f"Você está R$ {total_final:.2f} mais feliz e bem equipado!")

    st.divider()

    st.markdown("### 💳 Opções de Pagamento Seguras")
    st.info("Aceitamos Pix e Cartões.")

    st.subheader("🔑 Pagamento via Pix")
    st.info("Chave Pix: **SUA-CHAVE-PIX-AQUI**")

    linhas_pedido = [
        f"- {item['quantidade']}x {item['nome']} (R$ {item['subtotal']:.2f})"
        for item in st.session_state.carrinho
    ]
    itens_texto = "\n".join(linhas_pedido)
    mensagem = (
        f"Olá! Gostaria de confirmar o pedido:\n{itens_texto}\n\n"
        f"Total Geral: R$ {total_final:.2f}\nComprovante em anexo."
    )
    mensagem_codificada = urllib.parse.quote(mensagem)
    link_whatsapp = f"https://wa.me/5555996374854?text={mensagem_codificada}"

    st.link_button(
        "📲 Finalizar Pedido no WhatsApp",
        link_whatsapp,
    )
else:
    st.write("Seu carrinho está vazio.")
