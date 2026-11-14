import base64
import html
import json
import os
import random
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ===============================================================
# CONFIGURAÇÕES FIXAS - o resto você muda pelo painel
# ===============================================================
SENHA_ADMIN = "admin123"  # TROQUE por uma senha forte antes de publicar

ARQ_PRODUTOS = "dados_produtos.csv"
ARQ_CLIENTES = "dados_clientes.csv"
ARQ_PEDIDOS = "dados_pedidos.csv"
ARQ_FRETE = "dados_frete.csv"
ARQ_CLIQUES = "dados_cliques.csv"
ARQ_LOJA = "dados_loja.json"

MODELO_PADRAO = (
    "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/"
    "main/Models/CoffeeMug/glTF-Binary/CoffeeMug.glb"
)

# Configurações da loja. Tudo isso você edita na aba Loja do painel.
LOJA_PADRAO = {
    "nome_empresa": "Nome da Empresa",
    "subtitulo": "Catálogo Completo de Produtos Personalizados",
    "frase_banner": "Sua marca, do seu jeito.",
    "whatsapp": "5555996374854",
    "cor_principal": "#1d4ed8",
    "fundo": "Personalização (ícones)",
    "frete_gratis_ligado": True,
    "frete_gratis_acima": 300.0,
    "brinde_a_cada": 10,
    "brinde_ligado": True,
    "pix_chave": "",
    "pix_instrucoes": "Após o pedido, enviaremos a chave Pix pelo WhatsApp.",
    "cartao_ligado": True,
    "link_pagamento_cartao": "",
    "dias_adormecido": 30,
    "msgs_retorno": [
        "Oi {nome}! Faz um tempinho que não nos falamos. Que tal fazer um novo pedido? Comprando 2 produtos você ganha um brinde.",
        "Olá {nome}, sentimos sua falta! Tem novidade no catálogo e um acessório grátis esperando por você no próximo pedido.",
        "{nome}, tudo bem? Passando para lembrar que seus produtos personalizados favoritos estão disponíveis. Quer ver as novidades?",
    ],
    "msg_aniversario": "Parabéns, {nome}! 🎉 Preparamos uma condição especial de aniversário para você. Quer saber?",
    # Modo empresa (venda em lote)
    "empresa_pedido_minimo": 500.0,
    "empresa_frete_gratis": True,
    "empresa_brinde_a_cada": 10,
    "empresa_prazo_lote": "10 a 15 dias úteis",
    "empresa_faixas": [
        {"a_partir_de": 20, "desconto_pct": 5},
        {"a_partir_de": 50, "desconto_pct": 10},
        {"a_partir_de": 100, "desconto_pct": 15},
    ],
}

# ---------------------------------------------------------------
# Colunas de cada tabela
# ---------------------------------------------------------------
COLUNAS_PRODUTOS = [
    "categoria", "modelo", "preco", "imagem", "ativo",
    "descricao", "para_que_serve", "medidas", "dicas",
    "sku", "custo", "estoque", "destaque", "tags", "peso_g",
    "prazo_producao_dias", "obs_internas",
    "preco_promocional", "promo_inicio", "promo_fim", "variacoes",
]
COLUNAS_FRETE = ["uf", "estado", "valor", "prazo_dias"]
COLUNAS_CLIENTES = [
    "data", "nome", "telefone", "qtd_pedidos",
    "email", "cpf_cnpj", "data_nascimento", "empresa",
    "cep", "endereco", "cidade", "uf",
    "origem", "status", "etiquetas", "ultimo_contato", "proximo_contato",
    "aceita_promocoes", "observacoes",
    "tipo", "razao_social", "responsavel",
]
COLUNAS_PEDIDOS = [
    "data", "nome", "telefone", "itens", "total",
    "id_pedido", "status", "pagamento", "forma_pagamento", "codigo_rastreio",
    "previsao_entrega", "obs_internas", "tipo_cliente",
]
COLUNAS_CLIQUES = ["data", "evento", "categoria", "produto"]

STATUS_CLIENTE = ["Novo", "Em negociação", "Cliente ativo", "Cliente fiel (VIP)", "Inativo", "Bloqueado"]
ORIGENS_CLIENTE = ["Site", "Instagram", "Indicação", "WhatsApp", "Feira/Evento", "Outro"]
STATUS_PEDIDO = ["Novo", "Aguardando pagamento", "Pago", "Em produção", "Enviado", "Entregue", "Cancelado"]
STATUS_PAGAMENTO = ["Pendente", "Pago", "Parcial", "Reembolsado"]
FORMAS_PAGAMENTO = ["Pix", "Cartão de crédito", "Cartão de débito", "Boleto", "Dinheiro", "Transferência"]
ETAPAS_PEDIDO = ["Novo", "Pago", "Em produção", "Enviado", "Entregue"]
FUNDOS = ["Personalização (ícones)", "Listras suaves", "Pontinhos", "Liso"]

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
# CONFIGURAÇÃO DA LOJA (arquivo JSON editado pelo painel)
# ===============================================================
def carregar_loja() -> dict:
    loja = json.loads(json.dumps(LOJA_PADRAO))  # cópia
    if os.path.exists(ARQ_LOJA):
        try:
            with open(ARQ_LOJA, "r", encoding="utf-8") as f:
                loja.update(json.load(f))
        except Exception:
            pass
    return loja


def gravar_loja(loja: dict):
    with open(ARQ_LOJA, "w", encoding="utf-8") as f:
        json.dump(loja, f, ensure_ascii=False, indent=2)


LOJA = carregar_loja()

# ===============================================================
# PÁGINA E TEMA CLARO (cor e fundo vêm da aba Loja)
# ===============================================================
st.set_page_config(page_title=LOJA["nome_empresa"], page_icon="🏷️", layout="wide")


def css_fundo(tipo: str) -> str:
    """Fundo decorativo suave, em SVG embutido (não depende de internet)."""
    if tipo == "Liso":
        return "background-color: #f4f6fb !important;"
    if tipo == "Pontinhos":
        svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28'>"
               "<circle cx='3' cy='3' r='1.6' fill='%23c9d3ea'/></svg>")
    elif tipo == "Listras suaves":
        svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'>"
               "<path d='M0 40L40 0' stroke='%23e3e9f7' stroke-width='6'/></svg>")
    else:  # Personalização (ícones)
        icones = ["🥤", "👕", "🧃", "🧢", "🔑", "🛋️"]
        textos = ""
        posicoes = [(25, 40), (110, 85), (190, 30), (70, 150), (160, 175), (235, 120)]
        for (x, y), ic in zip(posicoes, icones):
            textos += (f"<text x='{x}' y='{y}' font-size='28' opacity='0.16' "
                       f"transform='rotate(-12 {x} {y})'>{ic}</text>")
        svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='270' height='210'>{textos}</svg>"
    svg_url = svg.replace("#", "%23").replace('"', "'")
    return ("background-color: #f4f6fb !important; "
            f"background-image: url(\"data:image/svg+xml;utf8,{svg_url}\") !important;")


COR = LOJA["cor_principal"]

st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        {css_fundo(LOJA["fundo"])}
        color: #1a2233 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}
    [data-testid="stSidebar"] {{
        background-color: #ffffff !important;
        border-right: 1px solid #d9dfeb;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label, li, div,
    [data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"], [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {{ color: #1a2233; }}
    [data-testid="stCaptionContainer"] p {{ color: #4a5568 !important; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #ffffff;
        border: 1px solid #d9dfeb !important;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(26, 34, 51, 0.06);
    }}
    input, textarea, [data-baseweb="input"], [data-baseweb="base-input"],
    [data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        color: #1a2233 !important;
    }}
    [data-baseweb="input"] {{ border: 1px solid #b8c2d6 !important; border-radius: 8px; }}
    .stButton > button, .stDownloadButton > button, .stLinkButton > a {{
        background-color: #ffffff;
        color: {COR} !important;
        border: 1.5px solid {COR};
        border-radius: 10px;
        font-weight: 600;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover {{
        background-color: #eef2ff;
        filter: brightness(0.92);
    }}
    .stButton > button[kind="primary"], .stLinkButton > a[kind="primary"] {{
        background-color: {COR};
        color: #ffffff !important;
        border: 1.5px solid {COR};
    }}
    .stButton > button p, .stDownloadButton > button p {{ color: inherit !important; }}
    [data-testid="stExpander"] {{
        background-color: #ffffff;
        border: 1px solid #d9dfeb;
        border-radius: 12px;
    }}
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {{ color: #1a2233 !important; }}
    button[data-baseweb="tab"] p {{ color: #1a2233 !important; font-weight: 600; }}
    .banner {{
        background: linear-gradient(120deg, {COR}, #0ea5e9);
        border-radius: 18px;
        padding: 26px 30px;
        margin-bottom: 18px;
        box-shadow: 0 6px 18px rgba(26,34,51,0.15);
    }}
    .banner h1, .banner p, .banner span {{ color: #ffffff !important; margin: 0; }}
    .banner h1 {{ font-size: 2.1rem; }}
    .cartao-carrinho {{
        display: flex; gap: 10px; align-items: center;
        background: #ffffff; border: 1px solid #d9dfeb; border-radius: 12px;
        padding: 8px; margin-bottom: 8px;
    }}
    .cartao-carrinho img {{ width: 58px; height: 58px; border-radius: 8px; object-fit: cover; }}
    .cartao-carrinho .nome {{ font-weight: 700; font-size: 0.9rem; }}
    .cartao-carrinho .detalhe {{ font-size: 0.8rem; color: #4a5568; }}
    .resumo-total {{
        background: #eaf0ff; border: 1px solid #b6c8f5; border-radius: 12px;
        padding: 12px 14px; margin: 8px 0;
    }}
    .resumo-total .valor {{ font-size: 1.5rem; font-weight: 800; color: #166534; }}
    .selo {{
        display: inline-block; padding: 2px 10px; border-radius: 999px;
        font-size: 0.75rem; font-weight: 700; background: #fee2e2; color: #991b1b;
    }}
    .selo-ok {{ background: #dcfce7; color: #166534; }}
    .selo-promo {{ background: #fef3c7; color: #92400e; }}
    .btn-top {{
        position: fixed; bottom: 20px; right: 20px;
        background-color: {COR}; color: #ffffff !important;
        padding: 10px 15px; border-radius: 50px; text-decoration: none;
        font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.25); z-index: 1000;
    }}
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


def url_segura(url: str, categoria: str, rotulo: str = "") -> str:
    url = (url or "").strip()
    return url if url else imagem_reserva(categoria, rotulo)


def mostrar_imagem(url: str, categoria: str, rotulo: str = ""):
    """Foto com zoom ao passar o mouse. Link vazio ou quebrado vira o desenho de reserva."""
    reserva = imagem_reserva(categoria, rotulo)
    st.markdown(
        '<div style="overflow:hidden;border-radius:8px;cursor:zoom-in;">'
        f'<img src="{html.escape(url_segura(url, categoria, rotulo), quote=True)}" '
        f'onerror="this.onerror=null;this.src=\'{reserva}\';" '
        'style="width:100%;aspect-ratio:4/3;object-fit:cover;display:block;'
        'transition:transform 0.35s ease;" '
        'onmouseover="this.style.transform=\'scale(1.35)\'" '
        'onmouseout="this.style.transform=\'scale(1)\'">'
        '</div>',
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
                "categoria": cat, "modelo": f"{cat} Modelo {i}",
                "preco": preco + i * 2.5, "imagem": url_imagem_exemplo(cat, i),
                "ativo": True, "descricao": ficha[0], "para_que_serve": ficha[1],
                "medidas": ficha[2], "dicas": ficha[3],
                "sku": f"{cat[:3].upper()}-{i:03d}", "custo": round(preco * 0.5, 2),
                "estoque": 0, "destaque": False, "tags": "", "peso_g": 0,
                "prazo_producao_dias": 5, "obs_internas": "",
                "preco_promocional": 0.0, "promo_inicio": "", "promo_fim": "", "variacoes": "",
            })
    return pd.DataFrame(linhas, columns=COLUNAS_PRODUTOS)


def carregar_produtos() -> pd.DataFrame:
    df = ler_csv(ARQ_PRODUTOS, COLUNAS_PRODUTOS)
    if df.empty:
        df = produtos_iniciais()
        gravar_csv(ARQ_PRODUTOS, df)
    for c in ["preco", "custo", "preco_promocional"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    for c in ["estoque", "peso_g", "prazo_producao_dias"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    for c in ["ativo", "destaque"]:
        df[c] = df[c].astype(str).str.lower().isin(["true", "1", "sim", "verdadeiro"])
    return df


def preco_atual(linha) -> tuple:
    """Devolve (preco_efetivo, em_promocao). Promo vale entre promo_inicio e promo_fim."""
    preco = float(linha["preco"])
    promo = float(linha["preco_promocional"] or 0)
    if promo <= 0 or promo >= preco:
        return preco, False
    hoje = datetime.now().strftime("%Y-%m-%d")
    ini = str(linha["promo_inicio"] or "").strip()
    fim = str(linha["promo_fim"] or "").strip()
    if (ini and hoje < ini) or (fim and hoje > fim):
        return preco, False
    return promo, True


def montar_catalogo(df: pd.DataFrame) -> dict:
    catalogo = {}
    df = df[df["ativo"]].reset_index(drop=True)
    for categoria, grupo in df.groupby("categoria", sort=False):
        itens = []
        for n, (_, linha) in enumerate(grupo.iterrows(), start=1):
            efetivo, em_promo = preco_atual(linha)
            itens.append({
                "id": f"{categoria[:3].lower()}{n}".replace(" ", ""),
                "nome": str(linha["modelo"]),
                "preco": efetivo,
                "preco_cheio": float(linha["preco"]),
                "em_promo": em_promo,
                "imagem": str(linha["imagem"]) or url_imagem_exemplo(categoria, n),
                "modelo_3d": MODELO_PADRAO,
                "descricao": str(linha["descricao"]),
                "para_que_serve": str(linha["para_que_serve"]),
                "medidas": str(linha["medidas"]),
                "dicas": str(linha["dicas"]),
                "variacoes": [v.strip() for v in str(linha["variacoes"]).split(",") if v.strip()],
                "destaque": bool(linha["destaque"]),
                "estoque": int(linha["estoque"]),
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


def calcular_frete(uf: str, subtotal: float, empresa: bool = False):
    """Devolve (valor, prazo_dias), ou None se o estado não está na tabela."""
    tabela = carregar_frete()
    linha = tabela[tabela["uf"].astype(str).str.upper() == uf.upper()]
    if linha.empty:
        return None
    valor = float(linha.iloc[0]["valor"])
    prazo = int(linha.iloc[0]["prazo_dias"])
    gratis_loja = LOJA["frete_gratis_ligado"] and LOJA["frete_gratis_acima"] > 0 \
        and subtotal >= LOJA["frete_gratis_acima"]
    gratis_empresa = empresa and LOJA["empresa_frete_gratis"]
    if gratis_loja or gratis_empresa:
        valor = 0.0
    return valor, prazo


def registrar_clique(evento: str, categoria: str = "", produto: str = ""):
    """Guarda um clique anônimo (sem nome) para a aba Interesse do painel."""
    try:
        df = ler_csv(ARQ_CLIQUES, COLUNAS_CLIQUES)
        novo = pd.DataFrame([{"data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                              "evento": evento, "categoria": categoria, "produto": produto}])
        gravar_csv(ARQ_CLIQUES, pd.concat([df, novo], ignore_index=True))
    except Exception:
        pass  # nunca deixa o cliente sem catálogo por causa de um registro


def registrar_pedido(nome: str, telefone: str, itens_txt: str, total: float, forma: str):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    frete = st.session_state.get("frete") or {}
    empresa = st.session_state.get("empresa") or {}
    tipo = "Empresa" if st.session_state.get("modo") == "empresa" else "Cliente"

    pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
    id_pedido = f"PED-{len(pedidos) + 1:05d}"
    novo = pd.DataFrame([{
        "data": agora, "nome": nome, "telefone": telefone,
        "itens": itens_txt, "total": round(total, 2),
        "id_pedido": id_pedido, "status": "Novo", "pagamento": "Pendente",
        "forma_pagamento": forma, "codigo_rastreio": "",
        "previsao_entrega": "", "obs_internas": "", "tipo_cliente": tipo,
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
            "tipo": tipo, "cpf_cnpj": empresa.get("cnpj", ""),
            "razao_social": empresa.get("razao_social", ""),
            "responsavel": empresa.get("responsavel", ""),
            "empresa": empresa.get("razao_social", ""),
        }])
        clientes = pd.concat([clientes, novo_cli], ignore_index=True)
    else:
        idx = existente.index[0]
        atual = pd.to_numeric(clientes.at[idx, "qtd_pedidos"], errors="coerce")
        clientes.at[idx, "qtd_pedidos"] = int(0 if pd.isna(atual) else atual) + 1
        clientes.at[idx, "ultimo_contato"] = agora
    gravar_csv(ARQ_CLIENTES, clientes)
    return id_pedido


# ===============================================================
# ESTADO DA SESSÃO
# ===============================================================
ESTADO_INICIAL = {
    "carrinho": [], "link_whatsapp": None, "ultimo_adicionado": None,
    "admin": False, "frete": None, "modo": None, "empresa": None,
    "ultimo_pedido_id": None,
}
for chave, valor in ESTADO_INICIAL.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor
# ===============================================================
# LÓGICA DO CARRINHO (com modo empresa e preço por lote)
# ===============================================================
def modo_empresa() -> bool:
    return st.session_state.get("modo") == "empresa"


def desconto_lote(quantidade_total: int) -> int:
    """Desconto (%) do modo empresa conforme a quantidade total no carrinho."""
    pct = 0
    for faixa in sorted(LOJA["empresa_faixas"], key=lambda f: f["a_partir_de"]):
        if quantidade_total >= faixa["a_partir_de"]:
            pct = faixa["desconto_pct"]
    return pct


def calcular_promocao(preco_unitario: float, quantidade: int):
    """A cada N unidades, 1 é brinde (N vem da aba Loja; empresas têm o seu próprio N)."""
    a_cada = LOJA["empresa_brinde_a_cada"] if modo_empresa() else LOJA["brinde_a_cada"]
    ligado = LOJA["brinde_ligado"] and a_cada > 0
    brindes = quantidade // int(a_cada) if ligado else 0
    total = quantidade * preco_unitario
    economia = brindes * preco_unitario
    return total, brindes, economia


def adicionar_ao_carrinho(item: dict, quantidade: int, variacao: str = ""):
    chave = item["id"] + ("|" + variacao if variacao else "")
    nome = item["nome"] + (f" ({variacao})" if variacao else "")
    for existente in st.session_state.carrinho:
        if existente["id"] == chave:
            nova_qtd = existente["quantidade"] + quantidade
            total, brindes, econ = calcular_promocao(item["preco"], nova_qtd)
            existente.update(quantidade=nova_qtd, unidades_gratis=brindes,
                             desconto=econ, subtotal=total)
            return
    total, brindes, econ = calcular_promocao(item["preco"], quantidade)
    st.session_state.carrinho.append({
        "id": chave, "nome": nome, "preco_unitario": item["preco"],
        "quantidade": quantidade, "unidades_gratis": brindes,
        "desconto": econ, "subtotal": total, "imagem": item["imagem"],
        "categoria": item.get("categoria", ""),
    })


def callback_adicionar(item: dict):
    qtd = st.session_state.get(f"qtd_{item['id']}", 1)
    variacao = st.session_state.get(f"var_{item['id']}", "")
    adicionar_ao_carrinho(item, qtd, variacao)
    registrar_clique("adicionou_carrinho", item.get("categoria", ""), item["nome"])
    st.session_state.link_whatsapp = None
    st.session_state.frete = None  # o subtotal mudou, o frete precisa ser recalculado
    st.session_state.ultimo_adicionado = f"{qtd}x {item['nome']}"


def remover_do_carrinho(indice: int):
    st.session_state.carrinho.pop(indice)
    st.session_state.link_whatsapp = None
    st.session_state.frete = None


def totais_carrinho():
    """Devolve (subtotal, quantidade, desconto_lote_pct, valor_do_desconto, total)."""
    subtotal = sum(i["subtotal"] for i in st.session_state.carrinho)
    qtd = sum(i["quantidade"] for i in st.session_state.carrinho)
    pct = desconto_lote(qtd) if modo_empresa() else 0
    valor_desc = subtotal * pct / 100
    return subtotal, qtd, pct, valor_desc, subtotal - valor_desc


def calcular_frete_cliente():
    """Roda ao clicar em Calcular frete: consulta o CEP e aplica a tabela por estado."""
    _, _, _, _, total = totais_carrinho()
    dados = consultar_cep(st.session_state.get("cli_cep", ""))
    if not dados:
        st.session_state.frete = None
        st.session_state.erro_frete = "CEP não encontrado. Confira os 8 números."
        return
    resultado = calcular_frete(dados.get("uf", ""), total, modo_empresa())
    if resultado is None:
        st.session_state.frete = None
        st.session_state.erro_frete = "Ainda não entregamos nesse estado. Fale com a gente pelo WhatsApp."
        return
    valor, prazo = resultado
    st.session_state.erro_frete = None
    st.session_state.link_whatsapp = None
    st.session_state.frete = {
        "cep": dados.get("cep", ""), "cidade": dados.get("localidade", ""),
        "uf": dados.get("uf", ""), "bairro": dados.get("bairro", ""),
        "rua": dados.get("logradouro", ""), "valor": valor, "prazo": prazo,
        "total_na_hora": total,
    }


def finalizar_pedido():
    """Valida os dados, grava o pedido e gera o link do WhatsApp."""
    nome = st.session_state.get("cli_nome", "").strip()
    telefone = "".join(ch for ch in st.session_state.get("cli_tel", "") if ch.isdigit())
    forma = st.session_state.get("forma_pag", "Pix")
    if len(nome) < 2 or len(telefone) < 10:
        st.session_state.erro_cliente = "Preencha seu nome e um WhatsApp válido com DDD."
        return
    subtotal, qtd, pct, valor_desc, total = totais_carrinho()
    if modo_empresa() and subtotal < LOJA["empresa_pedido_minimo"]:
        st.session_state.erro_cliente = (
            f"O pedido mínimo para empresas é R$ {LOJA['empresa_pedido_minimo']:.2f}.")
        return
    st.session_state.erro_cliente = None

    linhas = []
    for i in st.session_state.carrinho:
        extra = f" (+{i['unidades_gratis']} brinde)" if i["unidades_gratis"] > 0 else ""
        linhas.append(f"- {i['quantidade']}x {i['nome']}{extra} (R$ {i['subtotal']:.2f})")

    frete = st.session_state.get("frete")
    valor_frete = frete["valor"] if frete else 0.0
    total_com_frete = total + valor_frete

    id_pedido = ""
    try:
        extra_frete = f" | Frete {frete['uf']}: R$ {valor_frete:.2f}" if frete else ""
        id_pedido = registrar_pedido(nome, telefone, "; ".join(linhas) + extra_frete,
                                     total_com_frete, forma)
        st.session_state.ultimo_pedido_id = id_pedido
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
    bloco_desc = f"\nDesconto empresa ({pct}%): -R$ {valor_desc:.2f}" if pct else ""
    bloco_empresa = ""
    emp = st.session_state.get("empresa")
    if modo_empresa() and emp:
        bloco_empresa = f"\n*Empresa:* {emp['razao_social']} (CNPJ {emp['cnpj']}) - resp.: {emp['responsavel']}"

    msg = (
        f"Olá! Meu nome é {nome}. Pedido {id_pedido}:\n\n"
        + "\n".join(linhas)
        + f"\n\nSubtotal: R$ {subtotal:.2f}" + bloco_desc + bloco_entrega + bloco_empresa
        + f"\n\n*Total Geral: R$ {total_com_frete:.2f}*"
        + f"\n*Pagamento:* {forma}"
        + (f"\n\nPara acompanhar, use o número {id_pedido} no site." if id_pedido else "")
    )
    st.session_state.link_whatsapp = f"https://wa.me/{LOJA['whatsapp']}?text={urllib.parse.quote(msg)}"


# ===============================================================
# VISUALIZADOR 3D E TELA DE ZOOM
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
          <model-viewer src="{item['modelo_3d']}" alt="{html.escape(item['nome'])}"
            camera-controls touch-action="pan-y" auto-rotate></model-viewer>
          <div class="hint">🔄 Arraste para girar</div>
        </div>
      </body>
    </html>
    """
    components.html(html_code, height=height)


@st.dialog("Ver de perto", width="large")
def mostrar_imagem_zoom(item: dict, categoria: str):
    """Tela flutuante grande: foto ampliada com lupa que segue o mouse, ou o 3D."""
    registrar_clique("ver_de_perto", categoria, item["nome"])
    st.subheader(item["nome"])
    modo = st.radio("Como ver", ["🔍 Foto ampliada", "🔄 Modelo 3D"],
                    horizontal=True, key=f"modo_zoom_{item['id']}")
    if modo.startswith("🔍"):
        reserva = imagem_reserva(categoria, item["nome"])
        url = url_segura(item["imagem"], categoria, item["nome"])
        componente = f"""
        <div id="lupa" style="width:100%;height:520px;overflow:hidden;border-radius:10px;
             background:#e3eafc;position:relative;cursor:zoom-in;">
          <img id="foto" src="{html.escape(url, quote=True)}"
               onerror="this.onerror=null;this.src='{reserva}';"
               style="width:100%;height:100%;object-fit:contain;
                      transition:transform 0.15s ease;transform-origin:center;">
        </div>
        <script>
          const caixa = document.getElementById('lupa');
          const foto = document.getElementById('foto');
          caixa.addEventListener('mousemove', function(e) {{
            const r = caixa.getBoundingClientRect();
            const x = ((e.clientX - r.left) / r.width) * 100;
            const y = ((e.clientY - r.top) / r.height) * 100;
            foto.style.transformOrigin = x + '% ' + y + '%';
            foto.style.transform = 'scale(2.6)';
          }});
          caixa.addEventListener('mouseleave', function() {{
            foto.style.transform = 'scale(1)';
            foto.style.transformOrigin = 'center';
          }});
        </script>
        """
        components.html(componente, height=540)
        st.caption("Passe o mouse sobre a foto para ver os detalhes. No celular, toque na foto.")
    else:
        renderizar_visualizador_3d(item, height=520)
    if item.get("descricao"):
        st.write(item["descricao"])


# ===============================================================
# DADOS CARREGADOS
# ===============================================================
df_produtos = carregar_produtos()
CATALOGO = montar_catalogo(df_produtos)
for _cat, _dados in CATALOGO.items():
    for _it in _dados["itens"]:
        _it["categoria"] = _cat


# ===============================================================
# MODAL DE CATEGORIA (ficha do produto, preço, promoção, variações)
# ===============================================================
@st.dialog("Catálogo da Categoria", width="large")
def abrir_modal_categoria(categoria_nome: str):
    registrar_clique("abriu_categoria", categoria_nome)
    itens = CATALOGO[categoria_nome]["itens"]
    st.subheader(f"Modelos Disponíveis: {categoria_nome} ({len(itens)} opções)")
    if LOJA["brinde_ligado"] and LOJA["brinde_a_cada"] > 0:
        a_cada = LOJA["empresa_brinde_a_cada"] if modo_empresa() else LOJA["brinde_a_cada"]
        st.caption(f"🔥 Promoção: a cada {a_cada} unidades, ganhe 1 brinde!")
    if modo_empresa():
        st.info("🏢 Modo empresa: o desconto por lote é aplicado no carrinho.")

    if st.session_state.get("ultimo_adicionado"):
        st.success(f"✅ {st.session_state.ultimo_adicionado} adicionado ao carrinho!")

    sub, qtd_c, _, _, _ = totais_carrinho()
    st.info(f"🛒 No carrinho: {qtd_c} item(ns) | Subtotal: R$ {sub:.2f}")
    if st.button("✅ Fechar e ver carrinho", key=f"fechar_{categoria_nome}", type="primary"):
        st.session_state.ultimo_adicionado = None
        st.rerun()
    st.divider()

    num_colunas = 3
    for linha_inicio in range(0, len(itens), num_colunas):
        cols = st.columns(num_colunas)
        for idx, item in enumerate(itens[linha_inicio:linha_inicio + num_colunas]):
            with cols[idx]:
                with st.container(border=True):
                    mostrar_imagem(item["imagem"], categoria_nome, item["nome"])
                    if st.button("🔍 Ver de perto / 3D", key=f"zoom_{item['id']}",
                                 use_container_width=True):
                        mostrar_imagem_zoom(item, categoria_nome)

                    st.markdown(f"**{item['nome']}**")
                    if item["em_promo"]:
                        st.markdown(
                            f"<span class='selo selo-promo'>PROMOÇÃO</span> "
                            f"<s>R$ {item['preco_cheio']:.2f}</s>",
                            unsafe_allow_html=True)
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

                    if item["variacoes"]:
                        st.selectbox("Tamanho / cor", item["variacoes"], key=f"var_{item['id']}")
                    qtd = st.number_input("Qtd", min_value=1, max_value=10000, value=1,
                                          key=f"qtd_{item['id']}")
                    _, brindes, eco = calcular_promocao(item["preco"], qtd)
                    if brindes > 0:
                        st.success(f"+{brindes} brinde(s) grátis! (Economia: R$ {eco:.2f})")
                    st.button("🛒 Adicionar", key=f"add_{item['id']}",
                              use_container_width=True,
                              on_click=callback_adicionar, args=(item,))


# ===============================================================
# ACOMPANHAR MEU PEDIDO (o cliente consulta)
# ===============================================================
@st.dialog("Acompanhar meu pedido", width="large")
def abrir_acompanhamento():
    st.write("Digite o número do pedido e o WhatsApp usado na compra.")
    num = st.text_input("Número do pedido (ex.: PED-00001)", key="acomp_num").strip().upper()
    tel = "".join(ch for ch in st.text_input("Seu WhatsApp", key="acomp_tel") if ch.isdigit())
    if st.button("Consultar", type="primary", key="acomp_ok"):
        pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        achado = pedidos[(pedidos["id_pedido"] == num) & (pedidos["telefone"].astype(str) == tel)]
        if achado.empty:
            st.error("Não encontrei esse pedido. Confira o número e o WhatsApp.")
            return
        p = achado.iloc[0]
        st.success(f"Pedido {p['id_pedido']} de {p['data']}")
        if p["status"] == "Cancelado":
            st.error("Este pedido foi cancelado. Fale com a gente pelo WhatsApp.")
        else:
            atual = ETAPAS_PEDIDO.index(p["status"]) if p["status"] in ETAPAS_PEDIDO else 0
            if p["status"] == "Aguardando pagamento":
                atual = 0
            colunas = st.columns(len(ETAPAS_PEDIDO))
            for k, etapa in enumerate(ETAPAS_PEDIDO):
                with colunas[k]:
                    marca = "✅" if k < atual else ("🟢" if k == atual else "⚪")
                    st.markdown(f"<div style='text-align:center'>{marca}<br><small>{etapa}</small></div>",
                                unsafe_allow_html=True)
            st.progress((atual + 1) / len(ETAPAS_PEDIDO))
        d1, d2 = st.columns(2)
        d1.metric("Pagamento", p["pagamento"] or "-")
        d2.metric("Previsão de entrega", p["previsao_entrega"] or "a definir")
        if p["codigo_rastreio"]:
            st.info(f"Código de rastreio: **{p['codigo_rastreio']}**")
        st.caption(f"Itens: {p['itens']}")


# ===============================================================
# BARRA LATERAL: carrinho em cartões + frete + pagamento + finalização
# ===============================================================
with st.sidebar:
    st.header("🛒 Seu Carrinho")
    if not st.session_state.carrinho:
        st.info("O carrinho está vazio. Escolha uma categoria para começar.")
    else:
        subtotal, qtd_total, pct_lote, valor_desc, total_geral = totais_carrinho()

        # ----- Cartões dos itens, com foto em miniatura -----
        for i, item in enumerate(st.session_state.carrinho):
            reserva = imagem_reserva(item.get("categoria", ""), item["nome"])
            foto = html.escape(url_segura(item.get("imagem", ""), item.get("categoria", ""), item["nome"]), quote=True)
            brinde = (f"<br><span class='selo selo-ok'>+{item['unidades_gratis']} brinde</span>"
                      if item["unidades_gratis"] > 0 else "")
            st.markdown(
                f"<div class='cartao-carrinho'>"
                f"<img src='{foto}' onerror=\"this.onerror=null;this.src='{reserva}';\">"
                f"<div><div class='nome'>{html.escape(item['nome'])}</div>"
                f"<div class='detalhe'>{item['quantidade']}x R$ {item['preco_unitario']:.2f}</div>"
                f"<div class='detalhe'><b>R$ {item['subtotal']:.2f}</b>{brinde}</div></div></div>",
                unsafe_allow_html=True)
            st.button("🗑️ Remover", key=f"del_{i}_{item['id']}",
                      on_click=remover_do_carrinho, args=(i,), use_container_width=True)

        # ----- Resumo -----
        linha_desc = (f"<div>Desconto empresa ({pct_lote}%): -R$ {valor_desc:.2f}</div>" if pct_lote else "")
        st.markdown(
            f"<div class='resumo-total'><div>{qtd_total} item(ns)</div>"
            f"<div>Subtotal: R$ {subtotal:.2f}</div>{linha_desc}"
            f"<div class='valor'>R$ {total_geral:.2f}</div></div>",
            unsafe_allow_html=True)
        if modo_empresa():
            if subtotal < LOJA["empresa_pedido_minimo"]:
                st.warning(f"Pedido mínimo para empresas: R$ {LOJA['empresa_pedido_minimo']:.2f}.")
            proxima = [f for f in sorted(LOJA["empresa_faixas"], key=lambda f: f["a_partir_de"])
                       if f["a_partir_de"] > qtd_total]
            if proxima:
                st.caption(f"Faltam {proxima[0]['a_partir_de'] - qtd_total} unidade(s) para "
                           f"{proxima[0]['desconto_pct']}% de desconto.")

        # ----- Frete por CEP -----
        with st.container(border=True):
            st.subheader("🚚 Calcular frete")
            st.text_input("Seu CEP", key="cli_cep", placeholder="00000-000", max_chars=9)
            st.button("Calcular frete", use_container_width=True, on_click=calcular_frete_cliente)
            if st.session_state.get("erro_frete"):
                st.error(st.session_state.erro_frete)
            frete_atual = st.session_state.get("frete")
            if frete_atual:
                if abs(frete_atual["total_na_hora"] - total_geral) > 0.01:
                    st.warning("O carrinho mudou. Clique em Calcular frete de novo.")
                else:
                    texto_valor = "Grátis 🎉" if frete_atual["valor"] == 0 else f"R$ {frete_atual['valor']:.2f}"
                    st.success(f"Entrega em {frete_atual['cidade']}/{frete_atual['uf']}: {texto_valor} "
                               f"| prazo de {frete_atual['prazo']} dias úteis")
                    st.markdown(f"### Total com frete: R$ {total_geral + frete_atual['valor']:.2f}")
            elif LOJA["frete_gratis_ligado"] and LOJA["frete_gratis_acima"] > 0:
                st.caption(f"Frete grátis em pedidos a partir de R$ {LOJA['frete_gratis_acima']:.2f}")

        # ----- Pagamento e finalização -----
        with st.container(border=True):
            st.subheader("💳 Pagamento")
            formas = ["Pix"]
            if LOJA["cartao_ligado"]:
                formas += ["Cartão de crédito", "Cartão de débito"]
            st.radio("Forma de pagamento", formas, key="forma_pag", horizontal=True)
            if st.session_state.get("forma_pag", "Pix") == "Pix":
                if LOJA["pix_chave"]:
                    st.info(f"Chave Pix: **{LOJA['pix_chave']}**")
                st.caption(LOJA["pix_instrucoes"])
            else:
                if LOJA["link_pagamento_cartao"]:
                    st.link_button("🔒 Pagar com cartão (site seguro)", LOJA["link_pagamento_cartao"],
                                   use_container_width=True)
                    st.caption("Você digita os dados do cartão no site seguro do banco, nunca aqui.")
                else:
                    st.warning("Pagamento com cartão em breve. Enquanto isso, escolha Pix "
                               "ou combine com a gente pelo WhatsApp.")

            st.text_input("Seu nome", key="cli_nome")
            st.text_input("Seu WhatsApp (com DDD)", key="cli_tel", placeholder="55999999999")
            if st.session_state.get("erro_cliente"):
                st.error(st.session_state.erro_cliente)
            st.button("📲 Finalizar Pedido via WhatsApp", type="primary",
                      use_container_width=True, on_click=finalizar_pedido)
            if st.session_state.link_whatsapp:
                if st.session_state.ultimo_pedido_id:
                    st.success(f"Pedido registrado: {st.session_state.ultimo_pedido_id}")
                st.link_button("👉 Clique aqui para enviar no WhatsApp",
                               st.session_state.link_whatsapp, use_container_width=True)

    st.divider()
    if st.button("📦 Acompanhar meu pedido", use_container_width=True, key="btn_acomp"):
        abrir_acompanhamento()
# ===============================================================
# ENGRENAGEM DISCRETA DO ADMINISTRADOR (canto superior direito)
# ===============================================================
@st.dialog("Acesso do administrador")
def abrir_login_admin():
    senha = st.text_input("Senha", type="password", key="senha_admin")
    if st.button("Entrar", type="primary", key="btn_entrar_admin"):
        if senha == SENHA_ADMIN:
            st.session_state.admin = True
            st.rerun()
        else:
            st.error("Senha incorreta.")


_c_espaco, _c_engrenagem = st.columns([30, 1])
with _c_engrenagem:
    if st.session_state.admin:
        if st.button("✖", key="btn_sair_admin", help="Sair do modo administrador"):
            st.session_state.admin = False
            st.rerun()
    else:
        if st.button("⚙", key="btn_engrenagem", help=" "):
            abrir_login_admin()


# ===============================================================
# PAINEL DO ADMINISTRADOR (a vitrine do cliente some enquanto ele está aberto)
# ===============================================================
if st.session_state.admin:
    st.title(f"⚙️ Painel - {LOJA['nome_empresa']}")
    st.caption("Você está no modo administrador. A vitrine do cliente fica escondida. "
               "Clique no ✖ no canto superior direito para sair e ver a loja como o cliente vê.")
    (aba_resumo, aba_prod, aba_foto, aba_cli, aba_ped, aba_frete,
     aba_loja, aba_int, aba_backup) = st.tabs([
        "📊 Resumo", "📦 Produtos", "🖼️ Fotos", "👥 Clientes", "🧾 Pedidos",
        "🚚 Frete", "🎨 Loja", "👁️ Interesse", "💾 Backup",
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
        c6.metric("Empresas", int((clientes_r["tipo"] == "Empresa").sum()))
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
            st.dataframe(top[["nome", "telefone", "tipo", "qtd_pedidos", "gasto_total"]],
                         use_container_width=True, hide_index=True)

    # ---------------------------------------------------------- PRODUTOS (cartões)
    with aba_prod:
        st.caption("Cada produto é um cartão. Clique em Editar para mudar tudo dele. "
                   "Use os botões abaixo para criar produto e categoria.")

        with st.expander("➕ Nova categoria"):
            nova_cat = st.text_input("Nome da nova categoria", key="nova_cat_nome")
            preco_cat = st.number_input("Preço do primeiro produto (R$)", min_value=0.0, value=50.0,
                                        step=1.0, key="nova_cat_preco")
            if st.button("Criar categoria", type="primary", key="btn_nova_cat"):
                if nova_cat.strip():
                    linha = {c: "" for c in COLUNAS_PRODUTOS}
                    linha.update({"categoria": nova_cat.strip(), "modelo": f"{nova_cat.strip()} Modelo 1",
                                  "preco": preco_cat, "ativo": True, "destaque": False,
                                  "estoque": 0, "custo": 0.0, "peso_g": 0,
                                  "prazo_producao_dias": 5, "preco_promocional": 0.0})
                    gravar_csv(ARQ_PRODUTOS, pd.concat([df_produtos, pd.DataFrame([linha])], ignore_index=True))
                    st.success("Categoria criada com um produto de exemplo. Edite-o abaixo.")
                    st.rerun()
                else:
                    st.error("Digite o nome da categoria.")

        with st.expander("➕ Novo produto"):
            cats_existentes = sorted(df_produtos["categoria"].unique().tolist())
            np_cat = st.selectbox("Categoria", cats_existentes, key="np_cat") if cats_existentes else ""
            np_nome = st.text_input("Nome do produto", key="np_nome")
            np_preco = st.number_input("Preço (R$)", min_value=0.0, value=50.0, step=1.0, key="np_preco")
            if st.button("Criar produto", type="primary", key="btn_novo_prod"):
                if np_nome.strip() and np_cat:
                    linha = {c: "" for c in COLUNAS_PRODUTOS}
                    linha.update({"categoria": np_cat, "modelo": np_nome.strip(), "preco": np_preco,
                                  "ativo": True, "destaque": False, "estoque": 0, "custo": 0.0,
                                  "peso_g": 0, "prazo_producao_dias": 5, "preco_promocional": 0.0})
                    gravar_csv(ARQ_PRODUTOS, pd.concat([df_produtos, pd.DataFrame([linha])], ignore_index=True))
                    st.success("Produto criado! Ele aparece na lista abaixo.")
                    st.rerun()
                else:
                    st.error("Escolha a categoria e digite o nome.")

        st.divider()
        f1, f2, f3 = st.columns([2, 2, 1])
        busca_p = f1.text_input("🔎 Buscar produto", key="busca_prod")
        filtro_cat = f2.selectbox("Categoria", ["Todas"] + sorted(df_produtos["categoria"].unique().tolist()),
                                  key="filtro_cat_admin")
        so_alertas = f3.checkbox("Só com alerta", key="so_alertas")

        vista_p = df_produtos.copy()
        vista_p["_pos"] = range(len(vista_p))
        if busca_p.strip():
            vista_p = vista_p[vista_p["modelo"].str.lower().str.contains(busca_p.strip().lower(), regex=False)]
        if filtro_cat != "Todas":
            vista_p = vista_p[vista_p["categoria"] == filtro_cat]
        if so_alertas:
            vista_p = vista_p[(vista_p["custo"] > vista_p["preco"]) | (vista_p["imagem"] == "")]

        POR_PAGINA = 12
        total_pag = max(1, (len(vista_p) + POR_PAGINA - 1) // POR_PAGINA)
        pagina = st.number_input(f"Página (1 a {total_pag})", min_value=1, max_value=total_pag,
                                 value=1, step=1, key="pag_prod")
        trecho = vista_p.iloc[(pagina - 1) * POR_PAGINA: pagina * POR_PAGINA]
        st.caption(f"{len(vista_p)} produto(s) encontrado(s).")

        cols_p = st.columns(3)
        for n, (_, prod) in enumerate(trecho.iterrows()):
            pos = int(prod["_pos"])
            with cols_p[n % 3]:
                with st.container(border=True):
                    mostrar_imagem(prod["imagem"], prod["categoria"], prod["modelo"])
                    st.markdown(f"**{prod['modelo']}**")
                    efetivo, em_promo = preco_atual(prod)
                    st.markdown(f"R$ {efetivo:.2f}  ·  _{prod['categoria']}_")
                    selos = ""
                    if prod["custo"] > prod["preco"]:
                        selos += "<span class='selo'>custo &gt; preço</span> "
                    if prod["estoque"] <= 0:
                        selos += "<span class='selo'>sem estoque</span> "
                    if em_promo:
                        selos += "<span class='selo selo-promo'>em promoção</span> "
                    if prod["destaque"]:
                        selos += "<span class='selo selo-ok'>destaque</span>"
                    if selos:
                        st.markdown(selos, unsafe_allow_html=True)
                    ativo_novo = st.toggle("Ativo (visível ao cliente)", value=bool(prod["ativo"]),
                                           key=f"ativo_{pos}")
                    if ativo_novo != bool(prod["ativo"]):
                        base = df_produtos.copy()
                        base.at[pos, "ativo"] = ativo_novo
                        gravar_csv(ARQ_PRODUTOS, base)
                        st.rerun()
                    bt1, bt2 = st.columns(2)
                    editar = bt1.button("✏️ Editar", key=f"ed_{pos}", use_container_width=True)
                    duplicar = bt2.button("📋 Duplicar", key=f"dup_{pos}", use_container_width=True)
                    if duplicar:
                        copia = df_produtos.iloc[[pos]].copy()
                        copia["modelo"] = copia["modelo"] + " (cópia)"
                        gravar_csv(ARQ_PRODUTOS, pd.concat([df_produtos, copia], ignore_index=True))
                        st.rerun()
                    if editar:
                        st.session_state.editando_produto = pos

        pos_ed = st.session_state.get("editando_produto")
        if pos_ed is not None and pos_ed < len(df_produtos):
            ed = df_produtos.iloc[pos_ed]
            st.divider()
            st.subheader(f"✏️ Editando: {ed['modelo']}")
            with st.form(f"form_prod_{pos_ed}"):
                tab_a, tab_b, tab_c, tab_d = st.tabs(
                    ["Básico", "Ficha do produto", "Promoção e variações", "Controle interno"])
                with tab_a:
                    e_cat = st.text_input("Categoria", value=ed["categoria"])
                    e_nome = st.text_input("Nome do modelo", value=ed["modelo"])
                    e_preco = st.number_input("Preço (R$)", min_value=0.0, value=float(ed["preco"]), step=1.0)
                    e_img = st.text_input("Foto (link). Para enviar do computador use a aba Fotos",
                                          value="" if str(ed["imagem"]).startswith("data:") else ed["imagem"])
                    e_ativo = st.checkbox("Ativo (visível ao cliente)", value=bool(ed["ativo"]))
                    e_dest = st.checkbox("Destaque", value=bool(ed["destaque"]))
                with tab_b:
                    e_desc = st.text_area("Descrição", value=ed["descricao"])
                    e_serve = st.text_area("Para que serve", value=ed["para_que_serve"])
                    e_med = st.text_input("Medidas e material", value=ed["medidas"])
                    e_dicas = st.text_area("Dicas de uso", value=ed["dicas"])
                with tab_c:
                    e_promo = st.number_input("Preço promocional (R$, 0 = sem promoção)", min_value=0.0,
                                              value=float(ed["preco_promocional"]), step=1.0)
                    e_ini = st.text_input("Promoção começa em (aaaa-mm-dd, vazio = já)", value=ed["promo_inicio"])
                    e_fim = st.text_input("Promoção termina em (aaaa-mm-dd, vazio = sem fim)", value=ed["promo_fim"])
                    e_var = st.text_input("Variações separadas por vírgula (ex.: P, M, G, GG ou Azul, Vermelho)",
                                          value=ed["variacoes"])
                with tab_d:
                    e_sku = st.text_input("Código (SKU)", value=ed["sku"])
                    e_custo = st.number_input("Custo (R$)", min_value=0.0, value=float(ed["custo"]), step=1.0)
                    e_estq = st.number_input("Estoque", min_value=0, value=int(ed["estoque"]), step=1)
                    e_peso = st.number_input("Peso (g)", min_value=0, value=int(ed["peso_g"]), step=10)
                    e_prazo = st.number_input("Prazo de produção (dias)", min_value=0,
                                              value=int(ed["prazo_producao_dias"]), step=1)
                    e_tags = st.text_input("Etiquetas", value=ed["tags"])
                    e_obs = st.text_area("Observações internas (só você vê)", value=ed["obs_internas"])
                salvar_p = st.form_submit_button("💾 Salvar este produto", type="primary")
                excluir_p = st.form_submit_button("🗑️ Excluir produto")
            if salvar_p:
                base = df_produtos.copy()
                imagem_final = e_img if e_img else ed["imagem"]
                valores = {"categoria": e_cat, "modelo": e_nome, "preco": e_preco, "imagem": imagem_final,
                           "ativo": e_ativo, "destaque": e_dest, "descricao": e_desc,
                           "para_que_serve": e_serve, "medidas": e_med, "dicas": e_dicas,
                           "preco_promocional": e_promo, "promo_inicio": e_ini, "promo_fim": e_fim,
                           "variacoes": e_var, "sku": e_sku, "custo": e_custo, "estoque": e_estq,
                           "peso_g": e_peso, "prazo_producao_dias": e_prazo, "tags": e_tags,
                           "obs_internas": e_obs}
                for campo, valor in valores.items():
                    base.at[pos_ed, campo] = valor
                gravar_csv(ARQ_PRODUTOS, base)
                st.session_state.editando_produto = None
                st.success("Produto salvo! Os clientes já veem a mudança.")
                st.rerun()
            if excluir_p:
                gravar_csv(ARQ_PRODUTOS,
                           df_produtos.drop(index=df_produtos.index[pos_ed]).reset_index(drop=True))
                st.session_state.editando_produto = None
                st.rerun()

    # ---------------------------------------------------------- FOTOS
    with aba_foto:
        st.caption("Envie a foto do computador ou do celular. Ela fica guardada dentro do cadastro "
                   "do produto, então não precisa de link. Fotos até 2 MB.")
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
                            b64 = base64.b64encode(arquivo.getvalue()).decode()
                            novo_df = df_produtos.copy()
                            mascara = (novo_df["categoria"] == cat_f) & (novo_df["modelo"] == mod_f)
                            novo_df.loc[mascara, "imagem"] = f"data:{arquivo.type or 'image/jpeg'};base64,{b64}"
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
        pedidos_c["total_num"] = pd.to_numeric(pedidos_c["total"], errors="coerce").fillna(0.0)

        # ----- classificação automática: ativos, adormecidos e aniversariantes -----
        def ultima_compra(tel):
            ds = pedidos_c[pedidos_c["telefone"].astype(str) == str(tel)]["data"]
            datas = [datetime.strptime(d, "%d/%m/%Y %H:%M") for d in ds if d]
            return max(datas) if datas else None

        limite = datetime.now() - timedelta(days=int(LOJA["dias_adormecido"]))
        grupos = {"ativos": [], "adormecidos": [], "aniversariantes": []}
        mes_atual = datetime.now().strftime("%m")
        for _, cli in clientes.iterrows():
            uc = ultima_compra(cli["telefone"])
            if uc and uc >= limite:
                grupos["ativos"].append(cli)
            elif uc:
                grupos["adormecidos"].append(cli)
            nasc = str(cli["data_nascimento"])
            if len(nasc) >= 5 and nasc[3:5] == mes_atual:
                grupos["aniversariantes"].append(cli)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Clientes", len(clientes))
        m2.metric("Ativos", len(grupos["ativos"]))
        m3.metric("Adormecidos", len(grupos["adormecidos"]))
        m4.metric("Aniversariantes do mês", len(grupos["aniversariantes"]))
        m5.metric("Empresas", int((clientes["tipo"] == "Empresa").sum()))

        sub_todos, sub_ativos, sub_adorm, sub_aniv = st.tabs(
            ["📋 Todos", "🟢 Ativos", "😴 Adormecidos (chamar de volta)", "🎂 Aniversariantes"])

        with sub_todos:
            st.caption("Ficha completa. Os dados básicos entram sozinhos quando alguém finaliza um pedido; "
                       "o resto você completa aqui. Clique em Salvar para guardar.")
            busca = st.text_input("🔎 Buscar por nome, telefone, e-mail, cidade ou empresa", key="busca_cliente")
            filtro_status = st.multiselect("Filtrar por status", STATUS_CLIENTE, key="filtro_status_cli")
            filtro_tipo = st.multiselect("Filtrar por tipo", ["Cliente", "Empresa"], key="filtro_tipo_cli")
            vista = clientes.copy()
            if busca.strip():
                termo = busca.strip().lower()
                mascara = vista[["nome", "telefone", "email", "cidade", "empresa"]].apply(
                    lambda col: col.astype(str).str.lower().str.contains(termo, regex=False)).any(axis=1)
                vista = vista[mascara]
            if filtro_status:
                vista = vista[vista["status"].isin(filtro_status)]
            if filtro_tipo:
                vista = vista[vista["tipo"].isin(filtro_tipo)]
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
                    "tipo": st.column_config.SelectboxColumn("Tipo", options=["Cliente", "Empresa"]),
                    "razao_social": st.column_config.TextColumn("Razão social"),
                    "responsavel": st.column_config.TextColumn("Responsável"),
                    "cpf_cnpj": st.column_config.TextColumn("CPF / CNPJ"),
                    "data_nascimento": st.column_config.TextColumn("Nascimento (dd/mm/aaaa)"),
                    "origem": st.column_config.SelectboxColumn("Como chegou", options=ORIGENS_CLIENTE),
                    "status": st.column_config.SelectboxColumn("Status", options=STATUS_CLIENTE),
                    "proximo_contato": st.column_config.TextColumn("Próximo contato (aaaa-mm-dd)"),
                    "aceita_promocoes": st.column_config.CheckboxColumn("Aceita promoções"),
                    "observacoes": st.column_config.TextColumn("Observações", width="large"),
                },
            )
            if st.button("💾 Salvar clientes", type="primary", key="salvar_clientes"):
                if busca.strip() or filtro_status or filtro_tipo:
                    st.warning("Limpe a busca e os filtros antes de salvar, para não perder clientes escondidos.")
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
                hist = pedidos_c[pedidos_c["telefone"].astype(str) == tel_escolhido]
                gasto_cli = hist[hist["status"] != "Cancelado"]["total_num"].sum()
                h1, h2 = st.columns(2)
                h1.metric("Pedidos", len(hist))
                h2.metric("Total gasto", f"R$ {gasto_cli:,.2f}")
                if len(hist):
                    st.dataframe(hist[["data", "id_pedido", "itens", "total", "status", "pagamento"]].iloc[::-1],
                                 use_container_width=True, hide_index=True)
            else:
                st.info("Ainda não há clientes. Eles aparecem aqui quando alguém finaliza um pedido.")
            st.download_button("⬇️ Baixar clientes (CSV)", clientes.to_csv(index=False).encode("utf-8"),
                               "clientes.csv", "text/csv")

        with sub_ativos:
            if grupos["ativos"]:
                st.dataframe(pd.DataFrame(grupos["ativos"])[["nome", "telefone", "tipo", "qtd_pedidos", "cidade"]],
                             use_container_width=True, hide_index=True)
            else:
                st.info(f"Nenhum cliente comprou nos últimos {LOJA['dias_adormecido']} dias.")

        with sub_adorm:
            st.caption(f"Clientes que não compram há mais de {LOJA['dias_adormecido']} dias. "
                       "Clique no botão: o WhatsApp abre com a mensagem pronta e você só aperta enviar. "
                       "Edite os textos e o prazo na aba Loja.")
            if not grupos["adormecidos"]:
                st.success("Nenhum cliente adormecido. Todo mundo comprou recentemente.")
            for cli in grupos["adormecidos"]:
                uc = ultima_compra(cli["telefone"])
                dias = (datetime.now() - uc).days if uc else 0
                texto = random.choice(LOJA["msgs_retorno"]).replace("{nome}", cli["nome"].split()[0])
                num = "".join(ch for ch in str(cli["telefone"]) if ch.isdigit())
                with st.container(border=True):
                    a1, a2 = st.columns([3, 1])
                    a1.markdown(f"**{cli['nome']}** ({cli['tipo'] or 'Cliente'}) · última compra há {dias} dias")
                    a1.caption(texto)
                    a2.link_button("💬 Chamar no WhatsApp",
                                   f"https://wa.me/{num}?text={urllib.parse.quote(texto)}",
                                   use_container_width=True)

        with sub_aniv:
            if not grupos["aniversariantes"]:
                st.info("Nenhum aniversariante este mês. Preencha o nascimento na aba Todos (dd/mm/aaaa).")
            for cli in grupos["aniversariantes"]:
                texto = LOJA["msg_aniversario"].replace("{nome}", cli["nome"].split()[0])
                num = "".join(ch for ch in str(cli["telefone"]) if ch.isdigit())
                with st.container(border=True):
                    b1, b2 = st.columns([3, 1])
                    b1.markdown(f"🎂 **{cli['nome']}** · {cli['data_nascimento']}")
                    b2.link_button("💬 Parabenizar", f"https://wa.me/{num}?text={urllib.parse.quote(texto)}",
                                   use_container_width=True)

    # ---------------------------------------------------------- PEDIDOS
    with aba_ped:
        pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        pedidos["total_num"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0.0)
        st.caption("Acompanhe cada pedido: mude o status, marque o pagamento, coloque o código de rastreio "
                   "e a previsão de entrega. O cliente vê essas informações em Acompanhar meu pedido.")
        p1, p2, p3 = st.columns(3)
        p1.metric("Pedidos", len(pedidos))
        p2.metric("Total em pedidos", f"R$ {pedidos['total_num'].sum():,.2f}")
        p3.metric("Aguardando pagamento", int((pedidos["pagamento"] == "Pendente").sum()))
        filtro_status_p = st.multiselect("Filtrar por status do pedido", STATUS_PEDIDO, key="filtro_status_ped")
        vista_p2 = pedidos.drop(columns=["total_num"])
        if filtro_status_p:
            vista_p2 = vista_p2[vista_p2["status"].isin(filtro_status_p)]
        vista_p2 = vista_p2.iloc[::-1]
        ped_editado = st.data_editor(
            vista_p2, use_container_width=True, key="editor_pedidos", num_rows="fixed",
            column_config={
                "data": st.column_config.TextColumn("Data", disabled=True),
                "id_pedido": st.column_config.TextColumn("Nº", disabled=True),
                "nome": st.column_config.TextColumn("Cliente", disabled=True),
                "telefone": st.column_config.TextColumn("WhatsApp", disabled=True),
                "itens": st.column_config.TextColumn("Itens", disabled=True, width="large"),
                "total": st.column_config.TextColumn("Total (R$)", disabled=True),
                "tipo_cliente": st.column_config.TextColumn("Tipo", disabled=True),
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
            for _, linha in ped_editado.iterrows():
                alvo = completo["id_pedido"] == linha["id_pedido"]
                for campo in ["status", "pagamento", "forma_pagamento", "codigo_rastreio",
                              "previsao_entrega", "obs_internas"]:
                    completo.loc[alvo, campo] = linha[campo]
            gravar_csv(ARQ_PEDIDOS, completo)
            st.success("Pedidos salvos!")
            st.rerun()
        st.download_button("⬇️ Baixar pedidos (CSV)",
                           pedidos.drop(columns=["total_num"]).to_csv(index=False).encode("utf-8"),
                           "pedidos.csv", "text/csv")

    # ---------------------------------------------------------- FRETE
    with aba_frete:
        st.subheader("🎁 Frete grátis")
        fg1, fg2 = st.columns(2)
        fg_ligado = fg1.toggle("Frete grátis ligado", value=bool(LOJA["frete_gratis_ligado"]), key="fg_ligado")
        fg_valor = fg2.number_input("Frete grátis a partir de (R$)", min_value=0.0,
                                    value=float(LOJA["frete_gratis_acima"]), step=10.0, key="fg_valor")
        if st.button("💾 Salvar frete grátis", type="primary", key="salvar_fg"):
            LOJA["frete_gratis_ligado"] = fg_ligado
            LOJA["frete_gratis_acima"] = fg_valor
            gravar_loja(LOJA)
            st.success("Frete grátis salvo!")
            st.rerun()
        st.divider()
        st.subheader("📍 Valor e prazo por estado")
        st.caption("O cliente digita o CEP e o app aplica o valor do estado dele.")
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
        if st.button("💾 Salvar tabela de frete", type="primary", key="salvar_frete"):
            gravar_csv(ARQ_FRETE, frete_editado)
            st.success("Tabela de frete salva!")
            st.rerun()

    # ---------------------------------------------------------- LOJA (personalização)
    with aba_loja:
        st.caption("Tudo que o cliente vê no catálogo você muda aqui, sem mexer em código.")
        with st.form("form_loja"):
            t1, t2, t3, t4, t5 = st.tabs(
                ["Marca e visual", "Pagamento", "Promoção", "Mensagens", "Empresas (lote)"])
            with t1:
                l_nome = st.text_input("Nome da empresa", value=LOJA["nome_empresa"])
                l_sub = st.text_input("Subtítulo", value=LOJA["subtitulo"])
                l_frase = st.text_input("Frase do banner", value=LOJA["frase_banner"])
                l_wpp = st.text_input("WhatsApp que recebe os pedidos (só números, com 55 e DDD)",
                                      value=LOJA["whatsapp"])
                l_cor = st.color_picker("Cor principal", value=LOJA["cor_principal"])
                l_fundo = st.selectbox("Fundo da página", FUNDOS, index=FUNDOS.index(LOJA["fundo"])
                                       if LOJA["fundo"] in FUNDOS else 0)
            with t2:
                l_pix = st.text_input("Sua chave Pix (aparece para o cliente)", value=LOJA["pix_chave"])
                l_pixi = st.text_area("Instruções do Pix", value=LOJA["pix_instrucoes"])
                l_cartao = st.checkbox("Mostrar opção de cartão (crédito e débito)", value=bool(LOJA["cartao_ligado"]))
                l_linkc = st.text_input("Link de pagamento com cartão (Mercado Pago, PagSeguro, InfinitePay...)",
                                        value=LOJA["link_pagamento_cartao"])
                st.caption("O app nunca guarda número de cartão. O cliente digita o cartão no site seguro "
                           "do serviço de pagamento, pelo link que você colar aqui.")
            with t3:
                l_brl = st.checkbox("Promoção de brinde ligada", value=bool(LOJA["brinde_ligado"]))
                l_bac = st.number_input("A cada quantas unidades ganha 1 brinde (cliente comum)",
                                        min_value=1, value=int(LOJA["brinde_a_cada"]), step=1)
            with t4:
                l_dias = st.number_input("Dias sem comprar para virar cliente adormecido",
                                         min_value=7, value=int(LOJA["dias_adormecido"]), step=1)
                l_msgs = st.text_area("Mensagens para chamar de volta (uma por linha; use {nome})",
                                      value="\n".join(LOJA["msgs_retorno"]), height=150)
                l_aniv = st.text_area("Mensagem de aniversário (use {nome})", value=LOJA["msg_aniversario"])
            with t5:
                l_emin = st.number_input("Pedido mínimo para empresas (R$)", min_value=0.0,
                                         value=float(LOJA["empresa_pedido_minimo"]), step=50.0)
                l_efg = st.checkbox("Frete grátis para empresas", value=bool(LOJA["empresa_frete_gratis"]))
                l_ebr = st.number_input("A cada quantas unidades empresa ganha 1 brinde",
                                        min_value=1, value=int(LOJA["empresa_brinde_a_cada"]), step=1)
                l_epr = st.text_input("Prazo de produção em lote", value=LOJA["empresa_prazo_lote"])
                st.markdown("**Descontos por quantidade (edite a tabela)**")
                faixas_df = st.data_editor(
                    pd.DataFrame(LOJA["empresa_faixas"]), num_rows="dynamic", key="editor_faixas",
                    column_config={
                        "a_partir_de": st.column_config.NumberColumn("A partir de (unidades)", min_value=1, step=1),
                        "desconto_pct": st.column_config.NumberColumn("Desconto (%)", min_value=0, max_value=90, step=1),
                    })
            if st.form_submit_button("💾 Salvar configurações da loja", type="primary"):
                LOJA.update({
                    "nome_empresa": l_nome, "subtitulo": l_sub, "frase_banner": l_frase,
                    "whatsapp": "".join(ch for ch in l_wpp if ch.isdigit()),
                    "cor_principal": l_cor, "fundo": l_fundo,
                    "pix_chave": l_pix, "pix_instrucoes": l_pixi,
                    "cartao_ligado": l_cartao, "link_pagamento_cartao": l_linkc.strip(),
                    "brinde_ligado": l_brl, "brinde_a_cada": int(l_bac),
                    "dias_adormecido": int(l_dias),
                    "msgs_retorno": [m.strip() for m in l_msgs.split("\n") if m.strip()],
                    "msg_aniversario": l_aniv,
                    "empresa_pedido_minimo": float(l_emin), "empresa_frete_gratis": l_efg,
                    "empresa_brinde_a_cada": int(l_ebr), "empresa_prazo_lote": l_epr,
                    "empresa_faixas": [
                        {"a_partir_de": int(r["a_partir_de"]), "desconto_pct": int(r["desconto_pct"])}
                        for _, r in faixas_df.dropna().iterrows()],
                })
                gravar_loja(LOJA)
                st.success("Configurações salvas! O catálogo já usa os novos dados.")
                st.rerun()

    # ---------------------------------------------------------- INTERESSE (cliques)
    with aba_int:
        st.caption("O que os visitantes estão olhando, mesmo sem comprar. Os cliques são anônimos: "
                   "o app não sabe quem clicou, só o que foi clicado.")
        cliques = ler_csv(ARQ_CLIQUES, COLUNAS_CLIQUES)
        if cliques.empty:
            st.info("Ainda não há cliques registrados. Eles aparecem conforme os visitantes usam o catálogo.")
        else:
            i1, i2, i3 = st.columns(3)
            i1.metric("Cliques registrados", len(cliques))
            i2.metric("Categorias abertas", int((cliques["evento"] == "abriu_categoria").sum()))
            i3.metric("Adições ao carrinho", int((cliques["evento"] == "adicionou_carrinho").sum()))

            st.subheader("🔥 Produtos mais vistos de perto / 3D")
            vistos = cliques[cliques["evento"] == "ver_de_perto"]["produto"].value_counts().head(10)
            if len(vistos):
                st.bar_chart(vistos)
            else:
                st.write("Nenhum clique em Ver de perto ainda.")

            st.subheader("🛒 Produtos mais adicionados ao carrinho")
            add = cliques[cliques["evento"] == "adicionou_carrinho"]["produto"].value_counts().head(10)
            if len(add):
                st.bar_chart(add)
            else:
                st.write("Nenhuma adição ao carrinho ainda.")

            st.subheader("📂 Categorias mais abertas")
            cats_abertas = cliques[cliques["evento"] == "abriu_categoria"]["categoria"].value_counts()
            if len(cats_abertas):
                st.bar_chart(cats_abertas)

            st.subheader("👀 Muito interesse, pouca compra")
            olhados = cliques[cliques["evento"].isin(["ver_de_perto", "adicionou_carrinho"])]["produto"].value_counts()
            comprados = pd.Series(dtype=int)
            if len(pedidos_c := ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)):
                texto_pedidos = " ".join(pedidos_c["itens"].astype(str))
                comprados = pd.Series({p: texto_pedidos.count(p) for p in olhados.index})
            tabela_int = pd.DataFrame({"interesse": olhados})
            tabela_int["vendidos"] = comprados.reindex(tabela_int.index).fillna(0).astype(int)
            st.dataframe(tabela_int.sort_values("interesse", ascending=False).head(10),
                         use_container_width=True)
            st.caption("Produto com muito interesse e zero vendas: vale rever preço, foto ou descrição.")

            por_dia = cliques.assign(dia=cliques["data"].str[:10]).groupby("dia").size()
            st.subheader("📅 Cliques por dia")
            st.line_chart(por_dia)

    # ---------------------------------------------------------- BACKUP
    with aba_backup:
        st.caption("No Streamlit Cloud os arquivos podem ser apagados quando o app reinicia. "
                   "Baixe os backups de vez em quando. Para restaurar, envie o arquivo de volta aqui.")
        arquivos_backup = [
            ("Produtos", ARQ_PRODUTOS, COLUNAS_PRODUTOS),
            ("Clientes", ARQ_CLIENTES, COLUNAS_CLIENTES),
            ("Pedidos", ARQ_PEDIDOS, COLUNAS_PEDIDOS),
            ("Frete", ARQ_FRETE, COLUNAS_FRETE),
            ("Cliques", ARQ_CLIQUES, COLUNAS_CLIQUES),
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
        st.markdown("**Configurações da loja**")
        if os.path.exists(ARQ_LOJA):
            with open(ARQ_LOJA, "r", encoding="utf-8") as f_loja:
                st.download_button("⬇️ Baixar configurações da loja", f_loja.read().encode("utf-8"),
                                   "loja.json", "application/json", key="bk_loja")
        else:
            st.write("Ainda não há configurações salvas.")

    st.stop()  # com o painel aberto, a vitrine do cliente não aparece
# ===============================================================
# CADASTRO DA EMPRESA (modo empresa)
# ===============================================================
@st.dialog("Cadastro da empresa")
def abrir_cadastro_empresa():
    st.write("Informe os dados da sua empresa para ver os preços e vantagens de lote.")
    razao = st.text_input("Razão social ou nome fantasia", key="emp_razao")
    cnpj = st.text_input("CNPJ", key="emp_cnpj", placeholder="00.000.000/0000-00")
    resp = st.text_input("Nome do responsável", key="emp_resp")
    if st.button("Entrar como empresa", type="primary", key="btn_entrar_empresa"):
        so_numeros = "".join(ch for ch in cnpj if ch.isdigit())
        if len(razao.strip()) < 2 or len(resp.strip()) < 2 or len(so_numeros) != 14:
            st.error("Preencha a razão social, o responsável e um CNPJ com 14 números.")
        else:
            st.session_state.empresa = {"razao_social": razao.strip(), "cnpj": cnpj.strip(),
                                        "responsavel": resp.strip()}
            st.session_state.modo = "empresa"
            st.rerun()


# ===============================================================
# PÁGINA INICIAL (visão do cliente)
# ===============================================================
st.markdown(
    f"<div class='banner'><h1>🏷️ {html.escape(LOJA['nome_empresa'])}</h1>"
    f"<p>{html.escape(LOJA['subtitulo'])}</p>"
    f"<p><b>{html.escape(LOJA['frase_banner'])}</b></p></div>",
    unsafe_allow_html=True)

b1, b2, b3 = st.columns([1, 1, 2])
if b1.button("🙋 Sou cliente", use_container_width=True,
             type="primary" if st.session_state.modo != "empresa" else "secondary", key="modo_cliente"):
    st.session_state.modo = "cliente"
    st.session_state.carrinho = []
    st.session_state.frete = None
    st.rerun()
if b2.button("🏢 Sou empresa", use_container_width=True,
             type="primary" if st.session_state.modo == "empresa" else "secondary", key="modo_empresa"):
    if st.session_state.modo != "empresa":
        abrir_cadastro_empresa()

if modo_empresa():
    emp = st.session_state.empresa
    st.success(f"🏢 Bem-vindo, {emp['razao_social']}! Vantagens para empresas ativas.")
    with st.container(border=True):
        st.subheader("Vantagens para empresas")
        v1, v2, v3 = st.columns(3)
        v1.metric("Pedido mínimo", f"R$ {LOJA['empresa_pedido_minimo']:.2f}")
        v2.metric("Frete", "Grátis" if LOJA["empresa_frete_gratis"] else "Conforme tabela")
        v3.metric("Brinde", f"a cada {LOJA['empresa_brinde_a_cada']} un.")
        st.write(f"Prazo de produção em lote: **{LOJA['empresa_prazo_lote']}**")
        faixas = sorted(LOJA["empresa_faixas"], key=lambda f: f["a_partir_de"])
        if faixas:
            st.markdown("**Desconto por quantidade (soma de todos os itens do carrinho):**")
            st.table(pd.DataFrame(
                [{"A partir de": f"{f['a_partir_de']} unidades", "Desconto": f"{f['desconto_pct']}%"}
                 for f in faixas]))
else:
    st.caption("Compra para empresa em lote? Clique em Sou empresa para ver descontos e frete grátis.")

# ===============================================================
# GRADE DE CATEGORIAS
# ===============================================================
st.header("📦 Categorias Disponíveis")
st.caption("Clique em uma categoria para ver todos os modelos personalizáveis.")

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
