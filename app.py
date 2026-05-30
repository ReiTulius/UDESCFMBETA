import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json
import time

# ==============================================================================
# 1. CONFIGURAÇÕES DE LAYOUT E ESTILO (CSS)
# ==============================================================================
st.set_page_config(
    page_title="Music Hub - UDESC FM",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Customização visual escura (Dark Mode elegante)
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    .stButton>button {
        border-radius: 8px;
    }
    div[data-testid="stDataFrame"] {
        background-color: #1e293b;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DIRETRIZES DE LINKS E WEBHOOKS (LEGADOS + EXPANSÃO)
# ==============================================================================
# Seus acervos fixos e intocáveis (Substitua pelas suas URLs reais de produção se necessário)
WEBHOOK_TULIO = "SUA_URL_DO_WEBHOOK_ANTIGO_DO_TULIO"
WEBHOOK_JESSICA = "SUA_URL_DO_WEBHOOK_ANTIGO_DA_JESSICA"
WEBHOOK_SOM_DA_ILHA = "SUA_URL_DO_WEBHOOK_ANTIGO_DO_SOM_DA_ILHA"

# 🚀 Links reais da sua nova planilha central de expansão
WEBHOOK_EXPANSAO_CENTRAL = "https://script.google.com/macros/s/AKfycbxpqOsTpw0PTG7Zk9WTn7KV1cW4TEIB2jBxMrEgGqQuBRlp-dt2FCOs7gwlZVgBl9Jvew/exec"
URL_CSV_LISTA_ACERVOS = "https://docs.google.com/spreadsheets/d/1g8xnMOtDhhfN28s8MGAaKC5C2bPQ5FwHd4l-ksY4yNk/gviz/tq?tqx=out:csv&sheet=Lista_Acervos"

# ==============================================================================
# 3. FUNÇÕES AUXILIARES E INTEGRAÇÕES
# ==============================================================================
def carregar_acervos_novos():
    """Lê a aba de controle da planilha central e traz as abas dinâmicas criadas"""
    try:
        df_controle = pd.read_csv(URL_CSV_LISTA_ACERVOS)
        if not df_controle.empty and "Nome do Acervo" in df_controle.columns:
            return df_controle["Nome do Acervo"].dropna().tolist()
    except:
        pass
    return []

def extrair_dados_hashtags(texto):
    """Sua função original de extração de metadados via hashtags"""
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
# 4. INTERFACE E NAVEGAÇÃO LATERAL (SIDEBAR)
# ==============================================================================
st.sidebar.markdown("<h2 style='color: #38bdf8; text-align: center;'>UDESC FM</h2>", unsafe_allow_html=True)
opcao = st.sidebar.radio("Navegação do Sistema:", ["📥 Cadastro Individual", "📦 Cadastro em Lote (TXT)"])

# Bloco Administrativo de Expansão na Barra Lateral
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Expansão de Acervos")
novo_acervo_nome = st.sidebar.text_input("Criar Novo Acervo (Ex: Acervo Marcos):")

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

# ==============================================================================
# TELA 1: CADASTRO INDIVIDUAL (Mantida idêntica à sua estrutura padrão)
# ==============================================================================
if opcao == "📥 Cadastro Individual":
    st.markdown("<h1 style='color: #ffffff;'>📥 Cadastro Individual de Músicas</h1>", unsafe_allow_html=True)
    # ... Seu código padrão de inputs individuais (st.text_input para música, artista, etc.) vai aqui ...
    st.info("Esta seção segue o fluxo de preenchimento manual campo a campo.")

# ==============================================================================
# TELA 2: CADASTRO EM LOTE COM SUPORTE À EXPANSÃO DINÂMICA
# ==============================================================================
elif opcao == "📦 Cadastro Em Lote (TXT)":
    st.markdown("<h1 style='color: #ffffff;'>📦 Processamento de Lotes (.txt)</h1>", unsafe_allow_html=True)
    
    col_user, col_dest = st.columns(2)
    with col_user:
        u_nome_g = st.text_input("Nome do Programador / Usuário:", value="User_Radio")
        
    with col_dest:
        # Montagem do Selectbox Dinâmico: Legados + Novos Acervos da Planilha Mãe
        opcoes_destino = ["Som da Ilha", "Planilha Túlio (Ponte)", "Planilha Jéssica (Direto)"]
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
            
            # Garante a existência de todas as colunas padrão visualmente
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
            
            # Botão de envio definitivo para a nuvem
            if st.button("Enviar Lote para Nuvem 💾", type="primary", use_container_width=True):
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                lista_musicas_formatada = []
                
                # Monta a estrutura de dados base
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
                        # --- DIRECIONAMENTO ROTAS ANTIGAS (Legados) ---
                        if destino_escolhido == "Som da Ilha":
                            res = requests.post(WEBHOOK_SOM_DA_ILHA, json=lista_musicas_formatada)
                            sucesso = res.status_code == 200
                        elif destino_escolhido == "Planilha Túlio (Ponte)":
                            res = requests.post(WEBHOOK_TULIO, json=lista_musicas_formatada)
                            sucesso = res.status_code == 200
                        elif destino_escolhido == "Planilha Jéssica (Direto)":
                            res = requests.post(WEBHOOK_JESSICA, json=lista_musicas_formatada)
                            sucesso = res.status_code == 200
                            
                        # --- DIRECIONAMENTO NOVA ROTA INTELIGENTE (Expansão por Abas) ---
                        else:
                            payload_expansao = {
                                "acao": "salvar_musicas",
                                "destino_aba": destino_escolhido,
                                "musicas": lista_musicas_formatada
                            }
                            res = requests.post(WEBHOOK_EXPANSAO_CENTRAL, json=payload_expansao)
                            sucesso = res.status_code == 200 and res.json().get("status") == "success"
                            
                        if sucesso:
                            st.success(f"🎉 Lote de {len(lista_musicas_formatada)} músicas gravado com sucesso em '{destino_escolhido}'!")
                            st.balloons()
                        else:
                            st.error("Erro no processamento do Google. Verifique os parâmetros do Webhook.")
                    except Exception as e:
                        st.error(f"Erro crítico ao tentar conectar ao servidor: {e}")
        else:
            st.warning("Nenhuma estrutura de hashtag válida encontrada no arquivo .txt.")
