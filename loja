import base64
import hmac
import html
import io
import json
import os
import random
import threading
import time
import urllib.parse
import urllib.request
import uuid
import zipfile
from contextlib import contextmanager
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Horário de Brasília em tudo (datas dos pedidos, expediente do chat...). O servidor fica em outro país.
os.environ["TZ"] = "America/Sao_Paulo"
if hasattr(time, "tzset"):
    time.tzset()

# ===============================================================
# CONFIGURAÇÕES FIXAS - o resto você muda pelo painel
# ===============================================================
# A senha do painel NÃO fica mais aqui: ela fica nos Secrets do Streamlit (SENHA_ADMIN).

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
ARQ_FOTOS_SEP = "dados_fotos_separadas.json"  # lista das fotos do separador (Gemini)
PASTA_FOTOS_SEP = "fotos_separadas"            # as fotos em si ficam no banco com este começo de nome
PASTA_REVISAR = "Revisar"                      # pasta das fotos em que o Gemini não teve certeza
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
ARQ_HIST = "dados_historico_pedidos.csv"
COL_HIST = ["data", "id_pedido", "status"]
ARQ_CHAT = "dados_chat.csv"  # conversas do chat da loja
COL_CHAT = ["data", "conversa", "quem", "nome", "texto"]
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
    "twitter": "",
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
    # Chat da loja e horário de atendimento (tudo editável no painel, em 💬 Chat ao vivo)
    "chat_ligado": True,
    "exp_inicio": "08:00",
    "exp_fim": "18:00",
    "exp_dias": [0, 1, 2, 3, 4],  # 0 = segunda ... 6 = domingo
    "chat_nome_atendente": "",
    "chat_boas_vindas": "Olá! 👋 Sou o assistente virtual da {loja}. Toque numa das perguntas abaixo ou escreva "
                        "a sua dúvida. Se precisar, eu chamo uma pessoa para falar com você.",
    "chat_resolveu": "Isso respondeu a sua dúvida? Se não, toque em 🙋 Falar com uma pessoa.",
    "chat_nao_entendi": "Hmm, não encontrei a resposta para isso. 🤔 Tente uma das perguntas abaixo ou toque em "
                        "🙋 Falar com uma pessoa.",
    "chat_chamando": "Já avisei a equipe! 🙌 Fique à vontade para escrever aqui, a resposta aparece nesta conversa.",
    "chat_offline": "No momento não tem ninguém online, mas a sua mensagem ficou guardada e respondemos assim "
                    "que possível. Se preferir, chame no WhatsApp pelo botão abaixo.",
    "chat_fora_expediente": "Agora estamos fora do horário de atendimento ({horario}). 🌙 Deixe a sua mensagem aqui "
                            "que respondemos assim que voltarmos. Enquanto isso, as perguntas rápidas podem ajudar!",
    "chat_perguntas": [
        {"pergunta": "⏰ Prazo de produção", "palavras": "prazo, demora, pronto, quantos dias, quando fica",
         "resposta": "Cada produto mostra o prazo de produção na página dele (normalmente 5 dias úteis). Depois de "
                     "pronto, o envio leva o prazo do frete do seu estado, que aparece quando você calcula o frete."},
        {"pergunta": "🚚 Frete e entrega", "palavras": "frete, entrega, envio, enviar, correios, cep, chega",
         "resposta": "Digite o seu CEP no carrinho e toque em Calcular frete: o valor e o prazo aparecem na hora. "
                     "{frete_gratis} Entregamos para todo o Brasil."},
        {"pergunta": "💳 Formas de pagamento", "palavras": "pagamento, pagar, pix, cartao, parcela, boleto",
         "resposta": "Aceitamos Pix (o QR code aparece no carrinho) e cartão pelo link de pagamento seguro. Depois de "
                     "pagar, mande o comprovante no WhatsApp junto com o número do pedido."},
        {"pergunta": "🎨 Como personalizar", "palavras": "personalizar, arte, foto, imagem, nome, logo, estampa",
         "resposta": "Abra o produto e toque em Ver detalhes. Lá você envia a sua foto (até 3 MB) ou escolhe uma arte "
                     "pronta, escreve um nome e arrasta para posicionar. A prévia mostra como fica antes de comprar."},
        {"pergunta": "📦 Acompanhar meu pedido", "palavras": "acompanhar, rastreio, rastrear, codigo, onde esta, status",
         "resposta": "No fim do carrinho tem o botão 📦 Acompanhar meu pedido. Digite o número do pedido "
                     "(ex.: PED-00012) e o WhatsApp usado na compra."},
        {"pergunta": "🏢 Pedido para empresa", "palavras": "empresa, cnpj, lote, atacado, quantidade, brinde, revenda",
         "resposta": "Toque em 🏢 Sou empresa, no topo da loja, e informe o CNPJ. Empresas têm desconto por "
                     "quantidade, brindes e prazo de produção em lote."},
        {"pergunta": "🔄 Defeito ou erro no pedido", "palavras": "troca, trocar, defeito, quebrou, quebrado, chegou quebrado, veio errado, errado, "
                                                       "riscado, devolver",
         "resposta": "Se o produto chegou com defeito ou diferente do que você pediu, mande fotos no WhatsApp em até "
                     "7 dias depois de receber, com o número do pedido, que a gente resolve."},
        {"pergunta": "🕐 Horário de atendimento", "palavras": "horario, atendimento, aberto, funciona, sabado, domingo",
         "resposta": "Nosso atendimento é {horario}. Fora desse horário, deixe a sua mensagem que respondemos assim "
                     "que voltarmos."},
    ],
    # Textos prontos para colocar no WhatsApp Business (o painel mostra já preenchidos, para copiar)
    "wpp_saudacao": "Olá! 👋 Obrigado por chamar a {loja}. Para agilizar, responda com o número da opção:\n"
                    "1️⃣ Fazer um pedido\n2️⃣ Acompanhar meu pedido (mande o número PED-...)\n"
                    "3️⃣ Pedido para empresa\n4️⃣ Outra dúvida\n\n🛒 Nossa loja: {link}",
    "wpp_ausencia": "Olá! 😊 Agora estamos fora do horário de atendimento ({horario}). Sua mensagem ficou "
                    "guardada e respondemos assim que voltarmos.\n\nEnquanto isso:\n🛒 Faça seu pedido pela loja: "
                    "{link}\n📦 Acompanhe seu pedido em \"Acompanhar meu pedido\", na loja\n💬 Tire dúvidas rápidas "
                    "no chat da loja",
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
CORES_PECA = {"Branco": "#ffffff", "Preto": "#1f2937", "Cinza": "#9ca3af", "Rosa": "#f9a8d4", "Vermelho": "#dc2626",
              "Azul": "#3b82f6", "Azul-marinho": "#1e3a8a", "Verde": "#16a34a", "Amarelo": "#facc15", "Lilás": "#c4b5fd"}
LADOS_PECA = ["Frente", "Verso", "Frente e verso"]
# Posição da arte dentro da área de impressão (tudo em fração da área: 0 a 1)
GEO_PADRAO = {"cx": 0.5, "cy": 0.5, "w": 1.0, "h": 1.0, "rot": 0, "fit": "slice", "tx": 0.5, "ty": 0.85, "ts": 0.13}
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
# BANCO DE DADOS (Supabase)
# Tudo o que antes ficava em arquivos (pedidos, clientes, fotos, artes...) agora fica no banco,
# e não some quando o Streamlit reinicia. Os nomes continuam os mesmos (ex.: dados_pedidos.csv),
# mas viram registros dentro do banco. Sem banco configurado, o app usa arquivos locais (só para teste).
# ===============================================================
def _segredo(*chaves):
    """Lê um valor dos Secrets do Streamlit (a senha e o endereço do banco ficam lá, fora do código)."""
    try:
        valor = st.secrets
        for k in chaves:
            valor = valor[k]
        return valor
    except Exception:
        return None


URL_BANCO = str(_segredo("connections", "banco", "url") or "").strip()
SENHA_ADMIN = str(_segredo("SENHA_ADMIN") or "")  # fica nos Secrets: ninguém vê no código nem no GitHub
# Listas que só crescem (cliques, histórico...): cada linha nova é gravada sozinha, sem reescrever tudo
ANEXOS = {ARQ_CLIQUES, ARQ_MOVIMENTOS, ARQ_HIST, ARQ_PRECOS, ARQ_CHAT}

_local = threading.local()            # marca se esta conexão do cliente está dentro da trava
_CACHE, _GERACAO = {}, {}             # memória rápida: evita ir ao banco a cada clique
_CACHE_LOCK = threading.Lock()
_TRAVA_ARQUIVOS = threading.RLock()   # trava usada só quando não há banco (teste no computador)


def _sql(q: str):
    from sqlalchemy import text
    return text(q)


@st.cache_resource(show_spinner=False)
def _banco():
    from sqlalchemy import create_engine
    url = URL_BANCO
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    eng = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10, pool_recycle=300, pool_timeout=60)
    with eng.begin() as c:
        c.execute(_sql("CREATE TABLE IF NOT EXISTS arquivos (nome TEXT PRIMARY KEY, conteudo TEXT NOT NULL)"))
        c.execute(_sql("CREATE TABLE IF NOT EXISTS binarios (nome TEXT PRIMARY KEY, dados BYTEA NOT NULL)"))
        c.execute(_sql("CREATE TABLE IF NOT EXISTS linhas (id BIGSERIAL PRIMARY KEY, nome TEXT NOT NULL, "
                       "dados TEXT NOT NULL)"))
        c.execute(_sql("CREATE INDEX IF NOT EXISTS linhas_nome ON linhas (nome, id)"))
    return eng


def _na_trava() -> bool:
    return getattr(_local, "nivel", 0) > 0


@contextmanager
def _conexao(gravar: bool = False):
    """Conexão com o banco. Dentro da trava, usa a mesma conexão que segura a trava
    (assim a fila nunca fica esperando por uma conexão livre)."""
    c = getattr(_local, "con", None)
    if c is not None:
        try:
            yield c
            if gravar:
                c.commit()
        except Exception:
            c.rollback()
            raise
        return
    if gravar:
        with _banco().begin() as c:
            yield c
    else:
        with _banco().connect() as c:
            yield c


def _cacheado(chave, carregar):
    """Guarda na memória o que veio do banco. Dentro da trava, sempre lê o banco na hora."""
    if not _na_trava():
        with _CACHE_LOCK:
            if chave in _CACHE:
                return _CACHE[chave]
            geracao = _GERACAO.get(chave, 0)
    else:
        with _CACHE_LOCK:
            geracao = _GERACAO.get(chave, 0)
    valor = carregar()
    with _CACHE_LOCK:
        if _GERACAO.get(chave, 0) == geracao:  # ninguém gravou enquanto eu lia
            _CACHE[chave] = valor
    return valor


def _esquecer(chave):
    with _CACHE_LOCK:
        _GERACAO[chave] = _GERACAO.get(chave, 0) + 1
        _CACHE.pop(chave, None)


def _ler_texto(nome: str):
    def carregar():
        if URL_BANCO:
            with _conexao() as c:
                r = c.execute(_sql("SELECT conteudo FROM arquivos WHERE nome = :n"), {"n": nome}).fetchone()
            return r[0] if r else None
        if os.path.exists(nome):
            with open(nome, "r", encoding="utf-8") as f:
                return f.read()
        return None
    return _cacheado(("T", nome), carregar)


def _gravar_texto(nome: str, conteudo: str):
    if URL_BANCO:
        with _conexao(gravar=True) as c:
            c.execute(_sql("INSERT INTO arquivos (nome, conteudo) VALUES (:n, :c) "
                           "ON CONFLICT (nome) DO UPDATE SET conteudo = EXCLUDED.conteudo"),
                      {"n": nome, "c": conteudo})
    else:
        os.makedirs(os.path.dirname(nome) or ".", exist_ok=True)
        with open(nome, "w", encoding="utf-8") as f:
            f.write(conteudo)
    _esquecer(("T", nome))


def _ler_linhas(nome: str) -> list:
    """Linhas gravadas uma a uma (cliques, histórico, movimentos, preços)."""
    def carregar():
        if not URL_BANCO:
            return []
        with _conexao() as c:
            res = c.execute(_sql("SELECT dados FROM linhas WHERE nome = :n ORDER BY id"), {"n": nome})
            return [json.loads(r[0]) for r in res]
    return _cacheado(("L", nome), carregar)


def anexar_linha(arquivo: str, colunas: list, linha: dict):
    """Acrescenta UMA linha no fim da lista, sem reescrever o resto (rápido e sem perder nada)."""
    dados = {c: str(linha.get(c, "")) for c in colunas}
    if URL_BANCO:
        with _conexao(gravar=True) as c:
            c.execute(_sql("INSERT INTO linhas (nome, dados) VALUES (:n, :d)"),
                      {"n": arquivo, "d": json.dumps(dados, ensure_ascii=False)})
        _esquecer(("L", arquivo))
    else:
        with trava():
            df = ler_csv(arquivo, colunas)
            gravar_csv(arquivo, pd.concat([df, pd.DataFrame([dados])], ignore_index=True))


def gravar_bin(nome: str, dados: bytes):
    """Guarda foto ou arte do cliente no banco (não some quando o app reinicia)."""
    if URL_BANCO:
        with _banco().begin() as c:
            c.execute(_sql("INSERT INTO binarios (nome, dados) VALUES (:n, :d) "
                           "ON CONFLICT (nome) DO UPDATE SET dados = EXCLUDED.dados"), {"n": nome, "d": dados})
    else:
        os.makedirs(os.path.dirname(nome) or ".", exist_ok=True)
        with open(nome, "wb") as f:
            f.write(dados)


def ler_bin(nome: str):
    if not nome:
        return None
    if URL_BANCO:
        with _banco().connect() as c:
            r = c.execute(_sql("SELECT dados FROM binarios WHERE nome = :n"), {"n": nome}).fetchone()
        if r:
            return bytes(r[0])
    if os.path.exists(nome):  # artes antigas que ainda estão no computador
        with open(nome, "rb") as f:
            return f.read()
    return None


@contextmanager
def trava():
    """Fila única para gravar. Todos os clientes compram ao mesmo tempo; só o instante de GRAVAR
    (menos de 1 segundo) é feito um de cada vez. Assim nenhum pedido apaga o outro
    e nenhum número de pedido se repete."""
    nivel = getattr(_local, "nivel", 0)
    if nivel:  # já estou dentro da trava: só sigo em frente
        _local.nivel = nivel + 1
        try:
            yield
        finally:
            _local.nivel = nivel
        return
    if not URL_BANCO:
        with _TRAVA_ARQUIVOS:
            _local.nivel = 1
            try:
                yield
            finally:
                _local.nivel = 0
        return
    with _banco().connect() as c:
        c.execute(_sql("SELECT pg_advisory_lock(4242)"))
        c.commit()
        _local.nivel, _local.con = 1, c
        try:
            yield
        finally:
            _local.nivel, _local.con = 0, None
            try:
                c.rollback()
                c.execute(_sql("SELECT pg_advisory_unlock(4242)"))
                c.commit()
            except Exception:
                c.invalidate()  # fecha a conexão, o que também solta a trava


def ler_json(arquivo: str, padrao):
    txt = _ler_texto(arquivo)
    if txt:
        try:
            return json.loads(txt)
        except Exception:
            pass
    return json.loads(json.dumps(padrao))  # cópia


def gravar_json(arquivo: str, dados):
    _gravar_texto(arquivo, json.dumps(dados, ensure_ascii=False, indent=2))


def ler_csv(arquivo: str, colunas: list) -> pd.DataFrame:
    partes = []
    txt = _ler_texto(arquivo)
    if txt:
        try:
            partes.append(pd.read_csv(io.StringIO(txt), dtype=str).fillna(""))
        except Exception:
            pass
    if arquivo in ANEXOS:
        linhas = _ler_linhas(arquivo)
        if linhas:
            partes.append(pd.DataFrame(linhas, dtype=str).fillna(""))
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    return df[colunas].fillna("").copy()


def gravar_csv(arquivo: str, df: pd.DataFrame):
    _gravar_texto(arquivo, df.to_csv(index=False))
    if arquivo in ANEXOS and URL_BANCO:  # a lista inteira foi regravada: limpa as linhas soltas
        with _conexao(gravar=True) as c:
            c.execute(_sql("DELETE FROM linhas WHERE nome = :n"), {"n": arquivo})
        _esquecer(("L", arquivo))


def carregar_loja() -> dict:
    loja = json.loads(json.dumps(LOJA_PADRAO))
    loja.update(ler_json(ARQ_LOJA, {}))
    return loja


def gravar_loja(loja: dict):
    gravar_json(ARQ_LOJA, loja)


try:
    LOJA = carregar_loja()
    ERRO_BANCO = False
except Exception as _erro:
    print("Erro ao conectar no banco:", type(_erro).__name__)
    LOJA = json.loads(json.dumps(LOJA_PADRAO))
    ERRO_BANCO = True
st.set_page_config(page_title=LOJA["nome_empresa"], page_icon="🏷️", layout="wide",
                   initial_sidebar_state="expanded")
if ERRO_BANCO:
    st.error("😕 A loja está em manutenção por alguns instantes. Tente de novo daqui a pouco.")
    st.caption("Para o dono da loja: o app não conseguiu conectar no banco de dados. Confira, nos Secrets do "
               "Streamlit, se o endereço do Supabase está certo e se a senha dentro dele foi trocada.")
    st.stop()


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
REDES_SOCIAIS = [  # (chave no painel, nome, cor da marca, ícone)
    ("whatsapp", "WhatsApp", "#25D366", "whatsapp"),
    ("instagram", "Instagram", "#E4405F", "instagram"),
    ("facebook", "Facebook", "#1877F2", "facebook"),
    ("twitter", "X (Twitter)", "#111111", "x"),
]


def barra_redes(loja: dict, tamanho: int = 34, sempre: bool = False):
    """Ícones das redes sociais. Com sempre=True aparecem mesmo sem link (para testar a loja)."""
    if not sempre and not loja.get("mostrar_redes", True):
        return
    partes = ""
    for chave, nome, cor_rede, icone in REDES_SOCIAIS:
        if chave == "whatsapp":
            link = f"https://wa.me/{loja['whatsapp']}" if loja.get("whatsapp") else ""
        else:
            link = str(loja.get(chave, "")).strip()
        if not link and not sempre:
            continue
        img = (f"<img src='https://cdn.simpleicons.org/{icone}/ffffff' width='{int(tamanho * .55)}' "
               f"height='{int(tamanho * .55)}' alt='{nome[0]}' "
               "onerror=\"this.replaceWith(document.createTextNode(this.alt))\">")
        bola = (f"<span style='display:inline-flex;align-items:center;justify-content:center;width:{tamanho}px;"
                f"height:{tamanho}px;border-radius:50%;background:{cor_rede};color:#fff;font-weight:800;"
                f"box-shadow:0 3px 8px rgba(0,0,0,.18);'>{img}</span>")
        dica = nome if link else f"{nome} (link ainda não configurado no painel)"
        if link:
            partes += (f"<a href='{html.escape(link, quote=True)}' target='_blank' title='{dica}' "
                       f"style='margin:0 5px;text-decoration:none;'>{bola}</a>")
        else:
            partes += f"<span title='{dica}' style='margin:0 5px;cursor:default;'>{bola}</span>"
    if partes:
        st.markdown(f"<div style='text-align:center;margin:6px 0 10px;'>{partes}</div>", unsafe_allow_html=True)


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
    /* Foto clicável: o botão fica invisível por cima da foto inteira */
    [class*="st-key-fc_"] {{ position: relative !important; gap: 0 !important; }}
    [class*="st-key-fc_"] [data-testid="stElementContainer"]:has(.stButton),
    [class*="st-key-fc_"] .element-container:has(.stButton) {{
        position: absolute !important; top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
        z-index: 3; margin: 0 !important; width: 100% !important; height: 100% !important; }}
    [class*="st-key-fc_"] .stButton, [class*="st-key-fc_"] .stButton > button,
    [class*="st-key-fc_"] [data-testid="stTooltipHoverTarget"] {{
        width: 100% !important; height: 100% !important; min-height: 100% !important; }}
    [class*="st-key-fc_"] .stButton > button {{ opacity: 0 !important; cursor: zoom-in !important; }}
    [class*="st-key-fc_"] img {{ transition: transform .35s ease; }}
    [class*="st-key-fc_"]:hover img {{ transform: scale(1.12) !important; }}
    [class*="st-key-fc_"]:hover .foto-dica {{ opacity: 1; }}
    .foto-dica {{ position: absolute; right: 8px; top: 8px; background: rgba(255,255,255,.9); width: 30px; height: 30px;
        border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,.2); opacity: 0; transition: opacity .2s; pointer-events: none; }}
    /* Campo escondido que recebe a posição da arte arrastada com o mouse */
    [class*="st-key-pgeo_host_"] {{ position: absolute !important; width: 1px !important; height: 1px !important;
        overflow: hidden !important; opacity: 0 !important; }}
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
        return st.button(dica, key=f"fcb_{chave}", on_click=on_click, args=args or ())
# ===============================================================
# PRODUTOS, FRETE E REGISTROS
# ===============================================================
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
        anexar_linha(ARQ_CLIQUES, COLUNAS_CLIQUES, {"data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                                    "evento": evento, "categoria": categoria, "produto": produto})
    except Exception:
        pass


def numero_wpp(tel) -> str:
    n = "".join(c for c in str(tel) if c.isdigit())
    return ("55" + n) if n and len(n) <= 11 else n


def registrar_movimento(material: str, tipo: str, quantidade: float, referencia: str = ""):
    anexar_linha(ARQ_MOVIMENTOS, COL_MOV, {"data": datetime.now().strftime("%Y-%m-%d %H:%M"), "material": material,
                                           "tipo": tipo, "quantidade": round(float(quantidade), 2),
                                           "referencia": referencia})


def registrar_preco(material: str, fornecedor: str, preco: float, origem: str = "Cotação", data: str = ""):
    """Guarda o preço que o fornecedor cobrou, para o gráfico de preços."""
    anexar_linha(ARQ_PRECOS, COL_PRECO, {"data": data or datetime.now().strftime("%Y-%m-%d"), "fornecedor": fornecedor,
                                         "material": material, "preco": round(float(preco), 2), "origem": origem})


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
        anexar_linha(ARQ_HIST, COL_HIST, {"data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                          "id_pedido": id_pedido, "status": status})
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
def salvar_previa(ref: str, n: int, item: dict, p: dict) -> str:
    """Guarda no banco como a peça ficou, para conferir antes de imprimir."""
    try:
        caminho = f"{PASTA_ARTES}/{ref}_{n}_previa.html"
        _gravar_texto(caminho, html_mockup(p.get("tipo") or tipo_peca(item.get("categoria", "") + " " + item["nome"]),
                                           p.get("arte", ""), p, item["nome"], altura=360))
        return caminho
    except Exception:
        return ""


def salvar_artes(ref: str) -> str:
    """Grava no banco as fotos/artes do carrinho e devolve a lista em texto (JSON).
    Roda ANTES da trava, para a fila de gravar o pedido continuar rapidinha."""
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
            if dados:
                caminho = f"{PASTA_ARTES}/{ref}_{n}.{ext}"
                gravar_bin(caminho, dados)
        lista.append({"item": item["nome"], "quantidade": item["quantidade"], "arquivo": caminho,
                      "texto": p.get("texto", ""), "fonte": p.get("fonte", ""), "cor_texto": p.get("cor_texto", ""),
                      "obs": p.get("obs", ""), "arte_nome": p.get("arte_nome", ""), "geo": p.get("geo") or {},
                      "cor_peca": p.get("cor_peca", "Branco"), "lado": p.get("lado", "Frente"),
                      "tipo": p.get("tipo", ""), "previa": salvar_previa(ref, n, item, p)})
    return json.dumps(lista, ensure_ascii=False) if lista else ""


def ler_previa(caminho: str):
    """Prévia de como o cliente montou a peça (do banco; pedidos antigos podem estar no computador)."""
    if not caminho:
        return None
    txt = _ler_texto(caminho)
    if not txt and os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            txt = f.read()
    return txt


def registrar_pedido(nome: str, telefone: str, email: str, itens_txt: str, total: float, forma: str):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    frete = st.session_state.get("frete") or {}
    empresa = st.session_state.get("empresa") or {}
    tipo = "Empresa" if st.session_state.get("modo") == "empresa" else "Cliente"
    numero_casa = st.session_state.get("cli_numero", "").strip()
    complemento = st.session_state.get("cli_comp", "").strip()
    endereco = ", ".join(p for p in [frete.get("rua", ""), numero_casa, complemento, frete.get("bairro", "")] if p)
    if frete:
        endereco += f" - {frete.get('cidade', '')}/{frete.get('uf', '')} CEP {frete.get('cep', '')}"
    # 1) Fotos e artes vão para o banco antes (pode demorar uns segundos e não segura a fila)
    personalizacao = salvar_artes(f"{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}")

    # 2) Agora a parte rápida, um pedido de cada vez: número do pedido + gravar
    with trava():
        return _gravar_pedido_e_cliente(agora, nome, telefone, email, itens_txt, total, forma, tipo, frete,
                                        empresa, endereco, numero_casa, complemento, personalizacao)


def _gravar_pedido_e_cliente(agora, nome, telefone, email, itens_txt, total, forma, tipo, frete, empresa,
                             endereco, numero_casa, complemento, personalizacao) -> str:
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
        "ent_rua": frete.get("rua", ""), "ent_numero": numero_casa,
        "ent_complemento": complemento, "ent_bairro": frete.get("bairro", ""),
        "ent_cidade": frete.get("cidade", ""), "ent_uf": frete.get("uf", ""), "ent_cep": frete.get("cep", ""),
        "ent_peso": "", "personalizacao": personalizacao,
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
            "endereco": ", ".join(p for p in [frete.get("rua", ""), numero_casa, complemento,
                                              frete.get("bairro", "")] if p),
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


def geo_de(p: dict) -> dict:
    """Posição da arte guardada no pedido (pedidos antigos usam escala/dx/dy)."""
    g = dict(GEO_PADRAO)
    if isinstance(p.get("geo"), dict):
        g.update(p["geo"])
        return g
    e = float(p.get("escala", 100) or 100) / 100
    g.update(w=e, h=e, cx=0.5 + float(p.get("dx", 0) or 0) / 200, cy=0.5 + float(p.get("dy", 0) or 0) / 200,
             fit="meet")
    return g


def ler_geo(k: str) -> dict:
    g = dict(GEO_PADRAO)
    try:
        g.update(json.loads(st.session_state.get(f"pgeo_{k}") or "{}"))
    except Exception:
        pass
    g["ts"] = st.session_state.get(f"pts_{k}", 13) / 100
    return g


def mudar_geo(k: str, acao: str):
    """Botões rápidos: preencher, caber, girar, recomeçar, texto no meio."""
    g = ler_geo(k)
    if acao == "preencher":
        g.update(cx=0.5, cy=0.5, w=1.0, h=1.0, rot=0, fit="slice")
    elif acao == "caber":
        g.update(cx=0.5, cy=0.5, w=1.0, h=1.0, rot=0, fit="meet")
    elif acao == "girar":
        g["rot"] = (int(g.get("rot", 0)) + 90) % 360
    elif acao == "recomecar":
        g = dict(GEO_PADRAO)
    elif acao == "texto_meio":
        g.update(tx=0.5, ty=0.5)
    st.session_state[f"pgeo_{k}"] = json.dumps(g)


def marcar_origem(k: str, origem: str):
    """Lembra se o cliente usou por último a foto dele ou uma arte pronta, e já preenche a peça com ela."""
    st.session_state[f"porigem_{k}"] = origem
    mudar_geo(k, "preencher")


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
             "geo": ler_geo(k), "cor_peca": st.session_state.get(f"pcorpeca_{k}", "Branco"),
             "lado": st.session_state.get(f"plado_{k}", "Frente"),
             "tipo": tipo_peca(item.get("categoria", "") + " " + item["nome"]), "arte": ""}
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
    if st.session_state.get("link_whatsapp"):
        return  # pedido já registrado (clique duplo); só muda se o carrinho mudar
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
    # O pedido só sai com endereço: precisa calcular o frete (CEP) e informar o número da casa
    frete_ok = st.session_state.get("frete")
    if not frete_ok:
        st.session_state.erro_cliente = "Calcule o frete com o seu CEP antes de finalizar."
        return
    if abs(frete_ok["total_na_hora"] - total) > 0.01:
        st.session_state.erro_cliente = "O carrinho mudou. Clique em Calcular frete de novo."
        return
    if not st.session_state.get("cli_numero", "").strip():
        st.session_state.erro_cliente = "Preencha o número da casa (ou escreva S/N)."
        return
    st.session_state.erro_cliente = None

    linhas = []
    for i in st.session_state.carrinho:
        extra = f" (+{i['unidades_gratis']} brinde)" if i["unidades_gratis"] > 0 else ""
        if i.get("perso"):
            # " / " e não " | ": o "|" separa o frete e cortava os itens na etiqueta e na declaração
            extra += " [personalizado: " + " / ".join(x for x in [i["perso"].get("arte_nome", ""),
                                                              i["perso"].get("texto", ""),
                                                              "peça " + i["perso"].get("cor_peca", "Branco"),
                                                              i["perso"].get("lado", "")] if x) + "]"
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
    except Exception as erro:
        print("Falha ao registrar pedido:", type(erro).__name__, erro)
        # se o registro falhar, o cliente ainda consegue enviar o pedido pelo WhatsApp

    bloco_entrega = ""
    if frete:
        endereco = ", ".join(p for p in [frete["rua"], st.session_state.get("cli_numero", "").strip(),
                                         st.session_state.get("cli_comp", "").strip(), frete["bairro"]] if p)
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
        k = item["id"]
        if f"pgeo_{k}" not in st.session_state:
            st.session_state[f"pgeo_{k}"] = json.dumps(GEO_PADRAO)
        if modo.startswith("🎨"):
            components.html(mockup_perso(item), height=470)
            st.caption("🖱️ Arraste a arte para mover · puxe as bolinhas dos cantos para esticar (Shift mantém a "
                       "proporção) · bolinha de cima gira · rodinha do mouse aumenta e diminui · arraste o texto. "
                       "No celular, use o dedo.")
            b1, b2, b3, b4, b5 = st.columns(5)
            b1.button("⬛ Preencher", key=f"gpre_{k}", on_click=mudar_geo, args=(k, "preencher"),
                      use_container_width=True, help="A arte ocupa toda a peça")
            b2.button("🔲 Caber", key=f"gcab_{k}", on_click=mudar_geo, args=(k, "caber"),
                      use_container_width=True, help="A arte inteira aparece, sem cortar")
            b3.button("↻ Girar", key=f"ggir_{k}", on_click=mudar_geo, args=(k, "girar"),
                      use_container_width=True, help="Gira 90 graus")
            b4.button("🔤 Texto no meio", key=f"gtxt_{k}", on_click=mudar_geo, args=(k, "texto_meio"),
                      use_container_width=True)
            b5.button("↺ Recomeçar", key=f"grec_{k}", on_click=mudar_geo, args=(k, "recomecar"),
                      use_container_width=True)
        elif modo.startswith("🔍"):
            foto_com_lupa(item)
            st.caption("Passe o mouse sobre a foto para ver os detalhes.")
        else:
            renderizar_visualizador_3d(item, height=430)
        with st.container(key=f"pgeo_host_{k}"):  # campo escondido que recebe a posição arrastada
            st.text_input("posição da arte", key=f"pgeo_{k}", label_visibility="collapsed")
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
        c1, c2 = st.columns(2)
        c1.selectbox("Cor da peça", list(CORES_PECA), key=f"pcorpeca_{k}")
        c2.radio("Onde vai a arte", LADOS_PECA, key=f"plado_{k}")
        st.text_input("Texto ou nome na peça (opcional)", key=f"ptxt_{k}")
        f1, f2 = st.columns(2)
        f1.selectbox("Estilo da letra", FONTES_PERSO, key=f"pfonte_{k}")
        f2.color_picker("Cor do texto", "#000000", key=f"pcor_{k}")
        st.slider("Tamanho do texto", 5, 40, 13, key=f"pts_{k}")
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
    marcar_origem(k, "galeria")  # já preenche a peça inteira com a arte
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


COR_ORIGINAL_PECA = {"caneca": "#fff", "copo": "#eef2f7", "camiseta": "#fff", "bone": "#fff", "chaveiro": "#fff",
                     "almofada": "#fff", "mateira": "#92400e", "quadro": "#fff"}


def html_mockup(tipo: str, src: str, perso: dict, nome: str = "", altura: int = 450, editar: str = "") -> str:
    """Desenha a peça com a arte por cima. Com editar=<código do produto>, dá para mexer com o mouse."""
    fundo, (ax, ay, aw, ah), recorte, sombra = PECAS_MOCKUP.get(tipo, PECAS_MOCKUP["quadro"])
    cor_peca = CORES_PECA.get(perso.get("cor_peca"), "#ffffff")
    fundo = fundo.replace(f"fill='{COR_ORIGINAL_PECA.get(tipo, '#fff')}'", f"fill='{cor_peca}'")
    if tipo == "caneca":
        fundo = fundo.replace("stroke='#f9fafb'", f"stroke='{cor_peca}'")
    g = geo_de(perso)
    texto = str(perso.get("texto") or "")
    mistura = "multiply" if cor_peca == "#ffffff" else "normal"
    ajuste = {"slice": "xMidYMid slice", "meet": "xMidYMid meet", "none": "none"}.get(g["fit"], "xMidYMid slice")
    cx, cy, w, h = ax + g["cx"] * aw, ay + g["cy"] * ah, g["w"] * aw, g["h"] * ah
    giro = f"translate({cx:.1f},{cy:.1f}) rotate({float(g['rot']):.1f})"
    miolo = ""
    if src:
        miolo += (f"<g id='arte' transform='{giro}'><image id='img' href='{html.escape(src, quote=True)}' "
                  f"x='{-w / 2:.1f}' y='{-h / 2:.1f}' width='{w:.1f}' height='{h:.1f}' preserveAspectRatio='{ajuste}' "
                  f"style='mix-blend-mode:{mistura}'/></g>")
    tx, ty, fs = ax + g["tx"] * aw, ay + g["ty"] * ah, max(6.0, float(g["ts"]) * ah)
    estilo_txt = (f"text-anchor='middle' dominant-baseline='middle' font-size='{fs:.1f}' font-weight='700' "
                  f"style=\"font-family:{CSS_FONTES.get(perso.get('fonte'), 'Arial')}\"")
    if texto:
        miolo += (f"<text id='txt' x='{tx:.1f}' y='{ty:.1f}' {estilo_txt} "
                  f"fill='{html.escape(perso.get('cor_texto') or '#000', quote=True)}'>{html.escape(texto)}</text>")
    if not miolo:
        miolo = (f"<rect x='{ax + 4}' y='{ay + 4}' width='{aw - 8}' height='{ah - 8}' rx='8' fill='none' "
                 "stroke='#94a3b8' stroke-width='2' stroke-dasharray='8 6'/>"
                 f"<text x='{ax + aw / 2}' y='{ay + ah / 2}' text-anchor='middle' font-size='15' fill='#64748b' "
                 "font-family='Arial'>Sua arte aqui</text>"
                 f"<text x='{ax + aw / 2}' y='{ay + ah / 2 + 20}' text-anchor='middle' font-size='11' fill='#94a3b8' "
                 "font-family='Arial'>escolha ou envie uma imagem</text>")
    edicao, script = "", ""
    if editar and (src or texto):
        edicao = (f"<rect x='{ax}' y='{ay}' width='{aw}' height='{ah}' fill='none' stroke='#7c3aed' "
                  "stroke-opacity='.35' stroke-dasharray='3 4' pointer-events='none'/>")
        if src:
            cantos = "".join(f"<circle class='canto' data-acao='canto' data-sx='{sx}' data-sy='{sy}' r='7' fill='#fff' "
                             "stroke='#7c3aed' stroke-width='2.5' style='cursor:nwse-resize'/>"
                             for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)])
            edicao += (f"<g id='sel' transform='{giro}'><rect id='caixa' data-acao='mover' fill='rgba(124,58,237,.04)' "
                       "stroke='#7c3aed' stroke-width='1.6' stroke-dasharray='6 4' style='cursor:move'/>"
                       "<line id='haste' x1='0' x2='0' stroke='#7c3aed' stroke-width='1.6'/>"
                       "<circle id='gir' data-acao='girar' cx='0' r='7.5' fill='#7c3aed' stroke='#fff' stroke-width='2' "
                       f"style='cursor:grab'/>{cantos}</g>")
        if texto:
            estilo_hit = estilo_txt.replace('style="font-family:', 'style="cursor:move;font-family:')
            edicao += (f"<text id='txthit' data-acao='texto' x='{tx:.1f}' y='{ty:.1f}' {estilo_hit} fill='transparent' "
                       "stroke='#7c3aed' stroke-width='.6' stroke-dasharray='2 2'>"
                       f"{html.escape(texto)}</text>")
        script = (EDITOR_JS.replace("__A__", json.dumps([ax, ay, aw, ah])).replace("__G__", json.dumps(g))
                  .replace("__K__", json.dumps(editar)))
    defs = (_CIL + "<linearGradient id='tecido' x1='0' x2='0' y1='0' y2='1'><stop offset='0' stop-color='#000' "
            "stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.10'/></linearGradient>"
            "<radialGradient id='fofo' cx='.5' cy='.45' r='.65'><stop offset='.55' stop-color='#000' stop-opacity='0'/>"
            "<stop offset='1' stop-color='#000' stop-opacity='.22'/></radialGradient>"
            "<radialGradient id='luz' cx='.5' cy='.35' r='.75'><stop offset='0' stop-color='#ffffff'/>"
            "<stop offset='1' stop-color='#dbe4f3'/></radialGradient>"
            f"<clipPath id='area'>{recorte}</clipPath>")
    lado = html.escape(str(perso.get("lado") or "Frente"))
    return f"""<html><body style="margin:0;font-family:Arial,sans-serif;background:transparent">
<div style="border-radius:12px;overflow:hidden;border:1px solid #dbe1ea;background:#fff;position:relative">
<svg id="peca" viewBox="0 0 400 400" style="display:block;width:100%;height:{altura - 30}px;touch-action:none">
<defs>{defs}</defs><rect width="400" height="400" fill="url(#luz)"/>
{fundo}<g clip-path="url(#area)">{miolo}</g>{sombra}{edicao}
<rect x="8" y="8" width="{len(lado) * 7 + 16}" height="18" rx="9" fill="rgba(17,24,39,.75)"/>
<text x="16" y="21" font-size="11" fill="#fff" font-family="Arial">{lado}</text></svg>
<div id="salvo" style="position:absolute;right:10px;top:10px;background:#16a34a;color:#fff;font-size:12px;padding:3px 10px;
border-radius:999px;opacity:0;transition:opacity .3s">✓ posição salva</div>
<div style="padding:5px 10px;font-size:12px;color:#475569;border-top:1px solid #eef2f7">
👀 Prévia de como fica{(' · ' + html.escape(nome)) if nome else ''} · peça {html.escape(str(perso.get('cor_peca') or 'Branco'))}
· as cores reais podem variar um pouco</div>
</div>{script}</body></html>"""


def mockup_perso(item: dict) -> str:
    """Prévia (editável com o mouse) da peça com a arte escolhida ou a foto enviada pelo cliente."""
    k = item["id"]
    src, _ = arte_escolhida(k)
    perso = {"texto": st.session_state.get(f"ptxt_{k}", ""), "fonte": st.session_state.get(f"pfonte_{k}", "Padrão"),
             "cor_texto": st.session_state.get(f"pcor_{k}", "#000000"), "geo": ler_geo(k),
             "cor_peca": st.session_state.get(f"pcorpeca_{k}", "Branco"),
             "lado": st.session_state.get(f"plado_{k}", "Frente")}
    return html_mockup(tipo_peca(item["categoria"] + " " + item["nome"]), src, perso, item["nome"], editar=k)


EDITOR_JS = r"""<script>
(function(){
var svg=document.getElementById('peca'), A=__A__, G=__G__, K=__K__;
var arte=document.getElementById('arte'), img=document.getElementById('img'), sel=document.getElementById('sel'),
    caixa=document.getElementById('caixa'), txt=document.getElementById('txt'), hit=document.getElementById('txthit'),
    gir=document.getElementById('gir'), haste=document.getElementById('haste');
var cantos=[].slice.call(document.querySelectorAll('.canto'));
function P(e){var p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;return p.matrixTransform(svg.getScreenCTM().inverse());}
function lim(v,a,b){return Math.max(a,Math.min(b,v));}
function centro(){return [A[0]+G.cx*A[2], A[1]+G.cy*A[3]];}
function desenhar(){
  var c=centro(), w=G.w*A[2], h=G.h*A[3], tr='translate('+c[0].toFixed(1)+','+c[1].toFixed(1)+') rotate('+G.rot+')';
  if(arte){arte.setAttribute('transform',tr);img.setAttribute('x',-w/2);img.setAttribute('y',-h/2);img.setAttribute('width',w);img.setAttribute('height',h);}
  if(sel){sel.setAttribute('transform',tr);caixa.setAttribute('x',-w/2);caixa.setAttribute('y',-h/2);caixa.setAttribute('width',w);caixa.setAttribute('height',h);
    cantos.forEach(function(k){k.setAttribute('cx',(+k.getAttribute('data-sx'))*w/2);k.setAttribute('cy',(+k.getAttribute('data-sy'))*h/2);});
    gir.setAttribute('cy',-h/2-24);haste.setAttribute('y1',-h/2);haste.setAttribute('y2',-h/2-24);}
  if(txt){var tx=A[0]+G.tx*A[2], ty=A[1]+G.ty*A[3];[txt,hit].forEach(function(t){t.setAttribute('x',tx);t.setAttribute('y',ty);});}
}
var modo=null, ini=null, g0=null, timer=null;
svg.addEventListener('pointerdown',function(e){var a=e.target.getAttribute('data-acao'); if(!a) return;
  modo=a; ini=P(e); g0=JSON.parse(JSON.stringify(G)); try{svg.setPointerCapture(e.pointerId);}catch(_){} e.preventDefault();});
svg.addEventListener('pointermove',function(e){ if(!modo) return; var p=P(e), c=centro();
  if(modo==='mover'){G.cx=lim(g0.cx+(p.x-ini.x)/A[2],-.5,1.5);G.cy=lim(g0.cy+(p.y-ini.y)/A[3],-.5,1.5);}
  else if(modo==='texto'){G.tx=lim(g0.tx+(p.x-ini.x)/A[2],0,1);G.ty=lim(g0.ty+(p.y-ini.y)/A[3],0,1);}
  else if(modo==='canto'){var r=-G.rot*Math.PI/180, dx=p.x-c[0], dy=p.y-c[1], lx=dx*Math.cos(r)-dy*Math.sin(r), ly=dx*Math.sin(r)+dy*Math.cos(r);
    var nw=lim(2*Math.abs(lx)/A[2],.08,4), nh=lim(2*Math.abs(ly)/A[3],.08,4);
    if(e.shiftKey){var f=Math.max(nw/g0.w,nh/g0.h); nw=lim(g0.w*f,.08,4); nh=lim(g0.h*f,.08,4);}
    G.w=nw; G.h=nh;}
  else if(modo==='girar'){var ang=Math.atan2(p.y-c[1],p.x-c[0])*180/Math.PI+90, s=Math.round(ang/15)*15; if(Math.abs(ang-s)<5) ang=s; G.rot=Math.round(((ang%360)+360)%360);}
  desenhar();});
function soltar(){ if(!modo) return; modo=null; enviar(); }
svg.addEventListener('pointerup',soltar); svg.addEventListener('pointercancel',soltar);
svg.addEventListener('wheel',function(e){ if(!arte) return; e.preventDefault(); var f=e.deltaY<0?1.06:1/1.06;
  G.w=lim(G.w*f,.08,4); G.h=lim(G.h*f,.08,4); desenhar(); clearTimeout(timer); timer=setTimeout(enviar,700);},{passive:false});
function enviar(){
  try{ var inp=window.parent.document.querySelector('.st-key-pgeo_host_'+K+' input'); if(!inp) return;
    var v={}; for(var k in G){v[k]=typeof G[k]==='number'?Math.round(G[k]*1000)/1000:G[k];}
    var set=Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype,'value').set;
    inp.focus(); set.call(inp,JSON.stringify(v)); inp.dispatchEvent(new Event('input',{bubbles:true}));
    inp.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true}));
    inp.blur();
    var av=document.getElementById('salvo'); if(av){av.style.opacity=1; setTimeout(function(){av.style.opacity=0;},1200);}
  }catch(err){}
}
desenhar();
})();
</script>
"""
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
                  ARQ_FORNECEDORES, ARQ_ESTOQUE, ARQ_COMPRAS, ARQ_MOVIMENTOS, ARQ_PRECOS, ARQ_HIST, ARQ_CHAT,
                  ARQ_FOTOS_SEP]


def _nomes_textos() -> list:
    """Tudo o que está guardado como texto: listas (pedidos, clientes...) e as prévias das artes."""
    if URL_BANCO:
        with _banco().connect() as c:
            nomes = [r[0] for r in c.execute(_sql("SELECT nome FROM arquivos"))]
    else:
        nomes = [a for a in ARQUIVOS_DADOS if os.path.exists(a)]
        if os.path.isdir(PASTA_ARTES):
            nomes += [f"{PASTA_ARTES}/{n}" for n in os.listdir(PASTA_ARTES) if n.endswith(".html")]
    return sorted(set(nomes) | (ANEXOS & set(ARQUIVOS_DADOS)))


def _todos_binarios():
    """Fotos e artes enviadas pelos clientes."""
    if URL_BANCO:
        with _banco().connect() as c:
            for nome, dados in c.execute(_sql("SELECT nome, dados FROM binarios ORDER BY nome")):
                yield nome, bytes(dados)
    else:
        for pasta in (PASTA_ARTES, PASTA_FOTOS_SEP):
            if os.path.isdir(pasta):
                for n in os.listdir(pasta):
                    if not n.endswith(".html"):
                        with open(os.path.join(pasta, n), "rb") as f:
                            yield f"{pasta}/{n}", f.read()


def gerar_backup_zip() -> bytes:
    """Um .zip com TUDO: pedidos, clientes, produtos, fotos e artes dos clientes, configurações."""
    colunas = {ARQ_CLIQUES: COLUNAS_CLIQUES, ARQ_MOVIMENTOS: COL_MOV, ARQ_HIST: COL_HIST, ARQ_PRECOS: COL_PRECO,
               ARQ_CHAT: COL_CHAT}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for nome in _nomes_textos():
            if nome in ANEXOS:
                conteudo = ler_csv(nome, colunas[nome]).to_csv(index=False)
            else:
                conteudo = _ler_texto(nome)
            if conteudo is not None:
                z.writestr(nome, conteudo)
        for nome, dados in _todos_binarios():
            z.writestr(nome, dados)
        if os.path.isdir(PASTA_VIDEOS):
            for nome in os.listdir(PASTA_VIDEOS):
                z.write(os.path.join(PASTA_VIDEOS, nome), arcname=f"{PASTA_VIDEOS}/{nome}")
        prod = ler_csv(ARQ_PRODUTOS, COLUNAS_PRODUTOS).copy()
        prod["imagem"] = prod["imagem"].apply(lambda u: "(foto enviada)" if str(u).startswith("data:") else u)
        z.writestr("LEIA-ME/produtos_para_excel.csv", prod.to_csv(index=False, sep=";").encode("utf-8-sig"))
        cli = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
        z.writestr("LEIA-ME/clientes_para_excel.csv", cli.to_csv(index=False, sep=";").encode("utf-8-sig"))
        ped = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        z.writestr("LEIA-ME/pedidos_para_excel.csv",
                   ped.drop(columns=["personalizacao", "itens_json"]).to_csv(index=False, sep=";").encode("utf-8-sig"))
        z.writestr("LEIA-ME/LEIA-ME.txt",
                   "Backup completo da loja: pedidos, clientes, produtos, fotos e artes dos clientes.\n"
                   "Para restaurar: no painel, seção Backup, envie este mesmo arquivo .zip.\n"
                   "A pasta LEIA-ME tem planilhas para abrir no Excel (não são usadas na restauração).\n")
    return buf.getvalue()


def restaurar_backup_zip(arquivo) -> int:
    """Devolve para o banco tudo o que está no .zip (também aceita os backups antigos)."""
    restaurados = 0
    with zipfile.ZipFile(arquivo) as z, trava():
        for nome in z.namelist():
            if nome.startswith(("/", "\\")) or ".." in nome.replace("\\", "/").split("/") or nome.endswith("/"):
                continue  # segurança: não deixa o zip gravar fora da pasta da loja
            pasta = nome.split("/")[0]
            if nome in ARQUIVOS_DADOS or nome in ("dados_equipe.json", "dados_cidade_vida.json"):
                if nome in ("dados_equipe.json", "dados_cidade_vida.json"):
                    continue  # eram da cidade 3D, que saiu
                texto = z.read(nome).decode("utf-8")
                if nome in ANEXOS:
                    gravar_csv(nome, pd.read_csv(io.StringIO(texto), dtype=str).fillna("") if texto.strip()
                               else pd.DataFrame())
                else:
                    _gravar_texto(nome, texto)
            elif pasta == PASTA_ARTES:
                if nome.endswith(".html"):
                    _gravar_texto(nome, z.read(nome).decode("utf-8"))
                else:
                    gravar_bin(nome, z.read(nome))
            elif pasta == PASTA_FOTOS_SEP:
                gravar_bin(nome, z.read(nome))
            elif pasta == PASTA_VIDEOS:
                os.makedirs(PASTA_VIDEOS, exist_ok=True)
                with open(nome, "wb") as f:
                    f.write(z.read(nome))
            else:
                continue
            restaurados += 1
    return restaurados


# ===============================================================
# MUDAR A SITUAÇÃO DO PEDIDO (Mesa do chefe, esteira e entregas)
# ===============================================================
def mudar_status(id_pedido: str, novo_status: str):
    """Muda a situação do pedido e faz o resto sozinho (histórico e baixa do estoque)."""
    with trava():
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


def atualizar_pedido(id_pedido: str, campos: dict):
    """Muda só os campos de UM pedido, lendo a lista na hora, dentro da trava.
    Assim, se um cliente fizer um pedido enquanto você salva, o pedido dele não some."""
    with trava():
        ped = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
        alvo = ped["id_pedido"] == id_pedido
        if not alvo.any():
            return
        antigo = ped.loc[alvo, "status"].iloc[0]
        for campo, valor in campos.items():
            ped.loc[alvo, campo] = valor
        gravar_csv(ARQ_PEDIDOS, ped)
        if "status" in campos:
            depois_de_mudar_status(id_pedido, antigo, campos["status"])


# ===============================================================
# CHAT DA LOJA (assistente automático + atendimento ao vivo com você)
# O assistente responde sozinho pelas palavras da pergunta. Se não resolver, o cliente chama uma pessoa
# e vê se você está online. Tudo (perguntas, respostas, mensagens e horário) se edita no painel.
# ===============================================================
DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
QUEM_CHAT = {"cliente": ("user", "🙂"), "robo": ("assistant", "🤖"), "loja": ("assistant", "🧑‍💼")}


@st.cache_resource(show_spinner=False)
def _presenca() -> dict:
    """Guarda (na memória do servidor) se você está com o painel aberto e disponível no chat."""
    return {"visto": 0.0, "disponivel": True}


def marcar_dono_online():
    _presenca()["visto"] = time.time()


def dono_online() -> bool:
    p = _presenca()
    return p["disponivel"] and (time.time() - p["visto"]) < 150  # visto nos últimos 2,5 minutos


def _hora(txt, padrao: str) -> tuple:
    try:
        h, m = str(txt).strip().split(":")[:2]
        return int(h), int(m)
    except Exception:
        h, m = padrao.split(":")
        return int(h), int(m)


def texto_horario() -> str:
    dias = sorted(int(d) for d in LOJA.get("exp_dias", [0, 1, 2, 3, 4]))
    if not dias:
        return "a combinar pelo WhatsApp"
    seguidos = dias == list(range(dias[0], dias[-1] + 1))
    nomes = (f"de {DIAS_SEMANA[dias[0]]} a {DIAS_SEMANA[dias[-1]]}" if seguidos and len(dias) > 2
             else ", ".join(DIAS_SEMANA[d] for d in dias))
    hi, mi = _hora(LOJA.get("exp_inicio"), "08:00")
    hf, mf = _hora(LOJA.get("exp_fim"), "18:00")
    return f"{nomes}, das {hi:02d}:{mi:02d} às {hf:02d}:{mf:02d}"


def em_expediente(agora: datetime = None) -> bool:
    agora = agora or datetime.now()
    if agora.weekday() not in [int(d) for d in LOJA.get("exp_dias", [0, 1, 2, 3, 4])]:
        return False
    hi, mi = _hora(LOJA.get("exp_inicio"), "08:00")
    hf, mf = _hora(LOJA.get("exp_fim"), "18:00")
    minutos = agora.hour * 60 + agora.minute
    return hi * 60 + mi <= minutos < hf * 60 + mf


def preencher(msg: str) -> str:
    """Troca {loja}, {horario}, {link}, {whatsapp}, {frete_gratis} e {atendente} pelos dados da loja."""
    frete = (f"Frete grátis em pedidos a partir de R$ {LOJA['frete_gratis_acima']:.2f}."
             if LOJA.get("frete_gratis_ligado") and LOJA.get("frete_gratis_acima", 0) > 0 else "")
    trocas = {"{loja}": LOJA["nome_empresa"], "{horario}": texto_horario(), "{frete_gratis}": frete,
              "{link}": LOJA.get("link_loja") or "(endereço da loja)", "{whatsapp}": LOJA.get("whatsapp", ""),
              "{atendente}": LOJA.get("chat_nome_atendente") or "a equipe"}
    for k, v in trocas.items():
        msg = str(msg).replace(k, str(v))
    return msg.replace("  ", " ").strip()


def _normal(texto: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii").lower()
    return " ".join("".join(c if c.isalnum() else " " for c in t).split())


def resposta_automatica(texto: str):
    """O assistente: procura a pergunta cadastrada que tem mais palavras parecidas com a do cliente."""
    t = f" {_normal(texto)} "
    melhor, pontos = None, 0
    for p in LOJA.get("chat_perguntas", []):
        chaves = [_normal(k) for k in str(p.get("palavras", "")).split(",") if _normal(k)]
        chaves += [w for w in _normal(p.get("pergunta", "")).split() if len(w) > 3]
        n = 0
        for k in set(chaves):
            raiz = k if " " in k or len(k) <= 4 else k[:5] if len(k) > 5 else k[:-1]  # "quebrou" acha "quebrado"
            if f" {k} " in t or (" " not in k and f" {raiz}" in t):
                n += 2 if " " in k else 1
        if n > pontos:
            melhor, pontos = p, n
    return preencher(melhor["resposta"]) if melhor else None


def mensagens_chat(conversa: str = None) -> pd.DataFrame:
    df = ler_csv(ARQ_CHAT, COL_CHAT)
    return df[df["conversa"] == conversa].reset_index(drop=True) if conversa else df


def gravar_msg(conversa: str, quem: str, texto: str, nome: str = ""):
    anexar_linha(ARQ_CHAT, COL_CHAT, {"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "conversa": conversa,
                                      "quem": quem, "nome": nome[:60], "texto": str(texto)[:800]})


def resumo_conversas() -> pd.DataFrame:
    """Uma linha por conversa: quem é, última mensagem e se está esperando a sua resposta."""
    df = mensagens_chat()
    if df.empty:
        return pd.DataFrame(columns=["conversa", "nome", "ultima", "data", "esperando", "qtd"])
    linhas = []
    for conv, g in df.groupby("conversa", sort=False):
        humano, esperando = False, False
        for _, m in g.iterrows():
            if m["quem"] == "sistema" and m["texto"] == "chamou_atendente":
                humano, esperando = True, True
            elif m["quem"] == "sistema" and m["texto"] == "encerrado":
                humano, esperando = False, False
            elif m["quem"] == "cliente" and humano:
                esperando = True
            elif m["quem"] == "loja":
                esperando = False
        nomes = [n for n in g["nome"] if n]
        visiveis = g[g["quem"] != "sistema"]
        ult = visiveis.iloc[-1] if len(visiveis) else g.iloc[-1]
        linhas.append({"conversa": conv, "nome": nomes[-1] if nomes else "Visitante", "ultima": ult["texto"],
                       "data": g.iloc[-1]["data"], "esperando": esperando, "humano": humano, "qtd": len(visiveis)})
    res = pd.DataFrame(linhas)
    res["_dt"] = pd.to_datetime(res["data"], format="%d/%m/%Y %H:%M", errors="coerce")
    return res.sort_values(["esperando", "_dt"], ascending=[False, False]).reset_index(drop=True)


def _conversa_atual() -> str:
    """Cada visitante tem a sua conversa (fica no endereço da página, então não se perde ao recarregar)."""
    conv = st.session_state.get("chat_id") or st.query_params.get("chat")
    if not conv or len(str(conv)) > 20 or not str(conv).isalnum():
        conv = uuid.uuid4().hex[:12]
    st.session_state.chat_id = conv
    return conv


def _status_atendimento() -> tuple:
    if dono_online():
        return "🟢", "Online agora"
    if em_expediente():
        return "🟡", "Respondemos em breve"
    return "🌙", "Fora do horário"


def _aviso_sem_atendente(conv: str):
    """Mensagem automática quando ninguém está online (no máximo uma a cada 30 minutos)."""
    msgs = mensagens_chat(conv)
    autos = msgs[(msgs["quem"] == "robo") & msgs["texto"].isin(
        [preencher(LOJA["chat_fora_expediente"]), preencher(LOJA["chat_offline"])])]
    if len(autos):
        dt = pd.to_datetime(autos.iloc[-1]["data"], format="%d/%m/%Y %H:%M", errors="coerce")
        if pd.notna(dt) and datetime.now() - dt < timedelta(minutes=30):
            return
    texto = LOJA["chat_offline"] if em_expediente() else LOJA["chat_fora_expediente"]
    gravar_msg(conv, "robo", preencher(texto))


def _em_atendimento(conv: str) -> bool:
    r = resumo_conversas()
    linha = r[r["conversa"] == conv]
    return bool(len(linha) and linha.iloc[0]["humano"])


def _limite_ok(conv: str) -> bool:
    msgs = mensagens_chat(conv)
    return int((msgs["quem"] == "cliente").sum()) < 60  # proteção contra quem fica mandando sem parar


def _chat_pergunta_rapida(conv: str, p: dict):
    nome = st.session_state.get("chat_nome", "").strip()
    if not _limite_ok(conv):
        return
    st.query_params["chat"] = conv
    gravar_msg(conv, "cliente", p["pergunta"], nome)
    gravar_msg(conv, "robo", preencher(p["resposta"]))
    registrar_clique("chat_pergunta", "", p["pergunta"])


def _chat_enviar(conv: str):
    texto = st.session_state.get(f"chat_txt_{conv}", "").strip()
    nome = st.session_state.get("chat_nome", "").strip()
    st.session_state[f"chat_txt_{conv}"] = ""
    if not texto or not _limite_ok(conv):
        return
    st.query_params["chat"] = conv
    gravar_msg(conv, "cliente", texto[:500], nome)
    if _em_atendimento(conv):
        if not dono_online():
            _aviso_sem_atendente(conv)
        return
    resp = resposta_automatica(texto)
    if resp:
        gravar_msg(conv, "robo", resp)
        gravar_msg(conv, "robo", preencher(LOJA["chat_resolveu"]))
    else:
        gravar_msg(conv, "robo", preencher(LOJA["chat_nao_entendi"]))


def _chat_chamar_pessoa(conv: str):
    st.query_params["chat"] = conv
    nome = st.session_state.get("chat_nome", "").strip()
    gravar_msg(conv, "sistema", "chamou_atendente", nome)
    if dono_online():
        gravar_msg(conv, "robo", preencher(LOJA["chat_chamando"]))
    else:
        _aviso_sem_atendente(conv)


def _desenhar_chat_cliente(conv: str, ao_vivo: bool):
    msgs = mensagens_chat(conv)
    em_atend = _em_atendimento(conv)
    if em_atend and not ao_vivo:
        st.rerun()  # passou a falar com uma pessoa: liga a atualização automática da conversa
    with st.container(height=280, border=False):
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(html.escape(preencher(LOJA["chat_boas_vindas"])))
        for _, m in msgs.iterrows():
            if m["quem"] not in QUEM_CHAT:
                continue
            papel, avatar = QUEM_CHAT[m["quem"]]
            with st.chat_message(papel, avatar=avatar):
                if m["quem"] == "loja":
                    st.caption(m["nome"] or LOJA.get("chat_nome_atendente") or "Atendente")
                st.markdown(html.escape(m["texto"]).replace("\n", "  \n"))
    if not em_atend:
        perguntas = LOJA.get("chat_perguntas", [])
        for i in range(0, len(perguntas), 2):
            for c, p in zip(st.columns(2), perguntas[i:i + 2]):
                c.button(p["pergunta"], key=f"chatp_{conv}_{i}_{p['pergunta'][:12]}", use_container_width=True,
                         on_click=_chat_pergunta_rapida, args=(conv, p))
    with st.form(f"chat_form_{conv}", clear_on_submit=False, border=False):
        st.text_input("Sua mensagem", key=f"chat_txt_{conv}", placeholder="Escreva a sua dúvida...",
                      label_visibility="collapsed", max_chars=500)
        st.form_submit_button("Enviar ➤", use_container_width=True, on_click=_chat_enviar, args=(conv,))
    if not em_atend:
        st.button("🙋 Falar com uma pessoa", key=f"chat_humano_{conv}", use_container_width=True,
                  on_click=_chat_chamar_pessoa, args=(conv,))
    else:
        st.caption("🙋 Você está falando com a equipe. A resposta aparece aqui sozinha.")
    texto = urllib.parse.quote(f"Olá! Vim pelo chat da loja e quero tirar uma dúvida.")
    st.link_button("💬 Prefiro o WhatsApp", f"https://wa.me/{LOJA['whatsapp']}?text={texto}",
                   use_container_width=True)


@st.fragment
def _chat_cliente_parado(conv: str):
    _desenhar_chat_cliente(conv, ao_vivo=False)


@st.fragment(run_every=5)
def _chat_cliente_ao_vivo(conv: str):
    """Quando o cliente chama uma pessoa, a conversa se atualiza sozinha a cada 5 segundos."""
    _desenhar_chat_cliente(conv, ao_vivo=True)


def chat_cliente():
    """A caixinha de chat na barra da esquerda da loja."""
    if not LOJA.get("chat_ligado", True):
        return
    conv = _conversa_atual()
    bola, situacao = _status_atendimento()
    st.markdown(f"<div style='text-align:center;font-size:.8rem;color:#4a5568;'>{bola} Atendimento: "
                f"<b>{situacao}</b></div>", unsafe_allow_html=True)
    with st.expander("💬 Chat: tire suas dúvidas aqui"):
        st.caption(f"{bola} {situacao} · Horário: {texto_horario()}")
        st.text_input("Seu nome (opcional)", key="chat_nome", max_chars=60)
        if _em_atendimento(conv):
            _chat_cliente_ao_vivo(conv)
        else:
            _chat_cliente_parado(conv)


# ===============================================================
# ENGRENAGEM DISCRETA DO ADMINISTRADOR (canto superior direito)
# ===============================================================
@st.dialog("Acesso do administrador")
def abrir_login_admin():
    if not SENHA_ADMIN:
        st.error("A senha do painel ainda não foi configurada. No site do Streamlit, abra Settings > Secrets "
                 "e coloque a linha SENHA_ADMIN = \"sua-senha\".")
        return
    bloqueado = st.session_state.get("login_bloqueado_ate", 0) - time.time()
    if bloqueado > 0:
        st.error(f"Muitas tentativas erradas. Espere {int(bloqueado // 60) + 1} minuto(s) e tente de novo.")
        return
    senha = st.text_input("Senha", type="password", key="senha_admin")
    if st.button("Entrar", type="primary", key="btn_entrar_admin"):
        if hmac.compare_digest(senha.encode("utf-8"), SENHA_ADMIN.encode("utf-8")):
            st.session_state.admin = True
            st.session_state.login_erros = 0
            st.rerun()
        else:
            erros = st.session_state.get("login_erros", 0) + 1
            st.session_state.login_erros = erros
            if erros >= 5:  # 5 erros seguidos: bloqueia por 5 minutos
                st.session_state.login_bloqueado_ate = time.time() + 300
                st.session_state.login_erros = 0
            time.sleep(1)  # deixa mais lento quem tenta adivinhar a senha
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
    padding: 2px 10px !important; min-height: 0 !important; height: clamp(28px, calc((100vh - 200px) / 20), 52px); font-weight: 600 !important; box-shadow: none !important; }
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


@st.fragment(run_every=15)
def aviso_chat_admin():
    """Roda a cada 15 s em qualquer tela do painel: marca você como online e avisa se tem cliente esperando."""
    marcar_dono_online()
    if not LOJA.get("chat_ligado", True):
        return
    r = resumo_conversas()
    esperando = r[r["esperando"]] if len(r) else r
    n = len(esperando)
    if n > st.session_state.get("chat_esperando_antes", 0):
        st.toast(f"💬 {n} cliente(s) esperando resposta no chat!", icon="🔔")
    st.session_state.chat_esperando_antes = n
    if n and st.session_state.get("secao_admin") != "💬 Chat ao vivo":
        c1, c2 = st.columns([4, 1])
        c1.info(f"💬 {n} cliente(s) esperando resposta no chat: " + ", ".join(esperando["nome"].head(4).tolist()))
        if c2.button("Responder", key="aviso_chat", type="primary", use_container_width=True):
            st.session_state.secao_admin = "💬 Chat ao vivo"
            st.rerun(scope="app")


def _responder_chat(conv: str):
    texto = st.session_state.get(f"resp_{conv}", "").strip()
    st.session_state[f"resp_{conv}"] = ""
    if texto:
        if not _em_atendimento(conv):  # você puxou a conversa: ela vira atendimento com pessoa
            gravar_msg(conv, "sistema", "chamou_atendente")
        gravar_msg(conv, "loja", texto, LOJA.get("chat_nome_atendente") or "Atendente")


def _encerrar_chat(conv: str):
    gravar_msg(conv, "sistema", "encerrado")


@st.fragment(run_every=5)
def painel_conversas():
    """Lista de conversas e a conversa aberta. Atualiza sozinha a cada 5 segundos."""
    marcar_dono_online()
    r = resumo_conversas()
    if r.empty:
        st.info("Nenhuma conversa ainda. Quando um cliente usar o chat da loja, ele aparece aqui.")
        return
    so_esperando = st.toggle("Mostrar só quem está esperando resposta", key="chat_so_esp")
    lista = r[r["esperando"]] if so_esperando else r
    if lista.empty:
        st.success("✅ Ninguém esperando resposta.")
        return
    rotulos = {row["conversa"]: (("🔴 " if row["esperando"] else ("🙋 " if row["humano"] else "🤖 "))
                                 + f"{row['nome']} · {row['data']} · {str(row['ultima'])[:40]}")
               for _, row in lista.head(60).iterrows()}
    conv = st.selectbox("Conversa", list(rotulos), format_func=lambda c: rotulos[c], key="chat_conv_sel")
    st.caption("🔴 esperando você · 🙋 falando com pessoa · 🤖 só com o assistente")
    msgs = mensagens_chat(conv)
    with st.container(height=380, border=True):
        for _, m in msgs.iterrows():
            if m["quem"] == "sistema":
                aviso = "🙋 Cliente pediu para falar com uma pessoa" if m["texto"] == "chamou_atendente" \
                    else "✅ Atendimento encerrado (voltou para o assistente)"
                st.caption(f"{m['data']} · {aviso}")
                continue
            papel, avatar = QUEM_CHAT.get(m["quem"], ("assistant", "🤖"))
            with st.chat_message(papel, avatar=avatar):
                quem = {"cliente": m["nome"] or "Cliente", "robo": "Assistente automático",
                        "loja": m["nome"] or "Você"}.get(m["quem"], "")
                st.caption(f"{quem} · {m['data']}")
                st.markdown(html.escape(m["texto"]).replace("\n", "  \n"))
    with st.form(f"form_resp_{conv}", border=False):
        st.text_area("Sua resposta", key=f"resp_{conv}", height=80, placeholder="Escreva a resposta para o cliente...")
        st.form_submit_button("📨 Enviar resposta", type="primary", use_container_width=True,
                              on_click=_responder_chat, args=(conv,))
    linha = r[r["conversa"] == conv].iloc[0]
    if linha["humano"]:
        st.button("✅ Encerrar atendimento", key=f"enc_{conv}", use_container_width=True,
                  on_click=_encerrar_chat, args=(conv,), help="A conversa volta para o assistente automático")
    cli = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
    nome_c = str(linha["nome"])
    achado = cli[cli["nome"].str.lower() == nome_c.lower()] if nome_c and nome_c != "Visitante" else cli.iloc[0:0]
    if len(achado):
        num = "".join(ch for ch in str(achado.iloc[0]["telefone"]) if ch.isdigit())
        st.link_button(f"💬 Continuar no WhatsApp com {nome_c}", f"https://wa.me/{numero_wpp(num)}",
                       use_container_width=True)


# ===============================================================
# SEPARADOR DE FOTOS (Gemini)
# Você manda várias fotos misturadas; o Gemini diz de qual categoria é cada uma e a foto é guardada
# na "pasta" daquela categoria no banco (Supabase). As categorias NÃO ficam no código: elas são lidas
# na hora da lista de produtos do painel. Criou, mudou ou apagou uma categoria? O separador já segue.
# Na dúvida, a foto vai para a pasta "Revisar".
# ===============================================================
GEMINI_MODELOS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]  # plano grátis
FOTO_SEP_MAX_MB = 10


class ErroGemini(Exception):
    pass


def chave_gemini() -> str:
    return str(_segredo("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()


def categorias_do_painel() -> list:
    """A MESMA lista de categorias do painel de Produtos (lida na hora, nada fixo no código)."""
    df = carregar_produtos()
    return sorted({str(c).strip() for c in df["categoria"].tolist() if str(c).strip()} - {PASTA_REVISAR})


def _pistas_categorias(categorias: list) -> str:
    """Monta, para o Gemini, uma linha por categoria com exemplos de produtos dela (ajuda a acertar)."""
    df = carregar_produtos()
    linhas = []
    for cat in categorias:
        grupo = df[df["categoria"].astype(str).str.strip() == cat]
        modelos = ", ".join(grupo["modelo"].astype(str).head(4).tolist())
        desc = next((str(d) for d in grupo["descricao"].tolist() if str(d).strip()), "")[:160]
        extra = "; ".join(x for x in [f"produtos: {modelos}" if modelos else "", desc] if x)
        linhas.append(f"- {cat}" + (f" ({extra})" if extra else ""))
    return "\n".join(linhas)


def preparar_foto(dados: bytes, lado_max: int) -> bytes:
    """Gira a foto do jeito certo, tira transparência e diminui (foto menor = banco leve e Gemini rápido)."""
    from PIL import Image, ImageOps
    img = Image.open(io.BytesIO(dados))
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fundo = Image.new("RGB", img.size, (255, 255, 255))
        fundo.paste(img, mask=img.split()[-1])
        img = fundo
    else:
        img = img.convert("RGB")
    img.thumbnail((lado_max, lado_max))
    saida = io.BytesIO()
    img.save(saida, "JPEG", quality=85, optimize=True)
    return saida.getvalue()


def _chamar_gemini(modelo: str, corpo: dict) -> dict:
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": chave_gemini()}, method="POST")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def classificar_foto(jpeg: bytes, categorias: list) -> dict:
    """Pergunta ao Gemini de qual categoria é a foto. Devolve {categoria, confianca, motivo}."""
    import urllib.error
    opcoes = categorias + ["Nenhuma"]
    prompt = (
        "Você separa fotos de produtos de uma loja de presentes personalizados.\n"
        f"Categorias que existem hoje na loja:\n{_pistas_categorias(categorias)}\n\n"
        "Olhe a foto e diga a qual categoria ela pertence, usando EXATAMENTE um dos nomes da lista. "
        "Se a foto não for de nenhuma delas, responda \"Nenhuma\". "
        "Em \"confianca\", dê um número de 0 a 1: perto de 1 só se tiver certeza; se ficar em dúvida entre "
        "duas categorias ou a foto estiver ruim, dê um número baixo. "
        "Em \"motivo\", explique em poucas palavras, em português, o que você viu na foto.")
    corpo = {
        "contents": [{"parts": [{"text": prompt},
                                {"inline_data": {"mime_type": "image/jpeg",
                                                 "data": base64.b64encode(jpeg).decode()}}]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {"categoria": {"type": "STRING", "enum": opcoes},
                               "confianca": {"type": "NUMBER"},
                               "motivo": {"type": "STRING"}},
                "required": ["categoria", "confianca", "motivo"]},
        },
    }
    modelos = list(GEMINI_MODELOS)
    preferido = st.session_state.get("gemini_modelo_ok")
    if preferido in modelos:
        modelos.remove(preferido)
        modelos.insert(0, preferido)
    ultimo_erro = "sem resposta"
    for modelo in modelos:
        for tentativa in range(4):
            try:
                resp = _chamar_gemini(modelo, corpo)
            except urllib.error.HTTPError as e:
                texto = e.read().decode("utf-8", "ignore")
                if e.code == 429:  # passou do limite por minuto do plano grátis: espera e tenta de novo
                    espera = 20
                    try:
                        for d in json.loads(texto)["error"].get("details", []):
                            if "retryDelay" in d:
                                espera = float(str(d["retryDelay"]).rstrip("s"))
                    except Exception:
                        pass
                    if "PerDay" in texto or "per day" in texto.lower():
                        raise ErroGemini("O limite grátis de hoje do Gemini acabou. Tente de novo amanhã.")
                    ultimo_erro = "limite por minuto do Gemini"
                    time.sleep(min(max(espera, 5), 60) + 1)
                    continue
                if e.code in (400, 401, 403) and ("API key" in texto or "API_KEY" in texto or e.code != 400):
                    raise ErroGemini("A chave GEMINI_API_KEY foi recusada pelo Google. Confira nos Secrets.")
                if e.code in (500, 503):
                    ultimo_erro = "Gemini ocupado"
                    time.sleep(5)
                    continue
                ultimo_erro = f"erro {e.code} no modelo {modelo}"
                break  # modelo indisponível (ex.: 404): tenta o próximo da lista
            except Exception as e:
                ultimo_erro = type(e).__name__
                time.sleep(3)
                continue
            try:
                texto = resp["candidates"][0]["content"]["parts"][0]["text"]
                dados = json.loads(texto)
            except Exception:
                ultimo_erro = "resposta vazia do Gemini"
                break
            st.session_state.gemini_modelo_ok = modelo
            try:
                conf = float(dados.get("confianca", 0))
            except Exception:
                conf = 0.0
            return {"categoria": str(dados.get("categoria", "")).strip(),
                    "confianca": max(0.0, min(conf, 1.0)),
                    "motivo": str(dados.get("motivo", "")).strip()[:200]}
    raise ErroGemini(f"Não consegui falar com o Gemini ({ultimo_erro}).")


def ler_fotos_sep() -> list:
    return ler_json(ARQ_FOTOS_SEP, [])


def apagar_bin(nome: str):
    if URL_BANCO:
        with _banco().begin() as c:
            c.execute(_sql("DELETE FROM binarios WHERE nome = :n"), {"n": nome})
    elif os.path.exists(nome):
        os.remove(nome)


def guardar_foto_sep(jpeg: bytes, nome_original: str, pasta: str, sugestao: str, confianca: float,
                     motivo: str, hash_foto: str) -> dict:
    fid = uuid.uuid4().hex[:12]
    arquivo = f"{PASTA_FOTOS_SEP}/{fid}.jpg"
    gravar_bin(arquivo, jpeg)
    reg = {"id": fid, "pasta": pasta, "arquivo": arquivo, "nome": nome_original,
           "data": datetime.now().strftime("%d/%m/%Y %H:%M"), "sugestao": sugestao,
           "confianca": round(confianca, 2), "motivo": motivo, "hash": hash_foto}
    with trava():
        lista = ler_fotos_sep()
        lista.append(reg)
        gravar_json(ARQ_FOTOS_SEP, lista)
    return reg


def mover_fotos_sep(ids: set, pasta: str):
    with trava():
        lista = ler_fotos_sep()
        for f in lista:
            if f["id"] in ids:
                f["pasta"] = pasta
        gravar_json(ARQ_FOTOS_SEP, lista)


def excluir_foto_sep(fid: str):
    with trava():
        lista = ler_fotos_sep()
        alvo = [f for f in lista if f["id"] == fid]
        gravar_json(ARQ_FOTOS_SEP, [f for f in lista if f["id"] != fid])
    for f in alvo:
        apagar_bin(f["arquivo"])


def separar_fotos(arquivos: list, limite: float, aviso=None) -> dict:
    """Manda cada foto para o Gemini e guarda na pasta certa. Devolve um resumo do que aconteceu."""
    import hashlib
    categorias = categorias_do_painel()
    ja_tem = {f.get("hash") for f in ler_fotos_sep()}
    resumo = {"total": len(arquivos), "por_pasta": {}, "repetidas": 0, "erros": []}
    barra = st.progress(0.0, text="Começando...")
    for n, arq in enumerate(arquivos, start=1):
        barra.progress((n - 1) / len(arquivos), text=f"Foto {n} de {len(arquivos)}: {arq.name}")
        bruto = arq.getvalue()
        hash_foto = hashlib.sha1(bruto).hexdigest()
        if hash_foto in ja_tem:
            resumo["repetidas"] += 1
            continue
        if len(bruto) > FOTO_SEP_MAX_MB * 1024 * 1024:
            resumo["erros"].append(f"{arq.name}: passa de {FOTO_SEP_MAX_MB} MB")
            continue
        try:
            guardar = preparar_foto(bruto, 1600)
            pequena = preparar_foto(bruto, 768)
        except Exception:
            resumo["erros"].append(f"{arq.name}: não consegui abrir a imagem")
            continue
        try:
            r = classificar_foto(pequena, categorias)
            cat, conf, motivo = r["categoria"], r["confianca"], r["motivo"]
        except ErroGemini as e:
            resumo["erros"].append(f"{arq.name}: {e}")
            if "chave" in str(e).lower() or "hoje" in str(e).lower():
                # sem chave ou sem cota: guarda o resto no Revisar para não perder as fotos
                for resto in arquivos[n - 1:]:
                    b = resto.getvalue()
                    h = hashlib.sha1(b).hexdigest()
                    if h in ja_tem or len(b) > FOTO_SEP_MAX_MB * 1024 * 1024:
                        continue
                    try:
                        guardar_foto_sep(preparar_foto(b, 1600), resto.name, PASTA_REVISAR, "", 0.0,
                                         "Não foi separada: " + str(e), h)
                        ja_tem.add(h)
                        resumo["por_pasta"][PASTA_REVISAR] = resumo["por_pasta"].get(PASTA_REVISAR, 0) + 1
                    except Exception:
                        pass
                break
            cat, conf, motivo = "", 0.0, f"O Gemini não respondeu ({e})"
        if cat in categorias and conf >= limite:
            pasta = cat
        else:
            pasta = PASTA_REVISAR
            if cat not in categorias:
                motivo = (motivo + " · " if motivo else "") + "não parece ser de nenhuma categoria"
            else:
                motivo = (motivo + " · " if motivo else "") + f"certeza baixa ({conf:.0%})"
        guardar_foto_sep(guardar, arq.name, pasta, cat if cat in categorias else "", conf, motivo, hash_foto)
        ja_tem.add(hash_foto)
        resumo["por_pasta"][pasta] = resumo["por_pasta"].get(pasta, 0) + 1
    barra.progress(1.0, text="Pronto!")
    return resumo


# ===============================================================
# PAINEL DO ADMINISTRADOR
# ===============================================================
SECOES_ADMIN = {
    "VISÃO GERAL": ["📊 Resumo", "🔨 Mesa do chefe"],
    "CATÁLOGO": ["📦 Produtos", "🖼️ Fotos", "🗂️ Separador de fotos", "🎨 Galeria de artes"],
    "VENDAS": ["💬 Chat ao vivo", "👥 Clientes", "🧾 Pedidos", "🚚 Rastreio", "🏷️ Etiquetas", "🖨️ Artes", "📄 Nota fiscal", "📍 Frete"],
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

    # ----- Chat: você aparece online enquanto o painel está aberto, e vê quem está esperando -----
    if not URL_BANCO:
        st.warning("⚠️ Banco de dados não configurado: os dados estão ficando em arquivos e podem sumir quando o "
                   "app reiniciar. Coloque o endereço do Supabase nos Secrets do Streamlit.")
    aviso_chat_admin()

    # ---------------------------------------------------------- MESA DO CHEFE
    if secao == "🔨 Mesa do chefe":
        st.caption("Aprove os pedidos novos, mande para a produção e marque o que já foi enviado e entregue.")
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
            st.markdown("**✅ Esperando aprovação**")
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
    # ---------------------------------------------------------- CHAT AO VIVO
    elif secao == "💬 Chat ao vivo":
        p = _presenca()
        c1, c2 = st.columns([2, 3])
        disp = c1.toggle("🟢 Aparecer online para os clientes", value=p["disponivel"], key="chat_disp",
                         help="Desligue quando não puder responder. Com o painel fechado, você aparece offline.")
        p["disponivel"] = disp
        bola, situacao = _status_atendimento()
        c2.info(f"O cliente vê agora: {bola} **{situacao}** · Expediente: {texto_horario()}")
        t_conv, t_perg, t_msgs, t_wpp = st.tabs(["💬 Conversas", "❓ Perguntas rápidas", "🤖 Mensagens e horário",
                                                 "📱 WhatsApp"])
        with t_conv:
            painel_conversas()
        with t_perg:
            st.caption("Estas são as caixinhas de pergunta que o cliente toca no chat. Em 'Palavras-chave', escreva "
                       "as palavras que o cliente pode usar (separadas por vírgula): o assistente usa elas para "
                       "achar a resposta quando o cliente escreve a dúvida com as próprias palavras. "
                       "Na resposta você pode usar {horario}, {frete_gratis}, {loja}, {link} e {whatsapp}.")
            perg_df = pd.DataFrame(LOJA.get("chat_perguntas", []), columns=["pergunta", "palavras", "resposta"])
            perg_ed = st.data_editor(perg_df, num_rows="dynamic", use_container_width=True, key="editor_perguntas",
                                     column_config={
                                         "pergunta": st.column_config.TextColumn("Caixinha (o que o cliente vê)",
                                                                                 required=True, max_chars=40),
                                         "palavras": st.column_config.TextColumn("Palavras-chave", width="medium"),
                                         "resposta": st.column_config.TextColumn("Resposta automática", width="large",
                                                                                 required=True)})
            if st.button("💾 Salvar perguntas", type="primary", key="salvar_perguntas"):
                LOJA["chat_perguntas"] = [{k: str(v).strip() for k, v in row.items()}
                                          for row in perg_ed.fillna("").to_dict("records")
                                          if str(row.get("pergunta", "")).strip() and str(row.get("resposta", "")).strip()]
                gravar_loja(LOJA)
                st.success("Perguntas salvas!")
            st.markdown("**🧪 Testar o assistente**")
            teste = st.text_input("Escreva uma pergunta como se fosse o cliente", key="teste_robo",
                                  placeholder="ex.: quanto tempo demora pra chegar em SP?")
            if teste.strip():
                st.write("🤖 " + (resposta_automatica(teste) or preencher(LOJA["chat_nao_entendi"])))
        with t_msgs, st.form("form_chat_msgs"):
            m_lig = st.checkbox("Mostrar o chat na loja", value=bool(LOJA.get("chat_ligado", True)))
            h1, h2, h3 = st.columns([1, 1, 2])
            hi, mi = _hora(LOJA.get("exp_inicio"), "08:00")
            hf, mf = _hora(LOJA.get("exp_fim"), "18:00")
            from datetime import time as hora_do_dia
            m_ini = h1.time_input("Atendimento começa", hora_do_dia(hi, mi), step=1800)
            m_fim = h2.time_input("Atendimento termina", hora_do_dia(hf, mf), step=1800)
            m_dias = h3.multiselect("Dias de atendimento", DIAS_SEMANA,
                                    default=[DIAS_SEMANA[int(d)] for d in LOJA.get("exp_dias", [0, 1, 2, 3, 4])])
            m_nome = st.text_input("Seu nome no chat (aparece quando você responde)",
                                   value=LOJA.get("chat_nome_atendente", ""), placeholder="ex.: João, da loja")
            st.caption("Você pode usar {loja}, {horario}, {link}, {whatsapp} e {frete_gratis} nas mensagens.")
            m_boas = st.text_area("👋 Boas-vindas (primeira mensagem do chat)", LOJA["chat_boas_vindas"])
            m_res = st.text_area("✅ Depois de uma resposta automática", LOJA["chat_resolveu"])
            m_nao = st.text_area("🤔 Quando o assistente não entende", LOJA["chat_nao_entendi"])
            m_cham = st.text_area("🙋 Quando o cliente chama uma pessoa e você está online", LOJA["chat_chamando"])
            m_off = st.text_area("⚪ No horário de atendimento, mas você está offline", LOJA["chat_offline"])
            m_fora = st.text_area("🌙 Fora do horário de atendimento", LOJA["chat_fora_expediente"])
            if st.form_submit_button("💾 Salvar mensagens e horário", type="primary"):
                LOJA.update({"chat_ligado": m_lig, "exp_inicio": m_ini.strftime("%H:%M"),
                             "exp_fim": m_fim.strftime("%H:%M"), "exp_dias": [DIAS_SEMANA.index(d) for d in m_dias],
                             "chat_nome_atendente": m_nome.strip(), "chat_boas_vindas": m_boas,
                             "chat_resolveu": m_res, "chat_nao_entendi": m_nao, "chat_chamando": m_cham,
                             "chat_offline": m_off, "chat_fora_expediente": m_fora})
                gravar_loja(LOJA)
                st.rerun()
        with t_wpp:
            st.markdown("""
**Respostas automáticas no WhatsApp** (precisa do app **WhatsApp Business**, que é gratuito)

O WhatsApp não deixa a loja responder por você, mas o próprio WhatsApp Business faz isso sozinho. Configure uma vez:
1. No WhatsApp Business, toque nos **três pontinhos > Ferramentas comerciais**.
2. **Mensagem de saudação**: ative e cole o texto 1. Ela vai para quem chama pela primeira vez.
3. **Mensagem de ausência**: ative, escolha **Fora do horário comercial** e cole o texto 2.
4. Em **Perfil comercial > Horário comercial**, coloque o mesmo horário do chat.
5. **Respostas rápidas**: cadastre os atalhos do texto 3. Na conversa, digite **/** e escolha a resposta.
""")
            with st.form("form_wpp"):
                w_sau = st.text_area("Texto 1: saudação (pode usar {loja}, {link}, {horario})", LOJA["wpp_saudacao"],
                                     height=150)
                w_aus = st.text_area("Texto 2: ausência (pode usar {loja}, {link}, {horario})", LOJA["wpp_ausencia"],
                                     height=170)
                if st.form_submit_button("💾 Salvar textos do WhatsApp", type="primary"):
                    LOJA.update({"wpp_saudacao": w_sau, "wpp_ausencia": w_aus})
                    gravar_loja(LOJA)
                    st.rerun()
            if not LOJA.get("link_loja"):
                st.warning("Coloque o endereço da loja em 🎨 Loja e redes para o {link} sair certo.")
            st.markdown("**Texto 1 pronto para copiar** (toque no ícone de copiar, no canto)")
            st.code(preencher(LOJA["wpp_saudacao"]), language=None)
            st.markdown("**Texto 2 pronto para copiar**")
            st.code(preencher(LOJA["wpp_ausencia"]), language=None)
            st.markdown("**Texto 3: respostas rápidas** (as mesmas perguntas do chat)")
            for n, pq in enumerate(LOJA.get("chat_perguntas", []), start=1):
                atalho = "/" + (_normal(pq["pergunta"]).split() or [f"r{n}"])[0][:12]
                st.caption(f"Atalho {atalho}")
                st.code(preencher(pq["resposta"]), language=None)
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
        atalhos = [("🔨 Mesa do chefe", "🔨 Mesa do chefe"), ("➕ Novo produto", "📦 Produtos"),
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
        def criar_modelos(categoria: str, nome_base: str, qtd: int, preco: float, visivel: bool,
                          numerar: bool = False) -> int:
            """Cria vários modelos de uma vez: Nome Modelo 1, Nome Modelo 2... sem repetir nomes que já existem."""
            existentes = set(df_produtos["modelo"].astype(str))
            ficha = FICHA_PADRAO.get(categoria, ("", "", "", ""))
            linhas, n = [], 0
            while len(linhas) < qtd:
                n += 1
                nome = nome_base if (qtd == 1 and n == 1 and not numerar) else f"{nome_base} Modelo {n}"
                if nome in existentes:
                    continue
                linha = {c: "" for c in COLUNAS_PRODUTOS}
                linha.update({"categoria": categoria, "modelo": nome, "preco": preco, "ativo": visivel,
                              "destaque": False, "estoque": 0, "custo": 0.0, "peso_g": 0,
                              "prazo_producao_dias": 5, "preco_promocional": 0.0,
                              "descricao": ficha[0], "para_que_serve": ficha[1], "medidas": ficha[2],
                              "dicas": ficha[3], "sku": f"{categoria[:3].upper()}-{len(existentes) + len(linhas) + 1:03d}"})
                linhas.append(linha)
                existentes.add(nome)
            gravar_csv(ARQ_PRODUTOS, pd.concat([df_produtos, pd.DataFrame(linhas)], ignore_index=True))
            return len(linhas)

        if st.session_state.get("aviso_criados"):
            st.success(st.session_state.pop("aviso_criados"))
        n1, n2 = st.columns(2)
        with n1.expander("➕ Nova categoria"):
            nova_cat = st.text_input("Nome da nova categoria", key="nova_cat_nome")
            c1, c2 = st.columns(2)
            qtd_cat = c1.number_input("Quantos modelos criar", min_value=1, max_value=200, value=1, step=1,
                                      key="nova_cat_qtd")
            preco_cat = c2.number_input("Preço de cada modelo (R$)", min_value=0.0, value=50.0,
                                        step=1.0, key="nova_cat_preco")
            vis_cat = st.checkbox("Já aparecer para o cliente", value=True, key="nova_cat_vis")
            if st.button(f"Criar categoria com {int(qtd_cat)} modelo(s)", type="primary", key="btn_nova_cat"):
                if nova_cat.strip():
                    feitos = criar_modelos(nova_cat.strip(), nova_cat.strip(), int(qtd_cat),
                                           preco_cat, vis_cat, numerar=True)
                    st.session_state.aviso_criados = f"✅ Categoria {nova_cat.strip()} criada com {feitos} modelo(s)."
                    st.rerun()
                else:
                    st.error("Digite o nome da categoria.")
        with n2.expander("➕ Novo produto"):
            cats_existentes = sorted(df_produtos["categoria"].unique().tolist())
            np_cat = st.selectbox("Categoria", cats_existentes, key="np_cat") if cats_existentes else ""
            np_nome = st.text_input("Nome do produto", key="np_nome")
            c1, c2 = st.columns(2)
            np_qtd = c1.number_input("Quantos modelos criar", min_value=1, max_value=200, value=1, step=1,
                                     key="np_qtd", help="Com mais de 1, os nomes ficam: Nome Modelo 1, Nome Modelo 2...")
            np_preco = c2.number_input("Preço de cada modelo (R$)", min_value=0.0, value=50.0, step=1.0, key="np_preco")
            np_vis = st.checkbox("Já aparecer para o cliente", value=True, key="np_vis")
            if int(np_qtd) > 1 and np_nome.strip():
                st.caption(f"Vai criar: {np_nome.strip()} Modelo 1 até {np_nome.strip()} Modelo {int(np_qtd)}.")
            if st.button(f"Criar {int(np_qtd)} modelo(s)", type="primary", key="btn_novo_prod"):
                if np_nome.strip() and np_cat:
                    feitos = criar_modelos(np_cat, np_nome.strip(), int(np_qtd), np_preco, np_vis)
                    st.session_state.aviso_criados = f"✅ {feitos} modelo(s) de {np_nome.strip()} criados em {np_cat}."
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
    # ---------------------------------------------------------- SEPARADOR DE FOTOS (Gemini)
    elif secao == "🗂️ Separador de fotos":
        st.caption("Envie várias fotos misturadas de uma vez. O Gemini olha cada uma, descobre a categoria e "
                   "guarda na pasta certa. Na dúvida, a foto vai para a pasta **Revisar**.")
        cats_sep = categorias_do_painel()
        fotos_sep = ler_fotos_sep()
        if not chave_gemini():
            st.error("🔑 Falta a chave do Gemini. No Streamlit, abra Settings → Secrets e acrescente uma linha: "
                     "`GEMINI_API_KEY = \"sua-chave\"` (a chave grátis sai em aistudio.google.com).")
        if not cats_sep:
            st.info("Você ainda não tem categorias. Crie em 📦 Produtos → Nova categoria.")
        else:
            st.markdown("**Categorias que o separador usa agora** (vêm do seu painel de Produtos; mudou lá, "
                        "muda aqui sozinho): " + " · ".join(f"`{c}`" for c in cats_sep))
        if st.session_state.get("sep_resumo"):
            r = st.session_state.pop("sep_resumo")
            partes = [f"**{p}**: {q}" for p, q in sorted(r["por_pasta"].items(), key=lambda x: x[0] == PASTA_REVISAR)]
            st.success(f"✅ {sum(r['por_pasta'].values())} foto(s) separada(s). " + " · ".join(partes))
            if r["repetidas"]:
                st.info(f"♻️ {r['repetidas']} foto(s) já tinham sido separadas antes e foram puladas.")
            for e in r["erros"]:
                st.warning(e)

        with st.container(border=True):
            limite_sep = st.slider("Certeza mínima para separar sozinho (abaixo disso vai para Revisar)",
                                   50, 100, int(LOJA.get("separador_certeza", 80)), 5, format="%d%%",
                                   key="sep_limite")
            if limite_sep != int(LOJA.get("separador_certeza", 80)):
                LOJA["separador_certeza"] = int(limite_sep)
                gravar_loja(LOJA)
            with st.form("form_separador", clear_on_submit=True):
                sep_arqs = st.file_uploader(f"Fotos (pode escolher várias de uma vez, até {FOTO_SEP_MAX_MB} MB cada)",
                                            type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
                enviar_sep = st.form_submit_button("🤖 Separar fotos", type="primary",
                                                   disabled=not (chave_gemini() and cats_sep))
            if enviar_sep:
                if not sep_arqs:
                    st.error("Escolha pelo menos uma foto.")
                else:
                    st.session_state.sep_resumo = separar_fotos(sep_arqs, limite_sep / 100)
                    st.rerun()

        # ----- Pastas -----
        titulo_secao("📁 Pastas")
        # Foto de categoria que foi apagada ou renomeada volta para o Revisar automaticamente
        orfas = [f for f in fotos_sep if f["pasta"] != PASTA_REVISAR and f["pasta"] not in cats_sep]
        contagem = {c: sum(1 for f in fotos_sep if f["pasta"] == c) for c in cats_sep}
        n_revisar = sum(1 for f in fotos_sep if f["pasta"] == PASTA_REVISAR) + len(orfas)
        rotulos = {f"⚠️ {PASTA_REVISAR} ({n_revisar})": PASTA_REVISAR}
        rotulos.update({f"📁 {c} ({contagem[c]})": c for c in cats_sep})
        escolha = st.selectbox("Abrir pasta", list(rotulos), key="sep_pasta")
        pasta_ver = rotulos[escolha]
        destinos = cats_sep + [PASTA_REVISAR]

        if pasta_ver == PASTA_REVISAR:
            mostrar_sep = [f for f in fotos_sep if f["pasta"] == PASTA_REVISAR] + orfas
            for antiga in sorted({f["pasta"] for f in orfas}):
                ids_antiga = {f["id"] for f in orfas if f["pasta"] == antiga}
                with st.container(border=True):
                    o1, o2, o3 = st.columns([3, 2, 1])
                    o1.markdown(f"🗃️ **{len(ids_antiga)} foto(s)** da categoria **{antiga}**, que não existe mais "
                                "(foi apagada ou renomeada).")
                    novo = o2.selectbox("Mover todas para", cats_sep, key=f"sep_orf_{antiga}",
                                        label_visibility="collapsed") if cats_sep else None
                    if novo and o3.button("Mover todas", key=f"sep_orf_btn_{antiga}", use_container_width=True):
                        mover_fotos_sep(ids_antiga, novo)
                        st.rerun()
            pendentes = [f for f in mostrar_sep if cats_sep]
            if pendentes and chave_gemini():
                if st.button(f"🔁 Pedir para o Gemini tentar de novo as {len(pendentes)} foto(s) do Revisar",
                             key="sep_retentar"):
                    movidas, barra = 0, st.progress(0.0)
                    for n, f in enumerate(pendentes, start=1):
                        barra.progress(n / len(pendentes), text=f"Foto {n} de {len(pendentes)}")
                        try:
                            bruto = ler_bin(f["arquivo"])
                            r = classificar_foto(preparar_foto(bruto, 768), cats_sep)
                        except ErroGemini as e:
                            st.warning(str(e))
                            break
                        except Exception:
                            continue
                        if r["categoria"] in cats_sep and r["confianca"] >= limite_sep / 100:
                            mover_fotos_sep({f["id"]}, r["categoria"])
                            movidas += 1
                    st.session_state.sep_resumo = {"por_pasta": {"saíram do Revisar": movidas},
                                                   "repetidas": 0, "erros": []}
                    st.rerun()
        else:
            mostrar_sep = [f for f in fotos_sep if f["pasta"] == pasta_ver]

        mostrar_sep = list(reversed(mostrar_sep))  # mais novas primeiro
        if not mostrar_sep:
            st.caption("Pasta vazia.")
        else:
            por_pagina = 12
            paginas = (len(mostrar_sep) - 1) // por_pagina + 1
            pag = st.number_input(f"Página (de {paginas})", 1, paginas, 1, key=f"sep_pag_{pasta_ver}") if paginas > 1 else 1
            trecho = mostrar_sep[(pag - 1) * por_pagina: pag * por_pagina]
            for ini in range(0, len(trecho), 4):
                for col, f in zip(st.columns(4), trecho[ini:ini + 4]):
                    with col, st.container(border=True):
                        bruto = ler_bin(f["arquivo"])
                        if bruto:
                            st.image(bruto, use_container_width=True)
                        else:
                            st.caption("(imagem não encontrada)")
                        st.markdown(f"**{html.escape(f.get('nome', ''))}**")
                        info = f"{f.get('data', '')}"
                        if f["pasta"] != PASTA_REVISAR and f["pasta"] not in cats_sep:
                            info += f" · era de {f['pasta']}"
                        elif f.get("sugestao") and f["pasta"] == PASTA_REVISAR:
                            info += f" · palpite: {f['sugestao']} ({float(f.get('confianca') or 0):.0%})"
                        elif f.get("confianca") not in (None, ""):
                            info += f" · certeza {float(f.get('confianca') or 0):.0%}"
                        st.caption(info)
                        if f.get("motivo"):
                            st.caption(f"🤖 {f['motivo']}")
                        atual_idx = destinos.index(f["pasta"]) if f["pasta"] in destinos else (
                            destinos.index(f["sugestao"]) if f.get("sugestao") in destinos else 0)
                        dest = st.selectbox("Pasta", destinos, index=atual_idx, key=f"sep_dest_{f['id']}",
                                            label_visibility="collapsed")
                        b1, b2 = st.columns(2)
                        if b1.button("Mover", key=f"sep_mov_{f['id']}", use_container_width=True,
                                     disabled=dest == f["pasta"]):
                            mover_fotos_sep({f["id"]}, dest)
                            st.rerun()
                        if b2.button("🗑️", key=f"sep_del_{f['id']}", use_container_width=True, help="Excluir foto"):
                            excluir_foto_sep(f["id"])
                            st.rerun()
                        if f["pasta"] in cats_sep and bruto:
                            with st.popover("🖼️ Usar no produto", use_container_width=True):
                                mods = df_produtos[df_produtos["categoria"].astype(str).str.strip() == f["pasta"]]["modelo"].tolist()
                                prod = st.selectbox("Produto", mods, key=f"sep_prod_{f['id']}")
                                if st.button("Usar esta foto", key=f"sep_usar_{f['id']}", type="primary"):
                                    novo_df = df_produtos.copy()
                                    m = (novo_df["categoria"].astype(str).str.strip() == f["pasta"]) & (novo_df["modelo"] == prod)
                                    novo_df.loc[m, "imagem"] = "data:image/jpeg;base64," + base64.b64encode(bruto).decode()
                                    gravar_csv(ARQ_PRODUTOS, novo_df)
                                    st.rerun()
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
                    with trava():
                        # Clientes que chegaram pela loja enquanto você editava não são apagados
                        agora_cli = ler_csv(ARQ_CLIENTES, COLUNAS_CLIENTES)
                        tels_vistos = set(clientes["telefone"].astype(str))
                        novos_cli = agora_cli[~agora_cli["telefone"].astype(str).isin(tels_vistos)]
                        # e quem fez pedido nesse meio tempo mantém a contagem de pedidos certa
                        qtd_agora = dict(zip(agora_cli["telefone"].astype(str), agora_cli["qtd_pedidos"]))
                        ult_agora = dict(zip(agora_cli["telefone"].astype(str), agora_cli["ultimo_contato"]))
                        qtd_antes = dict(zip(clientes["telefone"].astype(str), clientes["qtd_pedidos"]))
                        for idx, cli_l in salvar.iterrows():
                            tel = str(cli_l["telefone"])
                            if tel in qtd_agora and str(qtd_agora[tel]) != str(qtd_antes.get(tel, "")):
                                salvar.at[idx, "qtd_pedidos"] = qtd_agora[tel]
                                salvar.at[idx, "ultimo_contato"] = ult_agora.get(tel, "")
                        gravar_csv(ARQ_CLIENTES, pd.concat([salvar, novos_cli], ignore_index=True))
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
            # Lê a lista na hora (dentro da trava) e só muda o que você mexeu:
            # pedidos novos que chegaram enquanto você editava continuam lá
            original = pedidos.set_index("id_pedido")
            with trava():
                completo = ler_csv(ARQ_PEDIDOS, COLUNAS_PEDIDOS)
                antes_st = dict(zip(completo["id_pedido"], completo["status"]))
                mudados = []
                for _, linha in ped_editado.iterrows():
                    pid = linha["id_pedido"]
                    if pid not in original.index:
                        continue
                    alvo = completo["id_pedido"] == pid
                    for campo in ["email", "status", "pagamento", "forma_pagamento", "obs_internas"]:
                        if str(linha[campo]) != str(original.at[pid, campo]):
                            completo.loc[alvo, campo] = linha[campo]
                            mudados.append(pid)
                gravar_csv(ARQ_PEDIDOS, completo)
                for pid in set(mudados):
                    novo_st = completo.loc[completo["id_pedido"] == pid, "status"].iloc[0]
                    depois_de_mudar_status(pid, antes_st.get(pid), novo_st)
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
                atualizar_pedido(id_sel, {"email": r_email, "status": r_status, "previsao_entrega": r_prev,
                                          "transportadora": r_transp, "codigo_rastreio": r_cod.strip().upper(),
                                          "link_rastreio": r_link.strip()})
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
                    atualizar_pedido(id_sel, dados)
                    # Guarda também no cadastro do cliente
                    with trava():
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
        def html_arte(src, a, larg, alt_cm, encaixe, espelhar, borda, copias, papel) -> str:
            """Folha para imprimir a arte no tamanho exato, em centímetros, do jeito que o cliente montou."""
            e = lambda v: html.escape(str(v or ""))
            g = geo_de(a)
            if encaixe == "Como o cliente montou":
                ajuste = {"slice": "cover", "meet": "contain", "none": "fill"}.get(g["fit"], "cover")
            else:
                ajuste = "contain" if encaixe.startswith("Caber") else "cover"
                g.update(cx=0.5, cy=0.5, w=1.0, h=1.0, rot=0)
            linha = "1px dashed #555" if borda else "none"
            fonte = CSS_FONTES.get(a.get("fonte") or "Padrão", "Arial, sans-serif")
            foto = (f"<img src='{src}' style='position:absolute;left:{(g['cx'] - g['w'] / 2) * 100:.2f}%;"
                    f"top:{(g['cy'] - g['h'] / 2) * 100:.2f}%;width:{g['w'] * 100:.2f}%;height:{g['h'] * 100:.2f}%;"
                    f"object-fit:{ajuste};transform:rotate({float(g['rot']):.1f}deg);'>" if src else "")
            texto = (f"<div class='txt' style='left:{g['tx'] * 100:.2f}%;top:{g['ty'] * 100:.2f}%;font-family:{fonte};"
                     f"color:{e(a.get('cor_texto') or '#000')};font-size:{float(g['ts']) * alt_cm:.2f}cm;'>"
                     f"{e(a.get('texto'))}</div>" if a.get("texto") else "")
            caixa = (f"<div class='area' style='width:{larg}cm;height:{alt_cm}cm;border:{linha};'>"
                     f"<div class='miolo' style='{'transform:scaleX(-1);' if espelhar else ''}'>{foto}{texto}</div></div>")
            return f"""<html><head><meta charset='utf-8'><title>Arte</title><style>
@page {{ size: {papel}; margin: 8mm; }}
body {{ margin: 0; font-family: Arial; }}
.grade {{ display: flex; flex-wrap: wrap; gap: 4mm; }}
.area {{ box-sizing: border-box; overflow: hidden; page-break-inside: avoid; background: #fff; position: relative; }}
.miolo {{ position: absolute; inset: 0; overflow: hidden; }}
.txt {{ position: absolute; transform: translate(-50%, -50%); text-align: center; line-height: 1.1; white-space: nowrap; font-weight: 700; }}
.info {{ font-size: 10px; color: #444; margin-bottom: 3mm; }}
</style></head><body onload='window.print()'>
<div class='info'>{e(a.get('item'))} · área {larg} x {alt_cm} cm · peça {e(a.get('cor_peca') or 'Branco')} · {e(a.get('lado') or 'Frente')}</div>
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
                    bruto = ler_bin(a.get("arquivo")) or b""  # a foto agora vem do banco
                    tem_foto = bool(bruto)
                    with col_a:
                        if tem_foto:
                            st.image(bruto, caption=a.get("arte_nome") or "Arte", use_container_width=True)
                            st.download_button("⬇️ Baixar arquivo original", bruto,
                                               os.path.basename(a["arquivo"].replace("\\", "/")),
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
                        st.markdown(f"**Peça:** {a.get('cor_peca') or 'Branco'} · **Lado:** {a.get('lado') or 'Frente'}")
                        previa_html = ler_previa(a.get("previa"))
                        if previa_html:
                            st.markdown("**Como o cliente montou:**")
                            components.html(previa_html, height=340)
                    with col_b:
                        molde = st.selectbox("Molde", list(MOLDES_IMPRESSAO.keys()), key=f"molde_{id_sel}_{n}")
                        lw, lh = MOLDES_IMPRESSAO[molde]
                        m1, m2 = st.columns(2)
                        larg = m1.number_input("Largura (cm)", 1.0, 60.0, float(lw), 0.5, key=f"larg_{id_sel}_{n}_{molde}")
                        alt_cm = m2.number_input("Altura (cm)", 1.0, 60.0, float(lh), 0.5, key=f"alt_{id_sel}_{n}_{molde}")
                        encaixe = st.radio("Encaixe da foto", ["Como o cliente montou", "Caber inteira",
                                                               "Preencher tudo (corta as bordas)"], key=f"enc_{id_sel}_{n}")
                        p1, p2 = st.columns(2)
                        espelhar = p1.checkbox("Espelhar (sublimação)", key=f"esp_{id_sel}_{n}")
                        borda = p2.checkbox("Linha de corte", value=True, key=f"bor_{id_sel}_{n}")
                        p3, p4 = st.columns(2)
                        dois_lados = 2 if a.get("lado") == "Frente e verso" else 1
                        copias = p3.number_input("Cópias", 1, 100, min(100, int(a.get("quantidade", 1) or 1) * dois_lados),
                                                 key=f"cop_{id_sel}_{n}",
                                                 help="Frente e verso já vem com o dobro de cópias")
                        papel = p4.selectbox("Papel", ["A4", "A3", "Carta"], key=f"pap_{id_sel}_{n}")
                    src = ""
                    if tem_foto:
                        ext = os.path.splitext(a["arquivo"])[1].lower().strip(".")
                        mime = "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
                        src = f"data:{mime};base64," + base64.b64encode(bruto).decode()
                    folha = html_arte(src, a, larg, alt_cm, encaixe, espelhar, borda, copias, papel)
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
            with trava():
                _entrar_estoque(material, qtd, custo, fornecedor, ref)

        def _entrar_estoque(material: str, qtd: float, custo: float, fornecedor: str, ref: str):
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
                with trava():
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
                with trava():
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
                            atualizar_pedido(id_sel, {"nf_status": nf_st, "nf_numero": nf_num.strip(),
                                                      "nf_chave": so_num, "nf_link": nf_lk.strip(),
                                                      "cpf_cnpj": nf_doc.strip()})
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
                l_tw = c1.text_input("Link do X (Twitter)", value=LOJA.get("twitter", ""),
                                     placeholder="https://x.com/sualoja")
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
                    "twitter": l_tw.strip(),
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
1. Clique em *Preparar backup* e depois em *Baixar backup completo*. Vem um arquivo `.zip` com a data no nome.
2. Guarde o arquivo numa pasta **Backup da Loja** (no computador, no celular ou no Google Drive).
3. Faça isso uma vez por semana. Seus dados ficam no banco e não somem, mas uma cópia extra é sempre bom.

O zip traz produtos, fotos, clientes, pedidos, **fotos e artes que os clientes enviaram**, conversas do chat,
frete, apresentações e configurações. A pasta *LEIA-ME* tem planilhas que abrem direto no Excel.
""")
        if st.button("📦 Preparar backup", key="bk_preparar", use_container_width=True):
            with st.spinner("Juntando tudo..."):
                st.session_state.bk_dados = gerar_backup_zip()
                st.session_state.bk_nome = f"backup_loja_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.zip"
        if st.session_state.get("bk_dados"):
            st.download_button("⬇️ Baixar backup completo", st.session_state.bk_dados, st.session_state.bk_nome,
                               "application/zip", type="primary", use_container_width=True)
        st.divider()
        st.markdown("**Restaurar um backup**")
        enviado = st.file_uploader("Envie o arquivo .zip do backup", type=["zip"], key="bk_zip")
        if enviado is not None and st.button("♻️ Restaurar agora (substitui os dados atuais)", key="bk_rest"):
            try:
                qtd = restaurar_backup_zip(enviado)
                st.success(f"✅ {qtd} arquivo(s) restaurado(s). Clique em qualquer seção do menu para ver os dados.")
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
    st.markdown("<div style='text-align:center;font-weight:700;font-size:.85rem;color:#4a5568;'>"
                "Fale com a gente</div>", unsafe_allow_html=True)
    barra_redes(LOJA, tamanho=50, sempre=True)
    chat_cliente()  # chat ao vivo: assistente automático + falar com você
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
                    rua_bairro = ", ".join(x for x in [frete_atual.get("rua", ""), frete_atual.get("bairro", "")] if x)
                    if rua_bairro:
                        st.caption(f"📍 Endereço: {rua_bairro}. Confira e preencha o número da casa lá embaixo.")
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
            st.text_input("Número da casa (obrigatório)", key="cli_numero", placeholder="ex.: 123 ou S/N")
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
    barra_redes(LOJA, tamanho=34, sempre=True)
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
                                                        zoom=False, dica="🔍"),
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
                                                        zoom=False, dica="🔍"),
                                            dica="Ver modelos")
                st.markdown(f"**{cat_nome}**  \nA partir de R$ {destaque['preco']:.2f}")
                if st.button(f"Ver {len(CATALOGO[cat_nome]['itens'])} modelos", key=f"btn_cat_{cat_nome}",
                             use_container_width=True) or clicou_foto:
                    registrar_clique("abriu_categoria", cat_nome)
                    ir_para("categoria", cat_nome)
                    st.rerun()
