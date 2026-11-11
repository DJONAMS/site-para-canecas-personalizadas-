# Configuração da página
import streamlit as st
st.set_page_config(page_title="Gestão de Pedidos", layout="wide")

# Cabeçalho com Logo e Nome
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("### [LOGO]")
with col2:
    st.title("Nome da Empresa")
    st.subheader("Catálogo e Gestão de Pedidos")

st.divider()

# Banner Promocional
st.error("🎉 PRODUTO DA SEMANA: Canecas Personalizadas com 10% de DESCONTO! Peça já a sua! 🎉")

st.write("")

# Barra Lateral para Filtros
with st.sidebar:
    st.header("Categorias")
    categoria = st.radio("Selecione uma categoria:", ["Todos", "Copos", "Camisas", "Mateiras"])
    st.divider()
    st.header("Dúvidas?")
    if st.button("Falar no WhatsApp"):
        st.link_button("Clique aqui para abrir o chat", "https://wa.me/seu_numero_aqui")

# Área Principal: Grade de Produtos
st.header("Catálogo de Produtos")

# Exemplo de dados de produtos
produtos = [
    {"nome": "Copo Térmico Personalizado", "preco": "R$ 80,00", "cat": "Copos", "destaque": True},
    {"nome": "Camisa Estampada Algodão", "preco": "R$ 60,00", "cat": "Camisas", "destaque": False},
    {"nome": "Mateira em Couro", "preco": "R$ 120,00", "cat": "Mateiras", "destaque": True},
]

# Seção de Destaques
st.subheader("🔥 Produtos em Destaque")
cols_destaque = st.columns(3)
destaques = [p for p in produtos if p["destaque"]]
for index, prod in enumerate(destaques):
    with cols_destaque[index]:
        st.info(prod["nome"])

st.divider()

# Filtrar produtos
if categoria != "Todos":
    produtos = [p for p in produtos if p["cat"] == categoria]

# Criar grade de 3 colunas
cols = st.columns(3)
for index, prod in enumerate(produtos):
    with cols[index % 3]:
        st.image("https://via.placeholder.com/300x200.png?text=Imagem+do+Produto", use_container_width=True)
        st.subheader(prod["nome"])
        st.write(f"**Preço:** {prod['preco']}")
        if st.button(f"Adicionar {prod['nome']}", key=f"btn_{index}"):
            st.success(f"{prod['nome']} adicionado ao pedido!")
