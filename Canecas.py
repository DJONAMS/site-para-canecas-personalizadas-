import urllib.parse
import streamlit as st

st.set_page_config(page_title="Canecas Personalizadas", layout="wide")

# Estado
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# Produtos
PRODUTOS = [
    {
        "id": "caneca_1",
        "nome": "Caneca Cerâmica Branca 325ml",
        "preco": 45.00,
        "imagem": "https://picsum.photos/400/300?random=1",
    },
    {
        "id": "caneca_2",
        "nome": "Caneca Cerâmica Alça Preta",
        "preco": 50.00,
        "imagem": "https://picsum.photos/400/300?random=2",
    },
    {
        "id": "caneca_3",
        "nome": "Caneca Mágica Personalizada",
        "preco": 55.00,
        "imagem": "https://picsum.photos/400/300?random=3",
    },
]


def calcular_preco(preco, quantidade):
    brindes = quantidade // 10
    subtotal = preco * quantidade
    economia = brindes * preco
    return subtotal, brindes, economia


def adicionar_carrinho(produto, quantidade):
    for item in st.session_state.carrinho:
        if item["id"] == produto["id"]:
            item["quantidade"] += quantidade

            subtotal, brindes, economia = calcular_preco(
                produto["preco"],
                item["quantidade"],
            )

            item["subtotal"] = subtotal
            item["brindes"] = brindes
            item["economia"] = economia
            return

    subtotal, brindes, economia = calcular_preco(
        produto["preco"],
        quantidade,
    )

    st.session_state.carrinho.append(
        {
            "id": produto["id"],
            "nome": produto["nome"],
            "preco": produto["preco"],
            "quantidade": quantidade,
            "subtotal": subtotal,
            "brindes": brindes,
            "economia": economia,
        }
    )


st.title("☕ Catálogo de Canecas Personalizadas")
st.caption("Promoção: a cada 10 unidades você ganha 1 grátis.")

# Produtos
cols = st.columns(3)

for i, produto in enumerate(PRODUTOS):
    with cols[i]:
        st.image(produto["imagem"], use_container_width=True)

        st.subheader(produto["nome"])
        st.write(f"R$ {produto['preco']:.2f}")

        qtd = st.number_input(
            "Quantidade",
            min_value=1,
            value=1,
            key=f"qtd_{produto['id']}",
        )

        subtotal, brindes, economia = calcular_preco(
            produto["preco"],
            qtd,
        )

        st.write(f"Total: R$ {subtotal:.2f}")

        if brindes > 0:
            st.success(
                f"🎁 {brindes} grátis | Economia R$ {economia:.2f}"
            )

        if st.button(
            "Adicionar ao Carrinho",
            key=f"add_{produto['id']}",
        ):
            adicionar_carrinho(produto, qtd)
            st.success("Produto adicionado!")

# Sidebar
with st.sidebar:
    st.header("🛒 Carrinho")

    if not st.session_state.carrinho:
        st.write("Carrinho vazio.")
    else:
        total = sum(i["subtotal"] for i in st.session_state.carrinho)

        for item in st.session_state.carrinho:
            st.write(
                f"{item['quantidade']}x {item['nome']} "
                f"- R$ {item['subtotal']:.2f}"
            )

        st.divider()
        st.subheader(f"Total: R$ {total:.2f}")

# Finalização
st.divider()
st.header("Finalizar Pedido")

if st.session_state.carrinho:

    total = sum(i["subtotal"] for i in st.session_state.carrinho)

    linhas = [
        f"- {i['quantidade']}x {i['nome']} "
        f"(R$ {i['subtotal']:.2f})"
        for i in st.session_state.carrinho
    ]

    mensagem = (
        "Olá! Gostaria de confirmar o pedido:\n\n"
        + "\n".join(linhas)
        + f"\n\nTotal: R$ {total:.2f}"
    )

    mensagem_codificada = urllib.parse.quote(mensagem)

    url = (
        "https://wa.me/5555996374854"
        f"?text={mensagem_codificada}"
    )

    st.link_button(
        "📲 Finalizar no WhatsApp",
        url,
    )

else:
    st.info("Adicione produtos ao carrinho.")
