import os
import urllib.parse
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ===============================================================
# CONFIGURAÇÕES - mude aqui
# ===============================================================
SENHA_ADMIN = "admin123"          # troque pela sua senha de administrador
WHATSAPP_NUMERO = "5555996374854"  # número que recebe os pedidos
NOME_EMPRESA = "Nome da Empresa"

ARQ_PRODUTOS = "dados_produtos.csv"
ARQ_CLIENTES = "dados_clientes.csv"
ARQ_PEDIDOS = "dados_pedidos.csv"

MODELO_PADRAO = (
    "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/"
    "main/Models/CoffeeMug/glTF-Binary/CoffeeMug.glb"
)

COLUNAS_PRODUTOS = ["categoria", "modelo", "preco", "imagem", "ativo"]
COLUNAS_CLIENTES = ["data", "nome", "telefone", "qtd_pedidos"]
COLUNAS_PEDIDOS = ["data", "nome", "telefone", "itens", "total"]

# Palavras-chave (em inglês) para as fotos de exemplo de cada categoria.
PALAVRAS_CHAVE = {
    "Copos Térmicos": "tumbler,cup",
    "Camisetas": "tshirt",
    "Mateiras": "thermos,flask",
    "Bonés": "cap,hat",
    "Chaveiros": "keychain",
    "Almofadas": "cushion,pillow",
}
PRECO_BASE = {
    "Copos Térmicos": 80.00, "Camisetas": 55.00, "Mateiras": 90.00,
    "Bonés": 35.00, "Chaveiros": 15.00, "Almofadas": 45.00,
}

# ===============================================================
# PÁGINA E TEMA
# ===============================================================
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
        background-color: #1c2130;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .btn-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #00FF88;
        color: #0f111a !important;
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


# ===============================================================
# BANCO DE DADOS (arquivos CSV locais)
# ===============================================================
def url_imagem_exemplo(categoria: str, numero: int) -> str:
    palavras = PALAVRAS_CHAVE.get(categoria, "product")
    return f"https://loremflickr.com/400/300/{palavras}?lock={numero}"


def ler_csv(arquivo: str, colunas: list) -> pd.DataFrame:
    if os.path.exists(arquivo):
        try:
            df = pd.read_csv(arquivo, dtype=str).fillna("")
            for c in colunas:
                if c not in df.columns:
                    df[c] = ""
            return df[colunas]
        except Exception:
            pass
    return pd.DataFrame(columns=colunas)


def gravar_csv(arquivo: str, df: pd.DataFrame):
    df.to_csv(arquivo, index=False)


def produtos_iniciais() -> pd.DataFrame:
    linhas = []
    for cat, preco in PRECO_BASE.items():
        for i in range(1, 21):
            linhas.append({
                "categoria": cat,
                "modelo": f"{cat} Modelo {i}",
                "preco": preco + i * 2.5,
                "imagem": url_imagem_exemplo(cat, i),
                "ativo": True,
            })
    return pd.DataFrame(linhas, columns=COLUNAS_PRODUTOS)


def carregar_produtos() -> pd.DataFrame:
    df = ler_csv(ARQ_PRODUTOS, COLUNAS_PRODUTOS)
    if df.empty:
        df = produtos_iniciais()
        gravar_csv(ARQ_PRODUTOS, df)
    df["preco"] = pd.to_numeric(df["preco"], errors="coerce").fillna(0.0)
    df["ativo"] = df["ativo"].astype(str).str.lower().isin(["true", "1", "sim", "verdadeiro"])
    return df


def montar_catalogo(df: pd.DataFrame) -> dict:
    catalogo = {}
    df = df[df["ativo"]].reset_index(drop=True)
    for categoria, grupo in df.groupby("categoria", sort=False):
        itens = []
        for n, (_, linha) in enumerate(grupo.iterrows(), start=1):
            itens.append({
                "id": f"{categoria[:3].lower()}{n}".replace(" ", ""),
                "nome": str(linha["modelo"]),
                "preco": float(linha["preco"]),
                "imagem": str(linha["imagem"]) or url_imagem_exemplo(categoria, n),
                "modelo_3d": MODELO_PADRAO,
            })
        catalogo[categoria] = {
            "destaque": {"preco": min(i["preco"] for i in itens), "imagem": itens[0]["imagem"]},
            "itens": itens,
        }
    return catalogo


def registrar_pedido(nome: str, telefone: str, itens_txt: str, total: float):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
    novo = pd.DataFrame([{"data": agora, "nome": nome, "telefone": telefone,
                          "itens": itens_txt, "total": round(total, 2)}])
    gravar_csv(ARQ_PEDIDOS, pd.concat([pedidos, novo], ignore_index=True))

    clientes = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
    existente = clientes[clientes["telefone"].astype(str) == telefone]
    if existente.empty:
        novo_cli = pd.DataFrame([{"data": agora, "nome": nome,
                                  "telefone": telefone, "qtd_pedidos": 1}])
        clientes = pd.concat([clientes, novo_cli], ignore_index=True)
    else:
        idx = existente.index[0]
        atual = pd.to_numeric(clientes.at[idx, "qtd_pedidos"], errors="coerce")
        clientes.at[idx, "qtd_pedidos"] = int(0 if pd.isna(atual) else atual) + 1
    gravar_csv(ARQ_CLIENTES, clientes)


# ===============================================================
# ESTADO DA SESSÃO
# ===============================================================
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "link_whatsapp" not in st.session_state:
    st.session_state.link_whatsapp = None
if "ultimo_adicionado" not in st.session_state:
    st.session_state.ultimo_adicionado = None
if "admin" not in st.session_state:
    st.session_state.admin = False


# ===============================================================
# LÓGICA DO CARRINHO
# ===============================================================
def calcular_promocao(preco_unitario: float, quantidade: int):
    """A cada 10 unidades, 1 é brinde (não muda o total pago, só informa)."""
    brindes = quantidade // 10
    total = quantidade * preco_unitario
    economia = brindes * preco_unitario
    return total, brindes, economia


def adicionar_ao_carrinho(item: dict, quantidade: int):
    for existente in st.session_state.carrinho:
        if existente["id"] == item["id"]:
            nova_qtd = existente["quantidade"] + quantidade
            total, brindes, econ = calcular_promocao(item["preco"], nova_qtd)
            existente.update(quantidade=nova_qtd, unidades_gratis=brindes,
                             desconto=econ, subtotal=total)
            return
    total, brindes, econ = calcular_promocao(item["preco"], quantidade)
    st.session_state.carrinho.append({
        "id": item["id"], "nome": item["nome"], "preco_unitario": item["preco"],
        "quantidade": quantidade, "unidades_gratis": brindes,
        "desconto": econ, "subtotal": total,
    })


def callback_adicionar(item: dict):
    qtd = st.session_state.get(f"qtd_{item['id']}", 1)
    adicionar_ao_carrinho(item, qtd)
    st.session_state.link_whatsapp = None
    st.session_state.ultimo_adicionado = f"{qtd}x {item['nome']}"


def remover_do_carrinho(indice: int):
    st.session_state.carrinho.pop(indice)
    st.session_state.link_whatsapp = None


def finalizar_pedido():
    """Valida os dados do cliente, grava no banco e gera o link do WhatsApp."""
    nome = st.session_state.get("cli_nome", "").strip()
    telefone = "".join(ch for ch in st.session_state.get("cli_tel", "") if ch.isdigit())
    if len(nome) < 2 or len(telefone) < 10:
        st.session_state.erro_cliente = "Preencha seu nome e um WhatsApp válido com DDD."
        return
    st.session_state.erro_cliente = None

    carrinho = st.session_state.carrinho
    total_geral = sum(i["subtotal"] for i in carrinho)
    linhas = []
    for i in carrinho:
        extra = f" (+{i['unidades_gratis']} brinde)" if i["unidades_gratis"] > 0 else ""
        linhas.append(f"- {i['quantidade']}x {i['nome']}{extra} (R$ {i['subtotal']:.2f})")

    try:
        registrar_pedido(nome, telefone, "; ".join(linhas), total_geral)
    except Exception:
        pass  # se o registro falhar, o cliente ainda consegue enviar o pedido

    msg = (
        f"Olá! Meu nome é {nome}. Gostaria de confirmar meu pedido:\n\n"
        + "\n".join(linhas)
        + f"\n\n*Total Geral: R$ {total_geral:.2f}*"
    )
    st.session_state.link_whatsapp = f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(msg)}"


# ===============================================================
# VISUALIZADOR 3D (só renderiza quando o usuário pede)
# ===============================================================
def renderizar_visualizador_3d(item: dict, height: int = 250):
    html_code = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"></script>
        <style>
          body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
          .container {{ width: 100%; height: {height}px; position: relative; border-radius: 8px; overflow: hidden; background: #141824; }}
          model-viewer {{ width: 100%; height: 100%; }}
          .hint {{ position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.7); color: #fff; font-size: 10px; padding: 3px 6px; border-radius: 4px; pointer-events: none; }}
        </style>
      </head>
      <body>
        <div class="container">
          <model-viewer src="{item['modelo_3d']}" alt="{item['nome']}"
            camera-controls touch-action="pan-y" auto-rotate></model-viewer>
          <div class="hint">🔄 Arraste para girar</div>
        </div>
      </body>
    </html>
    """
    components.html(html_code, height=height)


# ===============================================================
# DADOS CARREGADOS
# ===============================================================
df_produtos = carregar_produtos()
CATALOGO = montar_catalogo(df_produtos)


# ===============================================================
# MODAL DE CATEGORIA
# ===============================================================
@st.dialog("Catálogo da Categoria", width="large")
def abrir_modal_categoria(categoria_nome: str):
    itens = CATALOGO[categoria_nome]["itens"]
    st.subheader(f"Modelos Disponíveis: {categoria_nome} ({len(itens)} opções)")
    st.caption("🔥 Promoção: A cada 10 unidades, ganhe 1 brinde!")

    if st.session_state.get("ultimo_adicionado"):
        st.success(f"✅ {st.session_state.ultimo_adicionado} adicionado ao carrinho!")

    qtd_carrinho = sum(i["quantidade"] for i in st.session_state.carrinho)
    total_carrinho = sum(i["subtotal"] for i in st.session_state.carrinho)
    st.info(f"🛒 No carrinho: {qtd_carrinho} item(ns) | Subtotal: R$ {total_carrinho:.2f}")

    if st.button("✅ Fechar e ver carrinho", key=f"fechar_{categoria_nome}", type="primary"):
        st.session_state.ultimo_adicionado = None
        st.rerun()

    st.divider()

    num_colunas = 4
    for linha_inicio in range(0, len(itens), num_colunas):
        cols = st.columns(num_colunas)
        for idx, item in enumerate(itens[linha_inicio:linha_inicio + num_colunas]):
            with cols[idx]:
                with st.container(border=True):
                    if st.toggle("Ver em 3D", key=f"3d_{item['id']}"):
                        renderizar_visualizador_3d(item)
                    else:
                        st.image(item["imagem"], use_container_width=True)

                    st.markdown(f"**{item['nome']}**")
                    st.write(f"Unitário: R$ {item['preco']:.2f}")
                    qtd = st.number_input("Qtd", min_value=1, max_value=1000, value=1,
                                          key=f"qtd_{item['id']}")
                    _, brindes, eco = calcular_promocao(item["preco"], qtd)
                    if brindes > 0:
                        st.success(f"+{brindes} brinde(s) grátis! (Economia: R$ {eco:.2f})")
                    st.button("🛒 Adicionar", key=f"add_{item['id']}",
                              use_container_width=True,
                              on_click=callback_adicionar, args=(item,))


# ===============================================================
# BARRA LATERAL: login admin + carrinho + finalização
# ===============================================================
# A Área do administrador fica recolhida na barra lateral para todos.
# Quem não sabe a senha não consegue entrar no painel.
with st.sidebar:
    with st.expander("🔐 Área do administrador", expanded=st.session_state.admin):
        if st.session_state.admin:
            st.success("Você está no modo administrador.")
            if st.button("Sair do modo administrador"):
                st.session_state.admin = False
                st.rerun()
        else:
            senha = st.text_input("Senha", type="password", key="senha_admin")
            if st.button("Entrar"):
                if senha == SENHA_ADMIN:
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")

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
                info_b = f"(+{item['unidades_gratis']} grátis)" if item["unidades_gratis"] > 0 else ""
                st.write(f"**{item['nome']}**")
                st.write(f"{item['quantidade']}x R$ {item['preco_unitario']:.2f} {info_b} = R$ {item['subtotal']:.2f}")
            with col_btn:
                st.button("🗑️", key=f"del_{item['id']}",
                          on_click=remover_do_carrinho, args=(i,))
            st.divider()

        st.subheader("💳 Finalização (Pix)")
        st.text_input("Seu nome", key="cli_nome")
        st.text_input("Seu WhatsApp (com DDD)", key="cli_tel", placeholder="55999999999")
        if st.session_state.get("erro_cliente"):
            st.error(st.session_state.erro_cliente)

        st.button("📲 Finalizar Pedido via WhatsApp", type="primary",
                  use_container_width=True, on_click=finalizar_pedido)

        if st.session_state.link_whatsapp:
            st.link_button("👉 Clique aqui para enviar no WhatsApp",
                           st.session_state.link_whatsapp, use_container_width=True)

# ===============================================================
# CABEÇALHO
# ===============================================================
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.title("🏷️")
with col_titulo:
    st.title(NOME_EMPRESA)
    st.subheader("Catálogo Completo de Produtos Personalizados")
st.divider()

# ===============================================================
# PAINEL DO ADMINISTRADOR (só aparece com a senha)
# ===============================================================
if st.session_state.admin:
    st.header("⚙️ Painel do Administrador")
    aba_prod, aba_cli, aba_ped = st.tabs(["📦 Produtos", "👥 Clientes", "🧾 Pedidos"])

    with aba_prod:
        st.caption(
            "Edite direto na tabela: nome, preço, link da foto e se o produto está ativo. "
            "Use o + no fim da tabela para adicionar uma linha nova. "
            "Clique em Salvar para publicar."
        )
        editado = st.data_editor(
            df_produtos, num_rows="dynamic", use_container_width=True, key="editor_produtos",
            column_config={
                "categoria": st.column_config.TextColumn("Categoria", required=True),
                "modelo": st.column_config.TextColumn("Nome do modelo", required=True),
                "preco": st.column_config.NumberColumn("Preço (R$)", min_value=0.0, format="%.2f"),
                "imagem": st.column_config.TextColumn("Link da foto"),
                "ativo": st.column_config.CheckboxColumn("Ativo"),
            },
        )
        if st.button("💾 Salvar alterações", type="primary"):
            gravar_csv(ARQ_PRODUTOS, editado)
            st.success("Produtos salvos! Os clientes já veem as mudanças.")
            st.rerun()
        st.download_button("⬇️ Baixar backup dos produtos (CSV)",
                           editado.to_csv(index=False).encode("utf-8"),
                           "produtos.csv", "text/csv")

    with aba_cli:
        clientes = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
        st.metric("Total de clientes cadastrados", len(clientes))
        st.dataframe(clientes, use_container_width=True)
        st.download_button("⬇️ Baixar clientes (CSV)", clientes.to_csv(index=False).encode("utf-8"),
                           "clientes.csv", "text/csv")

    with aba_ped:
        pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        total_vendido = pd.to_numeric(pedidos["total"], errors="coerce").sum()
        c1, c2 = st.columns(2)
        c1.metric("Pedidos registrados", len(pedidos))
        c2.metric("Total em pedidos", f"R$ {total_vendido:,.2f}")
        st.dataframe(pedidos.iloc[::-1], use_container_width=True)
        st.download_button("⬇️ Baixar pedidos (CSV)", pedidos.to_csv(index=False).encode("utf-8"),
                           "pedidos.csv", "text/csv")

    st.divider()

# ===============================================================
# GRADE DE CATEGORIAS (visão do cliente)
# ===============================================================
st.header("📦 Categorias Disponíveis")
st.caption("Clique em qualquer categoria abaixo para abrir a grade completa de modelos personalizáveis.")

if not CATALOGO:
    st.info("Nenhum produto ativo no momento.")

categorias = list(CATALOGO.keys())
num_cols_cat = 3
for inicio in range(0, len(categorias), num_cols_cat):
    cols = st.columns(num_cols_cat)
    for idx, cat_nome in enumerate(categorias[inicio:inicio + num_cols_cat]):
        destaque = CATALOGO[cat_nome]["destaque"]
        qtd_modelos = len(CATALOGO[cat_nome]["itens"])
        with cols[idx]:
            with st.container(border=True):
                st.image(destaque["imagem"], use_container_width=True)
                st.subheader(cat_nome)
                st.write(f"A partir de: R$ {destaque['preco']:.2f}")
                if st.button(f"🔍 Ver {qtd_modelos} modelos de {cat_nome}",
                             key=f"btn_cat_{cat_nome}", use_container_width=True):
                    st.session_state.ultimo_adicionado = None
                    abrir_modal_categoria(cat_nome)
