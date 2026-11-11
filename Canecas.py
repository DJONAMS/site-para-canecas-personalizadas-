import streamlit as st

# Configuração da página
st.set_page_config(page_title="Catálogo e Pedidos", layout="wide")

# Cabeçalho
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("### [LOGO]")
with col2:
    st.title("Nome da Empresa")
    st.subheader("Catálogo de Produtos")

st.divider()

# Barra Lateral - Carrinho, Mascote e Pagamento
with st.sidebar:
    # GIF do Hamster
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueGZueGZueGZueGZueGZueGZueGZueGZueGZueGZueGZueGZueCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxxHOGTdzJC/giphy.gif", caption="Seu assistente!", width=150)
    
    st.header("🛒 Seu Carrinho")
    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []
        
    if not st.session_state.carrinho:
        st.write("O carrinho está vazio.")
    else:
        total = 0
        for item in st.session_state.carrinho:
            st.write(f"- {item['nome']}: R$ {item['preco']:.2f}")
            total += item['preco']
        st.write(f"**Total: R$ {total:.2f}**")
        
        st.divider()
        st.header("💳 Pagamento via Pix")
        st.info("Chave Pix (CNPJ/CPF/Celular): **SUA-CHAVE-PIX-AQUI**")
        st.warning("Após realizar o Pix, envie o comprovante abaixo com seu nome.")
        
        if st.button("Finalizar Pedido no WhatsApp"):
            itens_texto = ", ".join([i['nome'] for i in st.session_state.carrinho])
            mensagem = f"Olá! Gostaria de confirmar o pedido dos seguintes produtos: {itens_texto}. Segue em anexo o comprovante do Pix."
            link_whatsapp = f"https://wa.me/seu_numero_aqui?text={st.secrets.get('urlencode', str)(mensagem)}"
            st.link_button("Enviar Pedido e Comprovante", link_whatsapp)

# Área Principal - Produtos
st.header("Produtos Disponíveis")

produtos = [
    {"nome": "Copo Térmico Personalizado", "preco": 80.00, "cat": "Copos", "imagem": "https://picsum.photos/200"},
    {"nome": "Camisa Estampada Algodão", "preco": 60.00, "cat": "Camisas", "imagem": "https://picsum.photos/201"},
    {"nome": "Mateira em Couro", "preco": 120.00, "cat": "Mateiras", "imagem": "https://picsum.photos/202"}
]

cols = st.columns(3)
for index, prod in enumerate(produtos):
    with cols[index % 3]:
        st.image(prod["imagem"], use_container_width=True)
        st.subheader(prod["nome"])
        st.write(f"**Preço:** R$ {prod['preco']:.2f}")
        if st.button(f"Adicionar {prod['nome']}", key=f"btn_{index}"):
            st.session_state.carrinho.append(prod)
            st.success(f"{prod['nome']} adicionado!")

