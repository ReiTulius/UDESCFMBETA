import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json
import time

# ==============================================================================
# 1. CONFIGURAÇÕES DA PÁGINA E DESIGN SYSTEM (CSS CUSTOMIZADO)
# ==============================================================================
st.set_page_config(
    page_title="Music Hub - UDESC FM",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS que mantém o tema escuro e força o cursor (caret) e bordas ativas em vermelho
st.markdown("""
    <style>
    /* Estilização Geral do App */
    .stApp {
        background-color: #0f172a;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    
    /* Customização de Inputs (Cursor Vermelho e Borda de Foco) */
    input {
        caret-color: #ff4b4b !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 1px #ff4b4b !important;
    }
    div[data-baseweb="textarea"]:focus-within {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 1px #ff4b4b !important;
    }
    
    /* Tabelas e DataEditors */
    div[data-testid="stDataFrame"] {
        background-color: #1e293b;
        padding: 12px;
        border-radius: 10px;
    }
    
    /* Botões */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DIRETRIZES DE LINKS E WEBHOOKS (LEGADOS + EXPANSÃO CENTRAL)
# ==============================================================================
# Cole aqui os seus 3 Webhooks antigos que já funcionavam perfeitamente
WEBHOOK_TULIO = "SUA_URL_DO_WEBHOOK_ANTIGO_DO_TULIO"
WEBHOOK_JESSICA = "SUA_URL_DO_WEBHOOK_ANTIGO_DA_JESSICA"
WEBHOOK_SOM_DA_ILHA = "SUA_URL_DO_WEBHOOK_ANTIGO_DO_SOM_DA_ILHA"

# 🚀 URLs reais da nova planilha central de expansão por abas
WEBHOOK_EXPANSAO_CENTRAL = "https://script.google.com/macros/s/AKfycbxpqOsTpw0PTG7Zk9WTn7KV1cW4TEIB2jBxMrEgGqQuBRlp-dt2FCOs7gwlZVgBl9Jvew/exec"
URL_CSV_LISTA_ACERVOS = "https://docs.google.com/spreadsheets/d/1g8xnMOtDhhfN28s8MGAaKC5C2bPQ5FwHd4l-ksY4yNk/gviz/tq?tqx=out:csv&sheet=Lista_Acervos"

# ==============================================================================
# 3. FUNÇÕES MAESTRAS E LOGÍSTICA DE DADOS
# ==============================================================================
def carregar_acervos_novos():
    """Lê a aba de controle Lista_Acervos para renderizar dinamicamente no menu"""
    try:
        df_controle = pd.read_csv(URL_CSV_LISTA_ACERVOS)
        if not df_controle.empty and "Nome do Acervo" in df_controle.columns:
            return df_controle["Nome do Acervo"].dropna().tolist()
    except:
        pass
    return []

def extrair_dados_hashtags(texto):
    """Processa blocos de notas extraindo chaves mapeadas por hashtag"""
    if not isinstance(texto, str) or not texto.strip():
        return {}
    
    metadados = {}
    linhas = texto.split('\n')
    
    for line in linhas:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#musica '):
            metadados['Música'] = line.replace('#musica ', '', 1).strip()
        elif line.startswith('#artista '):
            metadados['Artista'] = line.replace('#artista ', '', 1).strip()
        elif line.startswith('#compositores '):
            metadados['Compositores'] = line.replace('#compositores ', '', 1).strip()
        elif line.startswith('#formato '):
            metadados['Formato'] = line.replace('#formato ', '', 1).strip()
        elif line.startswith('#ano '):
            metadados['Ano'] = line.replace('#ano ', '', 1).strip()
        elif line.startswith('#origem '):
            metadados['Origem'] = line.replace('#origem ', '', 1).strip()
        elif line.startswith('#genero '):
            metadados['Gênero'] = line.replace('#genero ', '', 1).strip()
        elif line.startswith('#genero_relacionado '):
            metadados['Gênero Relacionado'] = line.replace('#genero_relacionado ', '', 1).strip()
        elif line.startswith('#idioma_est '):
            metadados['Est/Idioma'] = line.replace('#idioma_est ', '', 1).strip()
        elif line.startswith('#classificacao '):
            metadados['Classificação'] = line.replace('#classificacao ', '', 1).strip()
        elif line.startswith('#andamento '):
            metadados['Andamento'] = line.replace('#andamento ', '', 1).strip()
        elif line.startswith('#participacoes '):
            metadados['Participações'] = line.replace('#participacoes ', '', 1).strip()
        elif line.startswith('#nome_arquivo '):
            metadados['Nome do Arquivo'] = line.replace('#nome_arquivo ', '', 1).strip()
            
    return metadados

# ==============================================================================
# 4. PAINEL DE NAVEGAÇÃO LATERAL (SIDEBAR)
# ==============================================================================
st.sidebar.markdown("<h2 style='color: #38bdf8; text-align: center; font-family: sans-serif;'>📻 UDESC FM</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; margin-top: -15px; color: #94a3b8;'>Acervo Oficial Integrado</p>", unsafe_allow_html=True)

# Navegação Exata das Suas Conquistas Anteriores
menu = st.sidebar.radio(
    "Navegação do Sistema:",
    ["📌 Painel Principal", "📂 Ver Todo o Acervo", "📥 Inserir Novo Lote", "📻 Roteiro Instagram"]
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔄 Sincronizar Bases", use_container_width=True):
    st.toast("Bases de dados atualizadas com sucesso!")
    time.sleep(0.5)
    st.rerun()

# ⚙️ MÓDULO ADMINISTRATIVO DE EXPANSÃO (O NOVO COMPONENTE)
st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #38bdf8;'>⚙️ Expansão de Acervos</h4>", unsafe_allow_html=True)
novo_acervo_nome = st.sidebar.text_input("Criar Novo Acervo (Ex: Acervo Marcos):", key="input_nova_aba")

if st.sidebar.button("Criar Estrutura na Nuvem 🚀", use_container_width=True):
    if novo_acervo_nome.strip():
        payload_criar = {
            "acao": "criar_acervo",
            "nome_acervo": novo_acervo_nome.strip()
        }
        with st.sidebar.spinner("Construindo aba no Sheets..."):
            try:
                res = requests.post(WEBHOOK_EXPANSAO_CENTRAL, json=payload_criar).json()
                if res.get("status") == "success":
                    st.sidebar.success(f"Acervo '{novo_acervo_nome}' integrado!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.sidebar.error(f"Erro: {res.get('message')}")
            except Exception as e:
                st.sidebar.error(f"Erro de conexão: {e}")
    else:
        st.sidebar.warning("Por favor, digite um nome válido.")

st.sidebar.markdown("<br><p style='font-size: 11px; color: #64748b; text-align: center;'>Desenvolvido para Gestão Interna • v1.4</p>", unsafe_allow_html=True)

# ==============================================================================
# TELA A: PAINEL PRINCIPAL (MÉTRICAS + BUSCA + RECENTES)
# ==============================================================================
if menu == "📌 Painel Principal":
    st.markdown("<h1 style='color: #ffffff;'>📊 Painel Geral do Acervo</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; margin-top: -10px;'>Visão analítica em tempo real e busca unificada do sistema.</p>", unsafe_allow_html=True)
    
    # Grid de Múltiplas Colunas com as Suas Métricas Reais do Print
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="📦 Banco Unificado", value="9845 faixas")
    with m2:
        st.metric(label="🌴 Som da Ilha", value="5404 mscs")
    with m3:
        st.metric(label="🎙️ Banco Túlio", value="4406 mscs")
    with m4:
        st.metric(label="🎙️ Banco Jéssica", value="35 mscs")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mecanismo de Busca Inteligente com o cursor vermelho aplicado
    st.markdown("### 🔍 Mecanismo de Busca Inteligente:")
    busca_termo = st.text_input("Digite o nome da música, artista ou trecho do arquivo...", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Lista de Músicas Adicionadas Recentemente
    st.markdown("### 📅 Adicionadas Recentemente no Acervo")
    
    # Mantive a tabela populada exatamente com os dados visíveis no seu print original
    dados_recentes = {
        "Nome do Arquivo": [
            "Melly - (part. Liniker) - Ana - Single - 2026",
            "Luedji Luna - Rota - Acústico - 2026",
            "LAURO - (part. CANETARIA) - Maria, Medusa - Álbum Caramelo Salgado - 2026",
            "LAURO - (part. CANETARIA) - Flor de Sal - Álbum Caramelo Salgado - 2026",
            "LAURO - (part. Ana Gabriela, CANETARIA) - Seca Palha - Álbum Caramelo Salgado - 2026",
            "The Something Specials - (part. Taylor Olin) - Wind - Single - 2025"
        ],
        "Acervo Origem": ["Túlio", "Túlio", "Túlio", "Túlio", "Túlio", "Túlio"]
    }
    df_recentes = pd.DataFrame(dados_recentes)
    st.dataframe(df_recentes, use_container_width=True, hide_index=True)

# ==============================================================================
# TELA B: VER TODO O ACERVO
# ==============================================================================
elif menu == "📂 Ver Todo o Acervo":
    st.markdown("<h1 style='color: #ffffff;'>📂 Banco de Dados Geral</h1>", unsafe_allow_html=True)
    st.info("Aqui é carregada a consolidação total de faixas registradas no banco.")

# ==============================================================================
# TELA C: INSERIR NOVO LOTE (INTEGRAÇÃO COMPLETA DAS ABAS)
# ==============================================================================
elif menu == "📥 Inserir Novo Lote":
    st.markdown("<h1 style='color: #ffffff;'>📦 Processamento de Lotes (.txt)</h1>", unsafe_allow_html=True)
    
    col_user, col_dest = st.columns(2)
    with col_user:
        u_nome_g = st.text_input("Nome do Programador / Usuário:", value="User_Radio")
        
    with col_dest:
        # Montagem Estrutural do Selectbox Inteligente
        opcoes_destino = ["Som da Ilha", "Planilha Túlio (Ponte)", "Planilha Jéssica (Direto)"]
        
        # Puxa as abas adicionais registradas dinamicamente na planilha central
        novos_acervos = carregar_acervos_novos()
        opcoes_destino.extend(novos_acervos)
        
        destino_escolhido = st.selectbox("Selecione a Planilha de Destino:", opcoes_destino)

    arquivo_post = st.file_uploader("Insira o arquivo de bloco de notas (.txt):", type=["txt"])
    
    if arquivo_post is not None:
        conteudo = arquivo_post.read().decode("utf-8")
        blocos = conteudo.split('---')
        lista_registros = []
        
        for bloco in blocos:
            dados_bloco = extrair_dados_hashtags(bloco)
            if dados_bloco:
                lista_registros.append(dados_bloco)
                
        if lista_registros:
            df_g = pd.DataFrame(lista_registros)
            
            # Padronização Estrita das Colunas do Sistema
            colunas_padrao = [
                "Música", "Artista", "Compositores", "Formato", "Ano", "Origem", 
                "Gênero", "Gênero Relacionado", "Est/Idioma", "Classificação", 
                "Andamento", "Participações", "Nome do Arquivo"
            ]
            for col in colunas_padrao:
                if col not in df_g.columns:
                    df_g[col] = ""
                    
            df_g = df_g[colunas_padrao]
            
            st.subheader("📋 Pré-visualização e Edição das Músicas Encontradas")
            df_editado_g = st.data_editor(df_g, num_rows="dynamic", use_container_width=True)
            
            if st.button("Enviar Lote para Nuvem 💾", type="primary", use_container_width=True):
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                lista_musicas_formatada = []
                
                for _, r in df_editado_g.iterrows():
                    lista_musicas_formatada.append({
                        "usuario": u_nome_g,
                        "musica": str(r.get("Música", "")),
                        "artista": str(r.get("Artista", "")),
                        "compositores": str(r.get("Compositores", "")),
                        "formato": str(r.get("Formato", "")),
                        "ano": str(r.get("Ano", "")),
                        "origem": str(r.get("Origem", "")),
                        "genero": str(r.get("Gênero", "")),
                        "genero_relacionado": str(r.get("Gênero Relacionado", "")),
                        "idioma_est": str(r.get("Est/Idioma", "")),
                        "classificacao": str(r.get("Classificação", "")),
                        "andamento": str(r.get("Andamento", "")),
                        "data_cadastro": data_atual,
                        "participacoes": str(r.get("Participações", "")),
                        "nome_arquivo": str(r.get("Nome do Arquivo", ""))
                    })
                
                with st.spinner("Despachando dados para o Google Sheets..."):
                    try:
                        # --- ROTEAR PARA SISTEMAS LEGADOS ---
                        if destino_escolhido == "Som da Ilha":
                            res = requests.post(WEBHOOK_SOM_DA_ILHA, json=lista_musicas_formatada)
                            sucesso = res.status_code == 200
                        elif destino_escolhido == "Planilha Túlio (Ponte)":
                            res = requests.post(WEBHOOK_TULIO, json=lista_musicas_formatada)
                            sucesso = res.status_code == 200
                        elif destino_escolhido == "Planilha Jéssica (Direto)":
                            res = requests.post(WEBHOOK_JESSICA, json=lista_musicas_formatada)
                            sucesso = res.status_code == 200
                            
                        # --- ROTEAR DINAMICAMENTE PARA AS NOVAS ABAS DA EXPANSÃO ---
                        else:
                            payload_expansao = {
                                "acao": "salvar_musicas",
                                "destino_aba": destino_escolhido,
                                "musicas": lista_musicas_formatada
                            }
                            res = requests.post(WEBHOOK_EXPANSAO_CENTRAL, json=payload_expansao)
                            sucesso = res.status_code == 200 and res.json().get("status") == "success"
                            
                        if sucesso:
                            st.success(f"🎉 Lote gravado com sucesso em '{destino_escolhido}'!")
                            st.balloons()
                        else:
                            st.error("Erro no processamento do Google. Verifique os parâmetros.")
                    except Exception as e:
                        st.error(f"Erro crítico ao tentar conectar ao servidor: {e}")
        else:
            st.warning("Nenhuma estrutura de hashtag válida encontrada no arquivo .txt.")

# ==============================================================================
# TELA D: ROTEIRO INSTAGRAM
# ==============================================================================
elif menu == "📻 Roteiro Instagram":
    st.markdown("<h1 style='color: #ffffff;'>📻 Gerador de Roteiros</h1>", unsafe_allow_html=True)
    st.info("Painel secundário destinado à formatação de posts e mídias sociais.")
