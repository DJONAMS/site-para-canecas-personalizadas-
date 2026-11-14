import base64
import html
import io
import json
import os
import random
import urllib.parse
import urllib.request
import uuid
import zipfile
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
ARQ_APRESENTACOES = "dados_apresentacoes.json"
ARQ_VITRINE = "dados_vitrine.json"
PASTA_VIDEOS = "videos"

MODELO_PADRAO = (
    "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/"
    "main/Models/CoffeeMug/glTF-Binary/CoffeeMug.glb"
)

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
    "pix_nome": "",
    "pix_cidade": "",
    "pix_instrucoes": "Aponte a câmera do app do banco para o QR code ou use o Pix Copia e Cola.",
    "cartao_ligado": True,
    "link_pagamento_cartao": "",
    "dias_adormecido": 30,
    "msgs_retorno": [
        "Oi {nome}! Faz um tempinho que não nos falamos. Que tal fazer um novo pedido? Comprando 2 produtos você ganha um brinde.",
        "Olá {nome}, sentimos sua falta! Tem novidade no catálogo e um acessório grátis esperando por você no próximo pedido.",
        "{nome}, tudo bem? Passando para lembrar que seus produtos personalizados favoritos estão disponíveis. Quer ver as novidades?",
    ],
    "msg_aniversario": "Parabéns, {nome}! 🎉 Preparamos uma condição especial de aniversário para você. Quer saber?",
    "msg_rastreio": "Oi {nome}! Seu pedido {pedido} está: {status}. Código de rastreio: {codigo}. Acompanhe em {link}",
    # Redes sociais e QR code da loja
    "instagram": "",
    "facebook": "",
    "mostrar_redes": True,
    "link_loja": "",
    # Dados fiscais (nota fiscal e declaração de conteúdo)
    "fiscal_razao": "",
    "fiscal_cnpj": "",
    "fiscal_ie": "",
    "fiscal_regime": "MEI",
    "fiscal_endereco": "",
    "fiscal_cidade_uf": "",
    "fiscal_cep": "",
    "fiscal_emissor_link": "",
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
    "data", "nome", "telefone", "email", "itens", "total",
    "id_pedido", "status", "pagamento", "forma_pagamento",
    "transportadora", "codigo_rastreio", "link_rastreio",
    "previsao_entrega", "obs_internas", "tipo_cliente",
    "cpf_cnpj", "endereco_entrega",
    "nf_status", "nf_numero", "nf_chave", "nf_link",
]
COLUNAS_CLIQUES = ["data", "evento", "categoria", "produto"]

STATUS_CLIENTE = ["Novo", "Em negociação", "Cliente ativo", "Cliente fiel (VIP)", "Inativo", "Bloqueado"]
ORIGENS_CLIENTE = ["Site", "Instagram", "Facebook", "Indicação", "WhatsApp", "Feira/Evento", "Outro"]
STATUS_PEDIDO = ["Novo", "Aguardando pagamento", "Pago", "Em produção", "Enviado", "Entregue", "Cancelado"]
STATUS_PAGAMENTO = ["Pendente", "Pago", "Parcial", "Reembolsado"]
FORMAS_PAGAMENTO = ["Pix", "Cartão de crédito", "Cartão de débito", "Boleto", "Dinheiro", "Transferência"]
ETAPAS_PEDIDO = ["Novo", "Pago", "Em produção", "Enviado", "Entregue"]
STATUS_NF = ["Não emitida", "Emitida", "Cancelada", "Sem nota (declaração de conteúdo)"]
REGIMES = ["MEI", "Simples Nacional", "Lucro Presumido", "Lucro Real", "Pessoa física (sem CNPJ)"]
TRANSPORTADORAS = {
    "Correios": "https://rastreamento.correios.com.br/app/index.php",
    "Jadlog": "https://www.jadlog.com.br/jadlog/tracking",
    "Loggi": "https://www.loggi.com/rastreador/",
    "Entrega própria": "",
    "Retirada na loja": "",
    "Outra": "",
}
FUNDOS = ["Personalização (ícones)", "Listras suaves", "Pontinhos", "Liso"]
# ---------------------------------------------------------------
# Dados iniciais de exemplo (você edita tudo depois no painel)
# ---------------------------------------------------------------
PALAVRAS_CHAVE = {
    "Copos Térmicos": "tumbler,cup", "Camisetas": "tshirt", "Mateiras": "thermos,flask",
    "Bonés": "cap,hat", "Chaveiros": "keychain", "Almofadas": "cushion,pillow",
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
        "Lave à mão com detergente neutro. Não leve ao micro-ondas."),
    "Camisetas": (
        "Camiseta 100% algodão, confortável e pronta para receber a sua arte.",
        "Uniformes de equipe, eventos, presentes e brindes personalizados.",
        "Tamanhos P ao GG | Algodão penteado",
        "Lave do avesso em água fria para a estampa durar mais."),
    "Mateiras": (
        "Mateira completa com bolsa para garrafa térmica, cuia e acessórios.",
        "Levar o chimarrão com praticidade para a rua, o campo ou a viagem.",
        "Cabe garrafa de até 1 litro | Alça ajustável",
        "Limpe com pano úmido. Evite deixar molhada guardada."),
    "Bonés": (
        "Boné com regulagem traseira, aba curva e ótimo caimento.",
        "Proteger do sol e compor o visual, ótimo para brindes e equipes.",
        "Tamanho único ajustável | Aba curva",
        "Lave à mão e seque à sombra para manter o formato."),
    "Chaveiros": (
        "Chaveiro resistente com personalização de nome, logo ou frase.",
        "Lembrancinhas, brindes de empresa e presentes para quem você gosta.",
        "Cerca de 5 cm | Argola metálica",
        "Evite contato prolongado com água para preservar a arte."),
    "Almofadas": (
        "Almofada macia com capa removível e estampa personalizada.",
        "Decorar a casa, presentear e criar lembranças especiais.",
        "40 x 40 cm | Capa com zíper | Enchimento em fibra",
        "Retire a capa para lavar. Seque à sombra."),
}


# ===============================================================
# ARQUIVOS JSON (loja, apresentações, vitrine)
# ===============================================================
def ler_json(arquivo: str, padrao):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return json.loads(json.dumps(padrao))  # cópia


def gravar_json(arquivo: str, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_loja() -> dict:
    loja = json.loads(json.dumps(LOJA_PADRAO))
    loja.update(ler_json(ARQ_LOJA, {}))
    return loja


def gravar_loja(loja: dict):
    gravar_json(ARQ_LOJA, loja)


LOJA = carregar_loja()
st.set_page_config(page_title=LOJA["nome_empresa"], page_icon="🏷️", layout="wide")


# ===============================================================
# QR CODE, PIX E REDES SOCIAIS
# ===============================================================
def gerar_qr(texto: str) -> str:
    """Transforma um texto ou link em imagem de QR code (data URI)."""
    import qrcode
    img = qrcode.make(texto, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _campo_pix(ident: str, valor: str) -> str:
    return f"{ident}{len(valor):02d}{valor}"


def _crc16(texto: str) -> str:
    crc = 0xFFFF
    for ch in texto.encode("utf-8"):
        crc ^= ch << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return f"{crc:04X}"


def codigo_pix(chave: str, nome: str, cidade: str, valor: float, txid: str = "***") -> str:
    """Gera o Pix Copia e Cola no padrão do Banco Central."""
    conta = _campo_pix("00", "BR.GOV.BCB.PIX") + _campo_pix("01", chave)
    txid = "".join(c for c in txid if c.isalnum())[:25] or "***"
    corpo = (_campo_pix("00", "01") + _campo_pix("26", conta)
             + _campo_pix("52", "0000") + _campo_pix("53", "986")
             + (_campo_pix("54", f"{valor:.2f}") if valor > 0 else "")
             + _campo_pix("58", "BR")
             + _campo_pix("59", (nome or "LOJA")[:25])
             + _campo_pix("60", (cidade or "BRASIL")[:15])
             + _campo_pix("62", _campo_pix("05", txid)) + "6304")
    return corpo + _crc16(corpo)


ICONES_REDES = {
    "instagram": "https://cdn.simpleicons.org/instagram/E4405F",
    "facebook": "https://cdn.simpleicons.org/facebook/1877F2",
    "whatsapp": "https://cdn.simpleicons.org/whatsapp/25D366",
}


def barra_redes(loja: dict, tamanho: int = 34):
    """Ícones clicáveis das redes sociais (configurados no painel)."""
    if not loja.get("mostrar_redes", True):
        return
    links = {
        "instagram": loja.get("instagram", ""),
        "facebook": loja.get("facebook", ""),
        "whatsapp": f"https://wa.me/{loja['whatsapp']}" if loja.get("whatsapp") else "",
    }
    partes = "".join(
        f"<a href='{html.escape(link, quote=True)}' target='_blank' title='{rede.title()}' "
        f"style='margin:0 8px;'><img src='{ICONES_REDES[rede]}' width='{tamanho}' height='{tamanho}'></a>"
        for rede, link in links.items() if link)
    if partes:
        st.markdown(f"<div style='text-align:center;margin:4px 0 10px;'>{partes}</div>",
                    unsafe_allow_html=True)
# ===============================================================
# TEMA CLARO (cor e fundo vêm do painel)
# ===============================================================
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
    else:
        icones = ["🥤", "👕", "🧃", "🧢", "🔑", "🛋️"]
        posicoes = [(25, 40), (110, 85), (190, 30), (70, 150), (160, 175), (235, 120)]
        textos = "".join(
            f"<text x='{x}' y='{y}' font-size='28' opacity='0.16' transform='rotate(-12 {x} {y})'>{ic}</text>"
            for (x, y), ic in zip(posicoes, icones))
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
    /* Esconde menu, rodapé e botões do Streamlit para o cliente */
    #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], [class*="viewerBadge"], [data-testid="stAppDeployButton"]
    {{ display: none !important; }}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}
    .block-container {{ padding-top: 1.2rem !important; padding-bottom: 1rem !important; }}
    [data-testid="stSidebar"] {{ background-color: #ffffff !important; border-right: 1px solid #d9dfeb; }}
    h1, h2, h3, h4, h5, h6, p, span, label, li, div,
    [data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"],
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {{ color: #1a2233; }}
    [data-testid="stCaptionContainer"] p {{ color: #4a5568 !important; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #ffffff; border: 1px solid #d9dfeb !important;
        border-radius: 14px; box-shadow: 0 2px 8px rgba(26, 34, 51, 0.06);
    }}
    [data-testid="stMetric"] {{
        background: #ffffff; border: 1px solid #d9dfeb; border-left: 5px solid {COR};
        border-radius: 12px; padding: 10px 14px;
    }}
    input, textarea, [data-baseweb="input"], [data-baseweb="base-input"],
    [data-baseweb="select"] > div {{ background-color: #ffffff !important; color: #1a2233 !important; }}
    [data-baseweb="input"] {{ border: 1px solid #b8c2d6 !important; border-radius: 8px; }}
    .stButton > button, .stDownloadButton > button, .stLinkButton > a {{
        background-color: #ffffff; color: {COR} !important; border: 1.5px solid {COR};
        border-radius: 10px; font-weight: 600;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover {{
        background-color: #eef2ff; filter: brightness(0.92);
    }}
    .stButton > button[kind="primary"], .stLinkButton > a[kind="primary"] {{
        background-color: {COR}; color: #ffffff !important; border: 1.5px solid {COR};
    }}
    .stButton > button p, .stDownloadButton > button p {{ color: inherit !important; }}
    [data-testid="stExpander"] {{ background-color: #ffffff; border: 1px solid #d9dfeb; border-radius: 12px; }}
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {{ color: #1a2233 !important; }}
    button[data-baseweb="tab"] p {{ color: #1a2233 !important; font-weight: 600; }}
    .banner {{
        background: linear-gradient(120deg, {COR}, #0ea5e9); border-radius: 18px;
        padding: 18px 26px; margin-bottom: 10px; box-shadow: 0 6px 18px rgba(26,34,51,0.15);
    }}
    .banner h1, .banner p, .banner span {{ color: #ffffff !important; margin: 0; }}
    .banner h1 {{ font-size: 1.9rem; }}
    .titulo-secao {{
        background: {COR}; color: #ffffff !important; padding: 8px 14px; border-radius: 10px;
        font-weight: 700; font-size: 1.05rem; margin: 6px 0 12px;
    }}
    .titulo-secao * {{ color: #ffffff !important; }}
    .cat-img {{ width: 100%; height: 16vh; min-height: 90px; object-fit: cover; border-radius: 10px; display: block; }}
    .cartao-carrinho {{
        display: flex; gap: 10px; align-items: center; background: #ffffff;
        border: 1px solid #d9dfeb; border-radius: 12px; padding: 8px; margin-bottom: 8px;
    }}
    .cartao-carrinho img {{ width: 58px; height: 58px; border-radius: 8px; object-fit: cover; }}
    .cartao-carrinho .nome {{ font-weight: 700; font-size: 0.9rem; }}
    .cartao-carrinho .detalhe {{ font-size: 0.8rem; color: #4a5568; }}
    .resumo-total {{ background: #eaf0ff; border: 1px solid #b6c8f5; border-radius: 12px; padding: 12px 14px; margin: 8px 0; }}
    .resumo-total .valor {{ font-size: 1.5rem; font-weight: 800; color: #166534; }}
    .selo {{ display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem;
             font-weight: 700; background: #fee2e2; color: #991b1b; }}
    .selo-ok {{ background: #dcfce7; color: #166534; }}
    .selo-promo {{ background: #fef3c7; color: #92400e; }}
    .btn-top {{
        position: fixed; bottom: 20px; right: 20px; background-color: {COR}; color: #ffffff !important;
        padding: 10px 15px; border-radius: 50px; text-decoration: none; font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.25); z-index: 1000;
    }}
    </style>
    <a href="#" class="btn-top">↑ Topo</a>
""", unsafe_allow_html=True)


def titulo_secao(texto: str):
    """Faixa colorida para destacar os tópicos do painel."""
    st.markdown(f"<div class='titulo-secao'>{html.escape(texto)}</div>", unsafe_allow_html=True)


# ===============================================================
# IMAGENS
# ===============================================================
def imagem_reserva(categoria: str, rotulo: str = "") -> str:
    """Desenho embutido (SVG) usado quando não há foto ou ela não carrega."""
    icone = ICONES.get(categoria, "🏷️")
    rotulo = html.escape(rotulo or categoria)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">'
           '<rect width="400" height="300" fill="#e3eafc"/>'
           f'<text x="200" y="150" font-size="90" text-anchor="middle">{icone}</text>'
           f'<text x="200" y="235" font-size="20" fill="#1a2233" text-anchor="middle" '
           f'font-family="Arial">{rotulo}</text></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


def url_imagem_exemplo(categoria: str, numero: int) -> str:
    return f"https://loremflickr.com/400/300/{PALAVRAS_CHAVE.get(categoria, 'product')}?lock={numero}"


def url_segura(url: str, categoria: str, rotulo: str = "") -> str:
    url = (url or "").strip()
    return url if url else imagem_reserva(categoria, rotulo)


def mostrar_imagem(url: str, categoria: str, rotulo: str = "", classe: str = ""):
    """Foto com zoom ao passar o mouse. Link vazio ou quebrado vira o desenho de reserva."""
    reserva = imagem_reserva(categoria, rotulo)
    estilo = ("" if classe else "width:100%;aspect-ratio:4/3;object-fit:cover;display:block;")
    st.markdown(
        '<div style="overflow:hidden;border-radius:10px;cursor:zoom-in;">'
        f'<img class="{classe}" src="{html.escape(url_segura(url, categoria, rotulo), quote=True)}" '
        f'onerror="this.onerror=null;this.src=\'{reserva}\';" '
        f'style="{estilo}transition:transform 0.35s ease;" '
        'onmouseover="this.style.transform=\'scale(1.25)\'" '
        'onmouseout="this.style.transform=\'scale(1)\'"></div>',
        unsafe_allow_html=True)
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
    """Devolve (preco_efetivo, em_promocao). A promoção vale entre promo_inicio e promo_fim."""
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
                "categoria": categoria,
                "nome": str(linha["modelo"]),
                "preco": efetivo, "preco_cheio": float(linha["preco"]), "em_promo": em_promo,
                "imagem": str(linha["imagem"]) or url_imagem_exemplo(categoria, n),
                "modelo_3d": MODELO_PADRAO,
                "descricao": str(linha["descricao"]),
                "para_que_serve": str(linha["para_que_serve"]),
                "medidas": str(linha["medidas"]),
                "dicas": str(linha["dicas"]),
                "variacoes": [v.strip() for v in str(linha["variacoes"]).split(",") if v.strip()],
                "destaque": bool(linha["destaque"]),
                "estoque": int(linha["estoque"]),
                "prazo": int(linha["prazo_producao_dias"]),
                "sku": str(linha["sku"]),
            })
        itens.sort(key=lambda i: not i["destaque"])  # destaques primeiro
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
        return None if dados.get("erro") else dados
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
    gratis_loja = (LOJA["frete_gratis_ligado"] and LOJA["frete_gratis_acima"] > 0
                   and subtotal >= LOJA["frete_gratis_acima"])
    if gratis_loja or (empresa and LOJA["empresa_frete_gratis"]):
        valor = 0.0
    return valor, prazo


def registrar_clique(evento: str, categoria: str = "", produto: str = ""):
    """Guarda um clique anônimo (sem nome) para a seção Interesse do painel."""
    try:
        df = ler_csv(ARQ_CLIQUES, COLUNAS_CLIQUES)
        novo = pd.DataFrame([{"data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                              "evento": evento, "categoria": categoria, "produto": produto}])
        gravar_csv(ARQ_CLIQUES, pd.concat([df, novo], ignore_index=True))
    except Exception:
        pass


def registrar_pedido(nome: str, telefone: str, email: str, itens_txt: str, total: float, forma: str):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    frete = st.session_state.get("frete") or {}
    empresa = st.session_state.get("empresa") or {}
    tipo = "Empresa" if st.session_state.get("modo") == "empresa" else "Cliente"
    endereco = ", ".join(p for p in [frete.get("rua", ""), frete.get("bairro", "")] if p)
    if frete:
        endereco += f" - {frete.get('cidade', '')}/{frete.get('uf', '')} CEP {frete.get('cep', '')}"

    pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
    id_pedido = f"PED-{len(pedidos) + 1:05d}"
    novo = pd.DataFrame([{
        "data": agora, "nome": nome, "telefone": telefone, "email": email,
        "itens": itens_txt, "total": round(total, 2), "id_pedido": id_pedido,
        "status": "Novo", "pagamento": "Pendente", "forma_pagamento": forma,
        "transportadora": "", "codigo_rastreio": "", "link_rastreio": "",
        "previsao_entrega": "", "obs_internas": "", "tipo_cliente": tipo,
        "cpf_cnpj": empresa.get("cnpj", ""), "endereco_entrega": endereco,
        "nf_status": "Não emitida", "nf_numero": "", "nf_chave": "", "nf_link": "",
    }])
    gravar_csv(ARQ_PEDIDOS, pd.concat([pedidos, novo], ignore_index=True))

    clientes = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
    existente = clientes[clientes["telefone"].astype(str) == telefone]
    if existente.empty:
        novo_cli = pd.DataFrame([{
            "data": agora, "nome": nome, "telefone": telefone, "qtd_pedidos": 1, "email": email,
            "cep": frete.get("cep", ""),
            "endereco": ", ".join(p for p in [frete.get("rua", ""), frete.get("bairro", "")] if p),
            "cidade": frete.get("cidade", ""), "uf": frete.get("uf", ""),
            "origem": "Site", "status": "Novo", "ultimo_contato": agora, "tipo": tipo,
            "cpf_cnpj": empresa.get("cnpj", ""), "razao_social": empresa.get("razao_social", ""),
            "responsavel": empresa.get("responsavel", ""), "empresa": empresa.get("razao_social", ""),
        }])
        clientes = pd.concat([clientes, novo_cli], ignore_index=True)
    else:
        idx = existente.index[0]
        atual = pd.to_numeric(clientes.at[idx, "qtd_pedidos"], errors="coerce")
        clientes.at[idx, "qtd_pedidos"] = int(0 if pd.isna(atual) else atual) + 1
        clientes.at[idx, "ultimo_contato"] = agora
        if email and not clientes.at[idx, "email"]:
            clientes.at[idx, "email"] = email
    gravar_csv(ARQ_CLIENTES, clientes)
    return id_pedido
# ===============================================================
# ESTADO DA SESSÃO
# ===============================================================
ESTADO_INICIAL = {
    "carrinho": [], "link_whatsapp": None, "ultimo_adicionado": None,
    "admin": False, "frete": None, "modo": None, "empresa": None,
    "ultimo_pedido_id": None, "pagina": "inicio", "categoria_aberta": None,
    "secao_admin": "📊 Resumo",
}
for chave, valor in ESTADO_INICIAL.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


# ===============================================================
# CARRINHO (com modo empresa e preço por lote)
# ===============================================================
def modo_empresa() -> bool:
    return st.session_state.get("modo") == "empresa"


def desconto_lote(quantidade_total: int) -> int:
    pct = 0
    for faixa in sorted(LOJA["empresa_faixas"], key=lambda f: f["a_partir_de"]):
        if quantidade_total >= faixa["a_partir_de"]:
            pct = faixa["desconto_pct"]
    return pct


def calcular_promocao(preco_unitario: float, quantidade: int):
    """A cada N unidades, 1 é brinde (empresas têm o seu próprio N)."""
    a_cada = LOJA["empresa_brinde_a_cada"] if modo_empresa() else LOJA["brinde_a_cada"]
    ligado = LOJA["brinde_ligado"] and a_cada > 0
    brindes = quantidade // int(a_cada) if ligado else 0
    return quantidade * preco_unitario, brindes, brindes * preco_unitario


def adicionar_ao_carrinho(item: dict, quantidade: int, variacao: str = ""):
    chave = item["id"] + ("|" + variacao if variacao else "")
    nome = item["nome"] + (f" ({variacao})" if variacao else "")
    for existente in st.session_state.carrinho:
        if existente["id"] == chave:
            nova_qtd = existente["quantidade"] + quantidade
            total, brindes, econ = calcular_promocao(item["preco"], nova_qtd)
            existente.update(quantidade=nova_qtd, unidades_gratis=brindes, desconto=econ, subtotal=total)
            return
    total, brindes, econ = calcular_promocao(item["preco"], quantidade)
    st.session_state.carrinho.append({
        "id": chave, "nome": nome, "preco_unitario": item["preco"], "quantidade": quantidade,
        "unidades_gratis": brindes, "desconto": econ, "subtotal": total,
        "imagem": item["imagem"], "categoria": item.get("categoria", ""),
    })


def callback_adicionar(item: dict):
    qtd = st.session_state.get(f"qtd_{item['id']}", 1)
    variacao = st.session_state.get(f"var_{item['id']}", "")
    adicionar_ao_carrinho(item, qtd, variacao)
    registrar_clique("adicionou_carrinho", item.get("categoria", ""), item["nome"])
    st.session_state.link_whatsapp = None
    st.session_state.frete = None
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
        "cep": dados.get("cep", ""), "cidade": dados.get("localidade", ""), "uf": dados.get("uf", ""),
        "bairro": dados.get("bairro", ""), "rua": dados.get("logradouro", ""),
        "valor": valor, "prazo": prazo, "total_na_hora": total,
    }


def email_valido(email: str) -> bool:
    email = email.strip()
    return "@" in email and "." in email.split("@")[-1] and " " not in email


def finalizar_pedido():
    """Valida os dados, grava o pedido e gera o link do WhatsApp."""
    nome = st.session_state.get("cli_nome", "").strip()
    telefone = "".join(ch for ch in st.session_state.get("cli_tel", "") if ch.isdigit())
    email = st.session_state.get("cli_email", "").strip()
    forma = st.session_state.get("forma_pag", "Pix")
    if len(nome) < 2 or len(telefone) < 10:
        st.session_state.erro_cliente = "Preencha seu nome e um WhatsApp válido com DDD."
        return
    if email and not email_valido(email):
        st.session_state.erro_cliente = "O e-mail parece incompleto. Confira ou deixe em branco."
        return
    subtotal, qtd, pct, valor_desc, total = totais_carrinho()
    if modo_empresa() and subtotal < LOJA["empresa_pedido_minimo"]:
        st.session_state.erro_cliente = f"O pedido mínimo para empresas é R$ {LOJA['empresa_pedido_minimo']:.2f}."
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
        id_pedido = registrar_pedido(nome, telefone, email, "; ".join(linhas) + extra_frete,
                                     total_com_frete, forma)
        st.session_state.ultimo_pedido_id = id_pedido
    except Exception:
        pass  # se o registro falhar, o cliente ainda consegue enviar o pedido

    bloco_entrega = ""
    if frete:
        endereco = ", ".join(p for p in [frete["rua"], frete["bairro"]] if p)
        texto_frete = "Grátis" if valor_frete == 0 else f"R$ {valor_frete:.2f}"
        bloco_entrega = (f"\n\n*Entrega:* {endereco} - {frete['cidade']}/{frete['uf']} (CEP {frete['cep']})"
                         f"\n*Frete:* {texto_frete} (prazo estimado: {frete['prazo']} dias úteis)")
    bloco_desc = f"\nDesconto empresa ({pct}%): -R$ {valor_desc:.2f}" if pct else ""
    bloco_empresa = ""
    emp = st.session_state.get("empresa")
    if modo_empresa() and emp:
        bloco_empresa = f"\n*Empresa:* {emp['razao_social']} (CNPJ {emp['cnpj']}) - resp.: {emp['responsavel']}"

    msg = (f"Olá! Meu nome é {nome}. Pedido {id_pedido}:\n\n" + "\n".join(linhas)
           + f"\n\nSubtotal: R$ {subtotal:.2f}" + bloco_desc + bloco_entrega + bloco_empresa
           + (f"\n*E-mail:* {email}" if email else "")
           + f"\n\n*Total Geral: R$ {total_com_frete:.2f}*\n*Pagamento:* {forma}"
           + (f"\n\nPara acompanhar, use o número {id_pedido} no site." if id_pedido else ""))
    st.session_state.link_whatsapp = f"https://wa.me/{LOJA['whatsapp']}?text={urllib.parse.quote(msg)}"
# ===============================================================
# VISUALIZADOR 3D E FOTO COM LUPA
# ===============================================================
def renderizar_visualizador_3d(item: dict, height: int = 250):
    components.html(f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"></script>
    <div style="width:100%;height:{height}px;border-radius:10px;overflow:hidden;background:#e3eafc;position:relative;">
      <model-viewer src="{item['modelo_3d']}" alt="{html.escape(item['nome'])}" camera-controls
        touch-action="pan-y" auto-rotate style="width:100%;height:100%;"></model-viewer>
      <div style="position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,.7);color:#fff;
           font-size:11px;padding:3px 6px;border-radius:4px;">🔄 Arraste para girar</div>
    </div>""", height=height + 10)


def foto_com_lupa(item: dict, height: int = 430):
    reserva = imagem_reserva(item["categoria"], item["nome"])
    url = url_segura(item["imagem"], item["categoria"], item["nome"])
    components.html(f"""
    <div id="lupa" style="width:100%;height:{height}px;overflow:hidden;border-radius:12px;
         background:#e3eafc;cursor:zoom-in;">
      <img id="foto" src="{html.escape(url, quote=True)}" onerror="this.onerror=null;this.src='{reserva}';"
           style="width:100%;height:100%;object-fit:contain;transition:transform .15s ease;">
    </div>
    <script>
      const c = document.getElementById('lupa'), f = document.getElementById('foto');
      c.addEventListener('mousemove', e => {{
        const r = c.getBoundingClientRect();
        f.style.transformOrigin = ((e.clientX-r.left)/r.width*100) + '% ' + ((e.clientY-r.top)/r.height*100) + '%';
        f.style.transform = 'scale(2.5)';
      }});
      c.addEventListener('mouseleave', () => {{ f.style.transform = 'scale(1)'; }});
    </script>""", height=height + 10)


# ===============================================================
# JANELA FLUTUANTE GRANDE DO PRODUTO (todas as informações)
# ===============================================================
@st.dialog("Detalhes do produto", width="large")
def abrir_produto(item: dict):
    registrar_clique("ver_de_perto", item["categoria"], item["nome"])
    esq, dir_ = st.columns([1.15, 1])
    with esq:
        modo = st.radio("Ver como", ["🔍 Foto ampliada", "🔄 Modelo 3D"], horizontal=True,
                        key=f"modo_ver_{item['id']}", label_visibility="collapsed")
        if modo.startswith("🔍"):
            foto_com_lupa(item)
            st.caption("Passe o mouse sobre a foto para ver os detalhes.")
        else:
            renderizar_visualizador_3d(item, height=430)
    with dir_:
        st.markdown(f"## {item['nome']}")
        st.caption(f"{item['categoria']}" + (f" · código {item['sku']}" if item["sku"] else ""))
        if item["em_promo"]:
            st.markdown(f"<span class='selo selo-promo'>PROMOÇÃO</span> <s>R$ {item['preco_cheio']:.2f}</s>",
                        unsafe_allow_html=True)
        st.markdown(f"### R$ {item['preco']:.2f}")
        if item["descricao"]:
            st.write(item["descricao"])
        if item["para_que_serve"]:
            st.markdown(f"**Para que serve:** {item['para_que_serve']}")
        if item["medidas"]:
            st.markdown(f"**Medidas e material:** {item['medidas']}")
        if item["dicas"]:
            st.markdown(f"**Dicas de uso:** {item['dicas']}")
        if item["prazo"]:
            st.markdown(f"**Prazo de produção:** {item['prazo']} dias úteis")
        if LOJA["brinde_ligado"]:
            a_cada = LOJA["empresa_brinde_a_cada"] if modo_empresa() else LOJA["brinde_a_cada"]
            st.caption(f"🔥 A cada {a_cada} unidades, ganhe 1 brinde!")
        st.divider()
        if item["variacoes"]:
            st.selectbox("Tamanho / cor", item["variacoes"], key=f"var_{item['id']}")
        qtd = st.number_input("Quantidade", min_value=1, max_value=10000, value=1, key=f"qtd_{item['id']}")
        _, brindes, eco = calcular_promocao(item["preco"], qtd)
        if brindes > 0:
            st.success(f"+{brindes} brinde(s) grátis! (Economia: R$ {eco:.2f})")
        if st.button("🛒 Adicionar ao carrinho", type="primary", use_container_width=True,
                     key=f"add_{item['id']}"):
            callback_adicionar(item)
            st.rerun()
        texto = urllib.parse.quote(f"Olá! Tenho interesse no produto {item['nome']}. Pode me ajudar?")
        st.link_button("💬 Tirar dúvida no WhatsApp", f"https://wa.me/{LOJA['whatsapp']}?text={texto}",
                       use_container_width=True)


# ===============================================================
# ACOMPANHAR MEU PEDIDO (o cliente consulta)
# ===============================================================
@st.dialog("Acompanhar meu pedido", width="large")
def abrir_acompanhamento():
    st.write("Digite o número do pedido e o WhatsApp usado na compra.")
    num = st.text_input("Número do pedido (ex.: PED-00001)", key="acomp_num").strip().upper()
    tel = "".join(ch for ch in st.text_input("Seu WhatsApp", key="acomp_tel") if ch.isdigit())
    if not st.button("Consultar", type="primary", key="acomp_ok"):
        return
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
        colunas = st.columns(len(ETAPAS_PEDIDO))
        for k, etapa in enumerate(ETAPAS_PEDIDO):
            marca = "✅" if k < atual else ("🟢" if k == atual else "⚪")
            colunas[k].markdown(f"<div style='text-align:center'>{marca}<br><small>{etapa}</small></div>",
                                unsafe_allow_html=True)
        st.progress((atual + 1) / len(ETAPAS_PEDIDO))
    d1, d2, d3 = st.columns(3)
    d1.metric("Pagamento", p["pagamento"] or "-")
    d2.metric("Previsão de entrega", p["previsao_entrega"] or "a definir")
    d3.metric("Transportadora", p["transportadora"] or "a definir")
    if p["codigo_rastreio"]:
        st.info(f"Código de rastreio: **{p['codigo_rastreio']}**")
        link = p["link_rastreio"] or TRANSPORTADORAS.get(p["transportadora"], "")
        if link:
            st.link_button("🚚 Rastrear na transportadora", link)
    if p["nf_link"]:
        st.link_button("🧾 Ver minha nota fiscal", p["nf_link"])
    st.caption(f"Itens: {p['itens']}")


# ===============================================================
# DADOS CARREGADOS
# ===============================================================
df_produtos = carregar_produtos()
CATALOGO = montar_catalogo(df_produtos)
APRESENTACOES = ler_json(ARQ_APRESENTACOES, [])
VITRINE = ler_json(ARQ_VITRINE, [])
os.makedirs(PASTA_VIDEOS, exist_ok=True)
# ===============================================================
# APRESENTAÇÃO PARA EMPRESAS E VITRINE DE VÍDEOS (usadas no painel e na loja)
# ===============================================================
def achar_item(nome: str):
    for dados in CATALOGO.values():
        for it in dados["itens"]:
            if it["nome"] == nome:
                return it
    return None


def render_apresentacao(ap: dict):
    """Monta a página de apresentação personalizada para uma empresa."""
    cor, cor2, texto = ap.get("cor", "#1d4ed8"), ap.get("cor2", "#0ea5e9"), ap.get("cor_texto", "#ffffff")
    if ap.get("fundo_tipo") == "Imagem" and ap.get("fundo_img"):
        fundo = f"background:url('{ap['fundo_img']}') center/cover;"
    elif ap.get("fundo_tipo") == "Cor sólida":
        fundo = f"background:{cor};"
    else:
        fundo = f"background:linear-gradient(120deg,{cor},{cor2});"
    e = lambda v: html.escape(str(v or ""))
    logo = (f"<img src='{ap['logo']}' style='height:80px;max-width:200px;object-fit:contain;"
            f"background:#fff;border-radius:12px;padding:6px;margin-bottom:10px;'>" if ap.get("logo") else "")
    st.markdown(f"""
    <div style="{fundo}border-radius:20px;padding:34px 30px;margin-bottom:16px;text-align:center;
         box-shadow:0 8px 24px rgba(0,0,0,.18);">
      <div style="background:rgba(0,0,0,.25);border-radius:16px;padding:22px;">
        {logo}
        <h1 style="color:{texto} !important;margin:0;font-size:2.2rem;">{e(ap.get('titulo'))}</h1>
        <p style="color:{texto} !important;font-size:1.15rem;margin:6px 0;">
           Proposta especial para <b style="color:{texto} !important;">{e(ap.get('empresa'))}</b></p>
        <p style="color:{texto} !important;font-size:1rem;margin:0;">{e(ap.get('mensagem'))}</p>
      </div>
    </div>""", unsafe_allow_html=True)

    itens = [i for i in (achar_item(n) for n in ap.get("produtos", [])) if i]
    desc = float(ap.get("desconto_pct", 0) or 0)
    marca = e(ap.get("nome_na_peca") or ap.get("empresa"))
    if itens:
        cols = st.columns(min(4, len(itens)))
        for k, it in enumerate(itens):
            reserva = imagem_reserva(it["categoria"], it["nome"])
            url = html.escape(url_segura(it["imagem"], it["categoria"], it["nome"]), quote=True)
            preco = it["preco"] * (1 - desc / 100)
            with cols[k % len(cols)], st.container(border=True):
                st.markdown(f"""
                <div style="position:relative;border-radius:10px;overflow:hidden;">
                  <img src="{url}" onerror="this.onerror=null;this.src='{reserva}';"
                       style="width:100%;aspect-ratio:1/1;object-fit:cover;display:block;">
                  <div style="position:absolute;left:50%;top:55%;transform:translate(-50%,-50%) rotate(-6deg);
                       background:rgba(255,255,255,.85);color:{cor} !important;font-weight:800;
                       padding:4px 12px;border-radius:8px;font-size:1.05rem;white-space:nowrap;">{marca}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"**{it['nome']}**")
                if desc:
                    st.markdown(f"<s>R$ {it['preco']:.2f}</s> → **R$ {preco:.2f}**", unsafe_allow_html=True)
                elif ap.get("mostrar_precos", True):
                    st.markdown(f"R$ {it['preco']:.2f}")
                if it["descricao"]:
                    st.caption(it["descricao"])
    if ap.get("oferta"):
        st.markdown(f"""<div style="background:#fef3c7;border:2px dashed #f59e0b;border-radius:14px;
            padding:16px;text-align:center;font-size:1.1rem;margin:10px 0;">🎁 <b>{e(ap['oferta'])}</b>
            {f"<br><small>Válido até {e(ap['validade'])}</small>" if ap.get('validade') else ''}</div>""",
                    unsafe_allow_html=True)
    texto_wpp = urllib.parse.quote(f"Olá! Vi a apresentação '{ap.get('titulo')}' para {ap.get('empresa')} "
                                   "e quero saber mais.")
    st.link_button("💬 Quero esta proposta (WhatsApp)", f"https://wa.me/{LOJA['whatsapp']}?text={texto_wpp}",
                   type="primary", use_container_width=True)


def link_video(v: dict):
    """Devolve o que o st.video entende: arquivo da pasta videos ou link do YouTube."""
    if v.get("arquivo") and os.path.exists(v["arquivo"]):
        return v["arquivo"]
    link = str(v.get("link", "")).strip()
    if "youtube.com/shorts/" in link:
        link = "https://www.youtube.com/watch?v=" + link.split("/shorts/")[1].split("?")[0]
    return link or None


def render_vitrine(videos: list, colunas: int = 3):
    ativos = [v for v in videos if v.get("ativo", True) and link_video(v)]
    if not ativos:
        st.info("Em breve, vídeos dos nossos produtos aqui.")
        return
    cols = st.columns(colunas)
    for k, v in enumerate(ativos):
        with cols[k % colunas], st.container(border=True):
            st.video(link_video(v))
            st.markdown(f"**{v.get('titulo', '')}**")
            if v.get("descricao"):
                st.caption(v["descricao"])
# ===============================================================
# DECLARAÇÃO DE CONTEÚDO (para enviar sem nota fiscal)
# ===============================================================
def html_declaracao(p) -> str:
    """Monta a declaração de conteúdo pronta para imprimir (Ctrl+P)."""
    itens = [i.strip("- ").strip() for i in str(p["itens"]).split("|")[0].split(";") if i.strip()]
    linhas = "".join(f"<tr><td>{k}</td><td>{html.escape(i)}</td></tr>" for k, i in enumerate(itens, 1))
    e = lambda v: html.escape(str(v or ""))
    return f"""<html><head><meta charset='utf-8'><title>Declaração {e(p['id_pedido'])}</title>
<style>body{{font-family:Arial;margin:30px}} table{{width:100%;border-collapse:collapse}}
td,th{{border:1px solid #333;padding:6px;font-size:13px}} h2{{text-align:center}}</style></head><body>
<h2>DECLARAÇÃO DE CONTEÚDO</h2>
<table><tr><th colspan='2'>REMETENTE</th></tr>
<tr><td>Nome</td><td>{e(LOJA['fiscal_razao'] or LOJA['nome_empresa'])}</td></tr>
<tr><td>CPF/CNPJ</td><td>{e(LOJA['fiscal_cnpj'])}</td></tr>
<tr><td>Endereço</td><td>{e(LOJA['fiscal_endereco'])} - {e(LOJA['fiscal_cidade_uf'])} CEP {e(LOJA['fiscal_cep'])}</td></tr>
<tr><th colspan='2'>DESTINATÁRIO</th></tr>
<tr><td>Nome</td><td>{e(p['nome'])}</td></tr>
<tr><td>CPF/CNPJ</td><td>{e(p['cpf_cnpj'])}</td></tr>
<tr><td>Endereço</td><td>{e(p['endereco_entrega'])}</td></tr></table><br>
<table><tr><th>Item</th><th>Conteúdo</th></tr>{linhas}</table><br>
<p><b>Valor total:</b> R$ {e(p['total'])} &nbsp;&nbsp; <b>Peso total:</b> ________ kg</p>
<p style='font-size:12px'>Declaro que não me enquadro no conceito de contribuinte previsto no art. 4º da
Lei Complementar nº 87/1996, uma vez que não realizo, com habitualidade ou em volume que caracterize
intuito comercial, operações de circulação de mercadoria. Declaro ainda que não estou postando
conteúdo inflamável, explosivo, causador de combustão ou qualquer outro proibido pela legislação.</p>
<p>_____________________, ____/____/______</p><br><p>_____________________________________<br>Assinatura do declarante</p>
</body></html>"""


# ===============================================================
# BACKUP TOTAL (um arquivo .zip com tudo)
# ===============================================================
ARQUIVOS_DADOS = [ARQ_PRODUTOS, ARQ_CLIENTES, ARQ_PEDIDOS, ARQ_FRETE, ARQ_CLIQUES,
                  ARQ_LOJA, ARQ_APRESENTACOES, ARQ_VITRINE]


def gerar_backup_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for arq in ARQUIVOS_DADOS:
            if os.path.exists(arq):
                z.write(arq, arcname=arq)
        if os.path.isdir(PASTA_VIDEOS):
            for nome in os.listdir(PASTA_VIDEOS):
                z.write(os.path.join(PASTA_VIDEOS, nome), arcname=f"{PASTA_VIDEOS}/{nome}")
        # Planilha fácil de abrir no Excel, com produtos e descrições
        prod = ler_csv(ARQ_PRODUTOS, COLUNAS_PRODUTOS).copy()
        prod["imagem"] = prod["imagem"].apply(lambda u: "(foto enviada)" if str(u).startswith("data:") else u)
        z.writestr("LEIA-ME/produtos_para_excel.csv", prod.to_csv(index=False, sep=";").encode("utf-8-sig"))
        cli = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
        z.writestr("LEIA-ME/clientes_para_excel.csv", cli.to_csv(index=False, sep=";").encode("utf-8-sig"))
        z.writestr("LEIA-ME/LEIA-ME.txt",
                   "Backup completo da loja.\n"
                   "Para restaurar: no painel, seção Backup, envie este mesmo arquivo .zip.\n"
                   "A pasta LEIA-ME tem planilhas para abrir no Excel (não são usadas na restauração).\n")
    return buf.getvalue()


def restaurar_backup_zip(arquivo) -> int:
    restaurados = 0
    with zipfile.ZipFile(arquivo) as z:
        for nome in z.namelist():
            if nome in ARQUIVOS_DADOS or (nome.startswith(PASTA_VIDEOS + "/") and not nome.endswith("/")):
                os.makedirs(os.path.dirname(nome) or ".", exist_ok=True)
                with open(nome, "wb") as f:
                    f.write(z.read(nome))
                restaurados += 1
    return restaurados


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
    elif st.button("⚙", key="btn_engrenagem", help=" "):
        abrir_login_admin()


# ===============================================================
# PAINEL DO ADMINISTRADOR (menu na lateral, uma seção por vez)
# ===============================================================
SECOES_ADMIN = {
    "Visão geral": ["📊 Resumo"],
    "Catálogo": ["📦 Produtos", "🖼️ Fotos"],
    "Vendas": ["👥 Clientes", "🧾 Pedidos", "🚚 Rastreio", "📄 Nota fiscal", "📍 Frete"],
    "Marketing": ["🏢 Apresentações", "🎬 Vitrine", "👁️ Interesse"],
    "Configuração": ["🎨 Loja e redes", "💾 Backup"],
}

if st.session_state.admin:
    with st.sidebar:
        st.markdown(f"### ⚙️ {LOJA['nome_empresa']}")
        st.caption("Painel do administrador")
        grupo = st.radio("Área", list(SECOES_ADMIN.keys()), key="grupo_admin")
        secao = st.radio("Seção", SECOES_ADMIN[grupo], key=f"secao_{grupo}")
        st.divider()
        st.caption("Clique no ✖ no alto da página para voltar à loja.")
    titulo_secao(secao)

    # ---------------------------------------------------------- RESUMO
    if secao == "📊 Resumo":
        clientes_r = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
        pedidos_r = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        pedidos_r["total_num"] = pd.to_numeric(pedidos_r["total"], errors="coerce").fillna(0.0)
        validos = pedidos_r[pedidos_r["status"] != "Cancelado"]
        faturamento = validos["total_num"].sum()
        recebido = validos[validos["pagamento"] == "Pago"]["total_num"].sum()
        ticket = faturamento / len(validos) if len(validos) else 0.0
        c = st.columns(4)
        c[0].metric("Pedidos", len(pedidos_r))
        c[1].metric("Faturamento", f"R$ {faturamento:,.2f}")
        c[2].metric("Já recebido", f"R$ {recebido:,.2f}")
        c[3].metric("Ticket médio", f"R$ {ticket:,.2f}")
        c = st.columns(4)
        c[0].metric("Clientes", len(clientes_r))
        c[1].metric("Pagamentos pendentes", int((pedidos_r["pagamento"] == "Pendente").sum()))
        c[2].metric("Em produção", int((pedidos_r["status"] == "Em produção").sum()))
        c[3].metric("Notas a emitir", int(((pedidos_r["nf_status"] == "Não emitida")
                                          & (pedidos_r["status"] != "Cancelado")).sum()))
        e1, e2 = st.columns(2)
        with e1:
            st.markdown("**⚠️ Retornos de clientes para hoje**")
            hoje = datetime.now().strftime("%Y-%m-%d")
            retornos = clientes_r[(clientes_r["proximo_contato"] != "") & (clientes_r["proximo_contato"] <= hoje)]
            if len(retornos):
                st.dataframe(retornos[["nome", "telefone", "proximo_contato"]], hide_index=True,
                             use_container_width=True, height=220)
            else:
                st.caption("Nenhum retorno pendente.")
        with e2:
            st.markdown("**🏆 Melhores clientes**")
            if len(clientes_r):
                gasto = validos.groupby("telefone")["total_num"].sum().rename("gasto_total")
                top = clientes_r.merge(gasto, on="telefone", how="left").fillna({"gasto_total": 0.0})
                st.dataframe(top.sort_values("gasto_total", ascending=False).head(5)[
                    ["nome", "tipo", "qtd_pedidos", "gasto_total"]], hide_index=True,
                    use_container_width=True, height=220)
            else:
                st.caption("Ainda não há clientes.")
    # ---------------------------------------------------------- PRODUTOS
    elif secao == "📦 Produtos":
        n1, n2 = st.columns(2)
        with n1.expander("➕ Nova categoria"):
            nova_cat = st.text_input("Nome da nova categoria", key="nova_cat_nome")
            preco_cat = st.number_input("Preço do primeiro produto (R$)", min_value=0.0, value=50.0,
                                        step=1.0, key="nova_cat_preco")
            if st.button("Criar categoria", type="primary", key="btn_nova_cat"):
                if nova_cat.strip():
                    linha = {c: "" for c in COLUNAS_PRODUTOS}
                    linha.update({"categoria": nova_cat.strip(), "modelo": f"{nova_cat.strip()} Modelo 1",
                                  "preco": preco_cat, "ativo": True, "destaque": False, "estoque": 0,
                                  "custo": 0.0, "peso_g": 0, "prazo_producao_dias": 5,
                                  "preco_promocional": 0.0})
                    gravar_csv(ARQ_PRODUTOS, pd.concat([df_produtos, pd.DataFrame([linha])], ignore_index=True))
                    st.rerun()
                else:
                    st.error("Digite o nome da categoria.")
        with n2.expander("➕ Novo produto"):
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
                    st.rerun()
                else:
                    st.error("Escolha a categoria e digite o nome.")

        f1, f2, f3, f4 = st.columns([2, 2, 1, 1])
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
        POR_PAGINA = 8
        total_pag = max(1, (len(vista_p) + POR_PAGINA - 1) // POR_PAGINA)
        pagina = f4.number_input(f"Página (de {total_pag})", min_value=1, max_value=total_pag,
                                 value=1, step=1, key="pag_prod")
        trecho = vista_p.iloc[(pagina - 1) * POR_PAGINA: pagina * POR_PAGINA]
        st.caption(f"{len(vista_p)} produto(s) encontrado(s).")

        cols_p = st.columns(4)
        for n, (_, prod) in enumerate(trecho.iterrows()):
            pos = int(prod["_pos"])
            with cols_p[n % 4], st.container(border=True):
                mostrar_imagem(prod["imagem"], prod["categoria"], prod["modelo"], classe="cat-img")
                efetivo, em_promo = preco_atual(prod)
                st.markdown(f"**{prod['modelo']}**  \nR$ {efetivo:.2f} · _{prod['categoria']}_")
                selos = ""
                if prod["custo"] > prod["preco"]:
                    selos += "<span class='selo'>custo &gt; preço</span> "
                if em_promo:
                    selos += "<span class='selo selo-promo'>promoção</span> "
                if prod["destaque"]:
                    selos += "<span class='selo selo-ok'>destaque</span>"
                if selos:
                    st.markdown(selos, unsafe_allow_html=True)
                ativo_novo = st.toggle("Visível ao cliente", value=bool(prod["ativo"]), key=f"ativo_{pos}")
                if ativo_novo != bool(prod["ativo"]):
                    base = df_produtos.copy()
                    base.at[pos, "ativo"] = ativo_novo
                    gravar_csv(ARQ_PRODUTOS, base)
                    st.rerun()
                bt1, bt2 = st.columns(2)
                if bt1.button("✏️ Editar", key=f"ed_{pos}", use_container_width=True):
                    st.session_state.editando_produto = pos
                if bt2.button("📋 Duplicar", key=f"dup_{pos}", use_container_width=True):
                    copia = df_produtos.iloc[[pos]].copy()
                    copia["modelo"] = copia["modelo"] + " (cópia)"
                    gravar_csv(ARQ_PRODUTOS, pd.concat([df_produtos, copia], ignore_index=True))
                    st.rerun()

        pos_ed = st.session_state.get("editando_produto")
        if pos_ed is not None and pos_ed < len(df_produtos):
            ed = df_produtos.iloc[pos_ed]
            titulo_secao(f"✏️ Editando: {ed['modelo']}")
            with st.form(f"form_prod_{pos_ed}"):
                tab_a, tab_b, tab_c, tab_d = st.tabs(["Básico", "Ficha do produto", "Promoção e variações",
                                                      "Controle interno"])
                with tab_a:
                    e_cat = st.text_input("Categoria", value=ed["categoria"])
                    e_nome = st.text_input("Nome do modelo", value=ed["modelo"])
                    e_preco = st.number_input("Preço (R$)", min_value=0.0, value=float(ed["preco"]), step=1.0)
                    e_img = st.text_input("Foto (link). Para enviar do computador use a seção Fotos",
                                          value="" if str(ed["imagem"]).startswith("data:") else ed["imagem"])
                    e_ativo = st.checkbox("Visível ao cliente", value=bool(ed["ativo"]))
                    e_dest = st.checkbox("Destaque (aparece primeiro)", value=bool(ed["destaque"]))
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
                    e_var = st.text_input("Variações separadas por vírgula (ex.: P, M, G)", value=ed["variacoes"])
                with tab_d:
                    e_sku = st.text_input("Código (SKU)", value=ed["sku"])
                    e_custo = st.number_input("Custo (R$)", min_value=0.0, value=float(ed["custo"]), step=1.0)
                    e_estq = st.number_input("Estoque", min_value=0, value=int(ed["estoque"]), step=1)
                    e_peso = st.number_input("Peso (g)", min_value=0, value=int(ed["peso_g"]), step=10)
                    e_prazo = st.number_input("Prazo de produção (dias)", min_value=0,
                                              value=int(ed["prazo_producao_dias"]), step=1)
                    e_tags = st.text_input("Etiquetas", value=ed["tags"])
                    e_obs = st.text_area("Observações internas (só você vê)", value=ed["obs_internas"])
                s1, s2 = st.columns(2)
                salvar_p = s1.form_submit_button("💾 Salvar este produto", type="primary")
                excluir_p = s2.form_submit_button("🗑️ Excluir produto")
            if salvar_p:
                base = df_produtos.copy()
                valores = {"categoria": e_cat, "modelo": e_nome, "preco": e_preco,
                           "imagem": e_img if e_img else ed["imagem"], "ativo": e_ativo, "destaque": e_dest,
                           "descricao": e_desc, "para_que_serve": e_serve, "medidas": e_med, "dicas": e_dicas,
                           "preco_promocional": e_promo, "promo_inicio": e_ini, "promo_fim": e_fim,
                           "variacoes": e_var, "sku": e_sku, "custo": e_custo, "estoque": e_estq,
                           "peso_g": e_peso, "prazo_producao_dias": e_prazo, "tags": e_tags, "obs_internas": e_obs}
                for campo, valor in valores.items():
                    base.at[pos_ed, campo] = valor
                gravar_csv(ARQ_PRODUTOS, base)
                st.session_state.editando_produto = None
                st.rerun()
            if excluir_p:
                gravar_csv(ARQ_PRODUTOS, df_produtos.drop(index=df_produtos.index[pos_ed]).reset_index(drop=True))
                st.session_state.editando_produto = None
                st.rerun()

    # ---------------------------------------------------------- FOTOS
    elif secao == "🖼️ Fotos":
        st.caption("Envie a foto do computador ou do celular (até 2 MB). Ela fica guardada no cadastro do produto.")
        categorias_f = sorted(df_produtos["categoria"].unique().tolist())
        if not categorias_f:
            st.info("Cadastre produtos primeiro.")
        else:
            s1, s2 = st.columns(2)
            cat_f = s1.selectbox("Categoria", categorias_f, key="foto_cat")
            mod_f = s2.selectbox("Produto", df_produtos[df_produtos["categoria"] == cat_f]["modelo"].tolist(),
                                 key="foto_mod")
            mascara = (df_produtos["categoria"] == cat_f) & (df_produtos["modelo"] == mod_f)
            atual = df_produtos[mascara].iloc[0]
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown("**Foto atual**")
                mostrar_imagem(atual["imagem"], cat_f, mod_f)
            with col_b:
                st.markdown("**Enviar nova foto**")
                arquivo = st.file_uploader("Imagem", type=["png", "jpg", "jpeg", "webp"], key="foto_upload")
                if arquivo is not None:
                    if arquivo.size > 2 * 1024 * 1024:
                        st.error("A foto passa de 2 MB.")
                    elif st.button("✅ Usar esta foto", type="primary", key="foto_salvar"):
                        novo_df = df_produtos.copy()
                        novo_df.loc[mascara, "imagem"] = (f"data:{arquivo.type or 'image/jpeg'};base64,"
                                                          + base64.b64encode(arquivo.getvalue()).decode())
                        gravar_csv(ARQ_PRODUTOS, novo_df)
                        st.rerun()
                link_foto = st.text_input("Ou cole o link da foto", key="foto_link")
                if st.button("Usar este link", key="foto_link_salvar") and link_foto.strip():
                    novo_df = df_produtos.copy()
                    novo_df.loc[mascara, "imagem"] = link_foto.strip()
                    gravar_csv(ARQ_PRODUTOS, novo_df)
                    st.rerun()
            with col_c:
                st.markdown("**Mesma foto para a categoria toda**")
                arq_cat = st.file_uploader("Imagem da categoria", type=["png", "jpg", "jpeg", "webp"],
                                           key="foto_upload_cat")
                if arq_cat is not None and arq_cat.size <= 2 * 1024 * 1024:
                    if st.button(f"Aplicar em todos de {cat_f}", key="foto_cat_salvar"):
                        novo_df = df_produtos.copy()
                        novo_df.loc[novo_df["categoria"] == cat_f, "imagem"] = (
                            f"data:{arq_cat.type};base64," + base64.b64encode(arq_cat.getvalue()).decode())
                        gravar_csv(ARQ_PRODUTOS, novo_df)
                        st.rerun()
                elif arq_cat is not None:
                    st.error("A foto passa de 2 MB.")
    # ---------------------------------------------------------- CLIENTES
    elif secao == "👥 Clientes":
        clientes = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
        pedidos_c = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        pedidos_c["total_num"] = pd.to_numeric(pedidos_c["total"], errors="coerce").fillna(0.0)

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
        m = st.columns(5)
        m[0].metric("Clientes", len(clientes))
        m[1].metric("Ativos", len(grupos["ativos"]))
        m[2].metric("Adormecidos", len(grupos["adormecidos"]))
        m[3].metric("Aniversariantes", len(grupos["aniversariantes"]))
        m[4].metric("Com e-mail", int((clientes["email"].astype(str).str.contains("@")).sum()))

        sub_todos, sub_adorm, sub_aniv, sub_hist = st.tabs(
            ["📋 Todos", "😴 Chamar de volta", "🎂 Aniversariantes", "📇 Histórico"])
        with sub_todos:
            busca = st.text_input("🔎 Buscar por nome, telefone, e-mail, cidade ou empresa", key="busca_cliente")
            vista = clientes.copy()
            if busca.strip():
                termo = busca.strip().lower()
                mascara = vista[["nome", "telefone", "email", "cidade", "empresa"]].apply(
                    lambda col: col.astype(str).str.lower().str.contains(termo, regex=False)).any(axis=1)
                vista = vista[mascara]
            vista = vista.copy()
            vista["aceita_promocoes"] = vista["aceita_promocoes"].astype(str).str.lower() == "true"
            vista["qtd_pedidos"] = pd.to_numeric(vista["qtd_pedidos"], errors="coerce").fillna(0).astype(int)
            cli_editado = st.data_editor(
                vista, num_rows="dynamic", use_container_width=True, key="editor_clientes", height=380,
                column_config={
                    "data": st.column_config.TextColumn("Cliente desde", disabled=True),
                    "nome": st.column_config.TextColumn("Nome", required=True),
                    "telefone": st.column_config.TextColumn("WhatsApp", required=True),
                    "email": st.column_config.TextColumn("E-mail"),
                    "qtd_pedidos": st.column_config.NumberColumn("Pedidos", min_value=0, step=1),
                    "tipo": st.column_config.SelectboxColumn("Tipo", options=["Cliente", "Empresa"]),
                    "cpf_cnpj": st.column_config.TextColumn("CPF / CNPJ"),
                    "data_nascimento": st.column_config.TextColumn("Nascimento (dd/mm/aaaa)"),
                    "origem": st.column_config.SelectboxColumn("Como chegou", options=ORIGENS_CLIENTE),
                    "status": st.column_config.SelectboxColumn("Status", options=STATUS_CLIENTE),
                    "proximo_contato": st.column_config.TextColumn("Próximo contato (aaaa-mm-dd)"),
                    "aceita_promocoes": st.column_config.CheckboxColumn("Aceita promoções"),
                    "observacoes": st.column_config.TextColumn("Observações", width="large"),
                })
            b1, b2 = st.columns(2)
            if b1.button("💾 Salvar clientes", type="primary", key="salvar_clientes"):
                if busca.strip():
                    st.warning("Limpe a busca antes de salvar, para não perder clientes escondidos.")
                else:
                    salvar = cli_editado.copy()
                    salvar["aceita_promocoes"] = salvar["aceita_promocoes"].astype(str)
                    gravar_csv(ARQ_CLIENTES, salvar)
                    st.rerun()
            emails = ",".join(e for e in clientes["email"].astype(str) if "@" in e)
            if emails:
                b2.link_button("✉️ Escrever e-mail para todos", f"mailto:?bcc={emails}")
        with sub_adorm:
            if not grupos["adormecidos"]:
                st.success("Nenhum cliente adormecido.")
            for cli in grupos["adormecidos"]:
                uc = ultima_compra(cli["telefone"])
                texto = random.choice(LOJA["msgs_retorno"]).replace("{nome}", cli["nome"].split()[0])
                num = "".join(ch for ch in str(cli["telefone"]) if ch.isdigit())
                with st.container(border=True):
                    a1, a2 = st.columns([3, 1])
                    a1.markdown(f"**{cli['nome']}** · última compra há {(datetime.now() - uc).days} dias")
                    a1.caption(texto)
                    a2.link_button("💬 WhatsApp", f"https://wa.me/{num}?text={urllib.parse.quote(texto)}",
                                   use_container_width=True)
        with sub_aniv:
            if not grupos["aniversariantes"]:
                st.info("Nenhum aniversariante este mês.")
            for cli in grupos["aniversariantes"]:
                texto = LOJA["msg_aniversario"].replace("{nome}", cli["nome"].split()[0])
                num = "".join(ch for ch in str(cli["telefone"]) if ch.isdigit())
                with st.container(border=True):
                    a1, a2 = st.columns([3, 1])
                    a1.markdown(f"🎂 **{cli['nome']}** · {cli['data_nascimento']}")
                    a2.link_button("💬 Parabenizar", f"https://wa.me/{num}?text={urllib.parse.quote(texto)}",
                                   use_container_width=True)
        with sub_hist:
            if len(clientes):
                nomes = [f"{r['nome']} - {r['telefone']}" for _, r in clientes.iterrows()]
                tel_escolhido = st.selectbox("Cliente", nomes, key="hist_cliente").rsplit(" - ", 1)[1]
                hist = pedidos_c[pedidos_c["telefone"].astype(str) == tel_escolhido]
                h1, h2 = st.columns(2)
                h1.metric("Pedidos", len(hist))
                h2.metric("Total gasto", f"R$ {hist[hist['status'] != 'Cancelado']['total_num'].sum():,.2f}")
                st.dataframe(hist[["data", "id_pedido", "itens", "total", "status"]].iloc[::-1],
                             use_container_width=True, hide_index=True)
            else:
                st.info("Ainda não há clientes.")

    # ---------------------------------------------------------- PEDIDOS
    elif secao == "🧾 Pedidos":
        pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        pedidos["total_num"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0.0)
        p = st.columns(3)
        p[0].metric("Pedidos", len(pedidos))
        p[1].metric("Total em pedidos", f"R$ {pedidos['total_num'].sum():,.2f}")
        p[2].metric("Aguardando pagamento", int((pedidos["pagamento"] == "Pendente").sum()))
        filtro_status_p = st.multiselect("Filtrar por status", STATUS_PEDIDO, key="filtro_status_ped")
        vista_p2 = pedidos[["data", "id_pedido", "nome", "telefone", "email", "itens", "total",
                            "status", "pagamento", "forma_pagamento", "obs_internas", "tipo_cliente"]]
        if filtro_status_p:
            vista_p2 = vista_p2[vista_p2["status"].isin(filtro_status_p)]
        ped_editado = st.data_editor(
            vista_p2.iloc[::-1], use_container_width=True, key="editor_pedidos", num_rows="fixed", height=400,
            column_config={
                "data": st.column_config.TextColumn("Data", disabled=True),
                "id_pedido": st.column_config.TextColumn("Nº", disabled=True),
                "nome": st.column_config.TextColumn("Cliente", disabled=True),
                "telefone": st.column_config.TextColumn("WhatsApp", disabled=True),
                "email": st.column_config.TextColumn("E-mail"),
                "itens": st.column_config.TextColumn("Itens", disabled=True, width="large"),
                "total": st.column_config.TextColumn("Total (R$)", disabled=True),
                "tipo_cliente": st.column_config.TextColumn("Tipo", disabled=True),
                "status": st.column_config.SelectboxColumn("Status", options=STATUS_PEDIDO),
                "pagamento": st.column_config.SelectboxColumn("Pagamento", options=STATUS_PAGAMENTO),
                "forma_pagamento": st.column_config.SelectboxColumn("Forma", options=FORMAS_PAGAMENTO),
                "obs_internas": st.column_config.TextColumn("Obs. internas", width="large"),
            })
        b1, b2 = st.columns(2)
        if b1.button("💾 Salvar pedidos", type="primary", key="salvar_pedidos"):
            completo = pedidos.drop(columns=["total_num"]).copy()
            for _, linha in ped_editado.iterrows():
                alvo = completo["id_pedido"] == linha["id_pedido"]
                for campo in ["email", "status", "pagamento", "forma_pagamento", "obs_internas"]:
                    completo.loc[alvo, campo] = linha[campo]
            gravar_csv(ARQ_PEDIDOS, completo)
            st.rerun()
        b2.download_button("⬇️ Baixar pedidos (CSV)",
                           pedidos.drop(columns=["total_num"]).to_csv(index=False).encode("utf-8"),
                           "pedidos.csv", "text/csv")

    # ---------------------------------------------------------- RASTREIO
    elif secao == "🚚 Rastreio":
        pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        abertos = pedidos[~pedidos["status"].isin(["Entregue", "Cancelado"])]
        r = st.columns(4)
        r[0].metric("Em aberto", len(abertos))
        r[1].metric("Em produção", int((pedidos["status"] == "Em produção").sum()))
        r[2].metric("Enviados", int((pedidos["status"] == "Enviado").sum()))
        r[3].metric("Sem código de rastreio", int(((pedidos["status"] == "Enviado")
                                                   & (pedidos["codigo_rastreio"] == "")).sum()))
        if pedidos.empty:
            st.info("Ainda não há pedidos.")
        else:
            so_abertos = st.toggle("Mostrar só pedidos em aberto", value=True, key="rast_abertos")
            lista = (abertos if so_abertos and len(abertos) else pedidos).iloc[::-1]
            opcoes = [f"{p['id_pedido']} · {p['nome']} · {p['status']}" for _, p in lista.iterrows()]
            escolha = st.selectbox("Pedido (código e nome do cliente)", opcoes, key="rast_pedido")
            id_sel = escolha.split(" · ")[0]
            ped = pedidos[pedidos["id_pedido"] == id_sel].iloc[0]
            with st.form(f"form_rast_{id_sel}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Cliente:** {ped['nome']}  \n**WhatsApp:** {ped['telefone']}")
                    r_email = st.text_input("E-mail do cliente", value=ped["email"])
                    r_status = st.selectbox("Andamento", STATUS_PEDIDO,
                                            index=STATUS_PEDIDO.index(ped["status"]) if ped["status"] in STATUS_PEDIDO else 0)
                    r_prev = st.text_input("Previsão de entrega (ex.: 25/11/2026)", value=ped["previsao_entrega"])
                with c2:
                    nomes_t = list(TRANSPORTADORAS.keys())
                    r_transp = st.selectbox("Transportadora", nomes_t,
                                            index=nomes_t.index(ped["transportadora"]) if ped["transportadora"] in nomes_t else 0)
                    r_cod = st.text_input("Código de rastreio", value=ped["codigo_rastreio"])
                    r_link = st.text_input("Link de rastreio (vazio = site da transportadora)", value=ped["link_rastreio"])
                salvar_r = st.form_submit_button("💾 Salvar rastreio", type="primary")
            if salvar_r:
                alvo = pedidos["id_pedido"] == id_sel
                for campo, valor in {"email": r_email, "status": r_status, "previsao_entrega": r_prev,
                                     "transportadora": r_transp, "codigo_rastreio": r_cod.strip().upper(),
                                     "link_rastreio": r_link.strip()}.items():
                    pedidos.loc[alvo, campo] = valor
                gravar_csv(ARQ_PEDIDOS, pedidos)
                st.success("Rastreio salvo! O cliente já vê em Acompanhar meu pedido.")
                st.rerun()
            link = ped["link_rastreio"] or TRANSPORTADORAS.get(ped["transportadora"], "") or LOJA.get("link_loja", "")
            msg = (LOJA["msg_rastreio"].replace("{nome}", ped["nome"].split()[0] if ped["nome"] else "")
                   .replace("{pedido}", ped["id_pedido"]).replace("{status}", ped["status"])
                   .replace("{codigo}", ped["codigo_rastreio"] or "em breve").replace("{link}", link))
            st.markdown("**Avisar o cliente**")
            st.caption(msg)
            a1, a2 = st.columns(2)
            num = "".join(ch for ch in str(ped["telefone"]) if ch.isdigit())
            a1.link_button("💬 Avisar no WhatsApp", f"https://wa.me/{num}?text={urllib.parse.quote(msg)}",
                           use_container_width=True)
            if "@" in str(ped["email"]):
                assunto = urllib.parse.quote(f"Seu pedido {ped['id_pedido']}")
                a2.link_button("✉️ Avisar por e-mail",
                               f"mailto:{ped['email']}?subject={assunto}&body={urllib.parse.quote(msg)}",
                               use_container_width=True)
    # ---------------------------------------------------------- NOTA FISCAL
    elif secao == "📄 Nota fiscal":
        guia, emitir, dados = st.tabs(["📘 Como funciona", "🧾 Notas dos pedidos", "🏢 Meus dados fiscais"])
        with guia:
            st.markdown("""
**O app organiza, mas quem emite a nota é um sistema oficial.** A nota só vale quando passa pela
prefeitura ou pela Sefaz do seu estado. Este painel guarda os dados e o número de cada nota.

**1. Descubra qual nota você precisa**
- Vende produto (copo, camiseta, boné): é **NF-e**, nota de produto, emitida pela Sefaz do estado.
- Vende só o serviço de personalização: é **NFS-e**, nota de serviço, emitida pela prefeitura.
- **MEI** que vende para pessoa física não é obrigado a emitir, mas precisa emitir quando vende para empresa (CNPJ).

**2. Escolha onde emitir**
- De graça: o emissor do Sebrae ou o portal da Sefaz do seu estado (NF-e) e o portal nacional da NFS-e.
- Pago e mais fácil: Bling, Tiny, NFE.io, eNotas e parecidos, que puxam os dados do pedido.
- Para a NF-e você vai precisar de um **certificado digital A1** e da **inscrição estadual**.

**3. Para cada pedido**
1. Abra a aba *Notas dos pedidos* e escolha o pedido.
2. Clique em *Abrir emissor* e copie os dados que aparecem (cliente, CPF/CNPJ, itens, valor).
3. Depois de emitir, cole aqui o número, a chave de 44 números e o link do PDF (DANFE).
4. O cliente passa a ver o botão *Ver minha nota fiscal* em Acompanhar meu pedido.

**4. Vai enviar sem nota?**
Pessoa física e MEI dispensado podem enviar pelos Correios com a **declaração de conteúdo**.
Na aba *Notas dos pedidos* existe um botão que gera a declaração pronta para imprimir.

**Dúvida sobre o seu caso?** Converse com um contador. As regras mudam de estado para estado.
""")
        with emitir:
            pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
            if pedidos.empty:
                st.info("Ainda não há pedidos.")
            else:
                n = st.columns(3)
                n[0].metric("A emitir", int((pedidos["nf_status"].isin(["", "Não emitida"])
                                             & (pedidos["status"] != "Cancelado")).sum()))
                n[1].metric("Emitidas", int((pedidos["nf_status"] == "Emitida").sum()))
                n[2].metric("Com declaração", int(pedidos["nf_status"].str.startswith("Sem nota").sum()))
                opcoes = [f"{p['id_pedido']} · {p['nome']} · {p['nf_status'] or 'Não emitida'}"
                          for _, p in pedidos.iloc[::-1].iterrows()]
                id_sel = st.selectbox("Pedido", opcoes, key="nf_pedido").split(" · ")[0]
                ped = pedidos[pedidos["id_pedido"] == id_sel].iloc[0]
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Dados para copiar no emissor**")
                    st.code(f"Cliente: {ped['nome']}\nCPF/CNPJ: {ped['cpf_cnpj'] or '(pedir ao cliente)'}\n"
                            f"E-mail: {ped['email']}\nEndereço: {ped['endereco_entrega']}\n"
                            f"Itens: {ped['itens']}\nValor total: R$ {ped['total']}", language=None)
                    if LOJA.get("fiscal_emissor_link"):
                        st.link_button("🌐 Abrir emissor de notas", LOJA["fiscal_emissor_link"],
                                       use_container_width=True)
                    st.download_button("📦 Baixar declaração de conteúdo", html_declaracao(ped).encode("utf-8"),
                                       f"declaracao_{id_sel}.html", "text/html", use_container_width=True)
                    st.caption("Abra o arquivo baixado e aperte Ctrl+P para imprimir.")
                with c2, st.form(f"form_nf_{id_sel}"):
                    st.markdown("**Registrar a nota emitida**")
                    nf_st = st.selectbox("Situação", STATUS_NF,
                                         index=STATUS_NF.index(ped["nf_status"]) if ped["nf_status"] in STATUS_NF else 0)
                    nf_num = st.text_input("Número da nota", value=ped["nf_numero"])
                    nf_ch = st.text_input("Chave de acesso (44 números)", value=ped["nf_chave"])
                    nf_lk = st.text_input("Link do PDF da nota (DANFE)", value=ped["nf_link"])
                    nf_doc = st.text_input("CPF/CNPJ do cliente", value=ped["cpf_cnpj"])
                    if st.form_submit_button("💾 Salvar nota", type="primary"):
                        so_num = "".join(ch for ch in nf_ch if ch.isdigit())
                        if nf_ch and len(so_num) != 44:
                            st.error("A chave de acesso precisa ter 44 números.")
                        else:
                            alvo = pedidos["id_pedido"] == id_sel
                            for campo, valor in {"nf_status": nf_st, "nf_numero": nf_num.strip(), "nf_chave": so_num,
                                                 "nf_link": nf_lk.strip(), "cpf_cnpj": nf_doc.strip()}.items():
                                pedidos.loc[alvo, campo] = valor
                            gravar_csv(ARQ_PEDIDOS, pedidos)
                            st.rerun()
        with dados, st.form("form_fiscal"):
            st.caption("Esses dados aparecem na declaração de conteúdo e ajudam no emissor.")
            c1, c2 = st.columns(2)
            f_razao = c1.text_input("Razão social ou seu nome", value=LOJA["fiscal_razao"])
            f_cnpj = c2.text_input("CNPJ ou CPF", value=LOJA["fiscal_cnpj"])
            f_ie = c1.text_input("Inscrição estadual (se tiver)", value=LOJA["fiscal_ie"])
            f_reg = c2.selectbox("Regime", REGIMES, index=REGIMES.index(LOJA["fiscal_regime"])
                                 if LOJA["fiscal_regime"] in REGIMES else 0)
            f_end = c1.text_input("Endereço (rua, número, bairro)", value=LOJA["fiscal_endereco"])
            f_cid = c2.text_input("Cidade/UF", value=LOJA["fiscal_cidade_uf"])
            f_cep = c1.text_input("CEP", value=LOJA["fiscal_cep"])
            f_link = c2.text_input("Link do seu emissor de notas", value=LOJA["fiscal_emissor_link"])
            if st.form_submit_button("💾 Salvar dados fiscais", type="primary"):
                LOJA.update({"fiscal_razao": f_razao, "fiscal_cnpj": f_cnpj, "fiscal_ie": f_ie,
                             "fiscal_regime": f_reg, "fiscal_endereco": f_end, "fiscal_cidade_uf": f_cid,
                             "fiscal_cep": f_cep, "fiscal_emissor_link": f_link.strip()})
                gravar_loja(LOJA)
                st.rerun()

    # ---------------------------------------------------------- FRETE
    elif secao == "📍 Frete":
        c1, c2, c3 = st.columns([1, 1, 1])
        fg_ligado = c1.toggle("Frete grátis ligado", value=bool(LOJA["frete_gratis_ligado"]), key="fg_ligado")
        fg_valor = c2.number_input("Frete grátis a partir de (R$)", min_value=0.0,
                                   value=float(LOJA["frete_gratis_acima"]), step=10.0, key="fg_valor")
        if c3.button("💾 Salvar frete grátis", type="primary", key="salvar_fg"):
            LOJA["frete_gratis_ligado"] = fg_ligado
            LOJA["frete_gratis_acima"] = fg_valor
            gravar_loja(LOJA)
            st.rerun()
        st.caption("O cliente digita o CEP e o app aplica o valor do estado dele.")
        frete_editado = st.data_editor(
            carregar_frete(), num_rows="dynamic", use_container_width=True, key="editor_frete", height=420,
            column_config={
                "uf": st.column_config.TextColumn("UF", max_chars=2, required=True),
                "estado": st.column_config.TextColumn("Estado", required=True),
                "valor": st.column_config.NumberColumn("Frete (R$)", min_value=0.0, format="%.2f"),
                "prazo_dias": st.column_config.NumberColumn("Prazo (dias úteis)", min_value=0, step=1),
            })
        if st.button("💾 Salvar tabela de frete", type="primary", key="salvar_frete"):
            gravar_csv(ARQ_FRETE, frete_editado)
            st.rerun()

    # ---------------------------------------------------------- LOJA E REDES
    elif secao == "🎨 Loja e redes":
        with st.form("form_loja"):
            t1, t2, t3, t4, t5, t6 = st.tabs(["Marca e visual", "Redes e QR code", "Pagamento", "Promoção",
                                              "Mensagens", "Empresas (lote)"])
            with t1:
                c1, c2 = st.columns(2)
                l_nome = c1.text_input("Nome da empresa", value=LOJA["nome_empresa"])
                l_sub = c2.text_input("Subtítulo", value=LOJA["subtitulo"])
                l_frase = c1.text_input("Frase do banner", value=LOJA["frase_banner"])
                l_wpp = c2.text_input("WhatsApp que recebe os pedidos (55 + DDD + número)", value=LOJA["whatsapp"])
                l_cor = c1.color_picker("Cor principal", value=LOJA["cor_principal"])
                l_fundo = c2.selectbox("Fundo da página", FUNDOS,
                                       index=FUNDOS.index(LOJA["fundo"]) if LOJA["fundo"] in FUNDOS else 0)
            with t2:
                c1, c2 = st.columns([2, 1])
                l_insta = c1.text_input("Link do Instagram", value=LOJA["instagram"],
                                        placeholder="https://instagram.com/sualoja")
                l_face = c1.text_input("Link do Facebook", value=LOJA["facebook"],
                                       placeholder="https://facebook.com/sualoja")
                l_redes = c1.checkbox("Mostrar ícones das redes na loja", value=bool(LOJA["mostrar_redes"]))
                l_link = c1.text_input("Endereço da sua loja (para o QR code)", value=LOJA["link_loja"],
                                       placeholder="https://sualoja.streamlit.app")
                c1.caption("O ícone do WhatsApp usa o número da aba Marca e visual.")
                if LOJA["link_loja"]:
                    c2.image(gerar_qr(LOJA["link_loja"]), caption="QR code da loja", width=180)
            with t3:
                c1, c2 = st.columns(2)
                l_pix = c1.text_input("Chave Pix", value=LOJA["pix_chave"])
                l_pixn = c2.text_input("Nome do recebedor (como no banco)", value=LOJA["pix_nome"])
                l_pixc = c1.text_input("Cidade do recebedor", value=LOJA["pix_cidade"])
                l_pixi = c2.text_area("Instruções do Pix", value=LOJA["pix_instrucoes"])
                l_cartao = c1.checkbox("Mostrar opção de cartão", value=bool(LOJA["cartao_ligado"]))
                l_linkc = c2.text_input("Link de pagamento com cartão (Mercado Pago, InfinitePay...)",
                                        value=LOJA["link_pagamento_cartao"])
            with t4:
                l_brl = st.checkbox("Promoção de brinde ligada", value=bool(LOJA["brinde_ligado"]))
                l_bac = st.number_input("A cada quantas unidades ganha 1 brinde", min_value=1,
                                        value=int(LOJA["brinde_a_cada"]), step=1)
            with t5:
                l_dias = st.number_input("Dias sem comprar para virar adormecido", min_value=7,
                                         value=int(LOJA["dias_adormecido"]), step=1)
                l_msgs = st.text_area("Mensagens para chamar de volta (uma por linha; use {nome})",
                                      value="\n".join(LOJA["msgs_retorno"]), height=120)
                l_aniv = st.text_area("Mensagem de aniversário (use {nome})", value=LOJA["msg_aniversario"])
                l_rast = st.text_area("Mensagem de rastreio (use {nome}, {pedido}, {status}, {codigo}, {link})",
                                      value=LOJA["msg_rastreio"])
            with t6:
                c1, c2 = st.columns(2)
                l_emin = c1.number_input("Pedido mínimo para empresas (R$)", min_value=0.0,
                                         value=float(LOJA["empresa_pedido_minimo"]), step=50.0)
                l_efg = c2.checkbox("Frete grátis para empresas", value=bool(LOJA["empresa_frete_gratis"]))
                l_ebr = c1.number_input("A cada quantas unidades a empresa ganha 1 brinde", min_value=1,
                                        value=int(LOJA["empresa_brinde_a_cada"]), step=1)
                l_epr = c2.text_input("Prazo de produção em lote", value=LOJA["empresa_prazo_lote"])
                faixas_df = st.data_editor(pd.DataFrame(LOJA["empresa_faixas"]), num_rows="dynamic", key="editor_faixas",
                    column_config={
                        "a_partir_de": st.column_config.NumberColumn("A partir de (unidades)", min_value=1, step=1),
                        "desconto_pct": st.column_config.NumberColumn("Desconto (%)", min_value=0, max_value=90, step=1)})
            if st.form_submit_button("💾 Salvar configurações da loja", type="primary"):
                LOJA.update({
                    "nome_empresa": l_nome, "subtitulo": l_sub, "frase_banner": l_frase,
                    "whatsapp": "".join(ch for ch in l_wpp if ch.isdigit()), "cor_principal": l_cor, "fundo": l_fundo,
                    "instagram": l_insta.strip(), "facebook": l_face.strip(), "mostrar_redes": l_redes,
                    "link_loja": l_link.strip(), "pix_chave": l_pix.strip(), "pix_nome": l_pixn.strip(),
                    "pix_cidade": l_pixc.strip(), "pix_instrucoes": l_pixi, "cartao_ligado": l_cartao,
                    "link_pagamento_cartao": l_linkc.strip(), "brinde_ligado": l_brl, "brinde_a_cada": int(l_bac),
                    "dias_adormecido": int(l_dias), "msg_aniversario": l_aniv, "msg_rastreio": l_rast,
                    "msgs_retorno": [m.strip() for m in l_msgs.split("\n") if m.strip()],
                    "empresa_pedido_minimo": float(l_emin), "empresa_frete_gratis": l_efg,
                    "empresa_brinde_a_cada": int(l_ebr), "empresa_prazo_lote": l_epr,
                    "empresa_faixas": [{"a_partir_de": int(r["a_partir_de"]), "desconto_pct": int(r["desconto_pct"])}
                                       for _, r in faixas_df.dropna().iterrows()],
                })
                gravar_loja(LOJA)
                st.rerun()
    # ---------------------------------------------------------- APRESENTAÇÕES PARA EMPRESAS
    elif secao == "🏢 Apresentações":
        st.caption("Monte uma página só para uma empresa, com a marca dela nos seus produtos. "
                   "Depois mande o link ou o QR code para o cliente.")
        nomes_ap = [f"{a['empresa']} · {a['titulo']}" for a in APRESENTACOES]
        c1, c2 = st.columns([3, 1])
        escolha = c1.selectbox("Apresentação", ["➕ Nova apresentação"] + nomes_ap, key="ap_escolha")
        if escolha == "➕ Nova apresentação":
            ap = {"id": uuid.uuid4().hex[:8], "empresa": "", "titulo": "Brindes com a sua marca",
                  "mensagem": "Preparamos uma seleção especial para a sua equipe e os seus clientes.",
                  "cor": COR, "cor2": "#0ea5e9", "cor_texto": "#ffffff", "fundo_tipo": "Degradê",
                  "fundo_img": "", "logo": "", "nome_na_peca": "", "produtos": [], "desconto_pct": 0,
                  "mostrar_precos": True, "oferta": "", "validade": "", "ativo": True}
            indice = None
        else:
            indice = nomes_ap.index(escolha)
            ap = dict(APRESENTACOES[indice])
        editor, previa = st.columns([1, 1.4])
        with editor, st.form(f"form_ap_{ap['id']}"):
            t1, t2, t3 = st.tabs(["Textos", "Visual", "Produtos e oferta"])
            with t1:
                a_emp = st.text_input("Nome da empresa cliente", value=ap["empresa"])
                a_tit = st.text_input("Título", value=ap["titulo"])
                a_msg = st.text_area("Mensagem", value=ap["mensagem"])
                a_marca = st.text_input("Nome que aparece nos produtos (vazio = nome da empresa)",
                                        value=ap["nome_na_peca"])
            with t2:
                a_ftipo = st.radio("Fundo", ["Degradê", "Cor sólida", "Imagem"], horizontal=True,
                                   index=["Degradê", "Cor sólida", "Imagem"].index(ap["fundo_tipo"]))
                k1, k2, k3 = st.columns(3)
                a_cor = k1.color_picker("Cor 1", value=ap["cor"])
                a_cor2 = k2.color_picker("Cor 2", value=ap["cor2"])
                a_cort = k3.color_picker("Texto", value=ap["cor_texto"])
                a_fimg = st.file_uploader("Imagem de fundo (até 2 MB)", type=["png", "jpg", "jpeg", "webp"])
                a_logo = st.file_uploader("Logo da empresa cliente (até 2 MB)", type=["png", "jpg", "jpeg", "webp"])
            with t3:
                todos = [it["nome"] for d in CATALOGO.values() for it in d["itens"]]
                a_prod = st.multiselect("Produtos para mostrar", todos, default=[p for p in ap["produtos"] if p in todos])
                a_desc = st.number_input("Desconto especial (%)", min_value=0, max_value=90,
                                         value=int(ap["desconto_pct"]), step=1)
                a_mprec = st.checkbox("Mostrar preços", value=bool(ap["mostrar_precos"]))
                a_ofer = st.text_input("Oferta em destaque", value=ap["oferta"],
                                       placeholder="Ex.: Na compra de 50 copos, 5 bonés de brinde")
                a_val = st.text_input("Válida até", value=ap["validade"], placeholder="30/12/2026")
                a_ativo = st.checkbox("Link ativo", value=bool(ap["ativo"]))
            g1, g2 = st.columns(2)
            salvar_ap = g1.form_submit_button("💾 Salvar", type="primary")
            excluir_ap = g2.form_submit_button("🗑️ Excluir")
        if salvar_ap:
            if not a_emp.strip():
                st.error("Digite o nome da empresa cliente.")
            else:
                para_b64 = lambda f: f"data:{f.type};base64," + base64.b64encode(f.getvalue()).decode()
                ap.update({"empresa": a_emp.strip(), "titulo": a_tit, "mensagem": a_msg, "nome_na_peca": a_marca,
                           "fundo_tipo": a_ftipo, "cor": a_cor, "cor2": a_cor2, "cor_texto": a_cort,
                           "produtos": a_prod, "desconto_pct": a_desc, "mostrar_precos": a_mprec,
                           "oferta": a_ofer, "validade": a_val, "ativo": a_ativo})
                if a_fimg is not None and a_fimg.size <= 2 * 1024 * 1024:
                    ap["fundo_img"] = para_b64(a_fimg)
                if a_logo is not None and a_logo.size <= 2 * 1024 * 1024:
                    ap["logo"] = para_b64(a_logo)
                if indice is None:
                    APRESENTACOES.append(ap)
                else:
                    APRESENTACOES[indice] = ap
                gravar_json(ARQ_APRESENTACOES, APRESENTACOES)
                st.rerun()
        if excluir_ap and indice is not None:
            APRESENTACOES.pop(indice)
            gravar_json(ARQ_APRESENTACOES, APRESENTACOES)
            st.rerun()
        with previa:
            st.markdown("**Prévia**")
            render_apresentacao(ap)
            if indice is not None and LOJA.get("link_loja"):
                link_ap = f"{LOJA['link_loja'].rstrip('/')}/?apresentacao={ap['id']}"
                q1, q2 = st.columns([2, 1])
                q1.code(link_ap, language=None)
                q1.caption("Mande este link para a empresa.")
                q2.image(gerar_qr(link_ap), width=140)
            elif indice is not None:
                st.warning("Preencha o endereço da loja em Loja e redes para gerar o link e o QR code.")

    # ---------------------------------------------------------- VITRINE DE VÍDEOS
    elif secao == "🎬 Vitrine":
        st.caption("Recomendado: suba o vídeo no YouTube como Não listado e cole o link. "
                   "Arquivos enviados ficam na pasta videos e podem sumir quando o Streamlit Cloud reinicia.")
        with st.form("form_video", clear_on_submit=True):
            c1, c2 = st.columns(2)
            v_tit = c1.text_input("Título do vídeo")
            v_desc = c2.text_input("Descrição curta")
            v_link = c1.text_input("Link do YouTube (ou Shorts)")
            v_arq = c2.file_uploader("Ou envie o arquivo (mp4, até 50 MB)", type=["mp4", "mov", "webm"])
            if st.form_submit_button("➕ Adicionar à vitrine", type="primary"):
                caminho = ""
                if v_arq is not None:
                    if v_arq.size > 50 * 1024 * 1024:
                        st.error("O vídeo passa de 50 MB. Prefira o link do YouTube.")
                        st.stop()
                    caminho = os.path.join(PASTA_VIDEOS, f"{uuid.uuid4().hex[:8]}_{v_arq.name}")
                    with open(caminho, "wb") as f:
                        f.write(v_arq.getvalue())
                if v_link.strip() or caminho:
                    VITRINE.append({"titulo": v_tit, "descricao": v_desc, "link": v_link.strip(),
                                    "arquivo": caminho, "ativo": True})
                    gravar_json(ARQ_VITRINE, VITRINE)
                    st.rerun()
                else:
                    st.error("Cole um link ou envie um arquivo.")
        for k, v in enumerate(VITRINE):
            with st.container(border=True):
                a1, a2, a3, a4 = st.columns([3, 1, 1, 1])
                a1.markdown(f"**{v.get('titulo') or 'Sem título'}** · {'arquivo' if v.get('arquivo') else 'YouTube'}")
                novo_ativo = a2.toggle("Visível", value=v.get("ativo", True), key=f"vid_at_{k}")
                if novo_ativo != v.get("ativo", True):
                    VITRINE[k]["ativo"] = novo_ativo
                    gravar_json(ARQ_VITRINE, VITRINE)
                    st.rerun()
                if a3.button("⬆️ Subir", key=f"vid_up_{k}", disabled=k == 0):
                    VITRINE[k - 1], VITRINE[k] = VITRINE[k], VITRINE[k - 1]
                    gravar_json(ARQ_VITRINE, VITRINE)
                    st.rerun()
                if a4.button("🗑️ Excluir", key=f"vid_del_{k}"):
                    removido = VITRINE.pop(k)
                    if removido.get("arquivo") and os.path.exists(removido["arquivo"]):
                        os.remove(removido["arquivo"])
                    gravar_json(ARQ_VITRINE, VITRINE)
                    st.rerun()
        with st.expander("👀 Ver como o cliente vê"):
            render_vitrine(VITRINE)

    # ---------------------------------------------------------- INTERESSE
    elif secao == "👁️ Interesse":
        cliques = ler_csv(ARQ_CLIQUES, COLUNAS_CLIQUES)
        if cliques.empty:
            st.info("Ainda não há cliques registrados.")
        else:
            i = st.columns(3)
            i[0].metric("Cliques", len(cliques))
            i[1].metric("Categorias abertas", int((cliques["evento"] == "abriu_categoria").sum()))
            i[2].metric("Adições ao carrinho", int((cliques["evento"] == "adicionou_carrinho").sum()))
            g1, g2 = st.columns(2)
            with g1:
                st.markdown("**🔥 Produtos mais vistos**")
                vistos = cliques[cliques["evento"] == "ver_de_perto"]["produto"].value_counts().head(10)
                st.bar_chart(vistos, height=250) if len(vistos) else st.caption("Nada ainda.")
            with g2:
                st.markdown("**🛒 Mais adicionados ao carrinho**")
                add = cliques[cliques["evento"] == "adicionou_carrinho"]["produto"].value_counts().head(10)
                st.bar_chart(add, height=250) if len(add) else st.caption("Nada ainda.")
            g3, g4 = st.columns(2)
            with g3:
                st.markdown("**📂 Categorias mais abertas**")
                cats_ab = cliques[cliques["evento"] == "abriu_categoria"]["categoria"].value_counts()
                st.bar_chart(cats_ab, height=250) if len(cats_ab) else st.caption("Nada ainda.")
            with g4:
                st.markdown("**📅 Cliques por dia**")
                st.line_chart(cliques.assign(dia=cliques["data"].str[:10]).groupby("dia").size(), height=250)

    # ---------------------------------------------------------- BACKUP TOTAL
    elif secao == "💾 Backup":
        st.markdown("""
**Como guardar tudo no seu computador**
1. Clique em *Baixar backup completo*. Vem um arquivo `.zip` com a data no nome.
2. Crie no computador uma pasta chamada **Backup da Loja** e guarde o arquivo lá.
3. Faça isso toda semana. No Streamlit Cloud os dados podem sumir quando o app reinicia.

O zip traz produtos, descrições, fotos, clientes, pedidos, frete, apresentações, vídeos e configurações.
Dentro dele, a pasta *LEIA-ME* tem planilhas que abrem direto no Excel.
""")
        nome_zip = f"backup_loja_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.zip"
        st.download_button("⬇️ Baixar backup completo", gerar_backup_zip(), nome_zip, "application/zip",
                           type="primary", use_container_width=True)
        st.divider()
        st.markdown("**Restaurar um backup**")
        enviado = st.file_uploader("Envie o arquivo .zip do backup", type=["zip"], key="bk_zip")
        if enviado is not None and st.button("♻️ Restaurar agora (substitui os dados atuais)", key="bk_rest"):
            try:
                qtd = restaurar_backup_zip(enviado)
                st.success(f"{qtd} arquivo(s) restaurado(s).")
                st.rerun()
            except Exception as erro:
                st.error(f"Não consegui ler o arquivo: {erro}")

    st.stop()  # com o painel aberto, a vitrine do cliente não aparece
# ===============================================================
# LINK DE APRESENTAÇÃO (?apresentacao=codigo) - abre só a proposta
# ===============================================================
codigo_ap = st.query_params.get("apresentacao")
if codigo_ap:
    ap = next((a for a in APRESENTACOES if a["id"] == codigo_ap and a.get("ativo", True)), None)
    if ap:
        render_apresentacao(ap)
        barra_redes(LOJA)
        if st.button("🛍️ Ver a loja completa", use_container_width=True):
            st.query_params.clear()
            st.rerun()
        st.stop()
    st.warning("Esta apresentação não está mais disponível. Veja nossa loja abaixo.")


# ===============================================================
# BARRA LATERAL DO CLIENTE: carrinho, frete, pagamento
# ===============================================================
with st.sidebar:
    st.header("🛒 Seu Carrinho")
    if not st.session_state.carrinho:
        st.info("O carrinho está vazio. Escolha uma categoria para começar.")
    else:
        subtotal, qtd_total, pct_lote, valor_desc, total_geral = totais_carrinho()
        for i, item in enumerate(st.session_state.carrinho):
            reserva = imagem_reserva(item.get("categoria", ""), item["nome"])
            foto = html.escape(url_segura(item.get("imagem", ""), item.get("categoria", ""), item["nome"]), quote=True)
            brinde = (f"<br><span class='selo selo-ok'>+{item['unidades_gratis']} brinde</span>"
                      if item["unidades_gratis"] > 0 else "")
            st.markdown(
                f"<div class='cartao-carrinho'><img src='{foto}' onerror=\"this.onerror=null;this.src='{reserva}';\">"
                f"<div><div class='nome'>{html.escape(item['nome'])}</div>"
                f"<div class='detalhe'>{item['quantidade']}x R$ {item['preco_unitario']:.2f}</div>"
                f"<div class='detalhe'><b>R$ {item['subtotal']:.2f}</b>{brinde}</div></div></div>",
                unsafe_allow_html=True)
            st.button("🗑️ Remover", key=f"del_{i}_{item['id']}", on_click=remover_do_carrinho,
                      args=(i,), use_container_width=True)
        linha_desc = f"<div>Desconto empresa ({pct_lote}%): -R$ {valor_desc:.2f}</div>" if pct_lote else ""
        st.markdown(f"<div class='resumo-total'><div>{qtd_total} item(ns)</div><div>Subtotal: R$ {subtotal:.2f}</div>"
                    f"{linha_desc}<div class='valor'>R$ {total_geral:.2f}</div></div>", unsafe_allow_html=True)
        if modo_empresa():
            if subtotal < LOJA["empresa_pedido_minimo"]:
                st.warning(f"Pedido mínimo para empresas: R$ {LOJA['empresa_pedido_minimo']:.2f}.")
            proxima = [f for f in sorted(LOJA["empresa_faixas"], key=lambda f: f["a_partir_de"])
                       if f["a_partir_de"] > qtd_total]
            if proxima:
                st.caption(f"Faltam {proxima[0]['a_partir_de'] - qtd_total} unidade(s) para "
                           f"{proxima[0]['desconto_pct']}% de desconto.")

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

        with st.container(border=True):
            st.subheader("💳 Pagamento")
            formas = ["Pix"] + (["Cartão de crédito", "Cartão de débito"] if LOJA["cartao_ligado"] else [])
            st.radio("Forma de pagamento", formas, key="forma_pag", horizontal=True)
            if st.session_state.get("forma_pag", "Pix") == "Pix":
                if LOJA["pix_chave"]:
                    valor_pix = total_geral + ((st.session_state.get("frete") or {}).get("valor", 0.0))
                    copia_cola = codigo_pix(LOJA["pix_chave"], LOJA["pix_nome"], LOJA["pix_cidade"], valor_pix)
                    st.image(gerar_qr(copia_cola), width=200, caption=f"Pix de R$ {valor_pix:.2f}")
                    st.code(copia_cola, language=None)
                    st.caption("Pix Copia e Cola: toque no ícone à direita do código para copiar.")
                st.caption(LOJA["pix_instrucoes"])
            elif LOJA["link_pagamento_cartao"]:
                st.link_button("🔒 Pagar com cartão (site seguro)", LOJA["link_pagamento_cartao"],
                               use_container_width=True)
                st.image(gerar_qr(LOJA["link_pagamento_cartao"]), width=160, caption="Ou aponte a câmera")
            else:
                st.warning("Pagamento com cartão em breve. Escolha Pix ou combine pelo WhatsApp.")
            st.text_input("Seu nome", key="cli_nome")
            st.text_input("Seu WhatsApp (com DDD)", key="cli_tel", placeholder="55999999999")
            st.text_input("Seu e-mail (opcional)", key="cli_email", placeholder="voce@email.com")
            if st.session_state.get("erro_cliente"):
                st.error(st.session_state.erro_cliente)
            st.button("📲 Finalizar Pedido via WhatsApp", type="primary", use_container_width=True,
                      on_click=finalizar_pedido)
            if st.session_state.link_whatsapp:
                if st.session_state.ultimo_pedido_id:
                    st.success(f"Pedido registrado: {st.session_state.ultimo_pedido_id}")
                st.link_button("👉 Clique aqui para enviar no WhatsApp", st.session_state.link_whatsapp,
                               use_container_width=True)
    st.divider()
    if st.button("📦 Acompanhar meu pedido", use_container_width=True, key="btn_acomp"):
        abrir_acompanhamento()
    barra_redes(LOJA, tamanho=28)


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
        if len(razao.strip()) < 2 or len(resp.strip()) < 2 or len("".join(c for c in cnpj if c.isdigit())) != 14:
            st.error("Preencha a razão social, o responsável e um CNPJ com 14 números.")
        else:
            st.session_state.empresa = {"razao_social": razao.strip(), "cnpj": cnpj.strip(), "responsavel": resp.strip()}
            st.session_state.modo = "empresa"
            st.rerun()


def ir_para(pagina: str, categoria: str = None):
    st.session_state.pagina = pagina
    st.session_state.categoria_aberta = categoria


# ===============================================================
# TOPO DA LOJA (banner, redes, menu)
# ===============================================================
st.markdown(f"<div class='banner'><h1>🏷️ {html.escape(LOJA['nome_empresa'])}</h1>"
            f"<p>{html.escape(LOJA['subtitulo'])}</p><p><b>{html.escape(LOJA['frase_banner'])}</b></p></div>",
            unsafe_allow_html=True)
m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1])
m1.button("🏠 Início", use_container_width=True, on_click=ir_para, args=("inicio",), key="nav_inicio")
if VITRINE:
    m2.button("🎬 Vitrine", use_container_width=True, on_click=ir_para, args=("vitrine",), key="nav_vitrine")
if m3.button("🙋 Sou cliente", use_container_width=True, key="modo_cliente",
             type="primary" if st.session_state.modo != "empresa" else "secondary"):
    st.session_state.update(modo="cliente", carrinho=[], frete=None)
    st.rerun()
if m4.button("🏢 Sou empresa", use_container_width=True, key="modo_empresa",
             type="primary" if st.session_state.modo == "empresa" else "secondary"):
    if st.session_state.modo != "empresa":
        abrir_cadastro_empresa()
with m5.popover("📱 QR da loja", use_container_width=True):
    if LOJA.get("link_loja"):
        st.image(gerar_qr(LOJA["link_loja"]), width=200)
        st.caption("Aponte a câmera do celular para abrir a loja.")
    else:
        st.caption("Em breve.")
barra_redes(LOJA)

if modo_empresa():
    emp = st.session_state.empresa
    with st.expander(f"🏢 {emp['razao_social']}: vantagens para empresas", expanded=False):
        v = st.columns(4)
        v[0].metric("Pedido mínimo", f"R$ {LOJA['empresa_pedido_minimo']:.2f}")
        v[1].metric("Frete", "Grátis" if LOJA["empresa_frete_gratis"] else "Conforme tabela")
        v[2].metric("Brinde", f"a cada {LOJA['empresa_brinde_a_cada']} un.")
        v[3].metric("Prazo em lote", LOJA["empresa_prazo_lote"])
        faixas = sorted(LOJA["empresa_faixas"], key=lambda f: f["a_partir_de"])
        if faixas:
            st.caption(" · ".join(f"a partir de {f['a_partir_de']} un.: {f['desconto_pct']}% off" for f in faixas))

# ===============================================================
# PÁGINAS
# ===============================================================
pagina = st.session_state.pagina

if pagina == "vitrine":
    titulo_secao("🎬 Vitrine de vídeos")
    render_vitrine(VITRINE)

elif pagina == "categoria" and st.session_state.categoria_aberta in CATALOGO:
    cat_nome = st.session_state.categoria_aberta
    itens = CATALOGO[cat_nome]["itens"]
    v1, v2 = st.columns([1, 5])
    v1.button("⬅️ Voltar", on_click=ir_para, args=("inicio",), key="voltar_cat", use_container_width=True)
    v2.markdown(f"## {ICONES.get(cat_nome, '🏷️')} {cat_nome} · {len(itens)} modelos")
    if st.session_state.get("ultimo_adicionado"):
        st.success(f"✅ {st.session_state.ultimo_adicionado} adicionado ao carrinho! Veja na barra lateral.")
        st.session_state.ultimo_adicionado = None
    busca = st.text_input("🔎 Buscar nesta categoria", key=f"busca_{cat_nome}")
    if busca.strip():
        itens = [i for i in itens if busca.strip().lower() in i["nome"].lower()]
    colunas = 5 if len(itens) > 8 else 4
    for inicio in range(0, len(itens), colunas):
        cols = st.columns(colunas)
        for idx, item in enumerate(itens[inicio:inicio + colunas]):
            with cols[idx], st.container(border=True):
                mostrar_imagem(item["imagem"], cat_nome, item["nome"], classe="cat-img")
                selo = "<span class='selo selo-promo'>PROMOÇÃO</span> " if item["em_promo"] else ""
                st.markdown(f"{selo}**{item['nome']}**  \nR$ {item['preco']:.2f}", unsafe_allow_html=True)
                if st.button("🔍 Ver detalhes", key=f"ver_{item['id']}", use_container_width=True, type="primary"):
                    abrir_produto(item)

else:
    st.markdown("### 📦 Categorias")
    if not CATALOGO:
        st.info("Nenhum produto ativo no momento.")
    categorias = list(CATALOGO.keys())
    total = len(categorias)
    # Mais categorias = mais colunas, para tudo caber na tela sem rolar
    colunas = 3 if total <= 3 else 4 if total <= 8 else 5 if total <= 10 else 6
    for inicio in range(0, total, colunas):
        cols = st.columns(colunas)
        for idx, cat_nome in enumerate(categorias[inicio:inicio + colunas]):
            destaque = CATALOGO[cat_nome]["destaque"]
            with cols[idx], st.container(border=True):
                mostrar_imagem(destaque["imagem"], cat_nome, cat_nome, classe="cat-img")
                st.markdown(f"**{cat_nome}**  \nA partir de R$ {destaque['preco']:.2f}")
                if st.button(f"Ver {len(CATALOGO[cat_nome]['itens'])} modelos", key=f"btn_cat_{cat_nome}",
                             use_container_width=True):
                    registrar_clique("abriu_categoria", cat_nome)
                    ir_para("categoria", cat_nome)
                    st.rerun()
