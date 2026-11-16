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
PASTA_ARTES = "artes"
ARQ_ARTES_PRONTAS = "dados_artes_prontas.json"
ARQ_FORNECEDORES = "dados_fornecedores.csv"
ARQ_ESTOQUE = "dados_estoque.csv"
ARQ_COMPRAS = "dados_compras.csv"
ARQ_MOVIMENTOS = "dados_movimentos.csv"
COL_FORN = ["nome", "contato", "whatsapp", "site", "email", "o_que_vende", "prazo_dias", "pedido_minimo", "obs"]
COL_EST = ["material", "categoria", "unidade", "quantidade", "minimo", "custo_unit", "fornecedor",
           "usado_em", "por_unidade", "obs"]
COL_COMP = ["data", "id_compra", "fornecedor", "material", "quantidade", "custo_unit", "total",
            "status", "previsao", "obs"]
COL_MOV = ["data", "material", "tipo", "quantidade", "referencia"]
STATUS_COMPRA = ["Orçamento", "Pedida", "Paga", "A caminho", "Recebida", "Cancelada"]
ARQ_PRECOS = "dados_precos_fornecedores.csv"
COL_PRECO = ["data", "fornecedor", "material", "preco", "origem"]
ARQ_EQUIPE = "dados_equipe.json"
ARQ_HIST = "dados_historico_pedidos.csv"
COL_HIST = ["data", "id_pedido", "status"]
# Status em que o material já saiu do estoque (o diretor autorizou)
STATUS_COM_MATERIAL = ["Pago", "Em produção", "Enviado", "Entregue"]

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
    "ent_rua", "ent_numero", "ent_complemento", "ent_bairro",
    "ent_cidade", "ent_uf", "ent_cep", "ent_peso", "personalizacao",
    "itens_json", "estoque_baixado",
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
FONTES_PERSO = ["Padrão", "Cursiva", "Bastão", "Manuscrita", "Elegante"]
CSS_FONTES = {"Padrão": "Arial, sans-serif", "Cursiva": "'Brush Script MT', cursive",
              "Bastão": "Impact, 'Arial Black', sans-serif", "Manuscrita": "'Comic Sans MS', cursive",
              "Elegante": "Georgia, 'Times New Roman', serif"}
# Área de impressão de cada produto (largura x altura em cm). Ajuste no painel na hora de imprimir.
MOLDES_IMPRESSAO = {
    "Caneca 325 ml (20 x 9,5 cm)": (20.0, 9.5),
    "Caneca 450 ml (22 x 10 cm)": (22.0, 10.0),
    "Copo térmico 500 ml (21 x 13 cm)": (21.0, 13.0),
    "Camiseta frente (21 x 29,7 cm)": (21.0, 29.7),
    "Camiseta peito (10 x 10 cm)": (10.0, 10.0),
    "Almofada 40 x 40 (38 x 38 cm)": (38.0, 38.0),
    "Boné (10 x 6 cm)": (10.0, 6.0),
    "Chaveiro (5 x 5 cm)": (5.0, 5.0),
    "Tamanho livre": (10.0, 10.0),
}
# ---------------------------------------------------------------
# Equipe da mini fábrica (você troca pelos nomes reais no painel, em Empresa ao vivo)
# ---------------------------------------------------------------
SETORES = ["Diretoria", "Atendimento", "Produção", "Estoque", "Expedição", "Entrega"]
TONS_PELE = {"Muito clara": "#FBE0CF", "Clara": "#F1C7A8", "Média": "#E0AC88",
             "Morena": "#C68642", "Negra": "#8D5524"}
CORES_CABELO = {"Preto": "#1a1a1a", "Castanho": "#5a3214", "Loiro": "#d4a64a",
                "Ruivo": "#a3401a", "Grisalho": "#9ca3af"}
ESTILOS_CABELO = ["Curto", "Longo", "Coque", "Rabo de cavalo", "Careca", "Boné"]
EQUIPE_PADRAO = [
    {"nome": "Diretor(a)", "cargo": "Diretor(a)", "setor": "Diretoria", "pele": "Média",
     "cabelo": "Grisalho", "estilo": "Curto", "camisa": "#1e293b", "ativo": True},
    {"nome": "Ana", "cargo": "Atendente", "setor": "Atendimento", "pele": "Clara",
     "cabelo": "Castanho", "estilo": "Longo", "camisa": "#db2777", "ativo": True},
    {"nome": "Bruno", "cargo": "Atendente", "setor": "Atendimento", "pele": "Negra",
     "cabelo": "Preto", "estilo": "Curto", "camisa": "#9333ea", "ativo": True},
    {"nome": "Carla", "cargo": "Impressão e sublimação", "setor": "Produção", "pele": "Morena",
     "cabelo": "Preto", "estilo": "Coque", "camisa": "#059669", "ativo": True},
    {"nome": "Diego", "cargo": "Prensa térmica", "setor": "Produção", "pele": "Clara",
     "cabelo": "Loiro", "estilo": "Boné", "camisa": "#0d9488", "ativo": True},
    {"nome": "Elisa", "cargo": "Canecas e copos", "setor": "Produção", "pele": "Média",
     "cabelo": "Ruivo", "estilo": "Rabo de cavalo", "camisa": "#10b981", "ativo": True},
    {"nome": "Fábio", "cargo": "Estoquista", "setor": "Estoque", "pele": "Negra",
     "cabelo": "Preto", "estilo": "Careca", "camisa": "#ea580c", "ativo": True},
    {"nome": "Gabi", "cargo": "Embalagem", "setor": "Expedição", "pele": "Muito clara",
     "cabelo": "Castanho", "estilo": "Rabo de cavalo", "camisa": "#2563eb", "ativo": True},
    {"nome": "Hugo", "cargo": "Motorista", "setor": "Entrega", "pele": "Morena",
     "cabelo": "Preto", "estilo": "Boné", "camisa": "#65a30d", "ativo": True},
]
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
st.set_page_config(page_title=LOJA["nome_empresa"], page_icon="🏷️", layout="wide",
                   initial_sidebar_state="expanded")


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


def _sem_acento(texto: str) -> str:
    """O Pix só aceita letras sem acento no nome e na cidade (São Paulo vira SAO PAULO)."""
    import unicodedata
    limpo = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii")
    return limpo.upper().strip()


def codigo_pix(chave: str, nome: str, cidade: str, valor: float, txid: str = "***") -> str:
    """Gera o Pix Copia e Cola no padrão do Banco Central."""
    nome, cidade, chave = _sem_acento(nome), _sem_acento(cidade), str(chave).strip()
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
    /* Mantém visível a setinha que abre e fecha a barra lateral */
    [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapseButton"] {{ display: flex !important; visibility: visible !important; }}
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
    /* Foto clicável: um botão invisível cobre a foto inteira */
    [class*="st-key-fc_"] {{ position: relative; gap: 0 !important; }}
    [class*="st-key-fcb_"] {{ position: absolute !important; top: 0; left: 0; right: 0; bottom: 0;
        z-index: 3; margin: 0 !important; width: 100% !important; height: 100% !important; }}
    [class*="st-key-fcb_"] .stButton, [class*="st-key-fcb_"] .stButton > button {{
        width: 100% !important; height: 100% !important; min-height: 100% !important; }}
    [class*="st-key-fcb_"] .stButton > button {{ opacity: 0 !important; cursor: zoom-in !important; }}
    [class*="st-key-fc_"] img {{ transition: transform .35s ease; }}
    [class*="st-key-fc_"]:hover img {{ transform: scale(1.12) !important; }}
    [class*="st-key-fc_"]:hover .foto-dica {{ opacity: 1; }}
    .foto-dica {{ position: absolute; left: 8px; bottom: 8px; background: rgba(17,24,39,.75); color: #fff !important;
        font-size: .75rem; padding: 2px 8px; border-radius: 999px; opacity: 0; transition: opacity .2s; pointer-events: none; }}
    /* Botões escondidos que a mini fábrica aperta sozinha */
    .st-key-mc_ocultos, .st-key-mc_host {{ position: absolute !important; width: 1px !important; height: 0 !important;
        overflow: hidden !important; opacity: 0 !important; pointer-events: none !important; }}
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


def html_imagem(url: str, categoria: str, rotulo: str = "", classe: str = "", zoom: bool = True,
                dica: str = "") -> str:
    """Monta a foto em HTML. Link vazio ou quebrado vira o desenho de reserva."""
    reserva = imagem_reserva(categoria, rotulo)
    estilo = ("" if classe else "width:100%;aspect-ratio:4/3;object-fit:cover;display:block;")
    mouse = ('onmouseover="this.style.transform=\'scale(1.25)\'" '
             'onmouseout="this.style.transform=\'scale(1)\'"') if zoom else ""
    etiqueta = f"<span class='foto-dica'>{html.escape(dica)}</span>" if dica else ""
    return ('<div style="overflow:hidden;border-radius:10px;cursor:zoom-in;position:relative;">'
            f'<img class="{classe}" src="{html.escape(url_segura(url, categoria, rotulo), quote=True)}" '
            f'onerror="this.onerror=null;this.src=\'{reserva}\';" '
            f'style="{estilo}transition:transform 0.35s ease;" {mouse}>{etiqueta}</div>')


def mostrar_imagem(url: str, categoria: str, rotulo: str = "", classe: str = ""):
    """Foto com zoom ao passar o mouse."""
    st.markdown(html_imagem(url, categoria, rotulo, classe), unsafe_allow_html=True)


def area_clicavel(chave: str, conteudo_html: str, on_click=None, args=None, dica: str = "Abrir") -> bool:
    """Deixa uma foto inteira clicável (um botão invisível fica por cima dela)."""
    chave = "".join(c if c.isalnum() or c in "_-" else "_" for c in chave)
    with st.container(key=f"fc_{chave}"):
        st.markdown(conteudo_html, unsafe_allow_html=True)
        return st.button(dica, key=f"fcb_{chave}", on_click=on_click, args=args or (), help=dica)
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


def numero_wpp(tel) -> str:
    n = "".join(c for c in str(tel) if c.isdigit())
    return ("55" + n) if n and len(n) <= 11 else n


def registrar_movimento(material: str, tipo: str, quantidade: float, referencia: str = ""):
    mov = ler_csv(ARQ_MOVIMENTOS, COL_MOV)
    novo = pd.DataFrame([{"data": datetime.now().strftime("%Y-%m-%d %H:%M"), "material": material,
                          "tipo": tipo, "quantidade": round(float(quantidade), 2), "referencia": referencia}])
    gravar_csv(ARQ_MOVIMENTOS, pd.concat([mov, novo], ignore_index=True))


def registrar_preco(material: str, fornecedor: str, preco: float, origem: str = "Cotação", data: str = ""):
    """Guarda o preço que o fornecedor cobrou, para o gráfico de preços."""
    tabela = ler_csv(ARQ_PRECOS, COL_PRECO)
    novo = pd.DataFrame([{"data": data or datetime.now().strftime("%Y-%m-%d"), "fornecedor": fornecedor,
                          "material": material, "preco": round(float(preco), 2), "origem": origem}])
    gravar_csv(ARQ_PRECOS, pd.concat([tabela, novo], ignore_index=True))


def baixar_estoque(carrinho: list, id_pedido: str):
    """Cada venda tira do estoque, sozinha, os materiais usados naquele produto."""
    try:
        est = ler_csv(ARQ_ESTOQUE, COL_EST)
        if est.empty:
            return
        est["quantidade"] = pd.to_numeric(est["quantidade"], errors="coerce").fillna(0.0)
        por = pd.to_numeric(est["por_unidade"], errors="coerce").fillna(1.0)
        mudou = False
        for item in carrinho:
            alvo = f"{item.get('categoria', '')} {item['nome']}".lower()
            for idx, linha in est.iterrows():
                chaves = [c.strip().lower() for c in str(linha["usado_em"]).split(",") if c.strip()]
                if chaves and any(c in alvo for c in chaves):
                    gasto = item["quantidade"] * float(por[idx])
                    est.at[idx, "quantidade"] = est.at[idx, "quantidade"] - gasto
                    registrar_movimento(linha["material"], "Saída (pedido)", gasto, id_pedido)
                    mudou = True
        if mudou:
            gravar_csv(ARQ_ESTOQUE, est)
    except Exception:
        pass  # o pedido nunca falha por causa do estoque


def registrar_status(id_pedido: str, status: str):
    """Guarda cada mudança de situação do pedido (a mini fábrica usa para medir o rendimento)."""
    try:
        hist = ler_csv(ARQ_HIST, COL_HIST)
        novo = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                              "id_pedido": id_pedido, "status": status}])
        gravar_csv(ARQ_HIST, pd.concat([hist, novo], ignore_index=True))
    except Exception:
        pass


def itens_do_pedido(p) -> list:
    """Devolve os itens do pedido como lista [{categoria, nome, quantidade}]."""
    try:
        lista = json.loads(p.get("itens_json") or "[]")
        if lista:
            return lista
    except Exception:
        pass
    import re
    catalogo = globals().get("CATALOGO", {})
    nomes = {it["nome"]: cat for cat, d in catalogo.items() for it in d["itens"]}
    lista = []
    texto = str(p.get("itens", "")).split(" | Frete")[0]
    for parte in texto.split(";"):
        m = re.match(r"\s*-?\s*(\d+)x\s+(.+?)(?:\s\(\+|\s\[|\s\(R\$|$)", parte.strip())
        if m:
            nome = m.group(2).strip()
            base = nome.split(" (")[0]
            lista.append({"categoria": nomes.get(base, nomes.get(nome, "")), "nome": nome,
                          "quantidade": int(m.group(1))})
    return lista


def baixar_estoque_pedido(id_pedido: str):
    """Tira do estoque o material do pedido, uma vez só, quando o diretor autoriza."""
    try:
        ped = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        alvo = ped["id_pedido"] == id_pedido
        if not alvo.any() or ped.loc[alvo, "estoque_baixado"].iloc[0] == "sim":
            return
        baixar_estoque(itens_do_pedido(ped[alvo].iloc[0]), id_pedido)
        ped.loc[alvo, "estoque_baixado"] = "sim"
        gravar_csv(ARQ_PEDIDOS, ped)
    except Exception:
        pass


def depois_de_mudar_status(id_pedido: str, antigo: str, novo: str):
    """Tudo o que acontece sozinho quando um pedido muda de situação."""
    if antigo == novo:
        return
    registrar_status(id_pedido, novo)
    if novo in STATUS_COM_MATERIAL:
        baixar_estoque_pedido(id_pedido)


def analise_estoque(margem_dias: int = 7) -> pd.DataFrame:
    """Calcula o consumo por dia, quantos dias o estoque ainda dura e quando pedir ao fornecedor."""
    est = ler_csv(ARQ_ESTOQUE, COL_EST)
    extras = ["consumo_dia", "prazo_forn", "dias_restantes", "repor", "comprar", "data_limite"]
    if est.empty:
        for c in extras:
            est[c] = []
        return est
    for c in ["quantidade", "minimo", "custo_unit"]:
        est[c] = pd.to_numeric(est[c], errors="coerce").fillna(0.0)
    mov = ler_csv(ARQ_MOVIMENTOS, COL_MOV)
    mov["quantidade"] = pd.to_numeric(mov["quantidade"], errors="coerce").fillna(0.0)
    mov["dt"] = pd.to_datetime(mov["data"], format="%Y-%m-%d %H:%M", errors="coerce")
    recentes = mov[mov["tipo"].astype(str).str.startswith("Saída")
                   & (mov["dt"] >= datetime.now() - timedelta(days=30))]
    consumo = recentes.groupby("material")["quantidade"].sum() / 30
    forn = ler_csv(ARQ_FORNECEDORES, COL_FORN)
    prazos = dict(zip(forn["nome"], pd.to_numeric(forn["prazo_dias"], errors="coerce").fillna(7)))
    est["consumo_dia"] = est["material"].map(consumo).fillna(0.0)
    est["prazo_forn"] = est["fornecedor"].map(prazos).fillna(7).astype(int)
    est["dias_restantes"] = [q / c if c > 0 else float("nan") for q, c in zip(est["quantidade"], est["consumo_dia"])]
    repor, comprar, limite = [], [], []
    for _, r in est.iterrows():
        d = r["dias_restantes"]
        precisa = (r["minimo"] > 0 and r["quantidade"] <= r["minimo"]) or \
                  (pd.notna(d) and d <= r["prazo_forn"] + margem_dias)
        repor.append(bool(precisa))
        sugestao = r["consumo_dia"] * 30 + r["minimo"] - r["quantidade"]
        comprar.append(round(max(sugestao, r["minimo"], 1.0), 1) if precisa else 0.0)
        limite.append((datetime.now() + timedelta(days=max(0.0, d - r["prazo_forn"]))).strftime("%d/%m/%Y")
                      if pd.notna(d) else "")
    est["repor"], est["comprar"], est["data_limite"] = repor, comprar, limite
    return est
def salvar_artes(id_pedido: str) -> str:
    """Grava as fotos/artes do carrinho na pasta artes e devolve a lista em texto (JSON)."""
    os.makedirs(PASTA_ARTES, exist_ok=True)
    lista = []
    for n, item in enumerate(st.session_state.get("carrinho", []), start=1):
        p = item.get("perso") or {}
        if not p:
            continue
        caminho = ""
        if p.get("arte"):
            if p["arte"].startswith("http"):
                try:
                    with urllib.request.urlopen(p["arte"], timeout=8) as r:
                        dados = r.read()
                except Exception:
                    dados = b""
                cab = "jpg"
            else:
                cab, b64 = p["arte"].split(",", 1)
                dados = base64.b64decode(b64)
            ext = "png" if "png" in cab else "webp" if "webp" in cab else "jpg"
            caminho = os.path.join(PASTA_ARTES, f"{id_pedido}_{n}.{ext}")
            with open(caminho, "wb") as f:
                f.write(dados)
        lista.append({"item": item["nome"], "quantidade": item["quantidade"], "arquivo": caminho,
                      "texto": p.get("texto", ""), "fonte": p.get("fonte", ""), "cor_texto": p.get("cor_texto", ""),
                      "obs": p.get("obs", ""), "escala": p.get("escala", 100), "arte_nome": p.get("arte_nome", ""),
                      "dx": p.get("dx", 0), "dy": p.get("dy", 0)})
    return json.dumps(lista, ensure_ascii=False) if lista else ""


def registrar_pedido(nome: str, telefone: str, email: str, itens_txt: str, total: float, forma: str):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    frete = st.session_state.get("frete") or {}
    empresa = st.session_state.get("empresa") or {}
    tipo = "Empresa" if st.session_state.get("modo") == "empresa" else "Cliente"
    endereco = ", ".join(p for p in [frete.get("rua", ""), frete.get("bairro", "")] if p)
    if frete:
        endereco += f" - {frete.get('cidade', '')}/{frete.get('uf', '')} CEP {frete.get('cep', '')}"

    pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
    numeros = pd.to_numeric(pedidos["id_pedido"].astype(str).str.replace("PED-", "", regex=False),
                            errors="coerce").dropna()
    id_pedido = f"PED-{int(numeros.max() if len(numeros) else 0) + 1:05d}"
    novo = pd.DataFrame([{
        "data": agora, "nome": nome, "telefone": telefone, "email": email,
        "itens": itens_txt, "total": round(total, 2), "id_pedido": id_pedido,
        "status": "Novo", "pagamento": "Pendente", "forma_pagamento": forma,
        "transportadora": "", "codigo_rastreio": "", "link_rastreio": "",
        "previsao_entrega": "", "obs_internas": "", "tipo_cliente": tipo,
        "cpf_cnpj": empresa.get("cnpj", ""), "endereco_entrega": endereco,
        "nf_status": "Não emitida", "nf_numero": "", "nf_chave": "", "nf_link": "",
        "ent_rua": frete.get("rua", ""), "ent_numero": st.session_state.get("cli_numero", "").strip(),
        "ent_complemento": st.session_state.get("cli_comp", "").strip(), "ent_bairro": frete.get("bairro", ""),
        "ent_cidade": frete.get("cidade", ""), "ent_uf": frete.get("uf", ""), "ent_cep": frete.get("cep", ""),
        "ent_peso": "", "personalizacao": salvar_artes(id_pedido),
        "itens_json": json.dumps([{"categoria": i.get("categoria", ""), "nome": i["nome"],
                                   "quantidade": i["quantidade"]}
                                  for i in st.session_state.get("carrinho", [])], ensure_ascii=False),
        "estoque_baixado": "",
    }])
    gravar_csv(ARQ_PEDIDOS, pd.concat([pedidos, novo], ignore_index=True))
    registrar_status(id_pedido, "Novo")
    # O estoque agora só baixa quando o diretor autoriza o pedido (veja depois_de_mudar_status)

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


def adicionar_ao_carrinho(item: dict, quantidade: int, variacao: str = "", perso: dict = None):
    chave = item["id"] + ("|" + variacao if variacao else "")
    if perso:
        chave += "|" + uuid.uuid4().hex[:6]  # cada arte vira um item separado
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
        "imagem": item["imagem"], "categoria": item.get("categoria", ""), "perso": perso or {},
    })


def marcar_origem(k: str, origem: str):
    """Lembra se o cliente usou por último a foto dele ou uma arte pronta."""
    st.session_state[f"porigem_{k}"] = origem


def arte_escolhida(k: str) -> tuple:
    """Devolve (imagem, nome) da arte que vale agora: a última que o cliente escolheu."""
    arq = st.session_state.get(f"arte_{k}")
    foto = ""
    if arq is not None and arq.size <= 3 * 1024 * 1024:
        foto = f"data:{arq.type or 'image/png'};base64," + base64.b64encode(arq.getvalue()).decode()
    gal_id = st.session_state.get(f"pgal_{k}")
    gal = next((a for a in lista_artes() if a["id"] == gal_id), None) if gal_id else None
    usar_galeria = gal and (not foto or st.session_state.get(f"porigem_{k}") == "galeria")
    if usar_galeria:
        return gal["imagem"], "Arte pronta: " + gal["nome"]
    if foto:
        return foto, "Foto enviada pelo cliente"
    return "", ""


def coletar_perso(item: dict) -> dict:
    """Pega a foto, o texto e as observações que o cliente colocou na janela do produto."""
    k = item["id"]
    perso = {"texto": st.session_state.get(f"ptxt_{k}", "").strip(),
             "fonte": st.session_state.get(f"pfonte_{k}", "Padrão"),
             "cor_texto": st.session_state.get(f"pcor_{k}", "#000000"),
             "obs": st.session_state.get(f"pobs_{k}", "").strip(),
             "escala": st.session_state.get(f"pesc_{k}", 100),
             "dx": st.session_state.get(f"pdx_{k}", 0), "dy": st.session_state.get(f"pdy_{k}", 0),
             "arte": ""}
    perso["arte"], nome_arte = arte_escolhida(k)
    if nome_arte:
        perso["arte_nome"] = nome_arte
    return perso if (perso["arte"] or perso["texto"] or perso["obs"]) else {}


def callback_adicionar(item: dict):
    qtd = st.session_state.get(f"qtd_{item['id']}", 1)
    variacao = st.session_state.get(f"var_{item['id']}", "")
    adicionar_ao_carrinho(item, qtd, variacao, coletar_perso(item))
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
        if i.get("perso"):
            # " / " e não " | ": o "|" separa o frete e cortava os itens na etiqueta e na declaração
            extra += " [personalizado: " + " / ".join(x for x in [i["perso"].get("arte_nome", ""),
                                                              i["perso"].get("texto", "")] if x) + "]"
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
        modo = st.radio("Ver como", ["🎨 Como fica a minha arte", "🔍 Foto ampliada", "🔄 Modelo 3D"],
                        horizontal=True, key=f"modo_ver_{item['id']}", label_visibility="collapsed")
        if modo.startswith("🎨"):
            components.html(mockup_perso(item), height=450)
            st.caption("Escolha uma arte aqui embaixo ou envie a sua foto. A prévia muda na hora.")
        elif modo.startswith("🔍"):
            foto_com_lupa(item)
            st.caption("Passe o mouse sobre a foto para ver os detalhes.")
        else:
            renderizar_visualizador_3d(item, height=430)
        grade_artes(item)
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
            st.radio("Tamanho / tipo", item["variacoes"], key=f"var_{item['id']}", horizontal=True)
        st.markdown("**🎨 Personalize do seu jeito**")
        k = item["id"]
        st.file_uploader("Ou envie a sua foto ou arte (até 3 MB)", type=["png", "jpg", "jpeg", "webp"],
                         key=f"arte_{k}", on_change=marcar_origem, args=(k, "upload"))
        st.text_input("Texto ou nome na peça (opcional)", key=f"ptxt_{k}")
        f1, f2 = st.columns(2)
        f1.selectbox("Estilo da letra", FONTES_PERSO, key=f"pfonte_{k}")
        f2.color_picker("Cor do texto", "#000000", key=f"pcor_{k}")
        st.slider("Tamanho da arte na peça (%)", 30, 100, 100, step=5, key=f"pesc_{k}")
        g1, g2 = st.columns(2)
        g1.slider("Mover ⬅️ ➡️", -100, 100, 0, step=10, key=f"pdx_{k}")
        g2.slider("Mover ⬆️ ⬇️", -100, 100, 0, step=10, key=f"pdy_{k}")
        st.text_area("Como você quer? (posição, cores, detalhes)", key=f"pobs_{k}", height=70)
        arq = st.session_state.get(f"arte_{k}")
        if arq is not None and arq.size > 3 * 1024 * 1024:
            st.error("A foto passa de 3 MB. Diminua o tamanho e envie de novo.")
        st.divider()
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
ARTES_PRONTAS = ler_json(ARQ_ARTES_PRONTAS, [])
os.makedirs(PASTA_VIDEOS, exist_ok=True)
# ===============================================================
# GRADE DE ARTES PRONTAS (embaixo da foto grande do produto)
# ===============================================================
ARTES_EXEMPLO = [
    {"id": f"ex{n}", "nome": nome, "categorias": [], "exemplo": True,
     "imagem": f"https://picsum.photos/seed/{semente}/400/400"}
    for n, (nome, semente) in enumerate([
        ("Paisagem", "montanha"), ("Praia", "praia"), ("Flores", "flores"), ("Cidade", "cidade"),
        ("Café", "cafe"), ("Pôr do sol", "sol"), ("Animais", "animal"), ("Abstrata", "abstrata"),
        ("Floresta", "floresta"), ("Montanha", "neve"), ("Noite", "noite"), ("Mar", "mar"),
        ("Vintage", "vintage"), ("Esporte", "esporte"), ("Música", "musica"), ("Viagem", "viagem"),
        ("Campo", "campo"), ("Céu", "ceu"), ("Colorida", "cores"), ("Minimalista", "minimal")], start=1)
]


def lista_artes(categoria: str = "") -> list:
    """Suas artes da Galeria; enquanto não houver nenhuma, mostra exemplos da internet."""
    base = ARTES_PRONTAS if ARTES_PRONTAS else ARTES_EXEMPLO
    return [a for a in base if not categoria or not a.get("categorias") or categoria in a["categorias"]]


def escolher_arte(chave: str, arte_id):
    st.session_state[chave] = arte_id


def escolher_arte_galeria(k: str, arte_id: str):
    """O cliente clicou numa arte pronta: ela vai para a prévia na hora."""
    st.session_state[f"pgal_{k}"] = arte_id
    marcar_origem(k, "galeria")
    st.session_state[f"modo_ver_{k}"] = "🎨 Como fica a minha arte"


def grade_artes(item: dict):
    k = item["id"]
    artes = lista_artes(item["categoria"])
    st.markdown("**🎨 Escolha uma arte pronta** (clique na imagem)")
    if not ARTES_PRONTAS:
        st.caption("Exemplos provisórios. Cadastre as suas em Galeria de artes, no painel.")
    escolhida = st.session_state.get(f"pgal_{k}")
    with st.container(height=340, border=True):
        for ini in range(0, len(artes), 4):
            for c, a in zip(st.columns(4), artes[ini:ini + 4]):
                with c:
                    marcada = escolhida == a["id"]
                    borda = "3px solid #7c3aed" if marcada else "1px solid #d1d5db"
                    area_clicavel(
                        f"g{k}_{a['id']}",
                        f"<div style='overflow:hidden;border-radius:8px;border:{borda};'>"
                        f"<img src='{html.escape(a['imagem'], quote=True)}' style='width:100%;aspect-ratio:1/1;"
                        "object-fit:cover;display:block;'></div>",
                        on_click=escolher_arte_galeria, args=(k, a["id"]), dica="Usar esta arte")
                    st.caption(("✅ " if marcada else "") + a["nome"][:16])
    if escolhida:
        nome_sel = next((a["nome"] for a in artes if a["id"] == escolhida), "")
        st.success(f"✅ Arte escolhida: {nome_sel}. Ela vai junto com o pedido.")
        st.button("✖ Tirar a arte escolhida", key=f"galx_{k}", on_click=escolher_arte, args=(f"pgal_{k}", None))


def tipo_peca(texto: str) -> str:
    """Descobre o formato da peça pelo nome da categoria ou do produto."""
    t = str(texto).lower()
    for chave, tipo in [("canec", "caneca"), ("copo", "copo"), ("térm", "copo"), ("termic", "copo"),
                        ("garraf", "copo"), ("camis", "camiseta"), ("bon", "bone"), ("chav", "chaveiro"),
                        ("almof", "almofada"), ("mate", "mateira")]:
        if chave in t:
            return tipo
    return "quadro"


# Cada peça: (desenho de trás, área de impressão x/y/largura/altura, recorte da área, sombras por cima)
_CIL = ("<linearGradient id='cil' x1='0' x2='1'><stop offset='0' stop-color='#000' stop-opacity='.20'/>"
        "<stop offset='.18' stop-color='#000' stop-opacity='0'/><stop offset='.33' stop-color='#fff' stop-opacity='.45'/>"
        "<stop offset='.5' stop-color='#fff' stop-opacity='0'/><stop offset='.85' stop-color='#000' stop-opacity='.06'/>"
        "<stop offset='1' stop-color='#000' stop-opacity='.24'/></linearGradient>")
PECAS_MOCKUP = {
    "caneca": (
        "<ellipse cx='190' cy='344' rx='112' ry='14' fill='#000' opacity='.12'/>"
        "<path d='M283 140 q72 0 72 76 q0 76 -72 76' stroke='#d1d5db' stroke-width='24' fill='none'/>"
        "<path d='M283 140 q72 0 72 76 q0 76 -72 76' stroke='#f9fafb' stroke-width='15' fill='none'/>"
        "<rect x='95' y='95' width='190' height='247' rx='16' fill='#fff' stroke='#d1d5db' stroke-width='2'/>",
        (112, 130, 156, 185), "<rect x='112' y='130' width='156' height='185'/>",
        "<rect x='95' y='95' width='190' height='247' rx='16' fill='url(#cil)'/>"
        "<ellipse cx='190' cy='97' rx='95' ry='14' fill='#f3f4f6' stroke='#d1d5db' stroke-width='2'/>"
        "<ellipse cx='190' cy='99' rx='84' ry='9' fill='#e5e7eb'/>"),
    "copo": (
        "<ellipse cx='200' cy='350' rx='80' ry='11' fill='#000' opacity='.12'/>"
        "<path d='M118 92 h164 l-20 250 q-62 10 -124 0z' fill='#eef2f7' stroke='#9ca3af' stroke-width='2'/>",
        (140, 125, 120, 180), "<path d='M118 92 h164 l-20 250 q-62 10 -124 0z'/>",
        "<path d='M118 92 h164 l-20 250 q-62 10 -124 0z' fill='url(#cil)'/>"
        "<rect x='110' y='66' width='180' height='30' rx='9' fill='#334155'/>"
        "<rect x='170' y='58' width='60' height='12' rx='5' fill='#1f2937'/>"),
    "camiseta": (
        "<path d='M135 58 q65 30 130 0 l78 36 l-27 72 l-36 -15 v222 h-160 v-222 l-36 15 l-27 -72z' "
        "fill='#fff' stroke='#d1d5db' stroke-width='2'/>",
        (142, 105, 116, 160), "<rect x='142' y='105' width='116' height='160'/>",
        "<path d='M165 60 q35 26 70 0' stroke='#d1d5db' stroke-width='7' fill='none'/>"
        "<path d='M150 300 q20 -60 5 -150 M250 300 q-15 -70 0 -150' stroke='#000' stroke-opacity='.05' stroke-width='10' fill='none'/>"
        "<path d='M135 58 q65 30 130 0 l78 36 l-27 72 l-36 -15 v222 h-160 v-222 l-36 15 l-27 -72z' fill='url(#tecido)'/>"),
    "bone": (
        "<ellipse cx='200' cy='300' rx='150' ry='14' fill='#000' opacity='.10'/>"
        "<path d='M95 250 q0 -142 105 -142 q105 0 105 142z' fill='#fff' stroke='#d1d5db' stroke-width='2'/>",
        (140, 150, 120, 85), "<path d='M95 250 q0 -142 105 -142 q105 0 105 142z'/>",
        "<path d='M95 250 q0 -142 105 -142 q105 0 105 142z' fill='url(#cil)'/>"
        "<path d='M200 108 v142' stroke='#e5e7eb' stroke-width='2'/>"
        "<path d='M58 252 q142 -26 284 0 q-12 42 -142 42 q-130 0 -142 -42z' fill='#e5e7eb' stroke='#cbd5e1' stroke-width='2'/>"
        "<circle cx='200' cy='108' r='7' fill='#e5e7eb'/>"),
    "chaveiro": (
        "<circle cx='200' cy='82' r='28' stroke='#9ca3af' stroke-width='7' fill='none'/>"
        "<rect x='193' y='104' width='14' height='22' rx='4' fill='#9ca3af'/>"
        "<rect x='115' y='120' width='170' height='205' rx='40' fill='#fff' stroke='#cbd5e1' stroke-width='3'/>",
        (130, 136, 140, 172), "<rect x='130' y='136' width='140' height='172' rx='32'/>",
        "<path d='M135 150 q20 -20 60 -22' stroke='#fff' stroke-width='8' stroke-linecap='round' opacity='.8' fill='none'/>"),
    "almofada": (
        "<path d='M70 80 q130 -26 260 0 q26 120 0 240 q-130 26 -260 0 q-26 -120 0 -240z' fill='#fff' "
        "stroke='#d1d5db' stroke-width='2'/>",
        (92, 98, 216, 204), "<path d='M70 80 q130 -26 260 0 q26 120 0 240 q-130 26 -260 0 q-26 -120 0 -240z'/>",
        "<path d='M70 80 q130 -26 260 0 q26 120 0 240 q-130 26 -260 0 q-26 -120 0 -240z' fill='url(#fofo)'/>"),
    "mateira": (
        "<path d='M150 95 q50 -70 100 0' stroke='#78350f' stroke-width='10' fill='none'/>"
        "<rect x='118' y='90' width='164' height='252' rx='26' fill='#92400e' stroke='#78350f' stroke-width='3'/>"
        "<rect x='140' y='140' width='120' height='150' rx='10' fill='#fef3c7'/>",
        (140, 140, 120, 150), "<rect x='140' y='140' width='120' height='150' rx='10'/>",
        "<rect x='118' y='90' width='164' height='252' rx='26' fill='url(#cil)'/>"
        "<path d='M128 110 v220 M272 110 v220' stroke='#fbbf24' stroke-dasharray='6 5' stroke-width='2'/>"),
    "quadro": (
        "<rect x='66' y='66' width='268' height='268' fill='#fff' stroke='#94a3b8' stroke-width='12'/>",
        (90, 90, 220, 220), "<rect x='90' y='90' width='220' height='220'/>", ""),
}


def html_mockup(tipo: str, src: str, texto: str, fonte: str, cor: str, escala: int, dx: int, dy: int,
                nome: str = "", altura: int = 430) -> str:
    """Desenha a peça com a arte do cliente por cima, na área de impressão."""
    fundo, (ax, ay, aw, ah), recorte, sombra = PECAS_MOCKUP.get(tipo, PECAS_MOCKUP["quadro"])
    e = max(30, min(100, int(escala or 100))) / 100
    cx = ax + aw / 2 + (dx or 0) / 100 * aw / 2
    cy = ay + ah / 2 + (dy or 0) / 100 * ah / 2
    texto = str(texto or "")
    fs = max(12.0, min(34.0, aw / max(4, len(texto)) * 1.7)) if texto else 0
    iw, ih = aw * e, ah * e * (0.72 if texto else 1)
    miolo = ""
    if src:
        topo = cy - ih / 2 - (fs * 0.6 if texto else 0)
        miolo += (f"<image href='{html.escape(src, quote=True)}' x='{cx - iw / 2:.1f}' y='{topo:.1f}' "
                  f"width='{iw:.1f}' height='{ih:.1f}' preserveAspectRatio='xMidYMid meet' "
                  "style='mix-blend-mode:multiply'/>")
    if texto:
        ty = (cy + ih / 2 + fs * 0.5) if src else (cy + fs / 3)
        miolo += (f"<text x='{cx:.1f}' y='{ty:.1f}' text-anchor='middle' font-size='{fs:.1f}' font-weight='700' "
                  f"fill='{html.escape(cor or '#000', quote=True)}' "
                  f"style=\"font-family:{CSS_FONTES.get(fonte, 'Arial')}\">{html.escape(texto)}</text>")
    if not miolo:
        miolo = (f"<rect x='{ax + 4}' y='{ay + 4}' width='{aw - 8}' height='{ah - 8}' rx='8' fill='none' "
                 "stroke='#94a3b8' stroke-width='2' stroke-dasharray='8 6'/>"
                 f"<text x='{ax + aw / 2}' y='{ay + ah / 2}' text-anchor='middle' font-size='15' fill='#64748b' "
                 "font-family='Arial'>Sua arte aqui</text>"
                 f"<text x='{ax + aw / 2}' y='{ay + ah / 2 + 20}' text-anchor='middle' font-size='11' fill='#94a3b8' "
                 "font-family='Arial'>escolha ou envie uma imagem</text>")
    defs = (_CIL + "<linearGradient id='tecido' x1='0' x2='0' y1='0' y2='1'><stop offset='0' stop-color='#000' "
            "stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.10'/></linearGradient>"
            "<radialGradient id='fofo' cx='.5' cy='.45' r='.65'><stop offset='.55' stop-color='#000' stop-opacity='0'/>"
            "<stop offset='1' stop-color='#000' stop-opacity='.22'/></radialGradient>"
            "<radialGradient id='luz' cx='.5' cy='.35' r='.75'><stop offset='0' stop-color='#ffffff'/>"
            "<stop offset='1' stop-color='#dbe4f3'/></radialGradient>"
            f"<clipPath id='area'>{recorte}</clipPath>")
    return f"""<html><body style="margin:0;font-family:Arial,sans-serif;background:transparent">
<div style="border-radius:12px;overflow:hidden;border:1px solid #dbe1ea;background:#fff">
<svg viewBox="0 0 400 400" style="display:block;width:100%;height:{altura - 30}px">
<defs>{defs}</defs><rect width="400" height="400" fill="url(#luz)"/>
{fundo}<g clip-path="url(#area)">{miolo}</g>{sombra}</svg>
<div style="padding:5px 10px;font-size:12px;color:#475569;border-top:1px solid #eef2f7">
👀 Prévia de como fica{(' · ' + html.escape(nome)) if nome else ''} · as cores reais podem variar um pouco</div>
</div></body></html>"""


def mockup_perso(item: dict) -> str:
    """Prévia da peça com a arte escolhida ou a foto enviada pelo cliente."""
    k = item["id"]
    src, _ = arte_escolhida(k)
    return html_mockup(tipo_peca(item["categoria"] + " " + item["nome"]), src,
                       st.session_state.get(f"ptxt_{k}", ""), st.session_state.get(f"pfonte_{k}", "Padrão"),
                       st.session_state.get(f"pcor_{k}", "#000000"), st.session_state.get(f"pesc_{k}", 100),
                       st.session_state.get(f"pdx_{k}", 0), st.session_state.get(f"pdy_{k}", 0), item["nome"])
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
import altair as alt


# ===============================================================
# DECLARAÇÃO DE CONTEÚDO (para enviar sem nota fiscal)
# ===============================================================
def html_declaracao(p) -> str:
    """Monta a declaração de conteúdo pronta para imprimir (Ctrl+P)."""
    itens = [i.strip("- ").strip() for i in str(p["itens"]).split(" | Frete")[0].split(";") if i.strip()]
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
                  ARQ_LOJA, ARQ_APRESENTACOES, ARQ_VITRINE, ARQ_ARTES_PRONTAS,
                  ARQ_FORNECEDORES, ARQ_ESTOQUE, ARQ_COMPRAS, ARQ_MOVIMENTOS, ARQ_PRECOS,
                  ARQ_EQUIPE, ARQ_HIST]


def gerar_backup_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for arq in ARQUIVOS_DADOS:
            if os.path.exists(arq):
                z.write(arq, arcname=arq)
        if os.path.isdir(PASTA_VIDEOS):
            for nome in os.listdir(PASTA_VIDEOS):
                z.write(os.path.join(PASTA_VIDEOS, nome), arcname=f"{PASTA_VIDEOS}/{nome}")
        if os.path.isdir(PASTA_ARTES):
            for nome in os.listdir(PASTA_ARTES):
                z.write(os.path.join(PASTA_ARTES, nome), arcname=f"{PASTA_ARTES}/{nome}")
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
            if nome.startswith(("/", "\\")) or ".." in nome.replace("\\", "/").split("/"):
                continue  # segurança: não deixa o zip gravar fora da pasta da loja
            if nome in ARQUIVOS_DADOS or (nome.split("/")[0] in (PASTA_VIDEOS, PASTA_ARTES) and not nome.endswith("/")):
                os.makedirs(os.path.dirname(nome) or ".", exist_ok=True)
                with open(nome, "wb") as f:
                    f.write(z.read(nome))
                restaurados += 1
    return restaurados


# ===============================================================
# MINI FÁBRICA AO VIVO (prédio com a equipe trabalhando com os dados reais)
# ===============================================================
NAV_CIDADE = {"resumo": "📊 Resumo", "pedidos": "🧾 Pedidos", "clientes": "👥 Clientes", "artes": "🖨️ Artes",
              "estoque": "🏭 Estoque e compras", "etiquetas": "🏷️ Etiquetas", "rastreio": "🚚 Rastreio",
              "ao_vivo": "🏙️ Empresa ao vivo"}
VERSAO_MOTOR = "mc4"


def mudar_status(id_pedido: str, novo_status: str):
    """Muda a situação do pedido e faz o resto sozinho (histórico e baixa do estoque)."""
    ped = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
    alvo = ped["id_pedido"] == id_pedido
    if not alvo.any():
        return
    antigo = ped.loc[alvo, "status"].iloc[0]
    ped.loc[alvo, "status"] = novo_status
    gravar_csv(ARQ_PEDIDOS, ped)
    depois_de_mudar_status(id_pedido, antigo, novo_status)


def decidir_pedido(id_pedido: str, novo_status: str):
    """O diretor autoriza (vai para a produção) ou recusa o pedido."""
    mudar_status(id_pedido, novo_status)


def carregar_equipe() -> list:
    return ler_json(ARQ_EQUIPE, EQUIPE_PADRAO)


def _dono(id_pedido, n: int) -> int:
    """Divide os pedidos entre as pessoas do setor, sempre do mesmo jeito."""
    if n <= 0:
        return 0
    return int("".join(c for c in str(id_pedido) if c.isdigit()) or 0) % n


def _espera(dt, agora) -> str:
    if pd.isna(dt):
        return "?"
    horas = int((agora - dt).total_seconds() // 3600)
    return f"{horas // 24} dia(s)" if horas >= 24 else (f"{horas}h" if horas >= 1 else "menos de 1h")


def _atrasado(p, agora) -> bool:
    if p["status"] in ("Entregue", "Cancelado"):
        return False
    try:
        return datetime.strptime(str(p["previsao_entrega"]).strip(), "%d/%m/%Y").date() < agora.date()
    except Exception:
        return bool(pd.notna(p["dt"]) and (agora - p["dt"]).days > 7)


def _resumo(p, n: int = 3) -> str:
    itens = itens_do_pedido(p)
    if not itens:
        return str(p["itens"]).split(" | Frete")[0][:80]
    txt = ", ".join(f"{i['quantidade']}x {i['nome']}" for i in itens[:n])
    return txt + (f" +{len(itens) - n}" if len(itens) > n else "")


def _cor_ok(c: str, padrao: str) -> str:
    import re
    return c if re.fullmatch(r"#[0-9a-fA-F]{3,8}", str(c or "")) else padrao


def dados_cidade(publico: bool) -> dict:
    """Junta tudo o que a mini fábrica mostra. Na loja (publico=True) não vai nome, endereço nem valores."""
    agora = datetime.now()
    ped = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
    ped["total_num"] = pd.to_numeric(ped["total"], errors="coerce").fillna(0.0)
    ped["dt"] = pd.to_datetime(ped["data"], format="%d/%m/%Y %H:%M", errors="coerce")
    validos = ped[ped["status"] != "Cancelado"]
    de_hoje = validos[validos["dt"].dt.date == agora.date()]
    hist = ler_csv(ARQ_HIST, COL_HIST)
    hist["dt"] = pd.to_datetime(hist["data"], format="%d/%m/%Y %H:%M", errors="coerce")
    sem = hist[hist["dt"] >= agora - timedelta(days=7)]

    def conta(status, n=0, i=None):
        h = sem[sem["status"] == status]
        if i is None or h.empty:
            return int(len(h))
        return int(sum(_dono(x, n) == i for x in h["id_pedido"]))

    def cidade(p):
        return f"{p['ent_cidade']}/{p['ent_uf']}" if str(p["ent_cidade"]).strip() else "cidade a confirmar"

    def quem(p):
        return "Cliente" if publico else (str(p["nome"]).strip() or "Cliente")

    equipe = [m for m in carregar_equipe() if m.get("ativo", True)]
    por_setor = {s: [m for m in equipe if m.get("setor") == s] for s in SETORES}
    n_prod = len(por_setor["Produção"])

    novos_df = ped[ped["status"] == "Novo"].sort_values("dt")
    novos = [{"id": p["id_pedido"], "nome": quem(p), "total": "" if publico else brl(float(p["total_num"])),
              "itens": _resumo(p), "espera": _espera(p["dt"], agora), "cidade": cidade(p),
              "velho": bool(pd.notna(p["dt"]) and (agora - p["dt"]).total_seconds() > 86400)}
             for _, p in novos_df.head(8).iterrows()]
    prod_df = ped[ped["status"].isin(["Pago", "Em produção"])].sort_values("dt")
    producao = []
    for _, p in prod_df.head(12).iterrows():
        itens = itens_do_pedido(p)
        producao.append({"id": p["id_pedido"], "nome": quem(p), "itens": _resumo(p),
                         "cats": [f"{i.get('categoria', '')} {i.get('nome', '')}" for i in itens[:3]] or [str(p["itens"])],
                         "atrasado": _atrasado(p, agora), "quem": _dono(p["id_pedido"], n_prod),
                         "espera": _espera(p["dt"], agora)})
    env_df = ped[ped["status"] == "Enviado"].sort_values("dt")
    entregas = []
    for _, p in env_df.head(6).iterrows():
        end = ", ".join(str(x) for x in [p["ent_rua"], p["ent_numero"], p["ent_complemento"], p["ent_bairro"]]
                        if str(x).strip())
        entregas.append({"id": p["id_pedido"], "nome": quem(p), "itens": _resumo(p), "cidade": cidade(p),
                         "endereco": "" if publico else (end or p["endereco_entrega"] or "endereço não informado"),
                         "cep": "" if publico else p["ent_cep"], "transportadora": p["transportadora"] or "a definir",
                         "codigo": "" if publico else p["codigo_rastreio"], "atrasado": _atrasado(p, agora),
                         "previsao": p["previsao_entrega"]})
    sem_codigo = int(((ped["status"] == "Enviado") & (ped["codigo_rastreio"].astype(str).str.strip() == "")).sum())
    atrasados = int(sum(_atrasado(p, agora) for _, p in validos.iterrows()))

    an = analise_estoque(int(LOJA.get("estoque_margem_dias", 7)))
    n_repor = int((an["repor"] == True).sum()) if len(an) else 0  # noqa: E712
    estoque = []
    for _, r in an.head(8).iterrows():
        q, mn = float(r["quantidade"]), float(r["minimo"])
        d = r["dias_restantes"]
        estoque.append({"material": str(r["material"]), "qtd": f"{q:g}", "unidade": str(r["unidade"] or "un"),
                        "minimo": f"{mn:g}", "repor": bool(r["repor"]) and not publico, "zerado": q <= 0,
                        "dias": f"{d:.0f}" if pd.notna(d) else "", "comprar": f"{float(r['comprar']):g}",
                        "nivel": round(0.0 if q <= 0 else (min(1.0, q / (mn * 3)) if mn > 0 else 1.0), 2),
                        "fornecedor": "" if publico else str(r["fornecedor"])})
    repor = [m for m in estoque if m["repor"]]

    pendentes = int(len(validos[(validos["pagamento"] == "Pendente") & (validos["dt"] < agora - timedelta(days=2))]))
    cli = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
    retornos = int(((cli["proximo_contato"] != "") & (cli["proximo_contato"] <= agora.strftime("%Y-%m-%d"))).sum())
    mov = ler_csv(ARQ_MOVIMENTOS, COL_MOV)
    movs_7d = int((pd.to_datetime(mov["data"], format="%Y-%m-%d %H:%M", errors="coerce")
                   >= agora - timedelta(days=7)).sum())

    pessoas = []
    for setor in SETORES:
        membros = por_setor[setor]
        n = len(membros)
        for i, m in enumerate(membros):
            estado, acao, fazendo, humor, motivo, rend, ids = "trabalhando", "", "", "feliz", "", "", []
            if setor == "Diretoria":
                acao = "lendo" if novos else ""
                fazendo = (f"Analisando {len(novos_df)} pedido(s) para autorizar" if novos
                           else "Acompanhando os números no painel da parede")
                if atrasados:
                    humor, motivo = "bravo", f"{atrasados} pedido(s) atrasado(s) na empresa"
                elif any(p["velho"] for p in novos):
                    humor, motivo = "estressado", "Tem pedido esperando autorização há mais de 1 dia"
                elif novos:
                    humor, motivo = "feliz", "Pedidos novos chegando!"
                else:
                    humor, motivo = ("feliz", "Dia com vendas") if len(de_hoje) else ("tranquilo", "Tudo em ordem")
                rend = f"{conta('Em produção')} pedido(s) autorizados em 7 dias"
                ids = [p["id"] for p in novos]
            elif setor == "Atendimento":
                meus = [p for p in novos if _dono(p["id"], n) == i]
                tarefas = ([f"falando com {len(meus)} cliente(s) novo(s)"] if meus else []) + \
                          ([f"cobrando {pendentes} pagamento(s) parado(s)"] if pendentes else []) + \
                          ([f"{retornos} retorno(s) para hoje"] if retornos else [])
                if tarefas or novos:
                    acao = "digitando"
                    fazendo = "No WhatsApp: " + ("; ".join(tarefas) or "acompanhando os pedidos novos")
                    if pendentes >= 3:
                        humor, motivo = "bravo", f"Cliente não responde: {pendentes} pagamento(s) parado(s) há mais de 2 dias"
                    elif pendentes:
                        humor, motivo = "estressado", "Esperando cliente responder sobre o pagamento"
                    else:
                        humor, motivo = "feliz", "Conversando com clientes"
                else:
                    estado, fazendo, humor, motivo = "pausa", "Sem mensagens agora, tomando um café", "tranquilo", "Mensagens em dia"
                criados = validos[validos["dt"] >= agora - timedelta(days=7)]
                rend = f"{sum(_dono(x, n) == i for x in criados['id_pedido'])} pedido(s) atendidos em 7 dias"
                ids = [p["id"] for p in meus]
            elif setor == "Produção":
                meus = [p for p in producao if p["quem"] == i]
                if meus:
                    acao, p0 = "trabalho", meus[0]
                    fazendo = f"Produzindo {p0['id']}: {p0['itens']}" + (f" (+{len(meus) - 1} na fila)" if len(meus) > 1 else "")
                    atr = sum(p["atrasado"] for p in meus)
                    if atr >= 2:
                        humor, motivo = "bravo", f"{atr} pedidos atrasados na bancada"
                    elif atr:
                        humor, motivo = "estressado", "Tem pedido atrasado"
                    elif len(meus) >= 4:
                        humor, motivo = "estressado", f"{len(meus)} pedidos na fila"
                    else:
                        humor, motivo = "feliz", "Produzindo no ritmo certo"
                else:
                    estado, fazendo, humor, motivo = ("pausa", "Sem pedido na produção, foi tomar um café", "tranquilo",
                                                      "Esperando o diretor autorizar pedidos")
                rend = f"{conta('Enviado', n, i)} pedido(s) finalizados em 7 dias"
                ids = [p["id"] for p in meus]
            elif setor == "Estoque":
                zerados = [x["material"] for x in estoque if x["zerado"]]
                if repor:
                    acao = "carregando"
                    fazendo = "Conferindo o que falta: " + ", ".join(x["material"] for x in repor[:3])
                    humor, motivo = (("bravo", "Acabou: " + ", ".join(zerados[:3])) if zerados
                                     else ("estressado", f"{n_repor} material(is) para repor"))
                elif producao:
                    acao, fazendo, humor, motivo = ("carregando", f"Separando material para {len(prod_df)} pedido(s)",
                                                    "feliz", "Estoque em dia")
                elif not estoque:
                    estado, fazendo, humor, motivo = "pausa", "Esperando o cadastro dos materiais", "tranquilo", "Nenhum material cadastrado"
                else:
                    estado, fazendo, humor, motivo = "pausa", "Estoque em dia, pausa para o café", "tranquilo", "Nada para repor"
                rend = f"{movs_7d} movimentação(ões) no estoque em 7 dias"
            elif setor == "Expedição":
                if producao or sem_codigo:
                    acao = "trabalho"
                    fazendo = "Embalando pedidos" + (f"; {sem_codigo} enviado(s) sem código de rastreio" if sem_codigo else "")
                    humor, motivo = (("estressado", "Tem pedido enviado sem código de rastreio") if sem_codigo
                                     else ("feliz", "Caixas saindo"))
                else:
                    estado, fazendo, humor, motivo = "pausa", "Nada para embalar agora", "tranquilo", "Esperando a produção"
                rend = f"{conta('Enviado')} pacote(s) despachados em 7 dias"
            else:
                if entregas:
                    estado, e0 = "dirigindo", entregas[0]
                    fazendo = f"Na van, levando {e0['id']} para {e0['cidade']}" + (
                        f" (+{len(env_df) - 1} entrega(s))" if len(env_df) > 1 else "")
                    atr = sum(e["atrasado"] for e in entregas)
                    humor, motivo = (("estressado", f"{atr} entrega(s) atrasada(s)") if atr else
                                     ("estressado", "Muitas entregas hoje") if len(env_df) > 4 else ("feliz", "Pé na estrada"))
                    ids = [e["id"] for e in entregas]
                else:
                    estado, fazendo, humor, motivo = "pausa", "Van na garagem, esperando entregas", "tranquilo", "Nenhum pedido a caminho"
                rend = f"{conta('Entregue')} entrega(s) concluídas em 7 dias"
            if publico:  # o cliente vê a equipe sempre de bem e sem dados internos
                humor, motivo, rend = ("feliz" if estado != "pausa" else "tranquilo"), "", ""
                fazendo = {"Diretoria": "Conferindo os pedidos", "Atendimento": "Respondendo clientes",
                           "Estoque": "Organizando o estoque"}.get(setor, fazendo) if estado != "pausa" else "Pausa para o café ☕"
            pessoas.append({"nome": str(m.get("nome") or setor), "cargo": str(m.get("cargo") or setor), "setor": setor,
                            "pele": TONS_PELE.get(m.get("pele"), "#E0AC88"),
                            "cabelo": CORES_CABELO.get(m.get("cabelo"), "#1a1a1a"),
                            "estilo": m.get("estilo") if m.get("estilo") in ESTILOS_CABELO else "Curto",
                            "camisa": _cor_ok(m.get("camisa"), "#2563eb"), "estado": estado, "acao": acao,
                            "fazendo": fazendo, "humor": humor, "motivo": motivo, "rendimento": rend, "ids": ids})

    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    semana = []
    for k in range(6, -1, -1):
        d = (agora - timedelta(days=k)).date()
        semana.append({"dia": dias[d.weekday()], "qtd": int((validos["dt"].dt.date == d).sum())})
    eventos = [f"{h['dt'].strftime('%d/%m %H:%M')} · {h['id_pedido']} → {h['status']}"
               for _, h in hist.dropna(subset=["dt"]).sort_values("dt").tail(8).iloc[::-1].iterrows()]
    return {"publico": publico, "empresa": LOJA["nome_empresa"], "cor": _cor_ok(COR, "#1d4ed8"),
            "numeros": {"hoje": int(len(de_hoje)), "fat": "" if publico else brl(float(de_hoje["total_num"].sum())),
                        "producao": int(len(prod_df)), "caminho": int(len(env_df)), "entregues": conta("Entregue"),
                        "novos": int(len(novos_df)), "repor": 0 if publico else n_repor,
                        "atrasados": 0 if publico else atrasados, "pendentes": 0 if publico else pendentes,
                        "retornos": 0 if publico else retornos, "sem_codigo": 0 if publico else sem_codigo},
            "semana": semana, "novos": novos, "producao": producao, "entregas": entregas, "estoque": estoque,
            "equipe": pessoas, "eventos": eventos}


def botoes_ocultos_cidade(d: dict):
    """Botões invisíveis: a mini fábrica aperta eles quando você clica em Autorizar, Enviar, Entregue..."""
    acao = None
    with st.container(key="mc_ocultos"):
        for p in d["novos"]:
            if st.button("Autorizar", key=f"mc_apr_{p['id']}"):
                acao = (p["id"], "Em produção")
            if st.button("Recusar", key=f"mc_rec_{p['id']}"):
                acao = (p["id"], "Cancelado")
        for p in d["producao"]:
            if st.button("Enviar", key=f"mc_env_{p['id']}"):
                acao = (p["id"], "Enviado")
        for p in d["entregas"]:
            if st.button("Entregue", key=f"mc_ent_{p['id']}"):
                acao = (p["id"], "Entregue")
        for chave, secao in NAV_CIDADE.items():
            if st.button(secao, key=f"mc_nav_{chave}"):
                acao = ("nav", secao)
    if acao:
        if acao[0] == "nav":
            st.session_state.secao_admin = acao[1]
        else:
            mudar_status(*acao)
        st.rerun(scope="app")


def _js(v) -> str:
    return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")


def _injetor_cidade(d) -> str:
    """Coloca (ou esconde) a janela flutuante da fábrica na página."""
    chamada = ("P.__mcEsconder&&P.__mcEsconder();" if d is None
               else f"P.__mcJanela({_js(d)},{_js(MOTOR_CIDADE)},'{VERSAO_MOTOR}');")
    return ("<script>(function(){try{var P=window.parent;"
            f"if(!P.__mcJanela||P.__mcVersao!=='{VERSAO_MOTOR}'){{var s=P.document.createElement('script');"
            "s.textContent=" + _js(CODIGO_JANELA) + ";P.document.head.appendChild(s);}"
            + chamada + "}catch(e){console.log('mini fabrica',e);}})();</script>")


@st.fragment(run_every=15)
def mini_cidade(local: str):
    """local: 'painel' (grande, na seção Empresa ao vivo), 'admin' (janela flutuante do painel)
    ou 'loja' (janela flutuante para o cliente, sem dados pessoais). Atualiza sozinha a cada 15 s."""
    d = dados_cidade(publico=(local == "loja"))
    if local != "loja":
        botoes_ocultos_cidade(d)
    if local == "painel":
        components.html(MOTOR_CIDADE.replace(
            "<!--DADOS-->", f"<script>mcAtualizar({_js(d)});try{{window.parent.__mcEsconder&&"
                            "window.parent.__mcEsconder()}}catch(e){{}}</script>"), height=640)
    else:
        with st.container(key="mc_host"):
            components.html(_injetor_cidade(d), height=0)


def esconder_cidade():
    with st.container(key="mc_host"):
        components.html(_injetor_cidade(None), height=0)


# Janela flutuante (roda na própria página): arrastar, mudar tamanho e minimizar
CODIGO_JANELA = r"""
(function(){
var W=window, D=document; W.__mcVersao='VERSAO';
var TAM=[380,560,820], cfg={};
try{cfg=JSON.parse(W.localStorage.getItem('mcJanela')||'{}')||{};}catch(e){cfg={};}
function salvar(){try{W.localStorage.setItem('mcJanela',JSON.stringify(cfg));}catch(e){}}
function el(){return D.getElementById('mc-janela');}
function aplicar(){
  var w=el(); if(!w) return;
  var corpo=w.querySelector('#mc-corpo'), fr=w.querySelector('#mc-frame'), t=(cfg.t===undefined?1:cfg.t);
  var larg=Math.max(260,Math.min(TAM[t],W.innerWidth-16));
  w.style.width=(cfg.min?240:larg)+'px'; corpo.style.display=cfg.min?'none':'block';
  fr.style.height=Math.round(larg*0.64)+'px';
  var ww=w.offsetWidth, hh=w.offsetHeight;
  var x=(typeof cfg.x==='number')?cfg.x:W.innerWidth-ww-16, y=(typeof cfg.y==='number')?cfg.y:W.innerHeight-hh-16;
  x=Math.max(4,Math.min(x,W.innerWidth-ww-4)); y=Math.max(4,Math.min(y,W.innerHeight-36));
  w.style.left=x+'px'; w.style.top=y+'px';
}
function criar(){
  var w=D.createElement('div'); w.id='mc-janela';
  w.style.cssText='position:fixed;z-index:1000001;background:#fff;border-radius:14px;box-shadow:0 14px 36px rgba(15,23,42,.35);overflow:hidden;border:1px solid #cbd5e1;font-family:Segoe UI,Arial,sans-serif;';
  var bt='background:rgba(255,255,255,.22);border:0;color:#fff;border-radius:7px;cursor:pointer;font-size:13px;width:26px;height:22px;line-height:20px;padding:0;';
  w.innerHTML='<div id="mc-cab" style="display:flex;align-items:center;gap:6px;padding:6px 8px;background:linear-gradient(90deg,#7c3aed,#06b6d4);color:#fff;cursor:move;user-select:none;touch-action:none;">'
   +'<span style="flex:1;font-weight:700;font-size:13px;white-space:nowrap;overflow:hidden;color:#fff;">🏭 Fábrica ao vivo <small style="opacity:.85;font-weight:400;color:#fff;">· arraste para mover</small></span>'
   +'<button data-a="tam" title="Mudar o tamanho" style="'+bt+'">⤢</button><button data-a="min" title="Minimizar / abrir" style="'+bt+'">–</button></div>'
   +'<div id="mc-corpo"><iframe id="mc-frame" title="Fábrica ao vivo" style="width:100%;border:0;display:block;background:#dbeafe;"></iframe></div>';
  D.body.appendChild(w);
  var cab=w.querySelector('#mc-cab'), fr=w.querySelector('#mc-frame'), arr=null;
  cab.addEventListener('click',function(e){var b=e.target.closest('button'); if(!b) return; var a=b.getAttribute('data-a');
    if(a==='tam'){cfg.t=((cfg.t===undefined?1:cfg.t)+1)%3; cfg.min=false;} if(a==='min'){cfg.min=!cfg.min;} salvar(); aplicar();});
  cab.addEventListener('pointerdown',function(e){ if(e.target.closest('button')) return;
    arr={dx:e.clientX-w.offsetLeft, dy:e.clientY-w.offsetTop}; try{cab.setPointerCapture(e.pointerId);}catch(_){}
    fr.style.pointerEvents='none'; e.preventDefault();});
  cab.addEventListener('pointermove',function(e){ if(!arr) return; cfg.x=e.clientX-arr.dx; cfg.y=e.clientY-arr.dy; aplicar();});
  function soltar(){ if(!arr) return; arr=null; fr.style.pointerEvents=''; salvar(); }
  cab.addEventListener('pointerup',soltar); cab.addEventListener('pointercancel',soltar);
  return w;
}
W.addEventListener('resize',aplicar);
W.__mcJanela=function(dados,motor,versao){
  var w=el()||criar(); w.style.display=''; var fr=w.querySelector('#mc-frame'); W.__mcDados=dados;
  if(fr.getAttribute('data-v')!==versao){
    fr.setAttribute('data-v',versao);
    fr.onload=function(){try{fr.contentWindow.mcAtualizar(W.__mcDados);}catch(e){}};
    fr.srcdoc=motor;
  } else { try{fr.contentWindow.mcAtualizar(dados);}catch(e){} }
  aplicar();
};
W.__mcEsconder=function(){var w=el(); if(w) w.style.display='none';};
})();
""".replace("VERSAO", VERSAO_MOTOR)

# Desenho animado da fábrica (prédio, salas, bonequinhos, esteira, van e casas dos clientes)
MOTOR_CIDADE = r"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
html,body{margin:0;padding:0;background:#dbeafe;font-family:'Segoe UI',Arial,sans-serif;overflow:hidden}
#mc{position:relative;width:100vw;height:100vh}
#cena{display:block;width:100vw;height:100vh;user-select:none}
.clic{cursor:pointer}
.clic:hover{filter:brightness(1.06) drop-shadow(0 0 3px rgba(124,58,237,.75))}
@keyframes mc-esteira{from{transform:translateX(0)}to{transform:translateX(450px)}}
.mc-item{animation:mc-esteira 10s linear infinite}
@keyframes mc-rolo{to{stroke-dashoffset:-16}}
.mc-rolo{stroke-dasharray:4 4;animation:mc-rolo .5s linear infinite}
.mc-parado .mc-rolo{animation:none}
@keyframes mc-prensa{0%,100%{transform:translateY(0)}50%{transform:translateY(12px)}}
.mc-prensa{animation:mc-prensa 1.8s ease-in-out infinite}
@keyframes mc-papel{0%{transform:translateY(-10px);opacity:0}25%{opacity:1}100%{transform:translateY(6px);opacity:0}}
.mc-papel{animation:mc-papel 2.2s linear infinite}
@keyframes mc-vapor{0%{transform:translateY(0);opacity:.8}100%{transform:translateY(-14px);opacity:0}}
.mc-vapor{animation:mc-vapor 2.2s ease-out infinite}
@keyframes mc-bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-1.2px)}}
.mc-respira{animation:mc-bob 2.8s ease-in-out infinite}
@keyframes mc-braco{0%,100%{transform:rotate(0)}50%{transform:rotate(-32deg)}}
.mc-trab .mc-bd{transform-box:fill-box;transform-origin:50% 8%;animation:mc-braco 1s ease-in-out infinite}
.mc-trab .mc-be{transform-box:fill-box;transform-origin:50% 8%;animation:mc-braco 1s ease-in-out infinite .5s}
@keyframes mc-digita{0%,100%{transform:rotate(0)}50%{transform:rotate(-14deg)}}
.mc-digitando .mc-bd,.mc-digitando .mc-be{transform-box:fill-box;transform-origin:50% 8%;animation:mc-digita .32s ease-in-out infinite}
.mc-digitando .mc-be{animation-delay:.16s}
@keyframes mc-gole{0%,70%,100%{transform:rotate(0)}80%,90%{transform:rotate(-70deg)}}
.mc-cafe .mc-bd{transform-box:fill-box;transform-origin:50% 8%;animation:mc-gole 5s ease-in-out infinite}
@keyframes mc-pisca{0%,100%{opacity:1}50%{opacity:.2}}
.mc-alerta{animation:mc-pisca 1s ease-in-out infinite}
@keyframes mc-pula{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.mc-pino{animation:mc-pula 1s ease-in-out infinite}
@keyframes mc-nuvem{from{transform:translateX(-160px)}to{transform:translateX(1160px)}}
.mc-nuvem{animation:mc-nuvem 70s linear infinite}
.pessoa{transition:transform 2.6s ease-in-out, opacity .8s}
#pop{position:absolute;display:none;left:50%;top:50%;transform:translate(-50%,-50%);width:min(94%,400px);max-height:90%;overflow:auto;background:#fff;border-radius:14px;box-shadow:0 14px 36px rgba(0,0,0,.35);border:1px solid #e5e7eb;font-size:13px;color:#1f2937;z-index:5}
#pop .cab{display:flex;align-items:center;gap:8px;padding:9px 12px;background:linear-gradient(90deg,#7c3aed,#06b6d4);color:#fff;position:sticky;top:0}
#pop .cab b{flex:1;font-size:14px}
#pop .x{background:rgba(255,255,255,.25);border:0;color:#fff;border-radius:8px;cursor:pointer;padding:2px 9px;font-size:14px}
#pop .corpo{padding:8px 12px 12px}
#pop .lin{display:flex;justify-content:space-between;gap:10px;padding:5px 0;border-bottom:1px dashed #e5e7eb}
#pop .lin b{text-align:right}
#pop h4{margin:10px 0 2px;font-size:13px;color:#5b21b6}
#pop .ped{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:7px 9px;margin:6px 0;line-height:1.35}
#pop .acoes{display:flex;gap:6px;margin-top:6px;flex-wrap:wrap}
#pop button.ac{border:1.5px solid #8b5cf6;background:#fff;color:#5b21b6;border-radius:8px;padding:4px 10px;font-weight:700;cursor:pointer;font-size:12px}
#pop button.ac.pri{background:linear-gradient(90deg,#7c3aed,#06b6d4);color:#fff;border:0}
#pop .humor{display:inline-block;padding:1px 8px;border-radius:999px;font-weight:700;font-size:12px}
#pop .motivo{font-size:12px;color:#6b7280;margin:5px 0}
#pop .vazio{color:#6b7280;font-size:12px}
#pop .ev{font-size:12px;padding:4px 6px;border-radius:8px;margin:3px 0;background:#f8fafc}
#pop .ev.clicavel{cursor:pointer}
#pop .ev.clicavel:hover{background:#ede9fe}
#aviso{position:absolute;left:50%;bottom:10px;transform:translateX(-50%);background:#111827;color:#fff;padding:6px 14px;border-radius:999px;font-size:12px;display:none;z-index:6;white-space:nowrap}
</style></head><body>
<div id="mc"><svg id="cena" viewBox="0 0 1000 640" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg"></svg>
<div id="pop"></div><div id="aviso"></div></div>
<script>
var D=null, posAnt={}, popAberto=null;
var vanRota=null, vanAssin='', vanPos={x:622,y:527}, vanSeg=0, vanEspera=0, vanUlt=0, vanCiclo=false, vanEsq=false;
var svg=document.getElementById('cena'), pop=document.getElementById('pop'), avisoEl=document.getElementById('aviso');
var GARAGEM={x:622,y:527};
var HUMOR={feliz:['😊','Feliz','#dcfce7','#166534'],tranquilo:['😌','Tranquilo','#e0f2fe','#075985'],
  estressado:['😰','Estressado','#fef3c7','#92400e'],bravo:['😠','Bravo','#fee2e2','#991b1b']};
var POSTOS={'Diretoria':[[232,206],[112,206]],'Atendimento':[[425,206],[585,206],[505,206]],
  'Produção':[[128,342],[256,342],[370,342],[440,342]],'Estoque':[[178,530],[160,530]],
  'Expedição':[[440,508],[395,508]],'Entrega':[[640,530]]};
var CAFE=[[594,372],[634,372],[674,372],[540,368],[560,368]];
var SALAS={
 'Diretoria':['🏢 Diretoria','Todo pedido novo passa por aqui. O diretor autoriza e o pedido vai para a produção.','pedidos','Diretoria'],
 'Atendimento':['💬 Atendimento','A equipe conversa com os clientes pelo WhatsApp, cobra pagamentos e faz os retornos.','clientes','Atendimento'],
 'Produção':['🔥 Produção','Impressora de sublimação, prensa térmica e prensa de canecas. A esteira leva os pedidos autorizados.','artes','Produção'],
 'Cafeteria':['☕ Cafeteria','Quem está sem serviço vem tomar um café. Quando chega pedido, volta para o posto.','',''],
 'Estoque':['📦 Estoque','Cada pedido autorizado tira o material das prateleiras.','estoque','Estoque'],
 'Expedição':['🏷️ Expedição','Embalagem e etiquetas dos pedidos prontos para sair.','etiquetas','Expedição'],
 'Garagem':['🚚 Garagem','A van sai daqui com os pedidos enviados e vai até a casa do cliente.','rastreio','Entrega']};

function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function cor(c,p){return /^#[0-9a-fA-F]{3,8}$/.test(c||'')?c:p;}
function corta(s,n){s=String(s||'');return s.length>n?s.slice(0,n-1)+'…':s;}
function tipo(t){t=String(t||'').toLowerCase();
  var r=[['canec','caneca'],['copo','copo'],['térm','copo'],['termic','copo'],['garraf','copo'],['camis','camiseta'],
         ['bon','bone'],['chav','chaveiro'],['almof','almofada'],['mate','mateira']];
  for(var i=0;i<r.length;i++){if(t.indexOf(r[i][0])>=0)return r[i][1];} return 'caixa';}
function produto(tp,c){
  switch(tp){
  case 'caneca':return '<rect x="-5" y="-12" width="10" height="12" rx="1.6" fill="#fff" stroke="#0f766e" stroke-width=".8"/><path d="M5 -9 q4.5 0 4.5 3.5 q0 3.5 -4.5 3.5" fill="none" stroke="#0f766e" stroke-width="1.3"/><rect x="-3.6" y="-9" width="7.2" height="4.6" fill="'+c+'"/>';
  case 'camiseta':return '<path d="M-7 -11 l4 -2 q3 2 6 0 l4 2 l-2 4.5 l-2 -1 v7.5 h-6 v-7.5 l-2 1z" fill="'+c+'" stroke="#334155" stroke-width=".6"/>';
  case 'copo':return '<path d="M-4.2 -12 h8.4 l-1.2 12 h-6z" fill="#cbd5e1" stroke="#475569" stroke-width=".7"/><rect x="-4.8" y="-14.4" width="9.6" height="2.6" rx="1" fill="#334155"/><rect x="-3" y="-8" width="6" height="4" fill="'+c+'"/>';
  case 'bone':return '<path d="M-6 -2 a6 6.5 0 0 1 12 0z" fill="'+c+'"/><path d="M4 -2.4 h7 q0 2.4 -7 2.4z" fill="'+c+'" stroke="#334155" stroke-width=".4"/>';
  case 'chaveiro':return '<circle cx="0" cy="-10.5" r="2.6" fill="none" stroke="#9ca3af" stroke-width="1.1"/><rect x="-4.5" y="-8" width="9" height="8" rx="2.4" fill="'+c+'"/>';
  case 'almofada':return '<rect x="-7.5" y="-10" width="15" height="10" rx="3.4" fill="'+c+'" stroke="#6d28d9" stroke-width=".5"/>';
  case 'mateira':return '<rect x="-4.4" y="-13" width="8.8" height="13" rx="2" fill="#92400e"/><path d="M-3 -13 q3 -5 6 0" stroke="#78350f" fill="none"/>';
  default:return '<rect x="-6" y="-10" width="12" height="10" fill="#d6a15c" stroke="#8a5a24" stroke-width=".7"/><path d="M-6 -6 h12" stroke="#8a5a24" stroke-width=".5"/>';}
}
function cabeloSVG(e,c,cam){
  switch(e){
  case 'Coque':return '<path d="M-7.9 -41 a7.9 7.9 0 0 1 15.8 0 q-7.9 -4.4 -15.8 0z" fill="'+c+'"/><circle cx="0" cy="-49.4" r="3.8" fill="'+c+'"/>';
  case 'Rabo de cavalo':return '<path d="M6.4 -44 q6.5 2 4.2 12.5 q-3 -4 -5.8 -9.4z" fill="'+c+'"/><path d="M-7.9 -41 a7.9 7.9 0 0 1 15.8 0 q-7.9 -4.4 -15.8 0z" fill="'+c+'"/>';
  case 'Careca':return '<path d="M-7.5 -38.5 q-.6 -3.4 1 -4.6" stroke="'+c+'" stroke-width="1.7" fill="none"/><path d="M7.5 -38.5 q.6 -3.4 -1 -4.6" stroke="'+c+'" stroke-width="1.7" fill="none"/>';
  case 'Boné':return '<path d="M-8.1 -41.2 a8.1 8.3 0 0 1 16.2 0z" fill="'+cam+'"/><path d="M-1 -41.6 h12.6 q1 1.6 -1 2.2 h-11.6z" fill="'+cam+'"/><path d="M-8.1 -41.2 h16.2" stroke="rgba(0,0,0,.25)" stroke-width=".7"/>';
  default:return '<path d="M-7.9 -40.4 a7.9 8.2 0 0 1 15.8 0 q-3 -3.6 -7.9 -3.1 q-4.9 -.5 -7.9 3.1z" fill="'+c+'"/>';}
}
function rosto(h){
  var s='stroke="#2b1b0e" fill="none" stroke-linecap="round"';
  if(h==='feliz')return '<path d="M-4.3 -43.4 l2.7 -.6 M1.6 -44 l2.7 .6" '+s+' stroke-width=".9"/><path d="M-3.1 -37.2 Q0 -34.2 3.1 -37.2z" fill="#fff" stroke="#7a2e1d" stroke-width="1"/>';
  if(h==='tranquilo')return '<path d="M-4.3 -43.5 h2.8 M1.5 -43.5 h2.8" '+s+' stroke-width=".9"/><path d="M-2.3 -36.7 Q0 -35.3 2.3 -36.7" stroke="#7a2e1d" stroke-width="1" fill="none" stroke-linecap="round"/>';
  if(h==='estressado')return '<path d="M-4.5 -42.6 l2.8 -1.3 M1.7 -43.9 l2.8 1.3" '+s+' stroke-width="1"/><path d="M-3.2 -36.3 q.8 -1 1.6 0 q.8 1 1.6 0 q.8 -1 1.6 0 q.8 1 1.6 0" stroke="#7a2e1d" stroke-width=".9" fill="none"/><path d="M7.6 -46 q1.8 2.8 0 3.9 q-1.8 -1.1 0 -3.9z" fill="#60a5fa"/>';
  return '<path d="M-4.6 -44.4 l2.9 1.5 M1.7 -42.9 l2.9 -1.5" '+s+' stroke-width="1.3"/><path d="M-3.1 -35.3 Q0 -38.2 3.1 -35.3" stroke="#7a2e1d" stroke-width="1.1" fill="none" stroke-linecap="round"/><circle cx="-4.7" cy="-38.2" r="1.6" fill="#f87171" opacity=".55"/><circle cx="4.7" cy="-38.2" r="1.6" fill="#f87171" opacity=".55"/>';
}
function pessoaSVG(p){
  var pele=cor(p.pele,'#E0AC88'), cam=cor(p.camisa,'#2563eb'), cab=cor(p.cabelo,'#1a1a1a'), cal='#1f2937';
  if(p.setor==='Diretoria') cal='#111827';
  if(p.setor==='Produção'||p.setor==='Estoque') cal='#1e3a8a';
  var tras=p.estilo==='Longo'?'<path d="M-8.7 -41 q0 -9.6 8.7 -9.6 q8.7 0 8.7 9.6 v12.5 q-3 1.6 -5 0 v-6.4 h-7.4 v6.4 q-2 1.6 -5 0z" fill="'+cab+'"/>':'';
  var frente=cabeloSVG(p.estilo==='Longo'?'Curto':p.estilo,cab,cam);
  var mao='';
  if(p.estado==='pausa') mao='<g><rect x="7.4" y="-21.4" width="4.4" height="5" rx=".9" fill="#fff" stroke="#92400e" stroke-width=".6"/><path class="mc-vapor" d="M9.4 -23.4 q1.2 -2 0 -4" stroke="#cbd5e1" stroke-width=".8" fill="none"/></g>';
  else if(p.acao==='carregando') mao='<rect x="-7.5" y="-27.5" width="15" height="10.5" fill="#d6a15c" stroke="#8a5a24" stroke-width=".7"/><path d="M-7.5 -23 h15" stroke="#8a5a24" stroke-width=".5"/>';
  else if(p.acao==='lendo') mao='<rect x="-6.4" y="-26" width="12.8" height="8.6" fill="#fff" stroke="#94a3b8" stroke-width=".6" transform="rotate(-6)"/><path d="M-4.6 -23.5 h8 M-4.6 -21.5 h6" stroke="#94a3b8" stroke-width=".5" transform="rotate(-6)"/>';
  var fone=p.setor==='Atendimento'&&p.estado!=='pausa'?'<path d="M-8.2 -41 a8.2 8.2 0 0 1 16.4 0" stroke="#111" stroke-width="1.2" fill="none"/><rect x="-9.6" y="-42.2" width="2.8" height="4.6" rx="1" fill="#111"/><path d="M-8.2 -38 q1 4.2 5.2 4.6" stroke="#111" stroke-width=".7" fill="none"/>':'';
  var gravata=p.setor==='Diretoria'?'<path d="M0 -31 l1.6 2 l-1 8 l-.6 1 l-.6 -1 l-1 -8z" fill="#b91c1c"/>':'';
  var cls='mc-respira'+(p.acao==='trabalho'||p.acao==='carregando'?' mc-trab':'')+(p.acao==='digitando'?' mc-digitando':'')+(p.estado==='pausa'?' mc-cafe':'');
  return '<ellipse cx="0" cy="0" rx="10" ry="2.4" fill="rgba(0,0,0,.18)"/><g class="'+cls+'">'
   +'<rect x="-6" y="-17" width="5.2" height="16" rx="1.5" fill="'+cal+'"/><rect x=".8" y="-17" width="5.2" height="16" rx="1.5" fill="'+cal+'"/>'
   +'<rect x="-7.3" y="-2.4" width="7" height="3" rx="1.4" fill="#222"/><rect x=".3" y="-2.4" width="7" height="3" rx="1.4" fill="#222"/>'
   +'<g class="mc-be"><rect x="-11.7" y="-31" width="4.5" height="14" rx="2.2" fill="'+cam+'"/><circle cx="-9.45" cy="-16.4" r="2.3" fill="'+pele+'"/></g>'
   +'<path d="M-8.6 -26 q0 -6 5 -6 h7.2 q5 0 5 6 v10 h-17.2z" fill="'+cam+'"/>'
   +'<path d="M-2.4 -32 l2.4 3 l2.4 -3" fill="none" stroke="rgba(0,0,0,.28)" stroke-width=".8"/>'+gravata
   +'<rect x="-2" y="-34.6" width="4" height="3.6" fill="'+pele+'"/>'+tras
   +'<circle cx="0" cy="-40" r="7.6" fill="'+pele+'"/>'
   +'<circle cx="-7.4" cy="-39.6" r="1.6" fill="'+pele+'"/><circle cx="7.4" cy="-39.6" r="1.6" fill="'+pele+'"/>'
   +'<circle cx="-2.7" cy="-40.4" r="1.05" fill="#1f2937"/><circle cx="2.7" cy="-40.4" r="1.05" fill="#1f2937"/>'
   +'<circle cx="-2.4" cy="-40.8" r=".32" fill="#fff"/><circle cx="3" cy="-40.8" r=".32" fill="#fff"/>'
   +'<path d="M0 -39.6 q.9 1.7 -.4 2.1" stroke="rgba(0,0,0,.28)" stroke-width=".6" fill="none"/>'
   +rosto(p.humor)+frente+fone
   +'<g class="mc-bd"><rect x="7.2" y="-31" width="4.5" height="14" rx="2.2" fill="'+cam+'"/><circle cx="9.45" cy="-16.4" r="2.3" fill="'+pele+'"/>'+mao+'</g>'
   +'</g>';
}
function sala(x,y,w,h,fundo,piso,nome,rotulo){
  return '<g class="clic" data-k="sala" data-v="'+nome+'"><rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" fill="'+fundo+'"/>'
   +'<rect x="'+x+'" y="'+(y+h-12)+'" width="'+w+'" height="12" fill="url(#'+piso+')"/>'
   +'<rect x="'+(x+6)+'" y="'+(y+6)+'" width="'+(rotulo.length*6.3+16)+'" height="16" rx="8" fill="rgba(255,255,255,.88)" stroke="rgba(0,0,0,.08)"/>'
   +'<text x="'+(x+14)+'" y="'+(y+18)+'" font-size="10" font-weight="700" fill="#1f2937">'+rotulo+'</text>'
   +'<path d="M'+(x+w/2)+' '+y+' v6" stroke="#475569"/><path d="M'+(x+w/2-7)+' '+(y+10)+' q7 -6 14 0z" fill="#475569"/>'
   +'</g>';
}
function janela(x,y,w,h,noite){
  return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" fill="'+(noite?'#1e3a8a':'#bae6fd')+'" stroke="#94a3b8" stroke-width="3"/>'
   +'<path d="M'+(x+w/2)+' '+y+' v'+h+' M'+x+' '+(y+h/2)+' h'+w+'" stroke="#94a3b8" stroke-width="2"/>'
   +(noite?'<circle cx="'+(x+w*0.7)+'" cy="'+(y+h*0.3)+'" r="3" fill="#fef9c3"/>':'<path d="M'+(x+5)+' '+(y+h-6)+' l10 -10" stroke="#fff" stroke-width="2" opacity=".7"/>');
}
function planta(x,y){return '<rect x="'+(x-7)+'" y="'+(y-14)+'" width="14" height="14" rx="2" fill="#b45309"/><path d="M'+x+' '+(y-14)+' q-10 -10 -4 -24 M'+x+' '+(y-14)+' q2 -14 10 -20 M'+x+' '+(y-14)+' q-2 -10 2 -28" stroke="#15803d" stroke-width="4" fill="none" stroke-linecap="round"/>';}
function num(x,y,rot,val,c){return '<text x="'+x+'" y="'+y+'" font-size="5.6" fill="#94a3b8">'+rot+'</text><text x="'+x+'" y="'+(y+11)+'" font-size="11" font-weight="800" fill="'+c+'">'+esc(val)+'</text>';}

function cenario(noite){
  var n=D.numeros, s=[], c=cor(D.cor,'#1d4ed8');
  s.push('<defs><linearGradient id="ceuD" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7dd3fc"/><stop offset="1" stop-color="#e0f2fe"/></linearGradient>'
   +'<linearGradient id="ceuN" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1d3a"/><stop offset="1" stop-color="#1e3a8a"/></linearGradient>'
   +'<pattern id="tijolo" width="24" height="12" patternUnits="userSpaceOnUse"><rect width="24" height="12" fill="#b9c3d3"/><path d="M0 12h24M12 0v6M0 6h24M6 6v6M18 6v6" stroke="#a7b2c4" stroke-width="1"/></pattern>'
   +'<pattern id="madeira" width="18" height="12" patternUnits="userSpaceOnUse"><rect width="18" height="12" fill="#c9a77c"/><path d="M0 12h18M9 0v12" stroke="#b08d61" stroke-width=".8"/></pattern>'
   +'<pattern id="ladrilho" width="12" height="12" patternUnits="userSpaceOnUse"><rect width="12" height="12" fill="#d6d3cd"/><path d="M0 12h12M12 0v12" stroke="#bdb8ae" stroke-width=".8"/></pattern>'
   +'<pattern id="concreto" width="20" height="12" patternUnits="userSpaceOnUse"><rect width="20" height="12" fill="#a8a29e"/><circle cx="5" cy="4" r=".8" fill="#78716c"/><circle cx="15" cy="9" r=".8" fill="#78716c"/></pattern>'
   +'<clipPath id="tvclip"><rect x="120" y="72" width="198" height="70"/></clipPath></defs>');
  s.push('<rect width="1000" height="640" fill="url(#'+(noite?'ceuN':'ceuD')+')" data-k="fundo"/>');
  if(noite){ for(var i=0;i<26;i++){ s.push('<circle cx="'+((i*137)%1000)+'" cy="'+(8+(i*53)%90)+'" r="'+(i%3?0.9:1.4)+'" fill="#fff" opacity=".8"/>'); }
    s.push('<circle cx="930" cy="60" r="20" fill="#fef9c3"/><circle cx="938" cy="54" r="18" fill="#1e3a8a" opacity=".55"/>');
  } else {
    s.push('<circle cx="930" cy="62" r="24" fill="#fde047"/><circle cx="930" cy="62" r="34" fill="#fde047" opacity=".25"/>');
    [[60,0],[120,-30],[30,-55]].forEach(function(nv){ s.push('<g class="mc-nuvem" style="animation-delay:'+nv[1]+'s"><g transform="translate(0,'+nv[0]+')" fill="#fff" opacity=".9"><ellipse cx="0" cy="0" rx="34" ry="11"/><ellipse cx="18" cy="-8" rx="20" ry="12"/><ellipse cx="-16" cy="-5" rx="16" ry="9"/></g></g>'); });
  }
  s.push('<text x="990" y="18" text-anchor="end" font-size="11" font-weight="800" fill="'+(noite?'#fca5a5':'#dc2626')+'"><tspan class="mc-alerta">●</tspan> AO VIVO</text>');
  // cidade ao fundo
  [[716,430,40],[760,400,34],[798,445,46],[848,410,30],[882,436,44],[930,395,36],[970,428,30]].forEach(function(b){
    s.push('<rect x="'+b[0]+'" y="'+b[1]+'" width="'+b[2]+'" height="'+(545-b[1])+'" fill="'+(noite?'#1e293b':'#94a3b8')+'" opacity=".55"/>');
    for(var yy=b[1]+8;yy<480;yy+=14){ for(var xx=b[0]+5;xx<b[0]+b[2]-6;xx+=10){ s.push('<rect x="'+xx+'" y="'+yy+'" width="5" height="6" fill="'+(noite?((xx+yy)%3?'#fde68a':'#334155'):'#cbd5e1')+'" opacity=".8"/>'); } }
  });
  // chão e rua
  s.push('<rect x="0" y="536" width="1000" height="10" fill="#86c56b"/><rect x="0" y="543" width="1000" height="13" fill="#d1d5db"/>'
   +'<path d="M0 556 h1000" stroke="#9ca3af" stroke-width="2"/><rect x="0" y="557" width="1000" height="83" fill="#374151"/>'
   +'<path d="M0 599 h1000" stroke="#facc15" stroke-width="3" stroke-dasharray="22 16"/>'
   +'<g><rect x="706" y="508" width="3" height="36" fill="#475569"/><rect x="684" y="500" width="48" height="12" rx="2" fill="#15803d"/><text x="708" y="509" font-size="6.5" fill="#fff" text-anchor="middle" font-weight="700">Rua dos Clientes</text></g>');
  // prédio
  s.push('<rect x="14" y="54" width="694" height="490" fill="url(#tijolo)" stroke="#64748b" stroke-width="2"/>'
   +'<rect x="8" y="10" width="706" height="46" rx="7" fill="'+c+'"/><rect x="8" y="46" width="706" height="10" fill="rgba(0,0,0,.15)"/>'
   +'<text x="361" y="40" text-anchor="middle" font-size="21" font-weight="800" fill="#fff" letter-spacing="1">🏷️ '+esc(corta(D.empresa,34))+'</text>'
   +'<rect x="14" y="214" width="694" height="9" fill="#64748b"/><rect x="14" y="374" width="694" height="9" fill="#64748b"/><rect x="14" y="534" width="694" height="9" fill="#64748b"/>');
  s.push(sala(22,62,306,152,'#e8eef7','madeira','Diretoria','🏢 Diretoria'));
  s.push(sala(334,62,366,152,'#fdf2f8','madeira','Atendimento','💬 Atendimento'));
  s.push(sala(22,223,478,151,'#ecfdf5','ladrilho','Produção','🔥 Produção'));
  s.push(sala(506,223,194,151,'#fef3c7','madeira','Cafeteria','☕ Cafeteria'));
  s.push(sala(22,383,308,151,'#fff7ed','concreto','Estoque','📦 Estoque'));
  s.push(sala(336,383,204,151,'#eff6ff','ladrilho','Expedição','🏷️ Expedição'));
  s.push(sala(546,383,154,151,'#e5e7eb','concreto','Garagem','🚚 Garagem'));
  s.push('<rect x="328" y="62" width="6" height="152" fill="#64748b"/><rect x="500" y="223" width="6" height="151" fill="#64748b"/>'
   +'<rect x="330" y="383" width="6" height="151" fill="#64748b"/><rect x="540" y="383" width="6" height="151" fill="#64748b"/>');
  // ---------- Diretoria ----------
  s.push(janela(36,84,62,52,noite));
  s.push('<g><rect x="34" y="150" width="66" height="52" fill="#7c4a24"/><path d="M34 167 h66 M34 184 h66" stroke="#5b3416" stroke-width="2"/>'
   +[0,1,2,3,4,5].map(function(i){return '<rect x="'+(38+i*10)+'" y="'+(154+(i%2)*1)+'" width="7" height="12" fill="'+['#ef4444','#3b82f6','#f59e0b','#10b981','#8b5cf6','#ec4899'][i]+'"/><rect x="'+(38+i*10)+'" y="'+(171+(i%2))+'" width="7" height="12" fill="'+['#64748b','#f97316','#0ea5e9','#84cc16','#e11d48','#a855f7'][i]+'"/>';}).join('')+'</g>');
  s.push('<rect x="218" y="150" width="28" height="44" rx="6" fill="#111827"/>'+planta(314,206));
  var mx=1; D.semana.forEach(function(x){mx=Math.max(mx,x.qtd);});
  var tv='<g class="clic" data-k="tv"><rect x="116" y="68" width="206" height="78" rx="5" fill="#111827"/><rect x="120" y="72" width="198" height="70" fill="#0b1220"/><g clip-path="url(#tvclip)">'
   +'<text x="125" y="82" font-size="7" font-weight="800" fill="#67e8f9">📊 PAINEL AO VIVO</text><text id="relogio" x="314" y="82" font-size="7" text-anchor="end" fill="#e2e8f0">--:--</text>'
   +(n.fat?'<text x="125" y="91" font-size="6.2" fill="#86efac">Faturamento hoje: '+esc(n.fat)+'</text>':'')
   +num(125,100,'Pedidos hoje',n.hoje,'#ffffff')+num(176,100,'Na produção',n.producao,'#fbbf24')
   +num(125,120,'A caminho',n.caminho,'#60a5fa')+num(176,120,'Entregues 7d',n.entregues,'#4ade80')
   +'<text x="232" y="91" font-size="5.6" fill="#94a3b8">Pedidos · 7 dias</text>';
  D.semana.forEach(function(x,i){ var hh=Math.max(1,30*x.qtd/mx); tv+='<rect x="'+(234+i*11)+'" y="'+(127-hh)+'" width="8" height="'+hh+'" rx="1.5" fill="'+(i===6?'#22d3ee':'#0e7490')+'"/><text x="'+(238+i*11)+'" y="134" font-size="4.8" text-anchor="middle" fill="#94a3b8">'+esc(x.dia.slice(0,1))+'</text>'; });
  tv+='<text id="evento" x="125" y="140.5" font-size="5.4" fill="#a5b4fc"></text></g></g>';
  s.push(tv);
  // ---------- Atendimento ----------
  s.push(janela(350,84,48,46,noite)+janela(486,84,48,46,noite));
  s.push('<rect x="411" y="152" width="28" height="42" rx="6" fill="#831843"/><rect x="571" y="152" width="28" height="42" rx="6" fill="#831843"/>');
  s.push('<g class="clic" data-k="sala" data-v="Atendimento"><rect x="626" y="78" width="66" height="70" rx="6" fill="#fff" stroke="#f9a8d4" stroke-width="2"/>'
   +'<text x="659" y="91" font-size="7.4" font-weight="800" text-anchor="middle" fill="#9d174d">💬 WhatsApp</text>'
   +'<text x="632" y="105" font-size="6.6" fill="#1f2937">Novos: <tspan font-weight="800">'+n.novos+'</tspan></text>'
   +(D.publico?'<text x="632" y="118" font-size="6.6" fill="#1f2937">Sempre online 😊</text>':
     '<text x="632" y="118" font-size="6.6" fill="'+(n.pendentes?'#b91c1c':'#1f2937')+'">Sem resposta: <tspan font-weight="800">'+n.pendentes+'</tspan></text>'
     +'<text x="632" y="131" font-size="6.6" fill="#1f2937">Retornos hoje: <tspan font-weight="800">'+n.retornos+'</tspan></text>')
   +(n.novos?'<text x="682" y="144" font-size="9" class="mc-alerta">🔔</text>':'')+'</g>');
  // ---------- Produção ----------
  var ativo=D.producao.length>0;
  s.push('<g class="clic" data-k="sala" data-v="Produção">'
   +'<rect x="40" y="282" width="70" height="48" rx="6" fill="#e5e7eb" stroke="#9ca3af"/><rect x="47" y="275" width="56" height="9" rx="3" fill="#374151"/>'
   +'<rect x="88" y="291" width="15" height="9" rx="1" fill="'+(ativo?'#22d3ee':'#64748b')+'"/><circle cx="50" cy="296" r="3" fill="'+(ativo?'#22c55e':'#9ca3af')+'"/>'
   +(ativo?'<g class="mc-papel"><rect x="55" y="304" width="40" height="18" fill="#fff" stroke="#cbd5e1"/><rect x="62" y="308" width="26" height="9" fill="'+c+'" opacity=".7"/></g>':'')
   +'<text x="75" y="327" font-size="6" text-anchor="middle" fill="#334155">Impressora</text>'
   +'<rect x="158" y="316" width="78" height="14" rx="2" fill="#475569"/><rect x="222" y="262" width="10" height="56" fill="#64748b"/><rect x="162" y="256" width="72" height="9" rx="2" fill="#475569"/>'
   +'<path d="M162 260 l-14 -8" stroke="#1f2937" stroke-width="3" stroke-linecap="round"/>'
   +'<g class="'+(ativo?'mc-prensa':'')+'"><rect x="166" y="282" width="58" height="11" rx="2" fill="#334155"/><rect x="168" y="293" width="54" height="2.4" fill="'+(ativo?'#f97316':'#94a3b8')+'"/></g>'
   +'<rect x="166" y="306" width="58" height="9" rx="1" fill="#94a3b8"/><path d="M182 306 l4 -3 q9 3 18 0 l4 3z" fill="#fff"/>'
   +'<text x="197" y="340" font-size="6" text-anchor="middle" fill="#334155">Prensa térmica</text>'
   +'<rect x="284" y="286" width="62" height="44" rx="5" fill="#1f2937"/><rect x="296" y="270" width="38" height="24" rx="8" fill="'+(ativo?'#ef4444':'#64748b')+'" opacity=".9"/>'
   +'<g transform="translate(315,292)">'+produto('caneca',c)+'</g><text x="315" y="312" font-size="7" text-anchor="middle" fill="'+(ativo?'#fca5a5':'#9ca3af')+'">'+(ativo?'180°C':'desligada')+'</text>'
   +'<text x="315" y="327" font-size="6" text-anchor="middle" fill="#e5e7eb">Canecas</text></g>');
  var feitos=n.entregues+n.caminho, fila=n.producao, tot=Math.max(1,feitos+fila);
  s.push('<g class="clic" data-k="prod"><rect x="398" y="232" width="96" height="40" rx="4" fill="#111827"/>'
   +'<text x="404" y="243" font-size="6.4" font-weight="800" fill="#6ee7b7">⚙️ PRODUÇÃO</text>'
   +'<text x="404" y="254" font-size="6" fill="#e5e7eb">Na fila: '+fila+' · Prontos: '+feitos+'</text>'
   +'<rect x="404" y="259" width="84" height="6" rx="3" fill="#374151"/><rect x="404" y="259" width="'+(84*feitos/tot).toFixed(1)+'" height="6" rx="3" fill="#10b981"/></g>');
  s.push('<g><rect x="398" y="284" width="96" height="4" fill="#94a3b8"/>'+[0,1,2,3,4].map(function(i){return '<g transform="translate('+(408+i*19)+',284)">'+produto(['caneca','camiseta','copo','bone','almofada'][i],['#7c3aed','#ec4899','#0ea5e9','#f59e0b','#10b981'][i])+'</g>';}).join('')+'</g>');
  // ---------- Cafeteria ----------
  s.push('<g class="clic" data-k="sala" data-v="Cafeteria"><rect x="512" y="300" width="56" height="62" rx="3" fill="#92400e"/><rect x="510" y="296" width="60" height="6" rx="2" fill="#b45309"/>'
   +'<rect x="520" y="270" width="30" height="27" rx="3" fill="#374151"/><rect x="524" y="275" width="12" height="7" fill="#22d3ee"/><rect x="531" y="288" width="8" height="8" rx="1" fill="#fff"/>'
   +'<path class="mc-vapor" d="M535 286 q2 -4 0 -8" stroke="#e5e7eb" stroke-width="1.4" fill="none"/>'
   +'<rect x="596" y="236" width="94" height="40" rx="4" fill="#1f2937" stroke="#92400e" stroke-width="3"/>'
   +'<text x="643" y="250" font-size="8" font-weight="800" fill="#fef3c7" text-anchor="middle">CAFÉ ☕</text>'
   +'<text x="643" y="261" font-size="6" fill="#fde68a" text-anchor="middle">pão de queijo · bolo</text>'
   +'<text x="643" y="271" font-size="6" fill="#fde68a" text-anchor="middle">chimarrão 🧉</text>'
   +'<path d="M620 223 v18 M668 223 v18" stroke="#78350f"/><circle cx="620" cy="243" r="4" fill="'+(noite?'#fde047':'#fef3c7')+'"/><circle cx="668" cy="243" r="4" fill="'+(noite?'#fde047':'#fef3c7')+'"/></g>');
  // ---------- Estoque ----------
  s.push('<g>');
  [36,210].forEach(function(rx){ s.push('<rect x="'+rx+'" y="392" width="4" height="130" fill="#475569"/><rect x="'+(rx+108)+'" y="392" width="4" height="130" fill="#475569"/>'); });
  for(var k2=0;k2<8;k2++){
    var rx2=k2<4?36:210, py=416+(k2%4)*31, m=D.estoque[k2], cheio=D.estoque.length?(m?m.nivel:0):0.5;
    var caixas=Math.round(cheio*6), alerta=m&&m.repor&&!D.publico, g='<g class="clic" data-k="prat" data-v="'+k2+'">';
    g+='<rect x="'+(rx2+4)+'" y="'+(py-22)+'" width="104" height="22" fill="transparent"/>';
    for(var b=0;b<caixas;b++){ g+='<rect x="'+(rx2+7+b*16.5)+'" y="'+(py-16)+'" width="15" height="16" fill="'+(alerta?'#fca5a5':'#d6a15c')+'" stroke="'+(alerta?'#b91c1c':'#8a5a24')+'" stroke-width=".8"/><path d="M'+(rx2+7+b*16.5)+' '+(py-11)+' h15" stroke="#8a5a24" stroke-width=".5"/>'; }
    g+='<rect x="'+(rx2+2)+'" y="'+py+'" width="108" height="7" fill="#64748b"/>';
    var rot=m?corta(m.material,20)+' · '+m.qtd:(D.estoque.length?'':'cadastre materiais');
    if(rot) g+='<text x="'+(rx2+6)+'" y="'+(py+5.6)+'" font-size="5" fill="#fff">'+esc(rot)+'</text>';
    if(alerta) g+='<g class="mc-alerta"><circle cx="'+(rx2+100)+'" cy="'+(py-20)+'" r="5.5" fill="#ef4444"/><text x="'+(rx2+100)+'" y="'+(py-17.6)+'" font-size="8" font-weight="800" fill="#fff" text-anchor="middle">!</text></g>';
    s.push(g+'</g>');
  }
  s.push('</g>');
  // ---------- Expedição ----------
  var pilha=Math.min(6,n.caminho+n.producao);
  s.push('<g class="clic" data-k="sala" data-v="Expedição">');
  for(var p2=0;p2<pilha;p2++){ var px=344+(p2%2)*18, pyy=508-Math.floor(p2/2)*14; s.push('<rect x="'+px+'" y="'+pyy+'" width="17" height="14" fill="#d6a15c" stroke="#8a5a24" stroke-width=".8"/><rect x="'+(px+3)+'" y="'+(pyy+4)+'" width="9" height="5" fill="#fff"/>'); }
  if(!D.publico&&n.sem_codigo) s.push('<g><rect x="470" y="402" width="62" height="30" fill="#fef9c3" stroke="#eab308" transform="rotate(3 500 417)"/><text x="501" y="414" font-size="6" text-anchor="middle" fill="#854d0e" transform="rotate(3 500 417)">Sem rastreio:</text><text x="501" y="426" font-size="9" font-weight="800" text-anchor="middle" fill="#b91c1c" transform="rotate(3 500 417)">'+n.sem_codigo+'</text></g>');
  s.push('</g>');
  // ---------- Garagem ----------
  s.push('<g class="clic" data-k="sala" data-v="Garagem"><rect x="552" y="389" width="142" height="12" fill="#94a3b8"/><path d="M552 393 h142 M552 397 h142" stroke="#64748b"/>'
   +'<rect x="560" y="408" width="44" height="28" fill="#cbd5e1" stroke="#64748b"/><path d="M566 414 l8 14 M580 412 v18 M592 414 l-6 14" stroke="#475569" stroke-width="2"/>'
   +'<ellipse cx="640" cy="528" rx="26" ry="4" fill="#57534e" opacity=".5"/></g>');
  return s.join('');
}
function posicoes(){
  var ocup={}, cafe=0, res=[];
  D.equipe.forEach(function(p,idx){
    var x=0,y=0,vis=true;
    if(p.estado==='dirigindo'){vis=false;}
    else if(p.estado==='pausa'){var cc=CAFE[cafe%CAFE.length]; x=cc[0]+(cafe>=CAFE.length?10:0); y=cc[1]; cafe++;}
    else {var l=POSTOS[p.setor]||[[360,530]], k=ocup[p.setor]||0; ocup[p.setor]=k+1; var b=l[Math.min(k,l.length-1)]; x=b[0]+(k>=l.length?(k-l.length+1)*26:0); y=b[1];}
    res.push({p:p,idx:idx,x:x,y:y,vis:vis});
  });
  return res;
}
function pessoas(lista){
  return '<g id="pessoas">'+lista.filter(function(o){return o.vis;}).map(function(o){
    var p=o.p, H=HUMOR[p.humor]||HUMOR.feliz, ch=esc(p.nome+'|'+p.setor);
    return '<g class="pessoa clic" data-k="p" data-v="'+o.idx+'" data-id="'+ch+'" data-x="'+o.x+'" data-y="'+o.y+'" style="transform:translate('+o.x+'px,'+o.y+'px)">'
     +'<g transform="scale(1.1)">'+pessoaSVG(p)+'<g transform="translate(0,-62)"><circle r="6.8" fill="#fff" stroke="#cbd5e1"/><text y="3" font-size="8.4" text-anchor="middle">'+H[0]+'</text></g></g>'
     +'<title>'+esc(p.nome+' · '+p.fazendo)+'</title></g>';
  }).join('')+'</g>';
}
function frente(lista){
  var s=[], c=cor(D.cor,'#1d4ed8'), n=D.numeros;
  var papeis=Math.min(n.novos,8), g='<g class="clic" data-k="novos">';
  g+='<path d="M186 186 l4 -18 h30 l4 18z" fill="#475569"/><circle cx="205" cy="177" r="2.4" fill="#cbd5e1"/>';
  for(var i=0;i<papeis;i++){ g+='<rect x="'+(268-(i%2))+'" y="'+(184-i*2.2-3)+'" width="26" height="3" fill="#fff" stroke="#cbd5e1" stroke-width=".5"/>'; }
  g+='<rect x="160" y="184" width="150" height="6" rx="2" fill="#8b5a2b"/><rect x="166" y="190" width="138" height="16" fill="#6b4423"/>'
   +'<rect x="210" y="193" width="50" height="9" rx="2" fill="#fde68a"/><text x="235" y="199.6" font-size="6" font-weight="800" text-anchor="middle" fill="#78350f">DIRETORIA</text>';
  if(papeis) g+='<g class="mc-alerta"><circle cx="298" cy="168" r="7" fill="#ef4444"/><text x="298" y="171" font-size="8" font-weight="800" text-anchor="middle" fill="#fff">'+n.novos+'</text></g>';
  s.push(g+'</g>');
  [380,540].forEach(function(x0){ s.push('<g class="clic" data-k="sala" data-v="Atendimento"><rect x="'+(x0+24)+'" y="164" width="44" height="21" rx="2" fill="#334155"/><rect x="'+(x0+43)+'" y="185" width="6" height="2" fill="#334155"/>'
    +'<rect x="'+x0+'" y="184" width="92" height="6" rx="2" fill="#f9a8d4"/><rect x="'+(x0+4)+'" y="190" width="84" height="16" fill="#e2e8f0" stroke="#cbd5e1"/></g>'); });
  var prod=D.producao.slice(0,8), tot=prod.length;
  var e='<g class="'+(tot?'':'mc-parado')+'"><rect x="28" y="352" width="470" height="12" rx="6" fill="#374151"/><path class="mc-rolo" d="M36 358 H490" stroke="#9ca3af" stroke-width="3"/>'
   +'<rect x="50" y="364" width="5" height="10" fill="#4b5563"/><rect x="250" y="364" width="5" height="10" fill="#4b5563"/><rect x="470" y="364" width="5" height="10" fill="#4b5563"/>';
  prod.forEach(function(p,i){ var cores=['#7c3aed','#ec4899','#0ea5e9','#f59e0b','#10b981','#ef4444'];
    e+='<g class="mc-item clic" data-k="item" data-v="'+i+'" style="animation-delay:-'+(i*10/Math.max(1,tot)).toFixed(2)+'s"><g transform="translate(34,352)">'
     +produto(tipo(p.cats[0]),cores[i%cores.length])+(p.atrasado&&!D.publico?'<circle cx="7" cy="-15" r="3" fill="#ef4444" class="mc-alerta"/>':'')+'</g></g>'; });
  s.push(e+'</g>');
  var naPausa=lista.filter(function(o){return o.vis&&o.p.estado==='pausa';});
  s.push('<g class="clic" data-k="sala" data-v="Cafeteria"><rect x="572" y="350" width="126" height="5" rx="2" fill="#78350f"/><rect x="578" y="355" width="114" height="17" fill="#a16207"/>'
   +naPausa.map(function(o){return '<rect x="'+(o.x-14)+'" y="344" width="5" height="6" rx="1" fill="#fff" stroke="#92400e" stroke-width=".5"/>';}).join('')+'</g>');
  var emb=lista.some(function(o){return o.vis&&o.p.setor==='Expedição'&&o.p.estado!=='pausa';});
  s.push('<g class="clic" data-k="sala" data-v="Expedição">'+(emb?'<path d="M420 490 v-12 h32 v12z" fill="#d6a15c" stroke="#8a5a24"/><path d="M420 478 l-6 -6 M452 478 l6 -6" stroke="#8a5a24" stroke-width="2"/>':'')
   +'<rect x="486" y="478" width="28" height="12" rx="2" fill="#1f2937"/><rect x="491" y="472" width="18" height="7" fill="#fff"/><circle cx="372" cy="486" r="4" fill="none" stroke="#a16207" stroke-width="3"/>'
   +'<rect x="352" y="490" width="176" height="5" rx="2" fill="#94a3b8"/><rect x="358" y="495" width="164" height="18" fill="#cbd5e1" stroke="#94a3b8"/></g>');
  return s.join('');
}
function casas(noite){
  var s=[], cores=['#fde68a','#bbf7d0','#fbcfe8'];
  for(var i=0;i<3;i++){
    var hx=726+i*92, e=D.entregas[i];
    s.push('<g class="clic" data-k="casa" data-v="'+i+'"><rect x="'+hx+'" y="490" width="72" height="53" fill="'+cores[i]+'" stroke="#a8a29e"/>'
     +'<path d="M'+(hx-6)+' 492 L'+(hx+36)+' 460 L'+(hx+78)+' 492z" fill="#b45309" stroke="#92400e"/>'
     +'<rect x="'+(hx+29)+'" y="515" width="14" height="28" fill="#7c2d12"/><circle cx="'+(hx+40)+'" cy="530" r="1.2" fill="#fde68a"/>'
     +'<rect x="'+(hx+8)+'" y="500" width="15" height="12" fill="'+(noite?'#fde047':'#bae6fd')+'" stroke="#fff"/><rect x="'+(hx+49)+'" y="500" width="15" height="12" fill="'+(noite?'#fde047':'#bae6fd')+'" stroke="#fff"/>'
     +'<rect x="'+(hx+60)+'" y="526" width="8" height="6" fill="#1d4ed8"/><rect x="'+(hx+63)+'" y="532" width="2" height="11" fill="#475569"/>');
    if(e){ s.push('<g class="mc-pino"><path d="M'+(hx+36)+' 456 c-9 -10 -9 -22 0 -22 c9 0 9 12 0 22z" fill="#ef4444"/><circle cx="'+(hx+36)+'" cy="441" r="3.6" fill="#fff"/></g>'
       +'<rect x="'+(hx-4)+'" y="545" width="80" height="10" rx="5" fill="rgba(17,24,39,.85)"/><text x="'+(hx+36)+'" y="552.4" font-size="5.6" text-anchor="middle" fill="#fff">📍 '+esc(corta(e.cidade,22))+'</text>'); }
    s.push('</g>');
  }
  s.push('<g><rect x="806" y="512" width="4" height="31" fill="#78350f"/><circle cx="808" cy="506" r="10" fill="#16a34a"/><rect x="898" y="512" width="4" height="31" fill="#78350f"/><circle cx="900" cy="506" r="10" fill="#15803d"/></g>');
  return s.join('');
}
function vanSVG(){
  var c=cor(D.cor,'#1d4ed8'), mot=null;
  D.equipe.forEach(function(p){if(!mot&&p.setor==='Entrega')mot=p;});
  var pele=mot?cor(mot.pele,'#C68642'):'#C68642';
  return '<g id="van" class="clic" data-k="van" transform="translate('+vanPos.x.toFixed(1)+','+vanPos.y.toFixed(1)+')"><g id="vanc"'+(vanEsq?' transform="scale(-1,1)"':'')+'>'
   +'<ellipse cx="0" cy="1" rx="47" ry="4" fill="rgba(0,0,0,.25)"/>'
   +'<rect x="-44" y="-36" width="70" height="30" rx="4" fill="#fff" stroke="#334155" stroke-width="1.2"/>'
   +'<path d="M26 -36 h7 q9 0 12 11 l3 8 v11 h-22z" fill="#fff" stroke="#334155" stroke-width="1.2"/>'
   +'<path d="M29 -33 h4 q6 0 8 9 h-12z" fill="#93c5fd" stroke="#334155" stroke-width=".6"/>'
   +(D.entregas.length?'<circle cx="33" cy="-25.5" r="3.4" fill="'+pele+'"/><path d="M29.6 -26.5 a3.4 3.4 0 0 1 6.8 0z" fill="'+(mot?cor(mot.camisa,'#1f2937'):'#1f2937')+'"/>':'')
   +'<rect x="-44" y="-22" width="70" height="5" fill="'+c+'"/><rect x="44" y="-14" width="4" height="4" rx="1" fill="#fde047"/><rect x="-46" y="-12" width="3" height="5" fill="#ef4444"/>'
   +'<circle cx="-26" cy="-6" r="6.5" fill="#111827"/><circle cx="-26" cy="-6" r="2.8" fill="#9ca3af"/><circle cx="32" cy="-6" r="6.5" fill="#111827"/><circle cx="32" cy="-6" r="2.8" fill="#9ca3af"/>'
   +'</g><text id="vant" x="'+(vanEsq?9:-9)+'" y="-26.5" font-size="8" font-weight="800" fill="'+c+'" text-anchor="middle">ENTREGA</text>'
   +'<g id="vanbal" style="display:none"><rect x="-62" y="-60" width="124" height="17" rx="8.5" fill="#111827"/><text id="vanbalt" x="0" y="-48.6" font-size="7.6" fill="#fff" text-anchor="middle"></text></g></g>';
}
function render(){
  var h=new Date().getHours(), noite=(h>=19||h<6), lista=posicoes();
  svg.innerHTML=cenario(noite)+pessoas(lista)+frente(lista)+casas(noite)+vanSVG();
  animarPessoas();
  iniciarVan();
  if(popAberto) abrir(popAberto[0],popAberto[1]);
}
function animarPessoas(){
  var novos={};
  Array.prototype.forEach.call(svg.querySelectorAll('g.pessoa'),function(g){
    var id=g.getAttribute('data-id'), x=+g.getAttribute('data-x'), y=+g.getAttribute('data-y'), a=posAnt[id];
    novos[id]=[x,y];
    if(a&&(a[0]!==x||a[1]!==y)){
      g.style.transition='none';
      if(Math.abs(a[1]-y)<40){ g.style.transform='translate('+a[0]+'px,'+a[1]+'px)'; }
      else { g.style.opacity='0'; }
      g.getBoundingClientRect();
      requestAnimationFrame(function(){ g.style.transition=''; g.style.transform='translate('+x+'px,'+y+'px)'; g.style.opacity='1'; });
    }
  });
  posAnt=novos;
}
function iniciarVan(){
  var ent=D.entregas.slice(0,3), assin=ent.map(function(e){return e.id;}).join(',');
  if(assin===vanAssin&&(vanRota||!ent.length)) return;
  vanAssin=assin;
  if(ent.length){
    var r=[{x:622,y:614}];
    ent.forEach(function(e,i){ r.push({x:762+i*92,y:614,espera:2600,txt:'📦 Entregando '+e.id}); });
    r.push({x:975,y:614}); r.push({x:975,y:584}); r.push({x:622,y:584});
    r.push({x:GARAGEM.x,y:GARAGEM.y,espera:3200,txt:'🅿️ De volta na garagem'});
    vanRota=r; vanCiclo=true;
  } else { vanRota=[{x:622,y:584},{x:GARAGEM.x,y:GARAGEM.y,txt:'🅿️ Van na garagem'}]; vanCiclo=false; }
  vanSeg=0; vanEspera=0;
}
function balao(txt,ms){
  var b=document.getElementById('vanbal'), t=document.getElementById('vanbalt'); if(!b||!txt) return;
  t.textContent=txt; b.style.display=''; clearTimeout(balao.t); balao.t=setTimeout(function(){var bb=document.getElementById('vanbal'); if(bb) bb.style.display='none';},ms||2500);
}
function virar(esq){
  if(esq===vanEsq) return; vanEsq=esq;
  var g=document.getElementById('vanc'), t=document.getElementById('vant');
  if(g) g.setAttribute('transform',esq?'scale(-1,1)':''); if(t) t.setAttribute('x',esq?9:-9);
}
function passoVan(t){
  var dt=Math.min(64,t-(vanUlt||t)); vanUlt=t;
  var g=document.getElementById('van');
  if(g&&vanRota){
    if(vanEspera>0){ vanEspera-=dt; }
    else {
      var alvo=vanRota[vanSeg], dx=alvo.x-vanPos.x, dy=alvo.y-vanPos.y, dist=Math.sqrt(dx*dx+dy*dy), v=0.085*dt;
      if(dist<=v){
        vanPos.x=alvo.x; vanPos.y=alvo.y;
        if(alvo.txt) balao(alvo.txt,alvo.espera||2500);
        if(alvo.espera) vanEspera=alvo.espera;
        if(vanSeg<vanRota.length-1) vanSeg++; else if(vanCiclo) vanSeg=0; else vanRota=null;
      } else { vanPos.x+=dx/dist*v; vanPos.y+=dy/dist*v; if(Math.abs(dx)>0.5) virar(dx<0); }
    }
    g.setAttribute('transform','translate('+vanPos.x.toFixed(1)+','+vanPos.y.toFixed(1)+')');
  }
  requestAnimationFrame(passoVan);
}
requestAnimationFrame(passoVan);

function btn(txt,key,pri){ if(D.publico||!key) return ''; return '<button class="ac'+(pri?' pri':'')+'" data-key="'+esc(key)+'">'+esc(txt)+'</button>'; }
function nav(txt,k){ return k?btn(txt,'mc_nav_'+k):''; }
function linha(a,b){ return '<div class="lin"><span>'+esc(a)+'</span><b>'+esc(b)+'</b></div>'; }
function membrosProducao(){ return D.equipe.filter(function(x){return x.setor==='Produção';}); }
function cardNovo(p){ return '<div class="ped"><b>'+esc(p.id)+'</b> · '+esc(p.nome)+(p.total?'<span style="float:right;font-weight:700">'+esc(p.total)+'</span>':'')
  +'<br><small>'+esc(p.itens)+'</small><br><small>⏱️ esperando '+esc(p.espera)+' · 📍 '+esc(p.cidade)+'</small>'
  +'<div class="acoes">'+btn('✅ Autorizar','mc_apr_'+p.id,1)+btn('❌ Recusar','mc_rec_'+p.id)+'</div></div>'; }
function cardProd(p){ var q=membrosProducao()[p.quem];
  return '<div class="ped"><b>'+esc(p.id)+'</b> · '+esc(p.nome)+(p.atrasado&&!D.publico?' <span class="humor" style="background:#fee2e2;color:#991b1b">atrasado</span>':'')
  +'<br><small>'+esc(p.itens)+'</small><br><small>👷 '+esc(q?q.nome:'equipe da produção')+' · na fila há '+esc(p.espera)+'</small>'
  +'<div class="acoes">'+btn('📦 Pronto, enviar','mc_env_'+p.id,1)+'</div></div>'; }
function cardEnt(e){ return '<div class="ped"><b>'+esc(e.id)+'</b> · '+esc(e.nome)+(e.atrasado&&!D.publico?' ⚠️ atrasado':'')
  +'<br><small>📍 '+(e.endereco?esc(e.endereco)+' - ':'')+esc(e.cidade)+(e.cep?' · CEP '+esc(e.cep):'')+'</small>'
  +'<br><small>📦 '+esc(e.itens)+'</small><br><small>🚚 '+esc(e.transportadora)+(e.codigo?' · código '+esc(e.codigo):(D.publico?'':' · sem código de rastreio'))+(e.previsao?' · previsão '+esc(e.previsao):'')+'</small>'
  +'<div class="acoes">'+btn('✅ Entregue','mc_ent_'+e.id,1)+'</div></div>'; }
function listaEstoque(){ if(!D.estoque.length) return '<p class="vazio">Nenhum material cadastrado ainda.</p>';
  return D.estoque.map(function(m){ return '<div class="ev">'+(m.repor&&!D.publico?'⚠️':'📦')+' <b>'+esc(m.material)+'</b> · tem '+esc(m.qtd)+' '+esc(m.unidade)+(m.repor&&!D.publico?' · comprar '+esc(m.comprar):'')+'</div>'; }).join(''); }
function listaPessoas(filtro){ var r=''; D.equipe.forEach(function(p,i){ if(filtro(p)){ var H=HUMOR[p.humor]||HUMOR.feliz; r+='<div class="ev clicavel" data-pessoa="'+i+'">'+H[0]+' <b>'+esc(p.nome)+'</b> · '+esc(p.fazendo)+'</div>'; } }); return r||'<p class="vazio">Ninguém aqui agora.</p>'; }
function abrir(k,v){
  var t='', c='';
  if(k==='p'){
    var p=D.equipe[+v]; if(!p){fechar();return;}
    var H=HUMOR[p.humor]||HUMOR.feliz; t=p.nome+' · '+p.cargo;
    c=linha('Setor',p.setor)+'<div class="lin"><span>Agora</span><b style="max-width:72%">'+esc(p.fazendo)+'</b></div>'
     +'<div class="lin"><span>Humor</span><span class="humor" style="background:'+H[2]+';color:'+H[3]+'">'+H[0]+' '+H[1]+'</span></div>'
     +(p.motivo?'<div class="motivo">💭 '+esc(p.motivo)+'</div>':'')+(p.rendimento?linha('Rendimento',p.rendimento):'');
    if(p.setor==='Diretoria') c+='<h4>Pedidos esperando autorização</h4>'+(D.novos.map(cardNovo).join('')||'<p class="vazio">Nenhum pedido esperando.</p>')+'<div class="acoes">'+nav('🧾 Abrir pedidos','pedidos')+'</div>';
    else if(p.setor==='Produção'){ var meus=D.producao.filter(function(x){return p.ids.indexOf(x.id)>=0;}); c+='<h4>Na bancada</h4>'+(meus.map(cardProd).join('')||'<p class="vazio">Sem pedido agora.</p>')+'<div class="acoes">'+nav('🖨️ Artes para imprimir','artes')+'</div>'; }
    else if(p.setor==='Entrega') c+='<h4>Entregas</h4>'+(D.entregas.map(cardEnt).join('')||'<p class="vazio">Nenhuma entrega.</p>')+'<div class="acoes">'+nav('🚚 Abrir rastreio','rastreio')+'</div>';
    else if(p.setor==='Atendimento'){ var mm=D.novos.filter(function(x){return p.ids.indexOf(x.id)>=0;}); c+=(mm.length?'<h4>Clientes com ele(a)</h4>'+mm.map(cardNovo).join(''):'')+'<div class="acoes">'+nav('👥 Abrir clientes','clientes')+'</div>'; }
    else if(p.setor==='Estoque') c+='<h4>Prateleiras</h4>'+listaEstoque()+'<div class="acoes">'+nav('🏭 Abrir estoque','estoque')+'</div>';
    else c+='<div class="acoes">'+nav('🏷️ Abrir etiquetas','etiquetas')+'</div>';
  } else if(k==='novos'){ t='📋 Mesa do diretor'; c=(D.novos.map(cardNovo).join('')||'<p class="vazio">Nenhum pedido esperando autorização.</p>')+'<div class="acoes">'+nav('🧾 Abrir pedidos','pedidos')+'</div>';
  } else if(k==='item'){ var pi=D.producao[+v]; if(!pi){fechar();return;} t='⚙️ Na esteira'; c=cardProd(pi);
  } else if(k==='van'){ t='🚚 Van de entrega'; c=(D.entregas.length?'<p class="vazio">Rota na ordem das casas:</p>'+D.entregas.map(cardEnt).join(''):'<p class="vazio">Van na garagem. Nenhum pedido a caminho.</p>')+'<div class="acoes">'+nav('🚚 Abrir rastreio','rastreio')+nav('🏷️ Etiquetas','etiquetas')+'</div>';
  } else if(k==='casa'){ var ec=D.entregas[+v]; t='🏠 Casa do cliente'; c=ec?cardEnt(ec):'<p class="vazio">Nenhuma entrega para esta casa agora.</p>';
  } else if(k==='prat'){ var m=D.estoque[+v]; t='📦 Prateleira';
    c=m?(linha('Material',m.material)+linha('Tem',m.qtd+' '+m.unidade)+linha('Mínimo',m.minimo)+(m.dias?linha('Dura cerca de',m.dias+' dia(s)'):'')+(m.fornecedor?linha('Fornecedor',m.fornecedor):'')
      +(m.repor&&!D.publico?'<div class="motivo" style="color:#991b1b">⚠️ Precisa repor: comprar '+esc(m.comprar)+' '+esc(m.unidade)+'</div>':'<div class="motivo">✅ Quantidade boa</div>'))
      :'<p class="vazio">Prateleira vazia. Cadastre os materiais no painel, em Estoque e compras.</p>';
    c+='<div class="acoes">'+nav('🏭 Abrir estoque','estoque')+'</div>';
  } else if(k==='tv'||k==='prod'){ var n=D.numeros; t=k==='tv'?'📊 Painel da parede':'⚙️ Quadro da produção';
    c=linha('Pedidos hoje',n.hoje)+(n.fat?linha('Faturamento hoje',n.fat):'')+linha('Esperando autorização',n.novos)+linha('Na produção',n.producao)+linha('A caminho',n.caminho)+linha('Entregues em 7 dias',n.entregues)
     +(D.publico?'':linha('Atrasados',n.atrasados)+linha('Materiais para repor',n.repor));
    if(k==='prod') c+='<h4>Na esteira</h4>'+(D.producao.map(cardProd).join('')||'<p class="vazio">Esteira parada.</p>');
    c+='<h4>Últimos acontecimentos</h4>'+(D.eventos.map(function(x){return '<div class="ev">'+esc(x)+'</div>';}).join('')||'<p class="vazio">Nada ainda.</p>')+'<div class="acoes">'+nav('📊 Abrir resumo','resumo')+'</div>';
  } else if(k==='sala'){ var S=SALAS[v]; if(!S){fechar();return;} t=S[0];
    c='<p class="vazio">'+esc(S[1])+'</p><h4>Quem está aqui</h4>'+listaPessoas(v==='Cafeteria'?function(p){return p.estado==='pausa';}:function(p){return p.setor===S[3]&&p.estado!=='pausa';});
    if(v==='Diretoria') c+='<h4>Esperando autorização</h4>'+(D.novos.map(cardNovo).join('')||'<p class="vazio">Nenhum.</p>');
    if(v==='Produção') c+='<h4>Na esteira</h4>'+(D.producao.map(cardProd).join('')||'<p class="vazio">Esteira parada.</p>');
    if(v==='Estoque') c+='<h4>Prateleiras</h4>'+listaEstoque();
    if(v==='Garagem') c+='<h4>Entregas</h4>'+(D.entregas.map(cardEnt).join('')||'<p class="vazio">Nenhuma.</p>');
    c+='<div class="acoes">'+nav('Abrir no painel',S[2])+'</div>';
  } else { fechar(); return; }
  popAberto=[k,v];
  pop.innerHTML='<div class="cab"><b>'+esc(t)+'</b><button class="x" data-fechar="1" title="Fechar">✕</button></div><div class="corpo">'+c+'</div>';
  pop.style.display='block';
}
function fechar(){ popAberto=null; pop.style.display='none'; }
function aviso(txt){ avisoEl.textContent=txt; avisoEl.style.display='block'; clearTimeout(aviso.t); aviso.t=setTimeout(function(){avisoEl.style.display='none';},2600); }
function acionar(chave){
  try{ var b=window.parent.document.querySelector('.st-key-'+chave+' button');
    if(b){ b.click(); aviso('✅ Feito! Atualizando a fábrica…'); fechar(); return; } }catch(e){}
  aviso('Não deu para fazer por aqui. Abra o painel e tente de novo.');
}
svg.addEventListener('click',function(e){ var t=e.target.closest('[data-k]'); if(!t||t.getAttribute('data-k')==='fundo'){fechar();return;} abrir(t.getAttribute('data-k'),t.getAttribute('data-v')); });
pop.addEventListener('click',function(e){ var b=e.target.closest('[data-key],[data-fechar],[data-pessoa]'); if(!b) return;
  if(b.getAttribute('data-fechar')) fechar(); else if(b.getAttribute('data-pessoa')!=null) abrir('p',b.getAttribute('data-pessoa')); else acionar(b.getAttribute('data-key')); });
setInterval(function(){ var r=document.getElementById('relogio'); if(r) r.textContent=new Date().toLocaleTimeString('pt-BR'); },1000);
var evI=0; setInterval(function(){ var e=document.getElementById('evento'); if(e&&D&&D.eventos.length){ e.textContent='🔔 '+D.eventos[evI%D.eventos.length]; evI++; } },3500);
function mcAtualizar(d){ D=d; render(); }
window.mcAtualizar=mcAtualizar;
</script>
<!--DADOS-->
</body></html>
"""


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


if not st.session_state.admin:
    _c_espaco, _c_engrenagem = st.columns([30, 1])
    if _c_engrenagem.button("⚙", key="btn_engrenagem", help=" "):
        abrir_login_admin()
# ===============================================================
# PAINEL EMPRESARIAL: estilo claro, menu fixo à esquerda
# ===============================================================
CSS_PAINEL = """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #eef2f7 !important; background-image: none !important; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
.block-container { padding-left: 290px !important; padding-right: 28px !important; max-width: 100% !important; }
h1, h2, h3, h4, h5, h6, p, span, label, li, div { color: #1f2937; }
[data-testid="stCaptionContainer"] p { color: #4b5563 !important; }

/* ---------- MENU FIXO À ESQUERDA ---------- */
.st-key-menu_admin {
    position: fixed; top: 0; left: 0; bottom: 0; width: 260px; z-index: 999990;
    background: #ffffff; border-right: 1px solid #dbe1ea; padding: 12px 12px 10px;
    overflow-y: auto; scrollbar-width: none; box-shadow: 4px 0 16px rgba(15, 23, 42, .08); }
.st-key-menu_admin::-webkit-scrollbar { display: none; }
.st-key-menu_admin [data-testid="stMarkdownContainer"] p, .st-key-menu_admin [data-testid="stMarkdown"],
.st-key-menu_admin .stButton, .st-key-menu_admin [data-testid="stElementContainer"] { margin: 0 !important; }
.st-key-menu_admin [data-testid="stVerticalBlock"] { gap: .22rem; }
.st-key-menu_admin .stButton > button {
    width: 100%; justify-content: flex-start !important; text-align: left;
    background: #f8fafc !important; color: #1f2937 !important;
    border: 1px solid #e2e8f0 !important; border-radius: 10px !important;
    padding: 2px 10px !important; min-height: 0 !important; height: clamp(30px, calc((100vh - 200px) / 19), 52px); font-weight: 600 !important; box-shadow: none !important; }
.st-key-menu_admin .stButton > button div { justify-content: flex-start !important; }
.st-key-menu_admin .stButton > button p { color: inherit !important; font-size: clamp(.8rem, 1.7vh, .98rem); margin: 0 !important; line-height: 1.1; }
.st-key-menu_admin .stButton > button:hover { background: #ede9fe !important; border-color: #8b5cf6 !important; }
.st-key-menu_admin .stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #7c3aed, #06b6d4) !important; color: #ffffff !important; border: none !important; }
.adm-logo { font-size: 1rem; font-weight: 800; color: #111827 !important; }
.adm-sub { font-size: .72rem; color: #6b7280 !important; margin-bottom: 2px; }
.adm-grupo { font-size: .7rem; letter-spacing: .12em; color: #7c3aed !important; font-weight: 800; margin: 6px 0 1px; font-size: .68rem !important; }
@media (max-width: 900px) {
    .st-key-menu_admin { position: static; width: auto; box-shadow: none; border: 1px solid #dbe1ea; border-radius: 14px; }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; } }

/* ---------- CONTEÚDO ---------- */
.adm-topo { display: flex; justify-content: space-between; align-items: center; background: #ffffff;
    border: 1px solid #dbe1ea; border-radius: 14px; padding: 12px 20px; margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, .05); }
.adm-topo .t { font-size: 1.35rem; font-weight: 800; color: #111827 !important; }
.adm-topo .d { font-size: .85rem; color: #6b7280 !important; }
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stExpander"] {
    background: #ffffff !important; border: 1px solid #dbe1ea !important; border-radius: 14px; }
[data-testid="stMetric"] { background: #ffffff; border: 1px solid #dbe1ea; border-left: 5px solid #7c3aed;
    border-radius: 12px; padding: 10px 14px; }
.stButton > button, .stDownloadButton > button, .stLinkButton > a {
    background: #ffffff !important; color: #5b21b6 !important; border: 1.5px solid #8b5cf6 !important;
    border-radius: 10px !important; font-weight: 700 !important; box-shadow: 0 1px 3px rgba(0, 0, 0, .08); }
.stButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover { background: #f5f3ff !important; }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
.stLinkButton > a[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] {
    background: linear-gradient(90deg, #7c3aed, #06b6d4) !important; color: #ffffff !important; border: none !important; }
.stButton > button p, .stDownloadButton > button p { color: inherit !important; }
button[data-baseweb="tab"] { background: #ffffff; border: 1px solid #dbe1ea !important; border-radius: 10px 10px 0 0;
    padding: 6px 14px !important; margin-right: 4px; }
button[data-baseweb="tab"][aria-selected="true"] { background: #ede9fe; }
.kpi { border-radius: 16px; padding: 16px 18px; min-height: 108px; box-shadow: 0 8px 20px rgba(15, 23, 42, .12); }
.kpi-t { font-size: .85rem; color: #ffffff !important; font-weight: 600; }
.kpi-v { font-size: 1.65rem; font-weight: 800; color: #ffffff !important; margin-top: 8px; }
.mini { display: flex; align-items: center; gap: 10px; background: #ffffff; border: 1px solid #dbe1ea;
    border-radius: 12px; padding: 9px 12px; margin-bottom: 8px; }
.mini-i { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.mini-t { flex: 1; font-weight: 600; }
.mini-v { padding: 2px 12px; border-radius: 999px; font-weight: 800; color: #1f2937 !important; }
</style>
"""

GRAD = {
    "rosa": "linear-gradient(135deg, #ec4899, #8b5cf6)",
    "agua": "linear-gradient(135deg, #14b8a6, #06b6d4)",
    "roxo": "linear-gradient(135deg, #6366f1, #4338ca)",
    "azul": "linear-gradient(135deg, #0ea5e9, #2563eb)",
}


def brl(v: float) -> str:
    """Valor no formato brasileiro: R$ 1.234,56"""
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def cartao_kpi(titulo: str, valor: str, fundo: str) -> str:
    return (f"<div class='kpi' style='background:{fundo}'><div class='kpi-t'>{html.escape(titulo)}</div>"
            f"<div class='kpi-v'>{html.escape(valor)}</div></div>")


def cartao_mini(icone: str, titulo: str, valor, cor: str) -> str:
    return (f"<div class='mini'><span class='mini-i' style='background:{cor}'>{icone}</span>"
            f"<span class='mini-t'>{html.escape(titulo)}</span>"
            f"<span class='mini-v' style='background:{cor}'>{valor}</span></div>")


def tema_grafico(graf):
    return (graf.configure(background="transparent")
            .configure_axis(labelColor="#374151", titleColor="#374151", gridColor="#e5e7eb",
                            domainColor="#9ca3af", tickColor="#9ca3af")
            .configure_view(strokeWidth=0)
            .configure_legend(labelColor="#1f2937", titleColor="#1f2937"))


def grafico(graf):
    st.altair_chart(tema_grafico(graf), use_container_width=True, theme=None)


def rosca(df: pd.DataFrame, campo: str, cores: list):
    return alt.Chart(df).mark_arc(innerRadius=58, cornerRadius=4).encode(
        theta=alt.Theta("qtd:Q"),
        color=alt.Color(f"{campo}:N", title=None, scale=alt.Scale(range=cores),
                        legend=alt.Legend(orient="bottom", columns=2)),
        tooltip=[campo, "qtd"]).properties(height=240)


def ir_secao(destino: str):
    st.session_state.secao_admin = destino


# ===============================================================
# PAINEL DO ADMINISTRADOR
# ===============================================================
SECOES_ADMIN = {
    "VISÃO GERAL": ["📊 Resumo", "🏙️ Empresa ao vivo"],
    "CATÁLOGO": ["📦 Produtos", "🖼️ Fotos", "🎨 Galeria de artes"],
    "VENDAS": ["👥 Clientes", "🧾 Pedidos", "🚚 Rastreio", "🏷️ Etiquetas", "🖨️ Artes", "📄 Nota fiscal", "📍 Frete"],
    "COMPRAS": ["🏭 Estoque e compras"],
    "MARKETING": ["🏢 Apresentações", "🎬 Vitrine", "👁️ Interesse"],
    "CONFIGURAÇÃO": ["🎨 Loja e redes", "💾 Backup"],
}
if st.session_state.admin:
    st.markdown(CSS_PAINEL, unsafe_allow_html=True)

    # ----- Menu fixo à esquerda, com todos os comandos -----
    with st.container(key="menu_admin"):
        st.markdown(f"<div class='adm-logo'>⚙️ {html.escape(LOJA['nome_empresa'])}</div>"
                    "<div class='adm-sub'>Painel administrativo</div>", unsafe_allow_html=True)
        for grupo, secoes in SECOES_ADMIN.items():
            st.markdown(f"<div class='adm-grupo'>{grupo}</div>", unsafe_allow_html=True)
            for s in secoes:
                st.button(s, key=f"menu_{s}", use_container_width=True, on_click=ir_secao, args=(s,),
                          type="primary" if st.session_state.secao_admin == s else "secondary")
        st.markdown("<div class='adm-grupo'>&nbsp;</div>", unsafe_allow_html=True)
        if st.button("🚪 Voltar para a loja", key="menu_sair", use_container_width=True):
            st.session_state.admin = False
            st.rerun()

    secao = st.session_state.secao_admin
    st.markdown(f"<div class='adm-topo'><span class='t'>{html.escape(secao)}</span>"
                f"<span class='d'>{datetime.now().strftime('%d/%m/%Y')}</span></div>", unsafe_allow_html=True)

    # ----- Aviso automático de reposição, em todas as telas do painel -----
    _aviso = analise_estoque(int(LOJA.get("estoque_margem_dias", 7)))
    _aviso = _aviso[_aviso["repor"] == True] if len(_aviso) else _aviso
    if len(_aviso) and secao != "🏭 Estoque e compras":
        av1, av2 = st.columns([4, 1])
        av1.warning(f"⚠️ Hora de repor {len(_aviso)} material(is): " + ", ".join(_aviso["material"].head(5).tolist()))
        av2.button("📦 Ver e repor", key="aviso_estoque", type="primary", use_container_width=True,
                   on_click=ir_secao, args=("🏭 Estoque e compras",))

    # ----- Mini fábrica: grande nesta seção, janela flutuante (arrastável) nas outras -----
    if secao != "🏙️ Empresa ao vivo":
        if LOJA.get("mini_no_painel", True):
            mini_cidade("admin")
        else:
            esconder_cidade()

    # ---------------------------------------------------------- EMPRESA AO VIVO (mini fábrica)
    if secao == "🏙️ Empresa ao vivo":
        st.caption("Sua empresa em miniatura, trabalhando com os pedidos de verdade. Clique em qualquer coisa: "
                   "pessoas, salas, painel da parede, esteira, prateleiras, van e casas dos clientes.")
        mini_cidade("painel")
        with st.expander("👥 Minha equipe (nomes reais, setores e aparência dos bonequinhos)"):
            st.caption("Cada pessoa aparece no setor escolhido. Camisa: cor em código (ex.: #2563eb). "
                       "Desmarque 'Ativo' para tirar alguém da fábrica sem apagar.")
            eq_df = pd.DataFrame(carregar_equipe())
            for c in ["nome", "cargo", "setor", "pele", "cabelo", "estilo", "camisa", "ativo"]:
                if c not in eq_df.columns:
                    eq_df[c] = True if c == "ativo" else ""
            eq_edit = st.data_editor(
                eq_df[["nome", "cargo", "setor", "pele", "cabelo", "estilo", "camisa", "ativo"]],
                num_rows="dynamic", use_container_width=True, key="editor_equipe",
                column_config={
                    "nome": st.column_config.TextColumn("Nome", required=True),
                    "cargo": st.column_config.TextColumn("Cargo"),
                    "setor": st.column_config.SelectboxColumn("Setor", options=SETORES, required=True),
                    "pele": st.column_config.SelectboxColumn("Tom de pele", options=list(TONS_PELE)),
                    "cabelo": st.column_config.SelectboxColumn("Cabelo", options=list(CORES_CABELO)),
                    "estilo": st.column_config.SelectboxColumn("Estilo", options=ESTILOS_CABELO),
                    "camisa": st.column_config.TextColumn("Cor da camisa"),
                    "ativo": st.column_config.CheckboxColumn("Ativo"),
                })
            q1, q2 = st.columns(2)
            if q1.button("💾 Salvar equipe", type="primary", key="salvar_equipe"):
                lista = eq_edit.dropna(subset=["nome"]).fillna("").to_dict("records")
                for m in lista:
                    m["ativo"] = bool(m.get("ativo", True))
                gravar_json(ARQ_EQUIPE, lista)
                st.rerun()
            novo_mini = q2.toggle("Mostrar a janela flutuante nas outras telas do painel",
                                  value=bool(LOJA.get("mini_no_painel", True)), key="tg_mini_painel")
            if novo_mini != bool(LOJA.get("mini_no_painel", True)):
                LOJA["mini_no_painel"] = novo_mini
                gravar_loja(LOJA)
                st.rerun()
        pedidos_v = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        s1, s2, s3, s4 = st.columns(4)
        with s1, st.container(border=True):
            st.markdown("**💬 Vendas**")
            st.caption(f"{len(pedidos_v)} pedido(s) no total")
            st.button("Ver clientes", key="mini_vend", use_container_width=True,
                      on_click=ir_secao, args=("👥 Clientes",))
            st.button("Ver interesse", key="mini_int", use_container_width=True,
                      on_click=ir_secao, args=("👁️ Interesse",))
        with s2, st.container(border=True):
            st.markdown("**🔨 Mesa do chefe**")
            novos_v = pedidos_v[pedidos_v["status"] == "Novo"]
            if novos_v.empty:
                st.success("Nenhum pedido esperando.")
            for _, p in novos_v.iloc[::-1].head(6).iterrows():
                st.markdown(f"**{p['id_pedido']}** · {p['nome']}  \nR$ {p['total']}")
                st.caption(str(p["itens"])[:120])
                a, b = st.columns(2)
                a.button("✅", key=f"apr_{p['id_pedido']}", help="Aprovar e mandar para a produção",
                         type="primary", use_container_width=True,
                         on_click=decidir_pedido, args=(p["id_pedido"], "Em produção"))
                b.button("❌", key=f"rec_{p['id_pedido']}", help="Recusar pedido", use_container_width=True,
                         on_click=decidir_pedido, args=(p["id_pedido"], "Cancelado"))
        with s3, st.container(border=True):
            st.markdown("**🔥 Produção (esteira)**")
            prod_v = pedidos_v[pedidos_v["status"].isin(["Pago", "Em produção"])]
            if prod_v.empty:
                st.caption("Esteira parada, sem pedidos.")
            for _, p in prod_v.iloc[::-1].head(6).iterrows():
                st.markdown(f"**{p['id_pedido']}** · {p['nome']}")
                st.button("📦 Pronto, enviar", key=f"env_{p['id_pedido']}", use_container_width=True,
                          on_click=mudar_status, args=(p["id_pedido"], "Enviado"))
            st.button("🖨️ Artes para imprimir", key="mini_art", use_container_width=True,
                      on_click=ir_secao, args=("🖨️ Artes",))
        with s4, st.container(border=True):
            st.markdown("**🚚 Entrega e estoque**")
            env_v = pedidos_v[pedidos_v["status"] == "Enviado"]
            for _, p in env_v.iloc[::-1].head(6).iterrows():
                st.markdown(f"**{p['id_pedido']}** · {p['nome']}")
                st.button("✅ Entregue", key=f"ent_{p['id_pedido']}", use_container_width=True,
                          on_click=mudar_status, args=(p["id_pedido"], "Entregue"))
            st.button("🏷️ Etiquetas", key="mini_etq", use_container_width=True,
                      on_click=ir_secao, args=("🏷️ Etiquetas",))
            st.button("📦 Estoque", key="mini_est", use_container_width=True,
                      on_click=ir_secao, args=("🏭 Estoque e compras",))
    # ---------------------------------------------------------- RESUMO (dashboard)
    elif secao == "📊 Resumo":
        clientes_r = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
        pedidos_r = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        pedidos_r["total_num"] = pd.to_numeric(pedidos_r["total"], errors="coerce").fillna(0.0)
        pedidos_r["dt"] = pd.to_datetime(pedidos_r["data"], format="%d/%m/%Y %H:%M", errors="coerce")
        validos = pedidos_r[pedidos_r["status"] != "Cancelado"]
        faturamento = validos["total_num"].sum()
        recebido = validos[validos["pagamento"] == "Pago"]["total_num"].sum()
        ticket = faturamento / len(validos) if len(validos) else 0.0

        # Atalhos rápidos (botões clicáveis)
        atalhos = [("🏙️ Empresa ao vivo", "🏙️ Empresa ao vivo"), ("➕ Novo produto", "📦 Produtos"),
                   ("🧾 Ver pedidos", "🧾 Pedidos"), ("🚚 Rastrear envios", "🚚 Rastreio"),
                   ("💾 Fazer backup", "💾 Backup")]
        for col, (rotulo, destino) in zip(st.columns(len(atalhos)), atalhos):
            col.button(rotulo, key=f"atalho_{destino}", use_container_width=True, type="primary",
                       on_click=ir_secao, args=(destino,))
        st.write("")

        k = st.columns(4)
        k[0].markdown(cartao_kpi("Faturamento", brl(faturamento), GRAD["rosa"]), unsafe_allow_html=True)
        k[1].markdown(cartao_kpi("Já recebido", brl(recebido), GRAD["agua"]), unsafe_allow_html=True)
        k[2].markdown(cartao_kpi("Ticket médio", brl(ticket), GRAD["roxo"]), unsafe_allow_html=True)
        k[3].markdown(cartao_kpi("Pedidos", str(len(pedidos_r)), GRAD["azul"]), unsafe_allow_html=True)
        st.write("")

        if pedidos_r["dt"].notna().sum() == 0:
            st.info("Os gráficos aparecem aqui assim que entrarem os primeiros pedidos.")
        else:
            base = pedidos_r.dropna(subset=["dt"]).copy()
            base["mes"] = base["dt"].dt.strftime("%Y-%m")
            esq, dir_ = st.columns([2.2, 1])
            with esq, st.container(border=True):
                st.markdown("**Pedidos feitos x entregues por mês**")
                feitos = base.groupby("mes").size().rename("Pedidos feitos")
                entregues = base[base["status"] == "Entregue"].groupby("mes").size().rename("Entregues")
                linha = (pd.concat([feitos, entregues], axis=1).fillna(0).reset_index()
                         .melt(id_vars="mes", var_name="tipo", value_name="qtd"))
                grafico(alt.Chart(linha).mark_line(
                    interpolate="monotone", strokeWidth=3, point=alt.OverlayMarkDef(size=70, filled=True)).encode(
                    x=alt.X("mes:N", title=None, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("qtd:Q", title=None),
                    color=alt.Color("tipo:N", title=None, scale=alt.Scale(range=["#06b6d4", "#ec4899"]),
                                    legend=alt.Legend(orient="top")),
                    tooltip=["mes", "tipo", "qtd"]).properties(height=260))
            with dir_:
                notas = int(((pedidos_r["nf_status"].isin(["", "Não emitida"]))
                             & (pedidos_r["status"] != "Cancelado")).sum())
                st.markdown(cartao_mini("💳", "Pagamentos pendentes",
                                        int((pedidos_r["pagamento"] == "Pendente").sum()), "#fbcfe8"),
                            unsafe_allow_html=True)
                st.markdown(cartao_mini("🛠️", "Em produção",
                                        int((pedidos_r["status"] == "Em produção").sum()), "#99f6e4"),
                            unsafe_allow_html=True)
                st.markdown(cartao_mini("🚚", "Enviados",
                                        int((pedidos_r["status"] == "Enviado").sum()), "#bae6fd"),
                            unsafe_allow_html=True)
                st.markdown(cartao_mini("🧾", "Notas a emitir", notas, "#ddd6fe"), unsafe_allow_html=True)
                st.markdown(cartao_mini("👥", "Clientes", len(clientes_r), "#fde68a"), unsafe_allow_html=True)

            g1, g2, g3 = st.columns(3)
            with g1, st.container(border=True):
                st.markdown("**Pedidos por situação**")
                por_status = pedidos_r["status"].value_counts().rename_axis("status").reset_index(name="qtd")
                grafico(rosca(por_status, "status",
                              ["#06b6d4", "#14b8a6", "#0ea5e9", "#6366f1", "#8b5cf6", "#d946ef", "#ec4899"]))
            with g2, st.container(border=True):
                st.markdown("**Clientes novos x que voltaram**")
                q = pd.to_numeric(clientes_r["qtd_pedidos"], errors="coerce").fillna(0)
                fidel = pd.DataFrame({"tipo": ["Clientes novos", "Voltaram a comprar"],
                                      "qtd": [int((q <= 1).sum()), int((q > 1).sum())]})
                grafico(rosca(fidel, "tipo", ["#ec4899", "#8b5cf6"]))
            with g3, st.container(border=True):
                st.markdown("**Pedidos por dia da semana**")
                dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
                base["dia"] = base["dt"].dt.dayofweek.map(dict(enumerate(dias)))
                barras = base["dia"].value_counts().reindex(dias, fill_value=0).rename_axis("dia").reset_index(name="qtd")
                degrade = alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0, stops=[
                    alt.GradientStop(color="#2563eb", offset=0), alt.GradientStop(color="#06b6d4", offset=1)])
                grafico(alt.Chart(barras).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6,
                                                   color=degrade).encode(
                    x=alt.X("dia:N", sort=dias, title=None, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("qtd:Q", title=None), tooltip=["dia", "qtd"]).properties(height=240))

        e1, e2 = st.columns(2)
        with e1, st.container(border=True):
            st.markdown("**⚠️ Retornos de clientes para hoje**")
            hoje = datetime.now().strftime("%Y-%m-%d")
            retornos = clientes_r[(clientes_r["proximo_contato"] != "") & (clientes_r["proximo_contato"] <= hoje)]
            if len(retornos):
                st.dataframe(retornos[["nome", "telefone", "proximo_contato"]], hide_index=True,
                             use_container_width=True, height=200)
            else:
                st.caption("Nenhum retorno pendente.")
            st.button("👥 Abrir clientes", key="res_cli", on_click=ir_secao, args=("👥 Clientes",))
        with e2, st.container(border=True):
            st.markdown("**🏆 Melhores clientes**")
            if len(clientes_r):
                gasto = validos.groupby("telefone")["total_num"].sum().rename("gasto_total")
                top = clientes_r.merge(gasto, on="telefone", how="left").fillna({"gasto_total": 0.0})
                st.dataframe(top.sort_values("gasto_total", ascending=False).head(5)[
                    ["nome", "tipo", "qtd_pedidos", "gasto_total"]], hide_index=True,
                    use_container_width=True, height=200)
            else:
                st.caption("Ainda não há clientes.")
            st.button("👁️ Ver interesse dos visitantes", key="res_int", on_click=ir_secao, args=("👁️ Interesse",))
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

        def salvar_pref(chave_loja: str, chave_estado: str):
            LOJA[chave_loja] = int(st.session_state[chave_estado])
            gravar_loja(LOJA)

        titulo_secao("🔢 Grade de produtos")
        o1, o2, o3 = st.columns(3)
        op_cols, op_pp = [2, 3, 4, 5, 6, 8], [4, 8, 12, 16, 20, 24, 32, 48, 100]
        cols_adm = int(LOJA.get("adm_grade_colunas", 4))
        pp_adm = int(LOJA.get("adm_grade_por_pagina", 8))
        o1.selectbox("Produtos por linha (aqui no painel)", op_cols,
                     index=op_cols.index(cols_adm) if cols_adm in op_cols else 2, key="adm_cols",
                     on_change=salvar_pref, args=("adm_grade_colunas", "adm_cols"))
        o2.selectbox("Produtos por página (aqui no painel)", op_pp,
                     index=op_pp.index(pp_adm) if pp_adm in op_pp else 1, key="adm_pp",
                     on_change=salvar_pref, args=("adm_grade_por_pagina", "adm_pp"))
        op_loja = {0: "Automático", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6"}
        cols_loja = int(LOJA.get("loja_grade_colunas", 0))
        o3.selectbox("Modelos por linha na loja (o que o cliente vê)", list(op_loja),
                     format_func=lambda v: op_loja[v], key="loja_cols",
                     index=list(op_loja).index(cols_loja) if cols_loja in op_loja else 0,
                     on_change=salvar_pref, args=("loja_grade_colunas", "loja_cols"))
        COLS_ADM = int(st.session_state.get("adm_cols", cols_adm))

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
        POR_PAGINA = int(st.session_state.get("adm_pp", pp_adm))
        total_pag = max(1, (len(vista_p) + POR_PAGINA - 1) // POR_PAGINA)
        pagina = f4.number_input(f"Página (de {total_pag})", min_value=1, max_value=total_pag,
                                 value=1, step=1, key="pag_prod")
        trecho = vista_p.iloc[(pagina - 1) * POR_PAGINA: pagina * POR_PAGINA]
        st.caption(f"{len(vista_p)} produto(s) encontrado(s).")

        for n, (_, prod) in enumerate(trecho.iterrows()):
            if n % COLS_ADM == 0:
                cols_p = st.columns(COLS_ADM)
            pos = int(prod["_pos"])
            with cols_p[n % COLS_ADM], st.container(border=True):
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
            antes_st = dict(zip(completo["id_pedido"], completo["status"]))
            for _, linha in ped_editado.iterrows():
                alvo = completo["id_pedido"] == linha["id_pedido"]
                for campo in ["email", "status", "pagamento", "forma_pagamento", "obs_internas"]:
                    completo.loc[alvo, campo] = linha[campo]
            gravar_csv(ARQ_PEDIDOS, completo)
            for _, linha in ped_editado.iterrows():
                depois_de_mudar_status(linha["id_pedido"], antes_st.get(linha["id_pedido"]), linha["status"])
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
                depois_de_mudar_status(id_sel, ped["status"], r_status)
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
    # ---------------------------------------------------------- ETIQUETAS DE ENVIO (Correios)
    elif secao == "🏷️ Etiquetas":
        def html_etiquetas(lista, imprimir: bool = True) -> str:
            """Etiquetas de 9 x 13 cm, 4 por folha A4, com destinatário e remetente."""
            e = lambda v: html.escape(str(v or ""))
            rem = (f"<b>{e(LOJA['fiscal_razao'] or LOJA['nome_empresa'])}</b><br>{e(LOJA['fiscal_endereco'])}<br>"
                   f"{e(LOJA['fiscal_cidade_uf'])} - CEP {e(LOJA['fiscal_cep'])}")
            cartoes = ""
            for p in lista:
                cep = "".join(c for c in str(p["ent_cep"]) if c.isdigit())
                cep_fmt = f"{cep[:5]}-{cep[5:]}" if len(cep) == 8 else e(p["ent_cep"])
                itens = [i.strip("- ").strip() for i in str(p["itens"]).split(" | Frete")[0].split(";") if i.strip()]
                lista_itens = "".join(f"<li>{e(i)}</li>" for i in itens) or "<li>(sem itens)</li>"
                end1 = f"{e(p['ent_rua'])}, {e(p['ent_numero'] or 'S/N')}"
                if p["ent_complemento"]:
                    end1 += f" - {e(p['ent_complemento'])}"
                cartoes += f"""<div class='etq'>
<div class='topo'><span>{e(LOJA['nome_empresa'])}</span><span>Pedido {e(p['id_pedido'])}</span></div>
<div class='rot'>DESTINATÁRIO</div>
<div class='dest'><b>{e(p['nome'])}</b><br>{end1}<br>{e(p['ent_bairro'])}<br>{e(p['ent_cidade'])} / {e(p['ent_uf'])}</div>
<div class='cep'>CEP {cep_fmt}</div>
<div class='info'>Tel.: {e(p['telefone'])} &nbsp;&nbsp; Peso: {e(p['ent_peso']) or '______'} kg</div>
<div class='rot'>CONTEÚDO DO PEDIDO</div><ul class='itens'>{lista_itens}</ul>
<div class='info'><b>Total do pedido:</b> R$ {e(p['total'])}</div>
<div class='rot'>REMETENTE</div><div class='rem'>{rem}</div></div>"""
            auto = " onload='window.print()'" if imprimir else ""
            return f"""<html><head><meta charset='utf-8'><title>Etiquetas</title><style>
@page {{ size: A4; margin: 8mm; }}
body {{ font-family: Arial, sans-serif; margin: 0; color: #000; }}
.grade {{ display: flex; flex-wrap: wrap; gap: 5mm; }}
.etq {{ width: 92mm; min-height: 130mm; border: 1.5px dashed #000; padding: 6mm; box-sizing: border-box;
        page-break-inside: avoid; display: flex; flex-direction: column; gap: 3mm; background: #fff; }}
.topo {{ display: flex; justify-content: space-between; font-size: 11px; border-bottom: 1px solid #000; padding-bottom: 2mm; }}
.rot {{ font-size: 11px; font-weight: bold; letter-spacing: 1px; background: #000; color: #fff; padding: 1mm 2mm; }}
.dest {{ font-size: 16px; line-height: 1.35; }}
.cep {{ font-size: 26px; font-weight: bold; border: 2px solid #000; text-align: center; padding: 2mm; }}
.info {{ font-size: 12px; }}
.rem {{ font-size: 12px; line-height: 1.3; }}
.itens {{ font-size: 12px; line-height: 1.35; margin: 0; padding-left: 5mm; }}
</style></head><body{auto}><div class='grade'>{cartoes}</div></body></html>"""

        pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        def corpo_html(h: str) -> str:
            return h.split("<body", 1)[1].split(">", 1)[1].rsplit("</body>", 1)[0]

        def pacote_impressao(lista, com_etq: bool, com_decl: bool) -> str:
            """Junta etiqueta e/ou declaração de conteúdo num arquivo só para imprimir."""
            if not (com_etq or com_decl):
                return "<html><body><p>Marque Etiqueta ou Declaração para imprimir.</p></body></html>"
            estilos, partes = "", []
            if com_etq:
                h = html_etiquetas(lista, imprimir=False)
                estilos += h.split("<style>", 1)[1].split("</style>", 1)[0]
                partes.append(corpo_html(h))
            if com_decl:
                estilos += (".decl{page-break-before:always;font-family:Arial;padding:6mm}"
                            ".decl table{width:100%;border-collapse:collapse}"
                            ".decl td,.decl th{border:1px solid #333;padding:6px;font-size:13px}"
                            ".decl h2{text-align:center}")
                for p in lista:
                    partes.append("<div class='decl'>" + corpo_html(html_declaracao(p)) + "</div>")
            return ("<html><head><meta charset='utf-8'><title>Impressão</title>"
                    f"<style>{estilos}</style></head><body onload='window.print()'>{''.join(partes)}</body></html>")

        st.caption("Quando o cliente finaliza o pedido, o endereço dele já aparece aqui sozinho. "
                   "Confira, complete se faltar algo e imprima a etiqueta para colar no pacote.")
        if not LOJA.get("fiscal_endereco"):
            st.warning("Preencha seu endereço em Nota fiscal > Meus dados fiscais. Ele sai como remetente.")
        if pedidos.empty:
            st.info("Ainda não há pedidos.")
        else:
            prontos = pedidos[pedidos["status"].isin(["Novo", "Pago", "Em produção", "Enviado"])]
            so_prontos = st.toggle("Mostrar só pedidos para enviar", value=True, key="etq_prontos")
            lista = (prontos if so_prontos and len(prontos) else pedidos).iloc[::-1]
            opcoes = [f"{p['id_pedido']} · {p['nome']} · {p['status']}" for _, p in lista.iterrows()]
            id_sel = st.selectbox("Pedido (código e nome do cliente)", opcoes, key="etq_pedido").split(" · ")[0]
            ped = pedidos[pedidos["id_pedido"] == id_sel].iloc[0]
            esq, dir_ = st.columns([1, 1])
            with esq, st.form(f"form_etq_{id_sel}"):
                st.markdown("**📮 Endereço de entrega**")
                e_nome = st.text_input("Nome do destinatário", value=ped["nome"])
                c1, c2 = st.columns([1, 2])
                e_cep = c1.text_input("CEP", value=ped["ent_cep"])
                e_rua = c2.text_input("Rua / avenida", value=ped["ent_rua"])
                c3, c4 = st.columns([1, 2])
                e_num = c3.text_input("Número", value=ped["ent_numero"])
                e_comp = c4.text_input("Complemento (apto, bloco, referência)", value=ped["ent_complemento"])
                e_bai = st.text_input("Bairro", value=ped["ent_bairro"])
                c5, c6 = st.columns([3, 1])
                e_cid = c5.text_input("Cidade", value=ped["ent_cidade"])
                e_uf = c6.text_input("UF", value=ped["ent_uf"], max_chars=2)
                c7, c8 = st.columns(2)
                e_tel = c7.text_input("Telefone", value=ped["telefone"])
                e_peso = c8.text_input("Peso do pacote (kg)", value=ped["ent_peso"], placeholder="0,5")
                b1, b2 = st.columns(2)
                buscar = b1.form_submit_button("🔎 Completar pelo CEP", use_container_width=True)
                salvar = b2.form_submit_button("💾 Salvar endereço", type="primary", use_container_width=True)
            if buscar or salvar:
                dados = {"nome": e_nome.strip(), "ent_cep": e_cep.strip(), "ent_rua": e_rua.strip(),
                         "ent_numero": e_num.strip(), "ent_complemento": e_comp.strip(),
                         "ent_bairro": e_bai.strip(), "ent_cidade": e_cid.strip(),
                         "ent_uf": e_uf.strip().upper(), "telefone": e_tel.strip(), "ent_peso": e_peso.strip()}
                ok = True
                if buscar:
                    achado = consultar_cep(e_cep)
                    if achado:
                        dados.update(ent_cep=achado.get("cep", dados["ent_cep"]),
                                     ent_rua=achado.get("logradouro") or dados["ent_rua"],
                                     ent_bairro=achado.get("bairro") or dados["ent_bairro"],
                                     ent_cidade=achado.get("localidade") or dados["ent_cidade"],
                                     ent_uf=achado.get("uf") or dados["ent_uf"])
                    else:
                        ok = False
                        st.error("CEP não encontrado. Confira os 8 números.")
                if ok:
                    dados["endereco_entrega"] = (
                        ", ".join(x for x in [dados["ent_rua"], dados["ent_numero"], dados["ent_complemento"],
                                              dados["ent_bairro"]] if x)
                        + f" - {dados['ent_cidade']}/{dados['ent_uf']} CEP {dados['ent_cep']}")
                    alvo = pedidos["id_pedido"] == id_sel
                    for campo, valor in dados.items():
                        pedidos.loc[alvo, campo] = valor
                    gravar_csv(ARQ_PEDIDOS, pedidos)
                    # Guarda também no cadastro do cliente
                    clientes = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
                    alvo_c = clientes["telefone"].astype(str) == str(ped["telefone"])
                    if alvo_c.any():
                        clientes.loc[alvo_c, "cep"] = dados["ent_cep"]
                        clientes.loc[alvo_c, "endereco"] = ", ".join(
                            x for x in [dados["ent_rua"], dados["ent_numero"], dados["ent_complemento"],
                                        dados["ent_bairro"]] if x)
                        clientes.loc[alvo_c, "cidade"] = dados["ent_cidade"]
                        clientes.loc[alvo_c, "uf"] = dados["ent_uf"]
                        gravar_csv(ARQ_CLIENTES, clientes)
                    st.rerun()

            with dir_:
                st.markdown("**🏷️ Prévia da etiqueta**")
                faltando = [n for n, c in [("CEP", "ent_cep"), ("rua", "ent_rua"), ("número", "ent_numero"),
                                           ("bairro", "ent_bairro"), ("cidade", "ent_cidade"), ("UF", "ent_uf")]
                            if not str(ped[c]).strip()]
                if faltando:
                    st.warning("Falta preencher: " + ", ".join(faltando) + ".")
                components.html(html_etiquetas([ped], imprimir=False), height=520, scrolling=True)
                st.markdown("**O que imprimir?**")
                ck1, ck2 = st.columns(2)
                com_etq = ck1.checkbox("🏷️ Etiqueta", value=True, key="imp_etq")
                com_decl = ck2.checkbox("📦 Declaração de conteúdo", value=False, key="imp_decl")
                st.download_button("🖨️ Imprimir o que está marcado",
                                   pacote_impressao([ped], com_etq, com_decl).encode("utf-8"),
                                   f"etiqueta_{id_sel}.html", "text/html", type="primary",
                                   use_container_width=True)
                st.caption("Abra o arquivo baixado: a tela de impressão abre sozinha.")
                texto = (f"{ped['nome']}\n{ped['ent_rua']}, {ped['ent_numero'] or 'S/N'}"
                         + (f" - {ped['ent_complemento']}" if ped["ent_complemento"] else "")
                         + f"\n{ped['ent_bairro']}\n{ped['ent_cidade']} / {ped['ent_uf']}\nCEP {ped['ent_cep']}")
                st.markdown("**📋 Endereço para copiar e colar**")
                st.code(texto, language=None)

            st.divider()
            st.markdown("**🖨️ Imprimir várias etiquetas de uma vez (4 por folha)**")
            ids_lote = st.multiselect("Escolha os pedidos", prontos["id_pedido"].tolist()[::-1],
                                      default=prontos["id_pedido"].tolist()[::-1], key="etq_lote")
            if ids_lote:
                lote = [p for _, p in pedidos[pedidos["id_pedido"].isin(ids_lote)].iterrows()]
                lk1, lk2 = st.columns(2)
                lote_etq = lk1.checkbox("🏷️ Etiquetas", value=True, key="lote_etq")
                lote_decl = lk2.checkbox("📦 Declarações de conteúdo", value=False, key="lote_decl")
                st.download_button(f"🖨️ Imprimir {len(lote)} pedido(s)",
                                   pacote_impressao(lote, lote_etq, lote_decl).encode("utf-8"),
                                   "etiquetas.html", "text/html", type="primary")
    # ---------------------------------------------------------- GALERIA DE ARTES PRONTAS
    elif secao == "🎨 Galeria de artes":
        st.caption("Cadastre suas artes prontas. O cliente vê todas numa grade quando abre o produto, "
                   "clica na que gostar e já vê o exemplo de como fica.")
        cats = sorted(df_produtos["categoria"].unique().tolist())
        with st.form("form_nova_arte", clear_on_submit=True):
            c1, c2 = st.columns(2)
            g_nome = c1.text_input("Nome da arte (ex.: Flores, Time, Dia dos Pais)")
            g_cats = c2.multiselect("Mostrar em quais categorias (vazio = em todas)", cats)
            g_arqs = st.file_uploader("Imagens (pode enviar várias de uma vez, até 2 MB cada)",
                                      type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
            if st.form_submit_button("➕ Adicionar à galeria", type="primary"):
                novos = 0
                for n, f in enumerate(g_arqs or []):
                    if f.size > 2 * 1024 * 1024:
                        continue
                    base = g_nome.strip() or f.name.rsplit(".", 1)[0]
                    nome = f"{base} {n + 1}" if g_nome.strip() and len(g_arqs) > 1 else base
                    ARTES_PRONTAS.append({"id": uuid.uuid4().hex[:8], "nome": nome, "categorias": g_cats,
                                          "imagem": f"data:{f.type or 'image/png'};base64,"
                                                    + base64.b64encode(f.getvalue()).decode()})
                    novos += 1
                if novos:
                    gravar_json(ARQ_ARTES_PRONTAS, ARTES_PRONTAS)
                    st.rerun()
                else:
                    st.error("Envie pelo menos uma imagem de até 2 MB.")
        filtro_g = st.selectbox("Ver artes de", ["Todas"] + cats, key="gal_filtro")
        mostrar = [a for a in ARTES_PRONTAS if filtro_g == "Todas" or not a.get("categorias")
                   or filtro_g in a["categorias"]]
        st.caption(f"{len(mostrar)} arte(s).")
        for ini in range(0, len(mostrar), 5):
            for c, a in zip(st.columns(5), mostrar[ini:ini + 5]):
                with c, st.container(border=True):
                    st.markdown(f"<img src='{a['imagem']}' style='width:100%;aspect-ratio:1/1;object-fit:cover;"
                                "border-radius:8px;'>", unsafe_allow_html=True)
                    st.markdown(f"**{a['nome']}**")
                    st.caption(", ".join(a.get("categorias") or []) or "Todas as categorias")
                    if st.button("🗑️ Excluir", key=f"gal_del_{a['id']}", use_container_width=True):
                        ARTES_PRONTAS[:] = [x for x in ARTES_PRONTAS if x["id"] != a["id"]]
                        gravar_json(ARQ_ARTES_PRONTAS, ARTES_PRONTAS)
                        st.rerun()
    # ---------------------------------------------------------- ARTES PARA IMPRIMIR
    elif secao == "🖨️ Artes":
        def html_arte(src, a, larg, alt_cm, encaixe, escala, espelhar, borda, copias, papel) -> str:
            """Folha para imprimir a arte no tamanho exato, em centímetros."""
            e = lambda v: html.escape(str(v or ""))
            ajuste = "contain" if encaixe.startswith("Caber") else "cover"
            mover = f"translate({float(a.get('dx', 0) or 0) / 2:.0f}%, {float(a.get('dy', 0) or 0) / 2:.0f}%)"
            giro = f"transform: {'scaleX(-1) ' if espelhar else ''}{mover};"
            linha = "1px dashed #555" if borda else "none"
            fonte = CSS_FONTES.get(a.get("fonte") or "Padrão", "Arial, sans-serif")
            alt_img = escala * (0.75 if a.get("texto") else 1)
            foto = (f"<img src='{src}' style='width:{escala}%;height:{alt_img}%;object-fit:{ajuste};'>" if src else "")
            tam_txt = max(0.6, min(alt_cm * 0.2, 4.0))
            texto = (f"<div class='txt' style='font-family:{fonte};color:{e(a.get('cor_texto') or '#000')};"
                     f"font-size:{tam_txt:.2f}cm;'>{e(a.get('texto'))}</div>" if a.get("texto") else "")
            caixa = (f"<div class='area' style='width:{larg}cm;height:{alt_cm}cm;border:{linha};'>"
                     f"<div class='miolo' style='{giro}'>{foto}{texto}</div></div>")
            return f"""<html><head><meta charset='utf-8'><title>Arte</title><style>
@page {{ size: {papel}; margin: 8mm; }}
body {{ margin: 0; font-family: Arial; }}
.grade {{ display: flex; flex-wrap: wrap; gap: 4mm; }}
.area {{ box-sizing: border-box; overflow: hidden; page-break-inside: avoid; background: #fff; }}
.miolo {{ width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.txt {{ text-align: center; line-height: 1.1; padding: 1mm; word-break: break-word; }}
.info {{ font-size: 10px; color: #444; margin-bottom: 3mm; }}
</style></head><body onload='window.print()'>
<div class='info'>{e(a.get('item'))} · área {larg} x {alt_cm} cm</div>
<div class='grade'>{caixa * int(copias)}</div></body></html>"""

        pedidos = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        com_arte = pedidos[pedidos["personalizacao"].astype(str).str.len() > 2]
        st.caption("Aqui ficam as fotos, artes prontas e textos que os clientes escolheram. "
                   "Escolha o molde, ajuste o tamanho em centímetros e imprima direto na sua impressora.")
        if com_arte.empty:
            st.info("Nenhum pedido com personalização ainda.")
        else:
            opcoes = [f"{p['id_pedido']} · {p['nome']} · {p['status']}" for _, p in com_arte.iloc[::-1].iterrows()]
            id_sel = st.selectbox("Pedido", opcoes, key="arte_pedido").split(" · ")[0]
            ped = pedidos[pedidos["id_pedido"] == id_sel].iloc[0]
            try:
                artes = json.loads(ped["personalizacao"])
            except Exception:
                artes = []
            st.markdown(f"**Cliente:** {ped['nome']} · {ped['telefone']}")
            for n, a in enumerate(artes):
                with st.container(border=True):
                    st.markdown(f"#### {a.get('quantidade', 1)}x {a.get('item', '')}")
                    col_a, col_b, col_c = st.columns([1, 1.2, 1.3])
                    tem_foto = bool(a.get("arquivo")) and os.path.exists(a["arquivo"])
                    bruto = b""
                    with col_a:
                        if tem_foto:
                            st.image(a["arquivo"], caption=a.get("arte_nome") or "Arte", use_container_width=True)
                            with open(a["arquivo"], "rb") as f:
                                bruto = f.read()
                            st.download_button("⬇️ Baixar arquivo original", bruto, os.path.basename(a["arquivo"]),
                                               key=f"orig_{id_sel}_{n}")
                        elif a.get("arquivo"):
                            st.warning("A foto não foi encontrada (o app pode ter reiniciado). "
                                       "Restaure o backup ou peça de novo ao cliente.")
                        else:
                            st.caption("Sem foto, só texto.")
                        if a.get("texto"):
                            st.markdown(f"**Texto:** {a['texto']}  \n**Letra:** {a.get('fonte') or 'Padrão'} · "
                                        f"**Cor:** {a.get('cor_texto') or '#000000'}")
                        if a.get("obs"):
                            st.markdown(f"**Pedido do cliente:** {a['obs']}")
                    with col_b:
                        molde = st.selectbox("Molde", list(MOLDES_IMPRESSAO.keys()), key=f"molde_{id_sel}_{n}")
                        lw, lh = MOLDES_IMPRESSAO[molde]
                        m1, m2 = st.columns(2)
                        larg = m1.number_input("Largura (cm)", 1.0, 60.0, float(lw), 0.5, key=f"larg_{id_sel}_{n}_{molde}")
                        alt_cm = m2.number_input("Altura (cm)", 1.0, 60.0, float(lh), 0.5, key=f"alt_{id_sel}_{n}_{molde}")
                        encaixe = st.radio("Encaixe da foto", ["Caber inteira", "Preencher tudo (corta as bordas)"],
                                           key=f"enc_{id_sel}_{n}")
                        escala = st.slider("Tamanho da arte dentro da área (%)", 30, 100,
                                           int(a.get("escala", 100) or 100), 5, key=f"esc_{id_sel}_{n}")
                        p1, p2 = st.columns(2)
                        espelhar = p1.checkbox("Espelhar (sublimação)", key=f"esp_{id_sel}_{n}")
                        borda = p2.checkbox("Linha de corte", value=True, key=f"bor_{id_sel}_{n}")
                        p3, p4 = st.columns(2)
                        copias = p3.number_input("Cópias", 1, 50, int(a.get("quantidade", 1) or 1), key=f"cop_{id_sel}_{n}")
                        papel = p4.selectbox("Papel", ["A4", "A3", "Carta"], key=f"pap_{id_sel}_{n}")
                    src = ""
                    if tem_foto:
                        ext = os.path.splitext(a["arquivo"])[1].lower().strip(".")
                        mime = "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
                        src = f"data:{mime};base64," + base64.b64encode(bruto).decode()
                    folha = html_arte(src, a, larg, alt_cm, encaixe, escala, espelhar, borda, copias, papel)
                    with col_c:
                        st.markdown("**Prévia**")
                        components.html(folha.replace("onload='window.print()'", ""), height=380, scrolling=True)
                        st.download_button("🖨️ Imprimir arte", folha.encode("utf-8"), f"arte_{id_sel}_{n + 1}.html",
                                           "text/html", type="primary", use_container_width=True, key=f"imp_{id_sel}_{n}")
                        st.caption("Na janela de impressão, deixe a escala em 100% (tamanho real).")
    # ---------------------------------------------------------- ESTOQUE, FORNECEDORES E COMPRAS
    elif secao == "🏭 Estoque e compras":
        margem = int(LOJA.get("estoque_margem_dias", 7))
        forn = ler_csv(ARQ_FORNECEDORES, COL_FORN)
        est = ler_csv(ARQ_ESTOQUE, COL_EST)
        comp = ler_csv(ARQ_COMPRAS, COL_COMP)
        mov = ler_csv(ARQ_MOVIMENTOS, COL_MOV)
        for c in ["quantidade", "minimo", "custo_unit", "por_unidade"]:
            est[c] = pd.to_numeric(est[c], errors="coerce").fillna(1.0 if c == "por_unidade" else 0.0)
        for c in ["quantidade", "custo_unit", "total"]:
            comp[c] = pd.to_numeric(comp[c], errors="coerce").fillna(0.0)
        an = analise_estoque(margem)
        repor = an[an["repor"] == True] if len(an) else an
        nomes_forn = [n for n in forn["nome"].tolist() if n]

        def entrar_estoque(material: str, qtd: float, custo: float, fornecedor: str, ref: str):
            base = ler_csv(ARQ_ESTOQUE, COL_EST)
            base["quantidade"] = pd.to_numeric(base["quantidade"], errors="coerce").fillna(0.0)
            alvo = base["material"] == material
            if alvo.any():
                base.loc[alvo, "quantidade"] = base.loc[alvo, "quantidade"] + qtd
                if custo > 0:
                    base.loc[alvo, "custo_unit"] = custo
            else:
                linha = {c: "" for c in COL_EST}
                linha.update(material=material, quantidade=qtd, custo_unit=custo, fornecedor=fornecedor,
                             unidade="un", minimo=0, por_unidade=1)
                base = pd.concat([base, pd.DataFrame([linha])], ignore_index=True)
            gravar_csv(ARQ_ESTOQUE, base)
            registrar_movimento(material, "Entrada (compra)", qtd, ref)

        k = st.columns(4)
        k[0].markdown(cartao_kpi("Precisa repor", str(len(repor)), GRAD["rosa"]), unsafe_allow_html=True)
        k[1].markdown(cartao_kpi("Materiais", str(len(est)), GRAD["azul"]), unsafe_allow_html=True)
        k[2].markdown(cartao_kpi("Valor em estoque", brl(float((est["quantidade"] * est["custo_unit"]).sum())),
                                 GRAD["agua"]), unsafe_allow_html=True)
        k[3].markdown(cartao_kpi("Compras em aberto",
                                 str(int((~comp["status"].isin(["Recebida", "Cancelada"])).sum())), GRAD["roxo"]),
                      unsafe_allow_html=True)
        st.write("")
        t_rep, t_est, t_forn, t_comp, t_preco, t_mov = st.tabs(
            ["⚠️ Repor agora", "📦 Meu estoque", "🏭 Fornecedores", "🛍️ Compras", "📈 Preços", "📜 Movimentações"])

        with t_rep:
            st.caption("O painel olha quanto saiu nos últimos 30 dias, calcula quantos dias o estoque ainda dura "
                       "e avisa antes de acabar, contando o prazo de entrega do fornecedor.")
            c1, c2 = st.columns([3, 1])
            nova_margem = c1.slider("Avisar com quantos dias de folga (além do prazo do fornecedor)", 1, 30, margem)
            if c2.button("💾 Salvar folga", key="salvar_margem"):
                LOJA["estoque_margem_dias"] = int(nova_margem)
                gravar_loja(LOJA)
                st.rerun()
            if est.empty:
                st.info("Cadastre seus materiais na aba Meu estoque para o controle automático começar.")
            elif repor.empty:
                st.success("✅ Tudo em dia. Nenhum material precisa de reposição agora.")
            for n, (_, r) in enumerate(repor.iterrows()):
                with st.container(border=True):
                    a1, a2, a3 = st.columns([3, 1.4, 1.6])
                    d = r["dias_restantes"]
                    dura = f"dura cerca de {d:.0f} dia(s)" if pd.notna(d) else "abaixo do mínimo"
                    a1.markdown(f"**{r['material']}** · tem {r['quantidade']:g} {r['unidade'] or 'un'} · **{dura}**")
                    a1.caption(f"Gasta {r['consumo_dia']:.1f} por dia · entrega do fornecedor: {r['prazo_forn']} dias"
                               + (f" · peça até {r['data_limite']}" if r["data_limite"] else " · peça hoje"))
                    a2.metric("Comprar", f"{r['comprar']:g} {r['unidade'] or 'un'}")
                    f = forn[forn["nome"] == r["fornecedor"]]
                    if len(f):
                        fr = f.iloc[0]
                        msg = (f"Olá {fr['contato'] or fr['nome']}! Quero fazer um pedido de {r['comprar']:g} "
                               f"{r['unidade'] or 'unidades'} de {r['material']}. Pode me passar o preço e o prazo?")
                        if fr["whatsapp"]:
                            a3.link_button("💬 Pedir no WhatsApp",
                                           f"https://wa.me/{numero_wpp(fr['whatsapp'])}?text={urllib.parse.quote(msg)}",
                                           type="primary", use_container_width=True)
                        if fr["site"]:
                            a3.link_button("🌐 Site do fornecedor", fr["site"], use_container_width=True)
                    else:
                        a3.caption("Escolha o fornecedor deste material na aba Meu estoque.")

        with t_est:
            st.caption("Em 'Usado em', escreva as categorias ou produtos que gastam este material, separados "
                       "por vírgula (ex.: Canecas, Copos). Em 'Gasta por peça', quanto sai a cada produto vendido.")
            est_edit = st.data_editor(
                est[COL_EST], num_rows="dynamic", use_container_width=True, key="editor_estoque", height=360,
                column_config={
                    "material": st.column_config.TextColumn("Material", required=True),
                    "categoria": st.column_config.TextColumn("Tipo (ex.: caneca branca, tinta)"),
                    "unidade": st.column_config.TextColumn("Unidade (un, folha, ml)"),
                    "quantidade": st.column_config.NumberColumn("Tenho", step=1.0, format="%g"),
                    "minimo": st.column_config.NumberColumn("Mínimo", min_value=0.0, step=1.0, format="%g"),
                    "custo_unit": st.column_config.NumberColumn("Custo unit. (R$)", min_value=0.0, format="%.2f"),
                    "fornecedor": st.column_config.SelectboxColumn("Fornecedor", options=nomes_forn or [""]),
                    "usado_em": st.column_config.TextColumn("Usado em"),
                    "por_unidade": st.column_config.NumberColumn("Gasta por peça", min_value=0.0, step=0.5, format="%g"),
                    "obs": st.column_config.TextColumn("Observações", width="large"),
                })
            if st.button("💾 Salvar estoque", type="primary", key="salvar_estoque"):
                gravar_csv(ARQ_ESTOQUE, est_edit)
                st.rerun()
            st.markdown("**Lançar entrada ou saída rápida**")
            with st.form("mov_rapido", clear_on_submit=True):
                m1, m2, m3, m4 = st.columns([2, 1, 1, 1])
                mat = m1.selectbox("Material", est["material"].tolist())
                tipo = m2.selectbox("Tipo", ["Entrada", "Saída"])
                qtd = m3.number_input("Quantidade", min_value=0.0, value=1.0, step=1.0)
                lancar = m4.form_submit_button("Lançar", type="primary")
            if lancar and mat:
                base = ler_csv(ARQ_ESTOQUE, COL_EST)
                base["quantidade"] = pd.to_numeric(base["quantidade"], errors="coerce").fillna(0.0)
                sinal = 1 if tipo == "Entrada" else -1
                base.loc[base["material"] == mat, "quantidade"] += sinal * qtd
                gravar_csv(ARQ_ESTOQUE, base)
                registrar_movimento(mat, f"{tipo} (manual)", qtd)
                st.rerun()
        with t_forn:
            forn["prazo_dias"] = pd.to_numeric(forn["prazo_dias"], errors="coerce").fillna(7).astype(int)
            forn_edit = st.data_editor(
                forn, num_rows="dynamic", use_container_width=True, key="editor_forn", height=300,
                column_config={
                    "nome": st.column_config.TextColumn("Fornecedor", required=True),
                    "contato": st.column_config.TextColumn("Pessoa de contato"),
                    "whatsapp": st.column_config.TextColumn("WhatsApp (DDD + número)"),
                    "site": st.column_config.LinkColumn("Site"),
                    "email": st.column_config.TextColumn("E-mail"),
                    "o_que_vende": st.column_config.TextColumn("O que vende"),
                    "prazo_dias": st.column_config.NumberColumn("Prazo de entrega (dias)", min_value=0, step=1),
                    "pedido_minimo": st.column_config.TextColumn("Pedido mínimo"),
                    "obs": st.column_config.TextColumn("Observações", width="large"),
                })
            if st.button("💾 Salvar fornecedores", type="primary", key="salvar_forn"):
                gravar_csv(ARQ_FORNECEDORES, forn_edit)
                st.rerun()
            for i0 in range(0, len(forn), 3):
                for c, (_, fr) in zip(st.columns(3), forn.iloc[i0:i0 + 3].iterrows()):
                    with c, st.container(border=True):
                        st.markdown(f"**{fr['nome']}**  \n{fr['o_que_vende']}")
                        st.caption(f"Entrega em {fr['prazo_dias']} dias" + (f" · mínimo {fr['pedido_minimo']}"
                                                                           if fr["pedido_minimo"] else ""))
                        if fr["whatsapp"]:
                            st.link_button("💬 WhatsApp", f"https://wa.me/{numero_wpp(fr['whatsapp'])}",
                                           use_container_width=True)
                        if fr["site"]:
                            st.link_button("🌐 Site", fr["site"], use_container_width=True)
                        if "@" in str(fr["email"]):
                            st.link_button("✉️ E-mail", f"mailto:{fr['email']}", use_container_width=True)

        with t_comp:
            st.caption("Quando uma compra muda para Recebida, a quantidade entra sozinha no estoque.")
            with st.form("nova_compra", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                n_forn = c1.selectbox("Fornecedor", nomes_forn or [""])
                n_mat = c2.selectbox("Material", est["material"].tolist() + ["(novo material)"])
                n_novo = c3.text_input("Nome do material novo")
                c4, c5, c6, c7 = st.columns(4)
                n_qtd = c4.number_input("Quantidade", min_value=0.0, value=1.0, step=1.0)
                n_custo = c5.number_input("Custo unit. (R$)", min_value=0.0, value=0.0, step=0.5)
                n_st = c6.selectbox("Situação", STATUS_COMPRA, index=1)
                n_prev = c7.text_input("Previsão de chegada", placeholder="25/11/2026")
                n_obs = st.text_input("Observações")
                if st.form_submit_button("➕ Registrar compra", type="primary"):
                    material = n_novo.strip() if n_mat == "(novo material)" else n_mat
                    if not material:
                        st.error("Digite o nome do material.")
                    else:
                        id_c = f"COMP-{len(comp) + 1:04d}"
                        nova = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y"), "id_compra": id_c,
                                              "fornecedor": n_forn, "material": material, "quantidade": n_qtd,
                                              "custo_unit": n_custo, "total": round(n_qtd * n_custo, 2),
                                              "status": n_st, "previsao": n_prev, "obs": n_obs}])
                        gravar_csv(ARQ_COMPRAS, pd.concat([comp, nova], ignore_index=True))
                        if n_custo > 0:
                            registrar_preco(material, n_forn, n_custo, f"Compra {id_c}")
                        if n_st == "Recebida":
                            entrar_estoque(material, n_qtd, n_custo, n_forn, id_c)
                        st.rerun()
            st.metric("Total gasto em compras recebidas", brl(float(comp[comp["status"] == "Recebida"]["total"].sum())))
            antes = dict(zip(comp["id_compra"], comp["status"]))
            comp_edit = st.data_editor(
                comp.iloc[::-1], use_container_width=True, key="editor_compras", num_rows="fixed", height=320,
                column_config={
                    "data": st.column_config.TextColumn("Data", disabled=True),
                    "id_compra": st.column_config.TextColumn("Nº", disabled=True),
                    "fornecedor": st.column_config.TextColumn("Fornecedor", disabled=True),
                    "material": st.column_config.TextColumn("Material", disabled=True),
                    "quantidade": st.column_config.NumberColumn("Qtd", disabled=True, format="%g"),
                    "custo_unit": st.column_config.NumberColumn("Custo unit.", format="%.2f"),
                    "total": st.column_config.NumberColumn("Total (R$)", disabled=True, format="%.2f"),
                    "status": st.column_config.SelectboxColumn("Situação", options=STATUS_COMPRA),
                    "previsao": st.column_config.TextColumn("Previsão"),
                    "obs": st.column_config.TextColumn("Observações", width="large"),
                })
            if st.button("💾 Salvar compras", type="primary", key="salvar_compras"):
                completo = comp.copy()
                for _, linha in comp_edit.iterrows():
                    alvo = completo["id_compra"] == linha["id_compra"]
                    for campo in ["custo_unit", "status", "previsao", "obs"]:
                        completo.loc[alvo, campo] = linha[campo]
                    completo.loc[alvo, "total"] = round(float(linha["quantidade"]) * float(linha["custo_unit"]), 2)
                    if linha["status"] == "Recebida" and antes.get(linha["id_compra"]) != "Recebida":
                        entrar_estoque(linha["material"], float(linha["quantidade"]), float(linha["custo_unit"]),
                                       linha["fornecedor"], linha["id_compra"])
                gravar_csv(ARQ_COMPRAS, completo)
                st.rerun()

        with t_mov:
            if mov.empty:
                st.info("As entradas e saídas aparecem aqui sozinhas, a cada venda e a cada compra recebida.")
            else:
                st.dataframe(mov.iloc[::-1], use_container_width=True, hide_index=True, height=400)
        with t_preco:
            st.caption("Anote cada preço que o fornecedor te passar. As compras com custo entram aqui sozinhas.")
            with st.form("novo_preco", clear_on_submit=True):
                p1, p2, p3, p4, p5 = st.columns([2, 2, 1, 1, 1])
                pr_mat = p1.selectbox("Material", est["material"].tolist() or [""])
                pr_forn = p2.selectbox("Fornecedor", nomes_forn or [""])
                pr_val = p3.number_input("Preço unit. (R$)", min_value=0.0, step=0.5)
                pr_data = p4.date_input("Data", value=datetime.now(), format="DD/MM/YYYY")
                anotar = p5.form_submit_button("➕ Anotar", type="primary")
            if anotar and pr_mat and pr_val > 0:
                registrar_preco(pr_mat, pr_forn, pr_val, "Cotação", pr_data.strftime("%Y-%m-%d"))
                st.rerun()
            precos = ler_csv(ARQ_PRECOS, COL_PRECO)
            precos["preco"] = pd.to_numeric(precos["preco"], errors="coerce")
            precos["dt"] = pd.to_datetime(precos["data"], errors="coerce")
            precos = precos.dropna(subset=["preco", "dt"])
            if precos.empty:
                st.info("Anote os primeiros preços para o gráfico aparecer.")
            else:
                cat_map = dict(zip(est["material"], est["categoria"].astype(str)))
                precos["categoria"] = precos["material"].map(cat_map).fillna("").replace("", "Sem categoria")
                cats_p = sorted(precos["categoria"].unique().tolist())
                st.markdown("#### 📊 Visão geral de todos os preços")
                filtro_cat = st.multiselect("Categorias", cats_p, default=cats_p, key="preco_cats")
                base_p = precos[precos["categoria"].isin(filtro_cat)] if filtro_cat else precos
                linhas_g = []
                for mat, g in base_p.sort_values("dt").groupby("material"):
                    ult = float(g["preco"].iloc[-1])
                    ant = float(g["preco"].iloc[-2]) if len(g) > 1 else ult
                    v = (ult - ant) / ant * 100 if ant else 0.0
                    rec = comp[(comp["material"] == mat) & (comp["status"] == "Recebida")]
                    q = float(rec["quantidade"].sum())
                    pago = float(rec["total"].sum()) / q if q > 0 else float(g["preco"].mean())
                    por_forn = g.groupby("fornecedor")["preco"].mean()
                    linhas_g.append({
                        "categoria": g["categoria"].iloc[0], "material": mat, "preco_medio": round(pago, 2),
                        "ultimo": round(ult, 2), "variacao": round(v, 1),
                        "tendencia": "📈 Subindo" if v > 1 else "📉 Baixando" if v < -1 else "➡️ Estável",
                        "mais_barato": por_forn.idxmin() if len(por_forn) else "",
                        "fornecedores": int(g["fornecedor"].nunique()), "precos": int(len(g))})
                geral = pd.DataFrame(linhas_g)
                if len(geral):
                    kg = st.columns(4)
                    kg[0].markdown(cartao_kpi("Materiais acompanhados", str(len(geral)), GRAD["roxo"]), unsafe_allow_html=True)
                    kg[1].markdown(cartao_kpi("Subindo", str(int((geral["variacao"] > 1).sum())), GRAD["rosa"]),
                                   unsafe_allow_html=True)
                    kg[2].markdown(cartao_kpi("Baixando", str(int((geral["variacao"] < -1).sum())), GRAD["agua"]),
                                   unsafe_allow_html=True)
                    kg[3].markdown(cartao_kpi("Categorias", str(geral["categoria"].nunique()), GRAD["azul"]),
                                   unsafe_allow_html=True)
                    st.write("")
                    st.dataframe(geral.sort_values(["categoria", "material"]), hide_index=True, use_container_width=True,
                                 column_config={
                                     "categoria": "Categoria", "material": "Material",
                                     "preco_medio": st.column_config.NumberColumn("Preço médio pago (R$)", format="%.2f"),
                                     "ultimo": st.column_config.NumberColumn("Último preço (R$)", format="%.2f"),
                                     "variacao": st.column_config.NumberColumn("Variação (%)", format="%+.1f"),
                                     "tendencia": "Tendência", "mais_barato": "Fornecedor mais barato",
                                     "fornecedores": "Fornecedores", "precos": "Preços anotados"})
                    g1, g2 = st.columns([1, 1.6])
                    with g1, st.container(border=True):
                        st.markdown("**Quanto cada preço subiu ou baixou (%)**")
                        grafico(alt.Chart(geral).mark_bar(cornerRadius=4).encode(
                            y=alt.Y("material:N", title=None, sort="-x"),
                            x=alt.X("variacao:Q", title="% em relação ao preço anterior"),
                            color=alt.condition(alt.datum.variacao > 0, alt.value("#ef4444"), alt.value("#10b981")),
                            tooltip=["categoria", "material", alt.Tooltip("variacao:Q", title="Variação %", format="+.1f")]
                        ).properties(height=max(160, 28 * len(geral))))
                    with g2, st.container(border=True):
                        st.markdown("**Preço de cada material ao longo do tempo**")
                        grafico(alt.Chart(base_p).mark_line(point=True, strokeWidth=2).encode(
                            x=alt.X("dt:T", title=None, axis=alt.Axis(format="%d/%m")),
                            y=alt.Y("preco:Q", title="R$", scale=alt.Scale(zero=False)),
                            color=alt.Color("fornecedor:N", title=None, legend=alt.Legend(orient="top")),
                            tooltip=["material", "fornecedor", alt.Tooltip("dt:T", format="%d/%m/%Y"),
                                     alt.Tooltip("preco:Q", format=".2f")]
                        ).properties(width=200, height=130).facet(facet=alt.Facet("material:N", title=None), columns=3
                        ).resolve_scale(y="independent"))
                st.divider()
                st.markdown("#### 🔎 Detalhe de um material")
                mat_sel = st.selectbox("Ver preços de", sorted(precos["material"].unique().tolist()), key="preco_mat")
                dados = precos[precos["material"] == mat_sel].sort_values("dt")
                media = float(dados["preco"].mean())
                ultimo = float(dados["preco"].iloc[-1])
                anterior = float(dados["preco"].iloc[-2]) if len(dados) > 1 else ultimo
                var = (ultimo - anterior) / anterior * 100 if anterior else 0.0
                tendencia = "📈 Subindo" if var > 1 else "📉 Baixando" if var < -1 else "➡️ Estável"
                menor = dados.loc[dados["preco"].idxmin()]
                recebidas = comp[(comp["material"] == mat_sel) & (comp["status"] == "Recebida")]
                pago_medio = (float(recebidas["total"].sum()) / float(recebidas["quantidade"].sum())
                              if float(recebidas["quantidade"].sum()) > 0 else media)
                m = st.columns(4)
                m[0].metric("Preço médio que você paga", brl(pago_medio))
                m[1].metric("Último preço", brl(ultimo), f"{var:+.1f}%", delta_color="inverse")
                m[2].metric("Menor preço", brl(float(menor["preco"])), menor["fornecedor"] or "-", delta_color="off")
                m[3].metric("Tendência", tendencia)
                with st.container(border=True):
                    st.markdown(f"**Preço de {mat_sel} ao longo do tempo** (linha vermelha = média)")
                    linhas = alt.Chart(dados).mark_line(point=alt.OverlayMarkDef(size=70, filled=True), strokeWidth=3).encode(
                        x=alt.X("dt:T", title=None, axis=alt.Axis(format="%d/%m/%y")),
                        y=alt.Y("preco:Q", title="R$ por unidade", scale=alt.Scale(zero=False)),
                        color=alt.Color("fornecedor:N", title=None, legend=alt.Legend(orient="top"),
                                        scale=alt.Scale(range=["#7c3aed", "#06b6d4", "#ec4899", "#f59e0b", "#10b981"])),
                        tooltip=[alt.Tooltip("dt:T", title="Data", format="%d/%m/%Y"), "fornecedor",
                                 alt.Tooltip("preco:Q", title="Preço", format=".2f"), "origem"])
                    linha_media = alt.Chart(pd.DataFrame({"m": [media]})).mark_rule(
                        color="#ef4444", strokeDash=[6, 4], strokeWidth=2).encode(y="m:Q")
                    grafico((linhas + linha_media).properties(height=300))
                st.markdown("**Comparar fornecedores**")
                resumo = dados.groupby("fornecedor").agg(
                    preco_medio=("preco", "mean"), menor=("preco", "min"), maior=("preco", "max"),
                    ultimo=("preco", "last"), cotacoes=("preco", "count")).round(2).sort_values("preco_medio").reset_index()
                st.dataframe(resumo, hide_index=True, use_container_width=True, column_config={
                    "fornecedor": "Fornecedor",
                    "preco_medio": st.column_config.NumberColumn("Preço médio (R$)", format="%.2f"),
                    "menor": st.column_config.NumberColumn("Menor (R$)", format="%.2f"),
                    "maior": st.column_config.NumberColumn("Maior (R$)", format="%.2f"),
                    "ultimo": st.column_config.NumberColumn("Último (R$)", format="%.2f"),
                    "cotacoes": st.column_config.NumberColumn("Preços anotados")})
                if len(resumo) > 1:
                    st.success(f"💡 Mais barato em média: **{resumo.iloc[0]['fornecedor']}** "
                               f"({brl(float(resumo.iloc[0]['preco_medio']))} por unidade).")
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
                l_mini = c1.checkbox("Mostrar a fábrica ao vivo (janela flutuante) na loja",
                                     value=bool(LOJA.get("mostrar_mini", True)))
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
                    "mostrar_mini": l_mini,
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
st.markdown("""<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
.block-container { padding-left: 350px !important; max-width: 100% !important; }
.st-key-carrinho_fixo { position: fixed; top: 0; left: 0; bottom: 0; width: 330px; z-index: 999990;
    background: #ffffff; border-right: 1px solid #dbe1ea; padding: 16px 14px 60px; overflow-y: auto;
    box-shadow: 4px 0 16px rgba(15, 23, 42, .08); }
.st-key-carrinho_fixo [data-testid="stVerticalBlock"] { gap: .45rem; }
@media (max-width: 900px) {
    .st-key-carrinho_fixo { position: static; width: auto; box-shadow: none; border: 1px solid #dbe1ea;
        border-radius: 14px; }
    .block-container { padding-left: 1rem !important; } }
</style>""", unsafe_allow_html=True)


def mudar_qtd(indice: int, delta: int):
    """Aumenta ou diminui a quantidade de um item direto no carrinho."""
    item = st.session_state.carrinho[indice]
    nova = item["quantidade"] + delta
    if nova < 1:
        st.session_state.carrinho.pop(indice)
    else:
        total, brindes, econ = calcular_promocao(item["preco_unitario"], nova)
        item.update(quantidade=nova, unidades_gratis=brindes, desconto=econ, subtotal=total)
    st.session_state.link_whatsapp = None
    st.session_state.frete = None


with st.container(key="carrinho_fixo"):
    st.markdown("### 🛒 Seu Carrinho")
    if not st.session_state.carrinho:
        st.info("O carrinho está vazio. Escolha uma categoria para começar.")
    else:
        subtotal, qtd_total, pct_lote, valor_desc, total_geral = totais_carrinho()
        for i, item in enumerate(st.session_state.carrinho):
            reserva = imagem_reserva(item.get("categoria", ""), item["nome"])
            foto = html.escape(url_segura(item.get("imagem", ""), item.get("categoria", ""), item["nome"]), quote=True)
            brinde = (f"<br><span class='selo selo-ok'>+{item['unidades_gratis']} brinde</span>"
                      if item["unidades_gratis"] > 0 else "")
            if item.get("perso"):
                brinde += "<br><span class='selo selo-promo'>🎨 personalizado</span>"
            st.markdown(
                f"<div class='cartao-carrinho'><img src='{foto}' onerror=\"this.onerror=null;this.src='{reserva}';\">"
                f"<div><div class='nome'>{html.escape(item['nome'])}</div>"
                f"<div class='detalhe'>{item['quantidade']}x R$ {item['preco_unitario']:.2f}</div>"
                f"<div class='detalhe'><b>R$ {item['subtotal']:.2f}</b>{brinde}</div></div></div>",
                unsafe_allow_html=True)
            q1, q2, q3 = st.columns(3)
            q1.button("➖", key=f"menos_{i}_{item['id']}", on_click=mudar_qtd, args=(i, -1),
                      use_container_width=True, help="Diminuir")
            q2.button("➕", key=f"mais_{i}_{item['id']}", on_click=mudar_qtd, args=(i, 1),
                      use_container_width=True, help="Aumentar")
            q3.button("🗑️", key=f"del_{i}_{item['id']}", on_click=remover_do_carrinho, help="Tirar do carrinho",
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
            st.text_input("Número da casa", key="cli_numero")
            st.text_input("Complemento (opcional)", key="cli_comp", placeholder="apto, bloco, referência")
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
    if st.session_state.modo == "empresa":  # só limpa o carrinho quando troca de empresa para cliente
        st.session_state.update(modo="cliente", carrinho=[], frete=None)
    else:
        st.session_state.modo = "cliente"
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

# ----- Telinha flutuante: a equipe em miniatura trabalhando ao vivo (canto de baixo, à direita) -----
if LOJA.get("mostrar_mini", True):
    mini_cidade("loja")  # versão para o cliente: sem nomes, endereços nem valores
else:
    esconder_cidade()

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
    colunas = int(LOJA.get("loja_grade_colunas", 0)) or (5 if len(itens) > 8 else 4)
    for inicio in range(0, len(itens), colunas):
        cols = st.columns(colunas)
        for idx, item in enumerate(itens[inicio:inicio + colunas]):
            with cols[idx], st.container(border=True):
                # A foto inteira é clicável e abre os detalhes, igual ao botão
                clicou_foto = area_clicavel(f"prod_{item['id']}",
                                            html_imagem(item["imagem"], cat_nome, item["nome"], classe="cat-img",
                                                        zoom=False, dica="🔍 Ver detalhes"),
                                            dica="Ver detalhes")
                selo = "<span class='selo selo-promo'>PROMOÇÃO</span> " if item["em_promo"] else ""
                st.markdown(f"{selo}**{item['nome']}**  \nR$ {item['preco']:.2f}", unsafe_allow_html=True)
                clicou_botao = st.button("🔍 Ver detalhes", key=f"ver_{item['id']}", use_container_width=True,
                                         type="primary")
                if clicou_foto or clicou_botao:
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
                clicou_foto = area_clicavel(f"cat{inicio + idx}",
                                            html_imagem(destaque["imagem"], cat_nome, cat_nome, classe="cat-img",
                                                        zoom=False, dica="Ver modelos"),
                                            dica="Ver modelos")
                st.markdown(f"**{cat_nome}**  \nA partir de R$ {destaque['preco']:.2f}")
                if st.button(f"Ver {len(CATALOGO[cat_nome]['itens'])} modelos", key=f"btn_cat_{cat_nome}",
                             use_container_width=True) or clicou_foto:
                    registrar_clique("abriu_categoria", cat_nome)
                    ir_para("categoria", cat_nome)
                    st.rerun()
