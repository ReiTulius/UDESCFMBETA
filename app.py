import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# ==============================================================================
# 1. CONFIGURAÇÕES DA PÁGINA E CSS (CURSOR VERMELHO E DARK MODE)
# ==============================================================================
st.set_page_config(
    page_title="Music Hub - UDESC FM",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Fundo geral escuro */
    .stApp { background-color: #0f172a; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1e293b; }
    
    /* Cursor (caret) e borda vermelha nos inputs exatamente como no seu print */
    input { caret-color: #ff4b4b !important; }
    div[data-baseweb="input"]:focus-within {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 1px #ff4b4b !important;
    }
    div[data-baseweb="textarea"]:focus-within {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 1px #ff4b4b !important;
    }
    
    /* Estilo das tabelas */
    div[data-testid="stDataFrame"] {
        background-color: #1e293b;
        padding: 5px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. WEBHOOKS (SEUS ANTIGOS + OS NOVOS DA EXPANSÃO)
# ==============================================================================
# Mantenha os seus links originais de produção aqui:
WEBHOOK_TULIO = "SUA_URL_DO_WEBHOOK_TULIO"
WEBHOOK_JESSICA = "SUA_URL_DO_WEBHOOK_JESSICA"
WEBHOOK_SOM_DA_ILHA = "SUA_URL_DO_WEBHOOK_SOM_DA_ILHA"

# Novos links da Central de Expansão
WEBHOOK_EXPANSAO_CENTRAL = "https://script.google.com/macros/s/AKfycbxpqOsTpw0PTG7Zk9WTn7KV1cW4TEIB2jBxMrEgGqQuBRlp-dt2FCOs7gwlZVgBl9Jvew/exec"
URL_CSV_LISTA_ACERVOS = "https://docs.google.com/spreadsheets/d/1g8xnMOtDhhfN28s8MGAaKC5C2bPQ5FwHd4l-ksY4yNk/gviz/tq?tqx=out:csv&sheet=Lista_Acervos"

# ==============================================================================
# 3. FUNÇÕES BASE
# ==============================================================================
def carregar_acervos_novos():
    """Lê a lista de novas planilhas/acervos criados dinamicamente"""
    try:
        df = pd.read_csv(URL_CSV_LISTA_ACERVOS)
        if not df.empty and "Nome do Acervo" in df.columns:
            return df["Nome do Acervo"].dropna().tolist()
    except:
        pass
    return []

def extrair_dados_hashtags(texto):
    """Extrai os metadados do bloco de notas (.txt)"""
    if not isinstance(texto, str) or not texto.strip(): return {}
    metadados = {}
    linhas = texto.split('\n')
    for line in linhas:
        line = line.strip()
        if not line: continue
        if line.startswith('#musica '): metadados['Música'] = line.replace('#musica ', '', 1).strip()
        elif line.startswith('#artista '): metadados['Artista'] = line.replace('#artista ', '', 1).strip()
        elif line.startswith('#compositores '): metadados['Compositores'] = line.replace('#compositores ', '', 1).strip()
        elif line.startswith('#formato '): metadados['Formato'] = line.replace('#formato ', '', 1).strip()
        elif line.startswith('#ano '): metadados['Ano'] = line.replace('#ano ', '', 1).strip()
        elif line.startswith('#origem '): metadados['Origem'] = line.replace('#origem ', '', 1).strip()
        elif line.startswith('#genero '): metadados['Gênero'] = line.replace('#genero ', '', 1).strip()
        elif line.startswith('#genero_relacionado '): metadados['Gênero Relacionado'] = line.replace('#genero_relacionado ', '', 1).strip()
        elif line.startswith('#idioma_est '): metadados['Est/Idioma'] = line.replace('#idioma_est ', '', 1).strip()
        elif line.startswith('#classificacao '): metadados['Classificação'] = line.replace('#classificacao ', '', 1).strip()
        elif line.startswith('#andamento '): metadados['Andamento'] = line.replace('#andamento ', '', 1).strip()
        elif line.startswith('#participacoes '): metadados['Participações'] = line.replace('#participacoes ', '', 1).strip()
        elif line.startswith('#nome_arquivo '): metadados['Nome do Arquivo'] = line.replace('#nome_arquivo ', '', 1).strip()
    return metadados

# ==============================================================================
# 4. BARRA LATERAL (MENU ORIGINAL + MÓDULO DE EXPANSÃO NO FINAL)
# ==============================================================================
st.sidebar.markdown("<div style='text-align: center; margin-bottom: 20px;'><h2 style='margin-bottom: 0;'>📻 UDESC FM</h2><span style='color: #94a3b8; font-size: 13px;'>Acervo Oficial Integrado</span></div>", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navegação do Sistema:",
    ["📌 Painel Principal", "📂 Ver Todo o Acervo", "📥 Inserir Novo Lote", "📻 Roteiro Instagram"]
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔄 Sincronizar Bases", use_container_width=True):
    st.toast("Bases de dados sincronizadas!")
    time.sleep(0.5)
    st.rerun()

# --- NOVO BLOCO: EXPANSÃO DE ACERVOS ---
st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #38bdf8; margin-bottom: 5px;'>⚙️ Expansão de Acervos</h4>", unsafe_allow_html=True)
novo_acervo_nome = st.sidebar.text_input("Criar Novo Acervo (Ex: Acervo Marcos):")

if st.sidebar.button("Criar Estrutura na Nuvem 🚀", use_container_width=True):
    if novo_acervo_nome.strip():
        payload_criar = {"acao": "criar_acervo", "nome_acervo": novo_acervo_nome.strip()}
        with st.sidebar.spinner("Criando nova aba..."):
            try:
                res = requests.post(WEBHOOK_EXPANSAO_CENTRAL, json=payload_criar).json()
                if res.get("status") == "success":
                    st.sidebar.success(f"Acervo '{novo_acervo_nome}' criado!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.sidebar.error(res.get("message", "Erro no processamento."))
            except Exception as e:
                st.sidebar.error(f"Erro de conexão: {e}")

st.sidebar.markdown("<br><p style='font-size: 11px; color: #64748b; text-align: center;'>Desenvolvido para Gestão Interna • v1.4</p>", unsafe_allow_html=True)

# ==============================================================================
# TELA 1: PAINEL PRINCIPAL
# ==============================================================================
if menu == "📌 Painel Principal":
    st.markdown("<h1 style='margin-bottom: 0;'>📊 Painel Geral do Acervo</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 15px; margin-top: 5px; margin-bottom: 25px;'>Visão analítica em tempo real e busca unificada do sistema.</p>", unsafe_allow_html=True)
    
    # Suas métricas originais
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown("<p style='margin-bottom: 0; color: #94a3b8; font-size: 14px;'>📦 Banco Unificado</p><h2 style='margin-top: 0; font-size: 32px;'>9845 faixas</h2>", unsafe_allow_html=True)
    with m2: st.markdown("<p style='margin-bottom: 0; color: #94a3b8; font-size: 14px;'>🌴 Som da Ilha</p><h2 style='margin-top: 0; font-size: 32px;'>5404 mscs</h2>", unsafe_allow_html=True)
    with m3: st.markdown("<p style='margin-bottom: 0; color: #94a3b8; font-size: 14px;'>🎙️ Banco Túlio</p><h2 style='margin-top: 0; font-size: 32px;'>4406 mscs</h2>", unsafe_allow_html=True)
    with m4: st.markdown("<p style='margin-bottom: 0; color: #94a3b8; font-size: 14px;'>🎙️ Banco Jéssica</p><h2 style='margin-top: 0; font-size: 32px;'>35 mscs</h2>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-weight: bold; margin-bottom: 5px;'>🔍 Mecanismo de Busca Inteligente:</p>", unsafe_allow_html=True)
    busca_termo = st.text_input("Busca", label_visibility="collapsed", placeholder="Digite o nome da música, artista ou trecho do arquivo...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; margin-bottom: 10px;'>📅 Adicionadas Recentemente no Acervo</p>", unsafe_allow_html=True)
    
    # Tabela com as músicas do seu print
    df_recentes = pd.DataFrame({
        "Nome do Arquivo": [
            "Melly - (part. Liniker) - Ana - Single - 2026",
            "Luedji Luna - Rota - Acústico - 2026",
            "LAURO - (part. CANETARIA) - Maria, Medusa - Álbum Caramelo Salgado - 2026",
            "LAURO - (part. CANETARIA) - Flor de Sal - Álbum Caramelo Salgado - 2026",
            "LAURO - (part. Ana Gabriela, CANETARIA) - Seca Palha - Álbum Caramelo Salgado - 2026",
            "The Something Specials - (part. Taylor Olin) - Wind - Single - 2025"
        ],
        "Acervo Origem": ["Túlio", "Túlio", "Túlio", "Túlio", "Túlio", "Túlio"]
    })
    st.dataframe(df_recentes, use_container_width=True, hide_index=True)

# ==============================================================================
# TELA 2: VER TODO O ACERVO
# ==============================================================================
elif menu == "📂 Ver Todo o Acervo":
    st.markdown("<h1>📂 Banco de Dados Geral</h1>", unsafe_allow_html=True)
    st.info("Aqui é carregada a consolidação total de faixas registradas no banco.")

# ==============================================================================
# TELA 3: INSERIR NOVO LOTE (COM ROTEAMENTO INTELIGENTE)
# ==============================================================================
elif menu == "📥 Inserir Novo Lote":
    st.markdown("<h1>📦 Processamento de Lotes (.txt)</h1>", unsafe_allow_html=True)
    
    col_user, col_dest = st.columns(2)
    with col_user:
        u_nome_g = st.text_input("Nome do Programador / Usuário:", value="User_Radio")
        
    with col_dest:
        # Puxa os legados e injeta os novos acervos dinamicamente
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
            colunas_padrao = ["Música", "Artista", "Compositores", "Formato", "Ano", "Origem", "Gênero", "Gênero Relacionado", "Est/Idioma", "Classificação", "Andamento", "Participações", "Nome do Arquivo"]
            for col in colunas_padrao:
                if col not in df_g.columns: df_g[col] = ""
            df_g = df_g[colunas_padrao]
            
            st.subheader("📋 Pré-visualização e Edição das Músicas Encontradas")
            df_editado_g = st.data_editor(df_g, num_rows="dynamic", use_container_width=True)
            
            if st.button("Enviar Lote para Nuvem 💾", type="primary", use_container_width=True):
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                lista_musicas_formatada = []
                
                for _, r in df_editado_g.iterrows():
                    lista_musicas_formatada.append({
                        "usuario": u_nome_g, "musica": str(r.get("Música", "")),
                        "artista": str(r.get("Artista", "")), "compositores": str(r.get("Compositores", "")),
                        "formato": str(r.get("Formato", "")), "ano": str(r.get("Ano", "")),
                        "origem": str(r.get("Origem", "")), "genero": str(r.get("Gênero", "")),
                        "genero_relacionado": str(r.get("Gênero Relacionado", "")), "idioma_est": str(r.get("Est/Idioma", "")),
                        "classificacao": str(r.get("Classificação", "")), "andamento": str(r.get("Andamento", "")),
                        "data_cadastro": data_atual, "participacoes": str(r.get("Participações", "")),
                        "nome_arquivo": str(r.get("Nome do Arquivo", ""))
                    })
                
                with st.spinner("Despachando para o Sheets..."):
                    try:
                        # Roteamento dos acervos originais
                        if destino_escolhido == "Som da Ilha":
                            res = requests.post(WEBHOOK_SOM_DA_ILHA, json=lista_musicas_formatada)
                            sucesso = res.status_code == 200
                        elif destino_escolhido == "Planilha Túlio (Ponte)":
                            res = requests.post(WEBHOOK_TULIO, json=lista_musicas_formatada)
                            sucesso = res.status_code == 200
                        elif destino_escolhido == "Planilha Jéssica (Direto)":
                            res = requests.post(WEBHOOK_JESSICA, json=lista_musicas_formatada)
                            sucesso = res.status_code == 200
                        # Roteamento inteligente para acervos criados pelo usuário
                        else:
                            payload_expansao = {"acao": "salvar_musicas", "destino_aba": destino_escolhido, "musicas": lista_musicas_formatada}
                            res = requests.post(WEBHOOK_EXPANSAO_CENTRAL, json=payload_expansao)
                            sucesso = res.status_code == 200 and res.json().get("status") == "success"
                            
                        if sucesso:
                            st.success(f"🎉 Lote gravado com sucesso em '{destino_escolhido}'!")
                            st.balloons()
                        else:
                            st.error("Erro no processamento do Google Webhook.")
                    except Exception as e:
                        st.error(f"Erro de conexão: {e}")
        else:
            st.warning("Nenhuma estrutura válida encontrada no .txt.")

# ==============================================================================
# TELA 4: ROTEIRO INSTAGRAM
# ==============================================================================
elif menu == "📻 Roteiro Instagram":
    st.markdown("<h1>📻 Gerador de Roteiros</h1>", unsafe_allow_html=True)
    st.info("Painel secundário destinado à formatação de posts e mídias sociais.")
