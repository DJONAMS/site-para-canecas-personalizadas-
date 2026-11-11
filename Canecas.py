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

# Barra Lateral - Mascote e Resumo
with st.sidebar:
    st.image("https://media.giphy.com/media/3o7TKMGpxxHOGTdzJC/giphy.gif", caption="Seu assistente!", width=150)
    st.header("🛒 Resumo do Pedido")
    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []
        
    if not st.session_state.carrinho:
        st.write("O carrinho está vazio.")
    else:
        total = sum(item['preco'] for item in st.session_state.carrinho)
        st.write(f"**Total Parcial:** R$ {total:.2f}")

# Área Principal - Produtos com Ação Direta
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
        
        # Botões de ação para cada produto
        if st.button(f"🛒 Adicionar ao Carrinho", key=f"btn_add_{index}"):
            st.session_state.carrinho.append(prod)
            st.success(f"{prod['nome']} adicionado!")
            st.rerun()

st.divider()

# Seção Final do Carrinho e Pagamento (Visível na página principal)
st.header("Finalização do Pedido")

if "carrinho" in st.session_state and st.session_state.carrinho:
    st.write("### Itens Selecionados:")
    for i, item in enumerate(st.session_state.carrinho):
        col_item1, col_item2 = st.columns([4, 1])
        col_item1.write(f"{i+1}. {item['nome']} - R$ {item['preco']:.2f}")
        if col_item2.button("Remover", key=f"remove_{i}"):
            st.session_state.carrinho.pop(i)
            st.rerun()
            
    total_final = sum(item['preco'] for item in st.session_state.carrinho)
    st.subheader(f"Total Geral: R$ {total_final:.2f}")
    st.success(f"Você está R$ {total_final:.2f} mais feliz e muito bem equipado!")
    
    st.divider()
    # Visual aprimorado para a seção de pagamento
    st.markdown("### 💳 Opções de Pagamento Seguras")
    st.info("Aceitamos transferências via Pix (Instantâneo) e Cartões de Crédito/Débito.")
    
    st.subheader("🔑 Pagamento via Pix")
    st.info("Chave Pix (CNPJ/CPF/Celular): **SUA-CHAVE-PIX-AQUI**")
    st.warning("Após realizar o Pix, envie o comprovante abaixo com seu nome.")
    
    itens_texto = ", ".join([i['nome'] for i in st.session_state.carrinho])
    mensagem = f"Olá! Gostaria de confirmar o pedido dos seguintes produtos: {itens_texto}. Segue em anexo o comprovante do pagamento."
    link_whatsapp = f"https://wa.me/seu_numero_aqui?text={st.secrets.get('urlencode', str)(mensagem)}"
    
    st.link_button(
        "💬 Finalizar Pedido no WhatsApp",
        link_whatsapp,
        help="Clique para abrir o WhatsApp e enviar seu pedido"
    )
else:
    st.write("Seu carrinho está vazio. Adicione produtos acima para fechar o pedido.")

