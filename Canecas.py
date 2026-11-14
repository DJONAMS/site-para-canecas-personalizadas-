import base64
import html
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ===============================================================
# CONFIGURAÇÕES - mude aqui
# ===============================================================
SENHA_ADMIN = "admin123"           # troque pela sua senha de administrador
WHATSAPP_NUMERO = "5555996374854"  # número que recebe os pedidos
NOME_EMPRESA = "Nome da Empresa"
FRETE_GRATIS_ACIMA = 300.00        # frete grátis a partir deste valor (0 = desligado)

ARQ_PRODUTOS = "dados_produtos.csv"
ARQ_CLIENTES = "dados_clientes.csv"
ARQ_PEDIDOS = "dados_pedidos.csv"
ARQ_FRETE = "dados_frete.csv"

MODELO_PADRAO = (
    "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/"
    "main/Models/CoffeeMug/glTF-Binary/CoffeeMug.glb"
)

# ---------------------------------------------------------------
# Colunas de cada tabela
# ---------------------------------------------------------------
COLUNAS_PRODUTOS = [
    "categoria", "modelo", "preco", "imagem", "ativo",
    "descricao", "para_que_serve", "medidas", "dicas",
    "sku", "custo", "estoque", "destaque", "tags", "peso_g",
    "prazo_producao_dias", "obs_internas",
]
COLUNAS_FRETE = ["uf", "estado", "valor", "prazo_dias"]
COLUNAS_CLIENTES = [
    "data", "nome", "telefone", "qtd_pedidos",
    "email", "cpf_cnpj", "data_nascimento", "empresa",
    "cep", "endereco", "cidade", "uf",
    "origem", "status", "etiquetas", "ultimo_contato", "proximo_contato",
    "aceita_promocoes", "observacoes",
]
COLUNAS_PEDIDOS = [
    "data", "nome", "telefone", "itens", "total",
    "id_pedido", "status", "pagamento", "forma_pagamento", "codigo_rastreio",
    "previsao_entrega", "obs_internas",
]

STATUS_CLIENTE = ["Novo", "Em negociação", "Cliente ativo", "Cliente fiel (VIP)", "Inativo", "Bloqueado"]
ORIGENS_CLIENTE = ["Site", "Instagram", "Indicação", "WhatsApp", "Feira/Evento", "Outro"]
STATUS_PEDIDO = ["Novo", "Aguardando pagamento", "Pago", "Em produção", "Enviado", "Entregue", "Cancelado"]
STATUS_PAGAMENTO = ["Pendente", "Pago", "Parcial", "Reembolsado"]
FORMAS_PAGAMENTO = ["Pix", "Cartão", "Boleto", "Dinheiro", "Transferência"]

# ---------------------------------------------------------------
# Dados iniciais de exemplo (você edita tudo depois no painel)
# ---------------------------------------------------------------
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
ICONES = {
    "Copos Térmicos": "🥤", "Camisetas": "👕", "Mateiras": "🧉",
    "Bonés": "🧢", "Chaveiros": "🔑", "Almofadas": "🛋️",
}
FRETE_INICIAL = [
    ("RS", "Rio Grande do Sul", 15.0, 3), ("SC", "Santa Catarina", 20.0, 4),
    ("PR", "Paraná", 22.0, 4), ("SP", "São Paulo", 25.0, 5),
    ("RJ", "Rio de Janeiro", 28.0, 5), ("MG", "Minas Gerais", 28.0, 6),
    ("ES", "Espírito Santo", 30.0, 6), ("MS", "Mato Grosso do Sul", 30.0, 6),
    ("MT", "Mato Grosso", 35.0, 7), ("GO", "Goiás", 32.0, 6),
    ("DF", "Distrito Federal", 32.0, 6), ("BA", "Bahia", 38.0, 8),
    ("SE", "Sergipe", 40.0, 8), ("AL", "Alagoas", 40.0, 8),
    ("PE", "Pernambuco", 40.0, 8), ("PB", "Paraíba", 42.0, 9),
    ("RN", "Rio Grande do Norte", 42.0, 9), ("CE", "Ceará", 42.0, 9),
    ("PI", "Piauí", 42.0, 9), ("MA", "Maranhão", 45.0, 10),
    ("TO", "Tocantins", 42.0, 9), ("PA", "Pará", 48.0, 10),
    ("AP", "Amapá", 55.0, 12), ("AM", "Amazonas", 55.0, 12),
    ("RR", "Roraima", 58.0, 12), ("RO", "Rondônia", 50.0, 11),
    ("AC", "Acre", 58.0, 12),
]
FICHA_PADRAO = {
    "Copos Térmicos": (
        "Copo térmico em aço inox com tampa, ideal para levar a bebida para qualquer lugar.",
        "Manter bebidas geladas ou quentes por horas, no trabalho, na academia ou na viagem.",
        "Capacidade 500 ml | Altura 20 cm | Aço inox",
        "Lave à mão com detergente neutro. Não leve ao micro-ondas.",
    ),
    "Camisetas": (
        "Camiseta 100% algodão, confortável e pronta para receber a sua arte.",
        "Uniformes de equipe, eventos, presentes e brindes personalizados.",
        "Tamanhos P ao GG | Algodão penteado",
        "Lave do avesso em água fria para a estampa durar mais.",
    ),
    "Mateiras": (
        "Mateira completa com bolsa para garrafa térmica, cuia e acessórios.",
        "Levar o chimarrão com praticidade para a rua, o campo ou a viagem.",
        "Cabe garrafa de até 1 litro | Alça ajustável",
        "Limpe com pano úmido. Evite deixar molhada guardada.",
    ),
    "Bonés": (
        "Boné com regulagem traseira, aba curva e ótimo caimento.",
        "Proteger do sol e compor o visual, ótimo para brindes e equipes.",
        "Tamanho único ajustável | Aba curva",
        "Lave à mão e seque à sombra para manter o formato.",
    ),
    "Chaveiros": (
        "Chaveiro resistente com personalização de nome, logo ou frase.",
        "Lembrancinhas, brindes de empresa e presentes para quem você gosta.",
        "Cerca de 5 cm | Argola metálica",
        "Evite contato prolongado com água para preservar a arte.",
    ),
    "Almofadas": (
        "Almofada macia com capa removível e estampa personalizada.",
        "Decorar a casa, presentear e criar lembranças especiais.",
        "40 x 40 cm | Capa com zíper | Enchimento em fibra",
        "Retire a capa para lavar. Seque à sombra.",
    ),
}

# ===============================================================
# PÁGINA E TEMA CLARO
# ===============================================================
st.set_page_config(page_title="Catálogo Completo de Personalizados", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #f4f6fb !important;
        color: #1a2233 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    [data-testid="stHeader"] { background-color: #f4f6fb !important; }
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #d9dfeb;
    }
    h1, h2, h3, h4, h5, h6, p, span, label, li, div,
    [data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"], [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: #1a2233;
    }
    [data-testid="stCaptionContainer"] p { color: #4a5568 !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border: 1px solid #d9dfeb !important;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(26, 34, 51, 0.06);
    }
    input, textarea, [data-baseweb="input"], [data-baseweb="base-input"] {
        background-color: #ffffff !important;
        color: #1a2233 !important;
    }
    [data-baseweb="input"] { border: 1px solid #b8c2d6 !important; border-radius: 8px; }
    .stButton > button, .stDownloadButton > button, .stLinkButton > a {
        background-color: #ffffff;
        color: #1d4ed8 !important;
        border: 1.5px solid #1d4ed8;
        border-radius: 10px;
        font-weight: 600;
    }
    .stButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover {
        background-color: #eaf0ff;
        border-color: #1e40af;
        color: #1e40af !important;
    }
    .stButton > button[kind="primary"], .stLinkButton > a[kind="primary"] {
        background-color: #1d4ed8;
        color: #ffffff !important;
        border: 1.5px solid #1d4ed8;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1e40af;
        color: #ffffff !important;
    }
    .stButton > button p, .stDownloadButton > button p { color: inherit !important; }
    [data-testid="stExpander"] {
        background-color: #ffffff;
        border: 1px solid #d9dfeb;
        border-radius: 12px;
    }
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color: #1a2233 !important; }
    button[data-baseweb="tab"] p { color: #1a2233 !important; font-weight: 600; }
    .floating-summary {
        background-color: #eaf0ff;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #b6c8f5;
    }
    .floating-summary h3 { color: #166534 !important; }
    .btn-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #1d4ed8;
        color: #ffffff !important;
        padding: 10px 15px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.25);
        z-index: 1000;
    }
    </style>
    <a href="#" class="btn-top">↑ Topo</a>
""", unsafe_allow_html=True)


# ===============================================================
# IMAGENS
# ===============================================================
def imagem_reserva(categoria: str, rotulo: str = "") -> str:
    """Desenho embutido (SVG) usado quando não há foto ou ela não carrega."""
    icone = ICONES.get(categoria, "🏷️")
    rotulo = html.escape(rotulo or categoria)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">'
        '<rect width="400" height="300" fill="#e3eafc"/>'
        f'<text x="200" y="150" font-size="90" text-anchor="middle">{icone}</text>'
        f'<text x="200" y="235" font-size="20" fill="#1a2233" text-anchor="middle" '
        f'font-family="Arial">{rotulo}</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


def url_imagem_exemplo(categoria: str, numero: int) -> str:
    """Foto de exemplo por palavra-chave (serviço gratuito e instável)."""
    palavras = PALAVRAS_CHAVE.get(categoria, "product")
    return f"https://loremflickr.com/400/300/{palavras}?lock={numero}"


def mostrar_imagem(url: str, categoria: str, rotulo: str = ""):
    """Mostra a foto; se o link estiver vazio ou quebrado, mostra o desenho de reserva."""
    reserva = imagem_reserva(categoria, rotulo)
    url = (url or "").strip()
    if not url:
        url = reserva
    st.markdown(
        f'<img src="{html.escape(url, quote=True)}" '
        f'onerror="this.onerror=null;this.src=\'{reserva}\';" '
        f'style="width:100%;border-radius:8px;aspect-ratio:4/3;object-fit:cover;">',
        unsafe_allow_html=True,
    )


# ===============================================================
# BANCO DE DADOS (arquivos CSV locais)
# ===============================================================
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
        ficha = FICHA_PADRAO.get(cat, ("", "", "", ""))
        for i in range(1, 21):
            linhas.append({
                "categoria": cat,
                "modelo": f"{cat} Modelo {i}",
                "preco": preco + i * 2.5,
                "imagem": url_imagem_exemplo(cat, i),
                "ativo": True,
                "descricao": ficha[0],
                "para_que_serve": ficha[1],
                "medidas": ficha[2],
                "dicas": ficha[3],
                "sku": f"{cat[:3].upper()}-{i:03d}",
                "custo": round(preco * 0.5, 2),
                "estoque": 0,
                "destaque": False,
                "tags": "",
                "peso_g": 0,
                "prazo_producao_dias": 5,
                "obs_internas": "",
            })
    return pd.DataFrame(linhas, columns=COLUNAS_PRODUTOS)


def carregar_produtos() -> pd.DataFrame:
    df = ler_csv(ARQ_PRODUTOS, COLUNAS_PRODUTOS)
    if df.empty:
        df = produtos_iniciais()
        gravar_csv(ARQ_PRODUTOS, df)
    df["preco"] = pd.to_numeric(df["preco"], errors="coerce").fillna(0.0)
    df["custo"] = pd.to_numeric(df["custo"], errors="coerce").fillna(0.0)
    df["estoque"] = pd.to_numeric(df["estoque"], errors="coerce").fillna(0).astype(int)
    df["peso_g"] = pd.to_numeric(df["peso_g"], errors="coerce").fillna(0).astype(int)
    df["prazo_producao_dias"] = pd.to_numeric(df["prazo_producao_dias"], errors="coerce").fillna(0).astype(int)
    for coluna in ["ativo", "destaque"]:
        df[coluna] = df[coluna].astype(str).str.lower().isin(["true", "1", "sim", "verdadeiro"])
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
                "descricao": str(linha["descricao"]),
                "para_que_serve": str(linha["para_que_serve"]),
                "medidas": str(linha["medidas"]),
                "dicas": str(linha["dicas"]),
            })
        catalogo[categoria] = {
            "destaque": {"preco": min(i["preco"] for i in itens), "imagem": itens[0]["imagem"]},
            "itens": itens,
        }
    return catalogo


def carregar_frete() -> pd.DataFrame:
    df = ler_csv(ARQ_FRETE, COLUNAS_FRETE)
    if df.empty:
        df = pd.DataFrame(FRETE_INICIAL, columns=COLUNAS_FRETE)
        gravar_csv(ARQ_FRETE, df)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df["prazo_dias"] = pd.to_numeric(df["prazo_dias"], errors="coerce").fillna(0).astype(int)
    return df


def consultar_cep(cep: str):
    """Consulta o CEP no ViaCEP (gratuito). Devolve um dict ou None."""
    cep = "".join(ch for ch in cep if ch.isdigit())
    if len(cep) != 8:
        return None
    try:
        with urllib.request.urlopen(f"https://viacep.com.br/ws/{cep}/json/", timeout=8) as r:
            dados = json.loads(r.read().decode("utf-8"))
        if dados.get("erro"):
            return None
        return dados
    except Exception:
        return None


def calcular_frete(uf: str, subtotal: float):
    """Devolve (valor, prazo_dias), ou None se o estado não está na tabela."""
    tabela = carregar_frete()
    linha = tabela[tabela["uf"].astype(str).str.upper() == uf.upper()]
    if linha.empty:
        return None
    valor = float(linha.iloc[0]["valor"])
    prazo = int(linha.iloc[0]["prazo_dias"])
    if FRETE_GRATIS_ACIMA > 0 and subtotal >= FRETE_GRATIS_ACIMA:
        valor = 0.0
    return valor, prazo


def registrar_pedido(nome: str, telefone: str, itens_txt: str, total: float):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    frete = st.session_state.get("frete") or {}

    pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
    id_pedido = f"PED-{len(pedidos) + 1:05d}"
    novo = pd.DataFrame([{
        "data": agora, "nome": nome, "telefone": telefone,
        "itens": itens_txt, "total": round(total, 2),
        "id_pedido": id_pedido, "status": "Novo", "pagamento": "Pendente",
        "forma_pagamento": "Pix", "codigo_rastreio": "",
        "previsao_entrega": "", "obs_internas": "",
    }])
    gravar_csv(ARQ_PEDIDOS, pd.concat([pedidos, novo], ignore_index=True))

    clientes = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
    existente = clientes[clientes["telefone"].astype(str) == telefone]
    if existente.empty:
        novo_cli = pd.DataFrame([{
            "data": agora, "nome": nome, "telefone": telefone, "qtd_pedidos": 1,
            "cep": frete.get("cep", ""),
            "endereco": ", ".join(p for p in [frete.get("rua", ""), frete.get("bairro", "")] if p),
            "cidade": frete.get("cidade", ""), "uf": frete.get("uf", ""),
            "origem": "Site", "status": "Novo", "ultimo_contato": agora,
        }])
        clientes = pd.concat([clientes, novo_cli], ignore_index=True)
    else:
        idx = existente.index[0]
        atual = pd.to_numeric(clientes.at[idx, "qtd_pedidos"], errors="coerce")
        clientes.at[idx, "qtd_pedidos"] = int(0 if pd.isna(atual) else atual) + 1
        clientes.at[idx, "ultimo_contato"] = agora
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
if "frete" not in st.session_state:
    st.session_state.frete = None
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
    st.session_state.frete = None  # o subtotal mudou, o frete precisa ser recalculado
    st.session_state.ultimo_adicionado = f"{qtd}x {item['nome']}"


def remover_do_carrinho(indice: int):
    st.session_state.carrinho.pop(indice)
    st.session_state.link_whatsapp = None
    st.session_state.frete = None


def calcular_frete_cliente():
    """Roda ao clicar em Calcular frete: consulta o CEP e aplica a tabela por estado."""
    subtotal = sum(i["subtotal"] for i in st.session_state.carrinho)
    dados = consultar_cep(st.session_state.get("cli_cep", ""))
    if not dados:
        st.session_state.frete = None
        st.session_state.erro_frete = "CEP não encontrado. Confira os 8 números."
        return
    resultado = calcular_frete(dados.get("uf", ""), subtotal)
    if resultado is None:
        st.session_state.frete = None
        st.session_state.erro_frete = "Ainda não entregamos nesse estado. Fale com a gente pelo WhatsApp."
        return
    valor, prazo = resultado
    st.session_state.erro_frete = None
    st.session_state.link_whatsapp = None
    st.session_state.frete = {
        "cep": dados.get("cep", ""),
        "cidade": dados.get("localidade", ""),
        "uf": dados.get("uf", ""),
        "bairro": dados.get("bairro", ""),
        "rua": dados.get("logradouro", ""),
        "valor": valor,
        "prazo": prazo,
        "subtotal_na_hora": subtotal,
    }


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

    frete = st.session_state.get("frete")
    valor_frete = frete["valor"] if frete else 0.0
    total_com_frete = total_geral + valor_frete

    try:
        extra_frete = f" | Frete {frete['uf']}: R$ {valor_frete:.2f}" if frete else ""
        registrar_pedido(nome, telefone, "; ".join(linhas) + extra_frete, total_com_frete)
    except Exception:
        pass  # se o registro falhar, o cliente ainda consegue enviar o pedido

    bloco_entrega = ""
    if frete:
        endereco = ", ".join(p for p in [frete["rua"], frete["bairro"]] if p)
        texto_frete = "Grátis" if valor_frete == 0 else f"R$ {valor_frete:.2f}"
        bloco_entrega = (
            f"\n\n*Entrega:* {endereco} - {frete['cidade']}/{frete['uf']} (CEP {frete['cep']})"
            f"\n*Frete:* {texto_frete} (prazo estimado: {frete['prazo']} dias úteis)"
        )

    msg = (
        f"Olá! Meu nome é {nome}. Gostaria de confirmar meu pedido:\n\n"
        + "\n".join(linhas)
        + f"\n\nSubtotal: R$ {total_geral:.2f}"
        + bloco_entrega
        + f"\n\n*Total Geral: R$ {total_com_frete:.2f}*"
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
          .container {{ width: 100%; height: {height}px; position: relative; border-radius: 8px; overflow: hidden; background: #e3eafc; }}
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
# MODAL DE CATEGORIA (com ficha do produto)
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
                        mostrar_imagem(item["imagem"], categoria_nome, item["nome"])

                    st.markdown(f"**{item['nome']}**")
                    st.markdown(f"### R$ {item['preco']:.2f}")
                    if item["descricao"]:
                        st.caption(item["descricao"])
                    with st.expander("ℹ️ Detalhes do produto"):
                        if item["para_que_serve"]:
                            st.markdown(f"**Para que serve:** {item['para_que_serve']}")
                        if item["medidas"]:
                            st.markdown(f"**Medidas e material:** {item['medidas']}")
                        if item["dicas"]:
                            st.markdown(f"**Dicas de uso:** {item['dicas']}")
                        if not (item["para_que_serve"] or item["medidas"] or item["dicas"]):
                            st.write("Em breve mais detalhes deste produto.")

                    qtd = st.number_input("Qtd", min_value=1, max_value=1000, value=1,
                                          key=f"qtd_{item['id']}")
                    _, brindes, eco = calcular_promocao(item["preco"], qtd)
                    if brindes > 0:
                        st.success(f"+{brindes} brinde(s) grátis! (Economia: R$ {eco:.2f})")
                    st.button("🛒 Adicionar", key=f"add_{item['id']}",
                              use_container_width=True,
                              on_click=callback_adicionar, args=(item,))


# ===============================================================
# BARRA LATERAL: login admin + carrinho + frete + finalização
# ===============================================================
with st.sidebar:
    # A Área do administrador fica recolhida para todos.
    # Quem não sabe a senha não consegue entrar no painel.
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
                <h3>Subtotal: R$ {total_geral:.2f}</h3>
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

        # ----- Frete por CEP -----
        st.subheader("🚚 Calcular frete")
        st.text_input("Seu CEP", key="cli_cep", placeholder="00000-000", max_chars=9)
        st.button("Calcular frete", use_container_width=True, on_click=calcular_frete_cliente)
        if st.session_state.get("erro_frete"):
            st.error(st.session_state.erro_frete)

        frete_atual = st.session_state.get("frete")
        if frete_atual:
            if abs(frete_atual["subtotal_na_hora"] - total_geral) > 0.01:
                st.warning("O carrinho mudou. Clique em Calcular frete de novo.")
            else:
                texto_valor = "Grátis 🎉" if frete_atual["valor"] == 0 else f"R$ {frete_atual['valor']:.2f}"
                st.success(
                    f"Entrega em {frete_atual['cidade']}/{frete_atual['uf']}: {texto_valor} "
                    f"| prazo de {frete_atual['prazo']} dias úteis"
                )
                st.markdown(f"### Total com frete: R$ {total_geral + frete_atual['valor']:.2f}")
        elif FRETE_GRATIS_ACIMA > 0:
            st.caption(f"Frete grátis em pedidos a partir de R$ {FRETE_GRATIS_ACIMA:.2f}")

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
    (aba_resumo, aba_prod, aba_foto, aba_cli, aba_ped,
     aba_frete, aba_backup) = st.tabs([
        "📊 Resumo", "📦 Produtos", "🖼️ Fotos", "👥 Clientes",
        "🧾 Pedidos", "🚚 Frete", "💾 Backup",
    ])

    # ---------------------------------------------------------- RESUMO
    with aba_resumo:
        clientes_r = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
        pedidos_r = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        pedidos_r["total_num"] = pd.to_numeric(pedidos_r["total"], errors="coerce").fillna(0.0)
        validos = pedidos_r[pedidos_r["status"] != "Cancelado"]
        faturamento = validos["total_num"].sum()
        recebido = validos[validos["pagamento"] == "Pago"]["total_num"].sum()
        ticket = faturamento / len(validos) if len(validos) else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pedidos", len(pedidos_r))
        c2.metric("Faturamento", f"R$ {faturamento:,.2f}")
        c3.metric("Já recebido (pago)", f"R$ {recebido:,.2f}")
        c4.metric("Ticket médio", f"R$ {ticket:,.2f}")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Clientes", len(clientes_r))
        c6.metric("Produtos ativos", int(df_produtos["ativo"].sum()))
        c7.metric("Pagamentos pendentes", int((pedidos_r["pagamento"] == "Pendente").sum()))
        c8.metric("Em produção", int((pedidos_r["status"] == "Em produção").sum()))

        st.subheader("⚠️ Atenção")
        sem_estoque = df_produtos[(df_produtos["ativo"]) & (df_produtos["estoque"] <= 0)]
        st.write(f"Produtos ativos com estoque zerado: **{len(sem_estoque)}** "
                 "(se você produz sob encomenda, pode ignorar).")
        hoje = datetime.now().strftime("%Y-%m-%d")
        retornos = clientes_r[(clientes_r["proximo_contato"] != "") & (clientes_r["proximo_contato"] <= hoje)]
        if len(retornos):
            st.warning(f"{len(retornos)} cliente(s) com retorno marcado para hoje ou atrasado:")
            st.dataframe(retornos[["nome", "telefone", "proximo_contato", "status"]],
                         use_container_width=True, hide_index=True)
        else:
            st.write("Nenhum retorno de cliente pendente.")

        if len(clientes_r):
            st.subheader("🏆 Melhores clientes")
            gasto = validos.groupby("telefone")["total_num"].sum().rename("gasto_total")
            top = clientes_r.merge(gasto, on="telefone", how="left").fillna({"gasto_total": 0.0})
            top = top.sort_values("gasto_total", ascending=False).head(5)
            st.dataframe(top[["nome", "telefone", "qtd_pedidos", "gasto_total"]],
                         use_container_width=True, hide_index=True)

    # ---------------------------------------------------------- PRODUTOS
    with aba_prod:
        st.caption(
            "Edite tudo direto na tabela: nome, preço, ficha do produto, estoque, custo e mais. "
            "Use o + no fim da tabela para adicionar um produto novo e a lixeira para apagar. "
            "Clique em Salvar para publicar para os clientes."
        )
        filtro_cat = st.selectbox(
            "Filtrar por categoria",
            ["Todas"] + sorted(df_produtos["categoria"].unique().tolist()),
            key="filtro_cat_admin",
        )
        if filtro_cat == "Todas":
            base_editor = df_produtos
        else:
            base_editor = df_produtos[df_produtos["categoria"] == filtro_cat]

        editado = st.data_editor(
            base_editor, num_rows="dynamic", use_container_width=True,
            key=f"editor_produtos_{filtro_cat}",
            column_config={
                "categoria": st.column_config.TextColumn("Categoria", required=True),
                "modelo": st.column_config.TextColumn("Nome do modelo", required=True),
                "preco": st.column_config.NumberColumn("Preço (R$)", min_value=0.0, format="%.2f"),
                "custo": st.column_config.NumberColumn("Custo (R$)", min_value=0.0, format="%.2f"),
                "estoque": st.column_config.NumberColumn("Estoque", min_value=0, step=1),
                "imagem": st.column_config.TextColumn("Foto (link ou enviada)"),
                "ativo": st.column_config.CheckboxColumn("Ativo"),
                "destaque": st.column_config.CheckboxColumn("Destaque"),
                "descricao": st.column_config.TextColumn("Descrição", width="large"),
                "para_que_serve": st.column_config.TextColumn("Para que serve", width="large"),
                "medidas": st.column_config.TextColumn("Medidas e material"),
                "dicas": st.column_config.TextColumn("Dicas de uso"),
                "sku": st.column_config.TextColumn("Código (SKU)"),
                "tags": st.column_config.TextColumn("Etiquetas"),
                "peso_g": st.column_config.NumberColumn("Peso (g)", min_value=0, step=1),
                "prazo_producao_dias": st.column_config.NumberColumn("Prazo produção (dias)", min_value=0, step=1),
                "obs_internas": st.column_config.TextColumn("Obs. internas (só você vê)"),
            },
        )
        if len(editado) and (editado["custo"] > editado["preco"]).any():
            st.warning("Atenção: há produto com custo maior que o preço de venda.")

        if st.button("💾 Salvar produtos", type="primary", key="salvar_produtos"):
            if filtro_cat == "Todas":
                novo_df = editado
            else:
                resto = df_produtos[df_produtos["categoria"] != filtro_cat]
                novo_df = pd.concat([resto, editado], ignore_index=True)
            gravar_csv(ARQ_PRODUTOS, novo_df)
            st.success("Produtos salvos! Os clientes já veem as mudanças.")
            st.rerun()

        if len(base_editor):
            lucro = (base_editor["preco"] - base_editor["custo"]).mean()
            st.info(f"Lucro médio por unidade nesta lista: R$ {lucro:.2f}")

    # ---------------------------------------------------------- FOTOS
    with aba_foto:
        st.caption(
            "Envie a foto direto do computador ou do celular. Ela fica guardada dentro do cadastro "
            "do produto, então não precisa de link. Fotos até 2 MB."
        )
        categorias_f = sorted(df_produtos["categoria"].unique().tolist())
        if not categorias_f:
            st.info("Cadastre produtos primeiro.")
        else:
            cat_f = st.selectbox("Categoria", categorias_f, key="foto_cat")
            modelos_f = df_produtos[df_produtos["categoria"] == cat_f]["modelo"].tolist()
            mod_f = st.selectbox("Produto", modelos_f, key="foto_mod")
            atual = df_produtos[(df_produtos["categoria"] == cat_f) & (df_produtos["modelo"] == mod_f)].iloc[0]

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Foto atual**")
                mostrar_imagem(atual["imagem"], cat_f, mod_f)
            with col_b:
                st.markdown("**Enviar nova foto**")
                arquivo = st.file_uploader("Escolha a imagem", type=["png", "jpg", "jpeg", "webp"],
                                           key="foto_upload")
                if arquivo is not None:
                    if arquivo.size > 2 * 1024 * 1024:
                        st.error("A foto passa de 2 MB. Diminua o tamanho e tente de novo.")
                    else:
                        st.image(arquivo, caption="Prévia da nova foto", use_container_width=True)
                        if st.button("✅ Usar esta foto neste produto", type="primary", key="foto_salvar"):
                            tipo = arquivo.type or "image/jpeg"
                            b64 = base64.b64encode(arquivo.getvalue()).decode()
                            novo_df = df_produtos.copy()
                            mascara = (novo_df["categoria"] == cat_f) & (novo_df["modelo"] == mod_f)
                            novo_df.loc[mascara, "imagem"] = f"data:{tipo};base64,{b64}"
                            gravar_csv(ARQ_PRODUTOS, novo_df)
                            st.success("Foto salva! Já aparece no catálogo.")
                            st.rerun()
                st.markdown("**Ou colar um link de foto**")
                link_foto = st.text_input("Link direto da imagem", key="foto_link")
                if st.button("Usar este link", key="foto_link_salvar") and link_foto.strip():
                    novo_df = df_produtos.copy()
                    mascara = (novo_df["categoria"] == cat_f) & (novo_df["modelo"] == mod_f)
                    novo_df.loc[mascara, "imagem"] = link_foto.strip()
                    gravar_csv(ARQ_PRODUTOS, novo_df)
                    st.success("Link salvo!")
                    st.rerun()

            st.divider()
            st.markdown("**Aplicar a mesma foto em toda a categoria** (útil para começar)")
            arq_cat = st.file_uploader("Foto para todos os produtos da categoria",
                                       type=["png", "jpg", "jpeg", "webp"], key="foto_upload_cat")
            if arq_cat is not None and arq_cat.size <= 2 * 1024 * 1024:
                if st.button(f"Aplicar em todos de {cat_f}", key="foto_cat_salvar"):
                    b64 = base64.b64encode(arq_cat.getvalue()).decode()
                    novo_df = df_produtos.copy()
                    novo_df.loc[novo_df["categoria"] == cat_f, "imagem"] = f"data:{arq_cat.type};base64,{b64}"
                    gravar_csv(ARQ_PRODUTOS, novo_df)
                    st.success(f"Foto aplicada em todos os produtos de {cat_f}.")
                    st.rerun()
            elif arq_cat is not None:
                st.error("A foto passa de 2 MB.")

    # ---------------------------------------------------------- CLIENTES
    with aba_cli:
        clientes = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
        pedidos_c = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        st.caption(
            "Ficha completa dos clientes. Os dados básicos entram sozinhos quando alguém finaliza "
            "um pedido; o resto você completa aqui. Clique em Salvar para guardar."
        )
        m1, m2, m3 = st.columns(3)
        m1.metric("Clientes cadastrados", len(clientes))
        m2.metric("Aceitam promoções", int((clientes["aceita_promocoes"].astype(str).str.lower() == "true").sum()))
        m3.metric("Clientes fiéis (VIP)", int((clientes["status"] == "Cliente fiel (VIP)").sum()))

        busca = st.text_input("🔎 Buscar por nome, telefone, e-mail, cidade ou empresa", key="busca_cliente")
        filtro_status = st.multiselect("Filtrar por status", STATUS_CLIENTE, key="filtro_status_cli")

        vista = clientes.copy()
        if busca.strip():
            termo = busca.strip().lower()
            mascara = vista[["nome", "telefone", "email", "cidade", "empresa"]].apply(
                lambda col: col.astype(str).str.lower().str.contains(termo, regex=False)).any(axis=1)
            vista = vista[mascara]
        if filtro_status:
            vista = vista[vista["status"].isin(filtro_status)]

        vista = vista.copy()
        vista["aceita_promocoes"] = vista["aceita_promocoes"].astype(str).str.lower() == "true"
        vista["qtd_pedidos"] = pd.to_numeric(vista["qtd_pedidos"], errors="coerce").fillna(0).astype(int)

        cli_editado = st.data_editor(
            vista, num_rows="dynamic", use_container_width=True, key="editor_clientes",
            column_config={
                "data": st.column_config.TextColumn("Cliente desde", disabled=True),
                "nome": st.column_config.TextColumn("Nome", required=True),
                "telefone": st.column_config.TextColumn("WhatsApp", required=True),
                "qtd_pedidos": st.column_config.NumberColumn("Pedidos", min_value=0, step=1),
                "email": st.column_config.TextColumn("E-mail"),
                "cpf_cnpj": st.column_config.TextColumn("CPF / CNPJ"),
                "data_nascimento": st.column_config.TextColumn("Nascimento (dd/mm/aaaa)"),
                "empresa": st.column_config.TextColumn("Empresa"),
                "cep": st.column_config.TextColumn("CEP"),
                "endereco": st.column_config.TextColumn("Endereço"),
                "cidade": st.column_config.TextColumn("Cidade"),
                "uf": st.column_config.TextColumn("UF", max_chars=2),
                "origem": st.column_config.SelectboxColumn("Como chegou", options=ORIGENS_CLIENTE),
                "status": st.column_config.SelectboxColumn("Status", options=STATUS_CLIENTE),
                "etiquetas": st.column_config.TextColumn("Etiquetas"),
                "ultimo_contato": st.column_config.TextColumn("Último contato"),
                "proximo_contato": st.column_config.TextColumn("Próximo contato (aaaa-mm-dd)"),
                "aceita_promocoes": st.column_config.CheckboxColumn("Aceita promoções"),
                "observacoes": st.column_config.TextColumn("Observações", width="large"),
            },
        )
        if st.button("💾 Salvar clientes", type="primary", key="salvar_clientes"):
            if busca.strip() or filtro_status:
                st.warning("Limpe a busca e o filtro antes de salvar, para não perder clientes que estão escondidos.")
            else:
                salvar = cli_editado.copy()
                salvar["aceita_promocoes"] = salvar["aceita_promocoes"].astype(str)
                gravar_csv(ARQ_CLIENTES, salvar)
                st.success("Clientes salvos!")
                st.rerun()

        st.divider()
        st.subheader("📇 Histórico de um cliente")
        if len(clientes):
            nomes = [f"{r['nome']} - {r['telefone']}" for _, r in clientes.iterrows()]
            escolhido = st.selectbox("Escolha o cliente", nomes, key="hist_cliente")
            tel_escolhido = escolhido.rsplit(" - ", 1)[1]
            ficha = clientes[clientes["telefone"].astype(str) == tel_escolhido].iloc[0]
            hist = pedidos_c[pedidos_c["telefone"].astype(str) == tel_escolhido].copy()
            hist["total_num"] = pd.to_numeric(hist["total"], errors="coerce").fillna(0.0)
            gasto_cli = hist[hist["status"] != "Cancelado"]["total_num"].sum()
            h1, h2, h3 = st.columns(3)
            h1.metric("Pedidos", len(hist))
            h2.metric("Total gasto", f"R$ {gasto_cli:,.2f}")
            h3.metric("Status", ficha["status"] or "-")
            if len(hist):
                st.dataframe(hist[["data", "id_pedido", "itens", "total", "status", "pagamento"]].iloc[::-1],
                             use_container_width=True, hide_index=True)
            numero_wa = "".join(ch for ch in tel_escolhido if ch.isdigit())
            if numero_wa:
                st.link_button("💬 Chamar no WhatsApp", f"https://wa.me/{numero_wa}")
        else:
            st.info("Ainda não há clientes. Eles aparecem aqui quando alguém finaliza um pedido.")

        st.download_button("⬇️ Baixar clientes (CSV)", clientes.to_csv(index=False).encode("utf-8"),
                           "clientes.csv", "text/csv")

    # ---------------------------------------------------------- PEDIDOS
    with aba_ped:
        pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        pedidos["total_num"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0.0)
        st.caption(
            "Acompanhe cada pedido: mude o status, marque o pagamento, coloque o código de rastreio "
            "e a previsão de entrega. Clique em Salvar para guardar."
        )
        p1, p2, p3 = st.columns(3)
        p1.metric("Pedidos", len(pedidos))
        p2.metric("Total em pedidos", f"R$ {pedidos['total_num'].sum():,.2f}")
        p3.metric("Aguardando pagamento", int((pedidos["pagamento"] == "Pendente").sum()))

        filtro_status_p = st.multiselect("Filtrar por status do pedido", STATUS_PEDIDO, key="filtro_status_ped")
        vista_p = pedidos.drop(columns=["total_num"])
        if filtro_status_p:
            vista_p = vista_p[vista_p["status"].isin(filtro_status_p)]
        vista_p = vista_p.iloc[::-1]

        ped_editado = st.data_editor(
            vista_p, use_container_width=True, key="editor_pedidos", num_rows="fixed",
            column_config={
                "data": st.column_config.TextColumn("Data", disabled=True),
                "id_pedido": st.column_config.TextColumn("Nº", disabled=True),
                "nome": st.column_config.TextColumn("Cliente", disabled=True),
                "telefone": st.column_config.TextColumn("WhatsApp", disabled=True),
                "itens": st.column_config.TextColumn("Itens", disabled=True, width="large"),
                "total": st.column_config.TextColumn("Total (R$)", disabled=True),
                "status": st.column_config.SelectboxColumn("Status", options=STATUS_PEDIDO),
                "pagamento": st.column_config.SelectboxColumn("Pagamento", options=STATUS_PAGAMENTO),
                "forma_pagamento": st.column_config.SelectboxColumn("Forma", options=FORMAS_PAGAMENTO),
                "codigo_rastreio": st.column_config.TextColumn("Rastreio"),
                "previsao_entrega": st.column_config.TextColumn("Previsão de entrega"),
                "obs_internas": st.column_config.TextColumn("Obs. internas", width="large"),
            },
        )
        if st.button("💾 Salvar pedidos", type="primary", key="salvar_pedidos"):
            completo = pedidos.drop(columns=["total_num"]).copy()
            campos_editaveis = ["status", "pagamento", "forma_pagamento",
                                "codigo_rastreio", "previsao_entrega", "obs_internas"]
            for _, linha in ped_editado.iterrows():
                alvo = completo["id_pedido"] == linha["id_pedido"]
                for campo in campos_editaveis:
                    completo.loc[alvo, campo] = linha[campo]
            gravar_csv(ARQ_PEDIDOS, completo)
            st.success("Pedidos salvos!")
            st.rerun()

        st.download_button("⬇️ Baixar pedidos (CSV)",
                           pedidos.drop(columns=["total_num"]).to_csv(index=False).encode("utf-8"),
                           "pedidos.csv", "text/csv")

    # ---------------------------------------------------------- FRETE
    with aba_frete:
        st.caption(
            "Valor e prazo de entrega por estado. O cliente digita o CEP e o app aplica o valor do "
            f"estado dele. Pedidos a partir de R$ {FRETE_GRATIS_ACIMA:.2f} têm frete grátis "
            "(para mudar, edite FRETE_GRATIS_ACIMA no topo do código)."
        )
        frete_df = carregar_frete()
        frete_editado = st.data_editor(
            frete_df, num_rows="dynamic", use_container_width=True, key="editor_frete",
            column_config={
                "uf": st.column_config.TextColumn("UF", max_chars=2, required=True),
                "estado": st.column_config.TextColumn("Estado", required=True),
                "valor": st.column_config.NumberColumn("Frete (R$)", min_value=0.0, format="%.2f"),
                "prazo_dias": st.column_config.NumberColumn("Prazo (dias úteis)", min_value=0, step=1),
            },
        )
        if st.button("💾 Salvar frete", type="primary", key="salvar_frete"):
            gravar_csv(ARQ_FRETE, frete_editado)
            st.success("Tabela de frete salva!")
            st.rerun()

    # ---------------------------------------------------------- BACKUP
    with aba_backup:
        st.caption(
            "No Streamlit Cloud os arquivos podem ser apagados quando o app reinicia. "
            "Baixe os backups de vez em quando. Para restaurar, envie o arquivo de volta aqui."
        )
        arquivos_backup = [
            ("Produtos", ARQ_PRODUTOS, COLUNAS_PRODUTOS),
            ("Clientes", ARQ_CLIENTES, COLUNAS_CLIENTES),
            ("Pedidos", ARQ_PEDIDOS, COLUNAS_PEDIDOS),
            ("Frete", ARQ_FRETE, COLUNAS_FRETE),
        ]
        for rotulo, caminho, colunas in arquivos_backup:
            st.markdown(f"**{rotulo}**")
            cb1, cb2 = st.columns(2)
            with cb1:
                dados_atuais = ler_csv(caminho, colunas)
                st.download_button(f"⬇️ Baixar {rotulo.lower()} ({len(dados_atuais)} linhas)",
                                   dados_atuais.to_csv(index=False).encode("utf-8"),
                                   f"{rotulo.lower()}.csv", "text/csv", key=f"bk_baixar_{rotulo}")
            with cb2:
                enviado = st.file_uploader(f"Restaurar {rotulo.lower()}", type=["csv"], key=f"bk_up_{rotulo}")
                if enviado is not None and st.button(f"Restaurar {rotulo.lower()} agora", key=f"bk_rest_{rotulo}"):
                    try:
                        novo = pd.read_csv(enviado, dtype=str).fillna("")
                        gravar_csv(caminho, novo)
                        st.success(f"{rotulo} restaurado.")
                        st.rerun()
                    except Exception as erro:
                        st.error(f"Não consegui ler o arquivo: {erro}")
            st.divider()

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
                mostrar_imagem(destaque["imagem"], cat_nome, cat_nome)
                st.subheader(cat_nome)
                st.write(f"A partir de: R$ {destaque['preco']:.2f}")
                if st.button(f"🔍 Ver {qtd_modelos} modelos de {cat_nome}",
                             key=f"btn_cat_{cat_nome}", use_container_width=True):
                    st.session_state.ultimo_adicionado = None
                    abrir_modal_categoria(cat_nome)
