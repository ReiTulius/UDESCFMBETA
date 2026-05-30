import streamlit as st
import pandas as pd
import re
import smtplib
import requests
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import datetime as dt

# ==========================================
# 📻 CONFIGURAÇÃO DO PAINEL & CREDENCIAIS
# ==========================================
st.set_page_config(page_title="Acervo Oficial Integrado - Udesc FM", page_icon="📻", layout="wide")

# --- INJEÇÃO DE CSS AVANÇADO (ESTÉTICA PREMIUM & MODERNIZAÇÃO) ---
def injetar_css_premium():
    st.markdown("""
    <style>
        /* Ocultar elementos padrão do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Fundo geral da aplicação */
        .main {
            background-color: #f8fafc !important;
        }
        
        /* Customização da Barra Lateral (Visual Dark Premium) */
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important; /* Slate escuro moderno */
            padding-top: 20px;
        }
        section[data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
        }
        
        /* Transformando o menu de rádio em botões/cards modernos de navegação */
        div[data-testid="stRadio"] div[role="radiogroup"] > label {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            padding: 12px 16px !important;
            border-radius: 10px !important;
            margin-bottom: 10px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
            background-color: #334155 !important;
            border-color: #38bdf8 !important; /* Brilho azul sutil */
            transform: translateX(4px);
        }
        div[data-testid="stRadio"] div[role="radiogroup"] [data-checked="true"] > label {
            background-color: #0284c7 !important; /* Destaque azul ativo */
            border-color: #38bdf8 !important;
            font-weight: bold !important;
        }
        
        /* Cards de Métricas (Dashboard Executivo) */
        div[data-testid="metric-container"] {
            background: #ffffff !important;
            border-radius: 16px !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #e2e8f0 !important;
            padding: 20px !important;
            transition: all 0.3s ease !important;
            position: relative;
            overflow: hidden;
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1) !important;
        }
        div[data-testid="metric-container"]::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            width: 6px;
            background: linear-gradient(180deg, #38bdf8, #0284c7);
        }
        
        /* Inputs e Caixas de Texto com cantos arredondados e foco suave */
        div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
            border-radius: 12px !important;
            border: 1px solid #cbd5e1 !important;
            background-color: #ffffff !important;
        }
        
        /* FORÇAR TEXTO PRETO NA DIGITAÇÃO (Correção do contraste oculto) */
        div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }
        
        /* Botões Principais Estilo Moderno */
        .stButton>button {
            border-radius: 10px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            transition: all 0.2s ease !important;
        }
    </style>
    """, unsafe_allow_html=True)

injetar_css_premium()

EMAIL_ROBO_REMETENTE = "heytuliusradio@gmail.com"
SENHA_ROBO_REMETENTE = "nvfxdrlzpkzbugao"
EMAIL_DESTINATARIO_OFICIAL = "heytuliusmusic@gmail.com"

# 📊 LINKS DE LEITURA (PLANILHAS ORIGINAIS PRO)
URL_SOM_DA_ILHA_PRO = "https://docs.google.com/spreadsheets/d/1zw7RPhpuInL7JqSylB_zOMu5zaqO4KgnJ7sD2eoM6gs/export?format=csv"
URL_TULIO_PRO = "https://docs.google.com/spreadsheets/d/16inPMqGCr50-MNJvwV1R4bykDgEGRwlxdbjWrlW6mfY/export?format=csv"
URL_JESSICA_PRO = "https://docs.google.com/spreadsheets/d/1MQ7OcghWNTZwaYVBTmZlMojYTXZMOe5vT1px5VALpS0/export?format=csv"
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1zkPm3F9W8QbOBhKvdV7jFCYqH-U8Qbru5w5TDyAHQLw/edit?usp=sharing"

# 📊 LINKS DE LEITURA DAS PLANILHAS CÓPIAS (DO APP)
URL_SOM_DA_ILHA_APP_CSV = "https://docs.google.com/spreadsheets/d/1HPirfRjmjZjG23x9kc9Y1zB9zhZv6_iOmB9DIZsCgNo/export?format=csv"
URL_TULIO_APP_CSV = "https://docs.google.com/spreadsheets/d/1iVgHYv58Aknbf0Pa1V2gENWtWZVzkkghdT7vV4nKxTE/export?format=csv"
URL_JESSICA_APP_CSV = "https://docs.google.com/spreadsheets/d/1MQ7OcghWNTZwaYVBTmZlMojYTXZMOe5vT1px5VALpS0/export?format=csv"

# 🚀 WEBHOOKS DE ESCRITA (LOTE COMPLETO)
WEBHOOK_SOM_DA_ILHA = "https://script.google.com/macros/s/AKfycbw1Rzkirio_e9qIqLziKCqFXCmYICaOTVHixIuRgV2WCLdo4pzN1OGQSFtpicrWxf_Z/exec"
WEBHOOK_TULIO = "https://script.google.com/macros/s/AKfycbxR5g2pWU_2_ClapUxY5PWCnH-C9NBrmiT8F1wf0GoLm2KV9jAmMlOQLSGdWsLHNzqX/exec"
WEBHOOK_JESSICA = "https://script.google.com/macros/s/AKfycbwGif0xdjbzvo82mvG1CnrKwt8jvp-OWwHCFv3_FTQNJtGxT7m15hZGeO3k7ryWl3E9uQ/exec"

# ==========================================
# 📧 FUNÇÃO DE NOTIFICAÇÃO POR E-MAIL
# ==========================================
def enviar_notificacao_email(nome_acervo, df_novas, nome_usuario):
    if "@" not in EMAIL_ROBO_REMETENTE or "@" not in EMAIL_DESTINATARIO_OFICIAL:
        return
    try:
        fuso_brasilia = dt.timezone(dt.timedelta(hours=-3))
        agora_local = datetime.now(fuso_brasilia)
        
        msg = MIMEMultipart()
        msg['From'] = f"Painel Udesc FM <{EMAIL_ROBO_REMETENTE}>"
        msg['To'] = EMAIL_DESTINATARIO_OFICIAL
        msg['Subject'] = f"📻 Novo Cadastro por: {nome_usuario} ({nome_acervo})"
        
        linhas_musicas = []
        for _, linha in df_novas.iterrows():
            nome_arq = linha.get('Nome do Arquivo', '')
            if not nome_arq and 'Música' in linha:
                nome_arq = f"{linha.get('Artista', 'Desconhecido')} - {linha.get('Música', 'Sem Nome')}"
            linhas_musicas.append(f"• {nome_arq}.mp3")
        lista_texto = "\n".join(linhas_musicas)
        
        corpo = f"""Olá Túlio,

Um novo lote de músicas foi processado e saved na planilha!

👤 QUEM CADASTROU: {nome_usuario}
📍 DESTINO DO LOTE: {nome_acervo}
📅 DATA/HORA: {agora_local.strftime('%d/%m/%Y %H:%M:%S')}

🎵 Músicas Cadastradas ({len(df_novas)} itens):
{lista_texto}

---
Aviso automático do Painel de Controle Udesc FM."""
        
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ROBO_REMETENTE, SENHA_ROBO_REMETENTE)
        server.sendmail(EMAIL_ROBO_REMETENTE, EMAIL_DESTINATARIO_OFICIAL, msg.as_string())
        server.quit()
    except:
        pass

# ==========================================
# 🔄 LEITOR INTEGRADO DO ACERVO
# ==========================================
def puxar_dados_do_google(url, nome_acervo):
    try:
        if "docs.google.com" in url and "/export" not in url:
            if "/d/" in url:
                id_planilha = url.split("/d/")[1].split("/")[0]
                gid_part = ""
                if "gid=" in url:
                    gid_part = "&gid=" + url.split("gid=")[1].split("&")[0]
                url_base = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv{gid_part}"
            else:
                url_base = url
        else:
            url_base = url

        conector = "&" if "?" in url_base else "?"
        url_dinamica = f"{url_base}{conector}cachebuster={int(time.time())}"
        
        resposta = requests.get(url_dinamica, timeout=10)
        if resposta.status_code != 200 or "html" in resposta.headers.get('Content-Type', '').lower():
            st.sidebar.warning(f"⚠️ Planilha '{nome_acervo}' está privada.")
            return pd.DataFrame()

        df = pd.read_csv(url_dinamica, sep=',', on_bad_lines='skip', encoding='utf-8')
        
        if not df.empty:
            df.dropna(how='all', inplace=True)
            df.columns = [str(c).strip() for c in df.columns]
            df = df[[c for c in df.columns if "REF!" not in c and not c.startswith("Unnamed:")]]
            
            mapeamento = {
                "musica": "Música", "música": "Música", "artista": "Artista",
                "compositores": "Compositores", "compositor": "Compositores",
                "formato": "Formato", "ano": "Ano", "origem": "Origem",
                "genero": "Gênero", "gênero": "Gênero",
                "genero relacionado": "Gênero Relacionado", "gênero relacionado": "Gênero Relacionado",
                "est/idioma": "Est/Idioma", "idioma": "Est/Idioma", "est": "Est/Idioma",
                "classificacao": "Classificação", "classificação": "Classificação",
                "andamento": "Andamento", "data cadastro": "Data Cadastro", "data_cadastro": "Data Cadastro",
                "participacoes": "Participações", "participações": "Participações",
                "nome do arquivo": "Nome do Arquivo", "nome_arquivo": "Nome do Arquivo"
            }
            
            novas_colunas = []
            for col in df.columns:
                col_lower = col.lower().strip()
                if col_lower in mapeamento:
                    novas_colunas.append(mapeamento[col_lower])
                else:
                    novas_colunas.append(col)
            df.columns = novas_colunas
            df["Acervo Origem"] = nome_acervo
            return df
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar {nome_acervo}: {str(e)[:50]}")
    return pd.DataFrame()

def inicializar_acervos(forcar_recarga=False):
    if "banco_completo" not in st.session_state or forcar_recarga:
        with st.spinner("Sincronizando acervos em tempo real..."):
            df_som_pro = puxar_dados_do_google(URL_SOM_DA_ILHA_PRO, "Som da Ilha")
            df_tulio_pro = puxar_dados_do_google(URL_TULIO_PRO, "Túlio")
            df_jessica_pro = puxar_dados_do_google(URL_JESSICA_PRO, "Jéssica")
            
            df_som_app = puxar_dados_do_google(URL_SOM_DA_ILHA_APP_CSV, "Som da Ilha")
            df_tulio_app = puxar_dados_do_google(URL_TULIO_APP_CSV, "Túlio")
            df_jessica_app = puxar_dados_do_google(URL_JESSICA_APP_CSV, "Jéssica")
            
            lista_dfs = [df_som_pro, df_tulio_pro, df_jessica_pro, df_som_app, df_tulio_app, df_jessica_app]
            dfs = [df for df in lista_dfs if not df.empty]
            
            if dfs:
                df_unificado = pd.concat(dfs, ignore_index=True)
                if "Nome do Arquivo" not in df_unificado.columns:
                    df_unificado["Nome do Arquivo"] = ""
                
                df_unificado["Nome do Arquivo"] = df_unificado["Nome do Arquivo"].fillna("")
                mask_vazio = df_unificado["Nome do Arquivo"].astype(str).str.strip() == ""
                
                if "Artista" in df_unificado.columns and "Música" in df_unificado.columns:
                    df_unificado.loc[mask_vazio, "Nome do Arquivo"] = (
                        df_unificado.loc[mask_vazio, "Artista"].astype(str) + " - " + df_unificado.loc[mask_vazio, "Música"].astype(str)
                    )
                
                df_unificado.drop_duplicates(subset=["Nome do Arquivo"], keep="first", inplace=True)
                st.session_state["banco_completo"] = df_unificado
            else:
                st.session_state["banco_completo"] = pd.DataFrame()

inicializar_acervos()

def converter_link_google(url):
    if "docs.google.com/spreadsheets" in url:
        id_planilha = url.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
    return url

@st.cache_data(ttl=600)
def carregar_banco_instagram(url):
    try:
        url_direta = converter_link_google(url)
        df = pd.read_csv(url_direta, sep=',')
        df.columns = [str(c).strip().lower() for c in df.columns]
        col_artista = df.columns[0]
        col_insta = df.columns[1]
        
        banco = {}
        for _, linha_planilha in df.iterrows():
            nome_artista = str(linha_planilha[col_artista]).strip().lower()
            insta = str(linha_planilha[col_insta]).strip() if pd.notna(linha_planilha[col_insta]) else ""
            if insta.lower() in ["nan", "null", "none", "0"]:
                insta = ""
            banco[nome_artista] = insta
        return banco, None
    except Exception as e:
        return {}, f"Erro ao conectar com o Google Drive: {e}"

# ==========================================
# 🛠️ PARSER DE LINHAS
# ==========================================
def processar_linha_acervo_original(linha_bruta):
    linha_original = linha_bruta.strip()
    if not linha_original:
        return None

    eh_sc = bool(re.search(r'-\s*sc\b', linha_original, flags=re.IGNORECASE))
    linha_original = linha_original.replace('"', '')
    linha_original = re.sub(r'\.(mp3|wav|mpeg|mp4|m4a|flac|aac|ogg)$', '', linha_original, flags=re.IGNORECASE).strip()
    linha_original = re.sub(r'\s*-\s*sc\s*$', '', linha_original, flags=re.IGNORECASE).strip()
        
    if "\\" in linha_original:
        linha_trabalho = linha_original.split("\\")[-1]
    else:
        linha_trabalho = linha_original

    artista, participacao, musica, formato, ano, compositores = "", "", "", "", "", ""
    
    padrao_comp = r'\((comp\.|compa)[^)]+\)'
    busca_comp = re.search(padrao_comp, offset := linha_trabalho, flags=re.IGNORECASE)
    if busca_comp:
        compositores_com_parentese = busca_comp.group(0)
        compositores = re.sub(r'\((comp\.|compa)\s*', '', compositores_com_parentese, flags=re.IGNORECASE).rstrip(')')
        linha_trabalho = linha_trabalho.replace(compositores_com_parentese, "").replace("  ", " ")

    partes = [p.strip() for p in linha_trabalho.split(" - ")]
    
    if len(partes) >= 2:
        artista = partes[0]
        indice_atual = 1
        if "part." in partes[indice_atual].lower() or "part " in partes[indice_atual].lower():
            participacao = re.sub(r'\(?part\.?\s*', '', partes[indice_atual], flags=re.IGNORECASE).rstrip(')')
            indice_atual += 1
            
        if indice_atual < len(partes):
            musica = partes[indice_atual]
            indice_atual += 1
            
        if indice_atual < len(partes):
            if indice_atual == len(partes) - 1 and partes[indice_atual].isdigit():
                pass
            else:
                formato = partes[indice_atual]
                indice_atual += 1
                
        if len(partes) > indice_atual and partes[-1].isdigit():
            ano = partes[-1]
    else:
        musica = linha_trabalho

    part_str = f" - (part. {participacao})" if participacao else ""
    comp_str = f" (comp. {compositores})" if compositores else ""
    formato_str = f" - {formato}" if formato else ""
    ano_str = f" - {ano}" if ano else ""
    sc_str = " - SC" if eh_sc else ""
    
    nome_arquivo_formatado = f"{artista}{part_str} - {musica}{comp_str}{formato_str}{ano_str}{sc_str}"
    nome_arquivo_formatado = re.sub(r'\s+', ' ', nome_arquivo_formatado).strip()

    fuso_brasilia = dt.timezone(dt.timedelta(hours=-3))
    data_hoje = datetime.now(fuso_brasilia).strftime("%d/%m/%Y")

    return {
        "Música": musica, "Artista": artista, "Compositores": compositores,
        "Formato": formato, "Ano": ano, "Origem": "", "Gênero": "", "Gênero Relacionado": "",
        "Est/Idioma": "SC" if eh_sc else "", "Classificação": "", "Andamento": "",
        "Data Cadastro": data_hoje, "Participações": participacao, "Nome do Arquivo": nome_arquivo_formatado,
        "eh_sc": eh_sc
    }

def enviar_lote_completo_google(url, pacote_json):
    try:
        r = requests.post(url, json=pacote_json, headers={"Content-Type": "application/json"}, timeout=30)
        if r.status_code == 200:
            if "error" in r.text.lower():
                return False, f"Erro interno do Google Script: {r.text[:100]}"
            return True, "OK"
        return False, f"Rejeitado (HTTP {r.status_code})"
    except Exception as e:
        return False, f"Falha de conexão: {str(e)}"

# --- INTERFACE DE NAVEGAÇÃO LATERAL (MENU SAAS) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #38bdf8; margin-bottom: 0;'>📻 UDESC FM</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9em; margin-top: 0;'>Acervo Oficial Integrado</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    opcao = st.radio(
        "MENU DE NAVEGAÇÃO",
        ["🔍 Painel Principal", "📂 Ver Todo o Acervo", "💿 Inserir Novo Lote", "📸 Roteiro Instagram"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><hr style='border-color: #334155;'><br>", unsafe_allow_html=True)
    if st.button("🔄 Sincronizar Bases", use_container_width=True):
        inicializar_acervos(forcar_recarga=True)
        st.rerun()
    st.caption("Desenvolvido para Gestão Interna • v1.5")

# ==========================================
# 🔍 ABA: PAINEL PRINCIPAL (DASHBOARD)
# ==========================================
if opcao == "🔍 Painel Principal":
    st.markdown("<h1 style='color: #ffffff;'>📊 Painel Geral do Acervo</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1;'>Visão analítica em tempo real e busca unificada do sistema.</p>", unsafe_allow_html=True)
    
    df_total = st.session_state["banco_completo"]
    
    if not df_total.empty:
        total_musicas = len(df_total)
        total_sc = len(df_total[df_total["Acervo Origem"] == "Som da Ilha"])
        total_tulio = len(df_total[df_total["Acervo Origem"] == "Túlio"])
        total_jessica = len(df_total[df_total["Acervo Origem"] == "Jéssica"])
        
        # Grid de Métricas Premium
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Banco Unificado", f"{total_musicas} faixas")
        col2.metric("🏝️ Som da Ilha", f"{total_sc} mscs")
        col3.metric("🎙️ Banco Túlio", f"{total_tulio} mscs")
        col4.metric("🎙️ Banco Jéssica", f"{total_jessica} mscs")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- MECANISMO DE BUSCA INTELIGENTE (Texto Preto Configurado) ---
        termo = st.text_input("🔍 Mecanismo de Busca Inteligente:", placeholder="Digite o nome da música, artista ou trecho do arquivo...")
        
        if termo:
            termo_lower = termo.lower().strip()
            mascara = pd.Series(False, index=df_total.index)
            for col in df_total.columns:
                if col != "Acervo Origem":
                    mascara |= df_total[col].astype(str).str.lower().str.contains(termo_lower, na=False)
            
            resultados = df_total[mascara]
            if not resultados.empty:
                st.success(f"Encontramos {len(resultados)} correspondência(s) no sistema!")
                st.dataframe(resultados, use_container_width=True)
            else:
                st.error("Nenhum registro encontrado com os dados informados.")
        
        st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
        
        # SEÇÃO VISUAL: ADICIONADAS RECENTEMENTE ABAIXO DA BUSCA
        st.markdown("<h3 style='font-size: 1.2em; color: #ffffff;'>📅 Adicionadas Recentemente no Acervo</h3>", unsafe_allow_html=True)
        ultimas_cadastradas = df_total.tail(6).iloc[::-1]
        colunas_exibicao = [c for c in ["Nome do Arquivo", "Acervo Origem"] if c in ultimas_cadastradas.columns]
        st.dataframe(ultimas_cadastradas[colunas_exibicao], use_container_width=True, hide_index=True)

# ==========================================
# 📂 ABA: VER TODO O ACERVO
# ==========================================
elif opcao == "📂 Ver Todo o Acervo":
    st.markdown("<h1 style='color: #ffffff;'>📋 Exploração de Dados</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1;'>Filtre e visualize as tabelas brutas diretamente do ecossistema Google Sheets.</p>", unsafe_allow_html=True)
    
    filtro_banco = st.selectbox("Selecione a Base Alvo:", ["Todos os Acervos Juntos", "Apenas Túlio", "Apenas Jéssica", "Apenas Som da Ilha"])
    df_exibir = st.session_state["banco_completo"]
    
    if not df_exibir.empty:
        if filtro_banco == "Apenas Túlio":
            df_exibir = df_exibir[df_exibir["Acervo Origem"] == "Túlio"]
        elif filtro_banco == "Apenas Jéssica":
            df_exibir = df_exibir[df_exibir["Acervo Origem"] == "Jéssica"]
        elif filtro_banco == "Apenas Som da Ilha":
            df_exibir = df_exibir[df_exibir["Acervo Origem"] == "Som da Ilha"]
            
        st.dataframe(df_exibir, use_container_width=True)

# ==========================================
# 💿 ABA: INSERIR NOVO LOTE
# ==========================================
elif opcao == "💿 Inserir Novo Lote":
    st.markdown("<h1 style='color: #ffffff;'>💿 Formatador de Acervo Integrado</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1;'>Insira suas linhas de arquivos de áudio. O motor fará o desmembramento técnico padronizado.</p>", unsafe_allow_html=True)

    with st.container(border=True):
        texto_bruto = st.text_area("Cole as linhas aqui:", height=150, placeholder="Ex: Artista - Nome da Musica - MP3 - 2024")
        if st.button("Executar Engenharia de Linhas ⚡", type="primary", use_container_width=True):
            if texto_bruto:
                linhas = texto_bruto.split('\n')
                lista_geral, lista_sc = [], []
                
                for line in linhas:
                    res = processar_linha_acervo_original(line)
                    if res:
                        eh_sc = res.pop("eh_sc", False)
                        if eh_sc: 
                            lista_sc.append(res)
                        else: 
                            lista_geral.append(res)
                
                st.session_state["lote_geral_atual"] = pd.DataFrame(lista_geral) if lista_geral else pd.DataFrame()
                st.session_state["lote_sc_atual"] = pd.DataFrame(lista_sc) if lista_sc else pd.DataFrame()
                st.toast("Linhas processadas e separadas com sucesso!")

    # --- EDITE & GRAVE: LOTE GERAL ---
    if "lote_geral_atual" in st.session_state and not st.session_state["lote_geral_atual"].empty:
        st.markdown("<h3 style='color: #ffffff; margin-top: 20px;'>📝 Grade Editável: Lote Geral</h3>", unsafe_allow_html=True)
        df_editado_g = st.data_editor(st.session_state["lote_geral_atual"], use_container_width=True, key="edit_g_real")
        st.session_state["lote_geral_atual"] = df_editado_g
        
        with st.expander("📥 Configurações de Postagem Automática (Geral)", expanded=True):
            col_a, col_b = st.columns(2)
            u_nome_g = col_a.text_input("Nome do Operador:", key="usr_g", placeholder="Campo Obrigatório").strip()
            destino_geral = col_b.selectbox("Planilha de Destino:", ["Escolha uma opção...", "Planilha Túlio (Ponte)", "Planilha Jéssica (Direto)"], key="dest_g")
            
            lista_duplicadas_g = []
            if "banco_completo" in st.session_state and not st.session_state["banco_completo"].empty:
                arquivos_no_banco = set(st.session_state["banco_completo"]["Nome do Arquivo"].astype(str).str.lower().str.strip())
                for _, r in df_editado_g.iterrows():
                    if str(r["Nome do Arquivo"]).lower().strip() in arquivos_no_banco:
                        lista_duplicadas_g.append(str(r["Nome do Arquivo"]))

            if lista_duplicadas_g:
                st.error(f"🛑 Gravação Travada! Foram encontradas {len(lista_duplicadas_g)} música(s) duplicadas:")
                for dup in lista_duplicadas_g:
                    st.write(f"❌ Conflito de arquivo existente: `{dup}`")
            
            bloquear_envio_g = bool(lista_duplicadas_g) or not u_nome_g or destino_geral == "Escolha uma opção..."

            if st.button("Enviar Lote para Nuvem 💾", key="save_g_btn", disabled=bloquear_envio_g, type="primary"):
                url_webhook = WEBHOOK_TULIO if "Túlio" in destino_geral else WEBHOOK_JESSICA
                pacote_lote = []
                
                for _, r in df_editado_g.iterrows():
                    pacote_lote.append({
                        "usuario": u_nome_g, "musica": str(r.get("Música", "")), "artista": str(r.get("Artista", "")), 
                        "compositores": str(r.get("Compositores", "")), "formato": str(r.get("Formato", "")), "ano": str(r.get("Ano", "")), 
                        "origem": str(r.get("Origem", "")), "genero": str(r.get("Gênero", "")), "genero_relacionado": str(r.get("Gênero Relacionado", "")),
                        "idioma_est": str(r.get("Est/Idioma", "")), "classificacao": str(r.get("Classificação", "")), "andamento": str(r.get("Andamento", "")), 
                        "data_cadastro": str(r.get("Data Cadastro", "")), "participacoes": str(r.get("Participações", "")), "nome_arquivo": str(r.get("Nome do Arquivo", ""))
                    })
                
                with st.spinner("Despachando lote para os servidores do Google Sheets..."):
                    sucesso, motivo = enviar_lote_completo_google(url_webhook, pacote_lote)
                
                if sucesso:
                    enviar_notificacao_email(destino_geral, df_editado_g, u_nome_g)
                    inicializar_acervos(forcar_recarga=True)
                    st.success("Lote enviado com sucesso e integrado ao sistema!")
                    st.session_state["lote_geral_atual"] = pd.DataFrame()
                    time.sleep(1.0)
                    st.rerun()
                else:
                    st.error(f"Ocorreu um erro no disparo: {motivo}")

    # --- EDITE & GRAVE: LOTE SOM DA ILHA ---
    if "lote_sc_atual" in st.session_state and not st.session_state["lote_sc_atual"].empty:
        st.markdown("<h3 style='color: #ffffff; margin-top: 20px;'>🏝️ Grade Editável: Som da Ilha (Catarinenses)</h3>", unsafe_allow_html=True)
        df_editado_s = st.data_editor(st.session_state["lote_sc_atual"], use_container_width=True, key="edit_s_real")
        st.session_state["lote_sc_atual"] = df_editado_s
        
        with st.expander("📥 Configurações de Postagem Automática (Som da Ilha)", expanded=True):
            u_nome_s = st.text_input("Nome do Operador (SC):", key="usr_s", placeholder="Campo Obrigatório").strip()
            
            lista_duplicadas_s = []
            if "banco_completo" in st.session_state and not st.session_state["banco_completo"].empty:
                arquivos_no_banco = set(st.session_state["banco_completo"]["Nome do Arquivo"].astype(str).str.lower().str.strip())
                for _, r in df_editado_s.iterrows():
                    if str(r["Nome do Arquivo"]).lower().strip() in arquivos_no_banco:
                        lista_duplicadas_s.append(str(r["Nome do Arquivo"]))

            if lista_duplicadas_s:
                st.error(f"🛑 Gravação Travada! Foram encontradas músicas duplicadas:")
                for dup in lista_duplicadas_s:
                    st.write(f"❌ Conflito de arquivo existente: `{dup}`")

            bloquear_envio_s = bool(lista_duplicadas_s) or not u_nome_s
            
            if st.button("Enviar Lote Regional 💾", key="save_s_btn", disabled=bloquear_envio_s, type="primary"):
                pacote_lote_s = []
                
                for _, r in df_editado_s.iterrows():
                    pacote_lote_s.append({
                        "usuario": u_nome_s, "musica": str(r.get("Música", "")), "artista": str(r.get("Artista", "")), 
                        "compositores": str(r.get("Compositores", "")), "formato": str(r.get("Formato", "")), "ano": str(r.get("Ano", "")), 
                        "origem": str(r.get("Origem", "")), "genero": str(r.get("Gênero", "")), "genero_relacionado": str(r.get("Gênero Relacionado", "")),
                        "idioma_est": str(r.get("Est/Idioma", "")), "classificacao": str(r.get("Classificação", "")), "andamento": str(r.get("Andamento", "")), 
                        "data_cadastro": str(r.get("Data Cadastro", "")), "participacoes": str(r.get("Participações", "")), "nome_arquivo": str(r.get("Nome do Arquivo", ""))
                    })
                
                with st.spinner("Despachando lote catarinense..."):
                    sucesso, motivo = enviar_lote_completo_google(WEBHOOK_SOM_DA_ILHA, pacote_lote_s)
                            
                if sucesso:
                    enviar_notificacao_email("Som da Ilha (Ponte)", df_editado_s, u_nome_s)
                    inicializar_acervos(forcar_recarga=True)
                    st.success("Músicas salvas na base Som da Ilha!")
                    st.session_state["lote_sc_atual"] = pd.DataFrame()
                    time.sleep(1.0)
                    st.rerun()
                else:
                    st.error(f"Falha técnica: {motivo}")

# ==========================================
# 📸 ABA: ROTEIRO INSTAGRAM
# ==========================================
elif opcao == "📸 Roteiro Instagram":
    st.markdown("<h1 style='color: #ffffff;'>📸 Gerador de Roteiros para Redes Sociais</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1;'>Importe a listagem bruta do Sysrad para cruzar e anexar as marcações de Instagram cadastradas.</p>", unsafe_allow_html=True)
    banco_instagram, erro = carregar_banco_instagram(URL_GOOGLE_SHEETS)
    
    if erro: 
        st.error(erro)
    else:
        st.toast("Conexão ao Banco de Marcas Ativa!")
        
        with st.container(border=True):
            texto_bruto_sysrad = st.text_area("Cole o conteúdo do relatório Sysrad aqui:", height=200)

            if st.button("✨ Compilar Roteiro Limpo", type="primary", use_container_width=True):
                if texto_bruto_sysrad:
                    linhas = texto_bruto_sysrad.split('\n')
                    resultado = [datetime.now().strftime("%d/%m/%Y"), ""] 
                    for line in linhas:
                        line = line.strip()
                        if not line or "Marcador" in line or "Total:" in line or "DescriçãoDuração" in line:
                            continue
                        line = re.sub(r'\s*-\s*\(?part\.?[^)]+\)?\s*', ' ', line, flags=re.IGNORECASE)
                        line = re.sub(r'\s*\(?part\.?[^)]+\)?\s*', ' ', line, flags=re.IGNORECASE)
                        if " - " in line:
                            partes = line.split(" - ", 1)
                            artista_original = partes[0].strip()
                            artista_busca = artista_original.lower()
                            resto = partes[1]
                            padrao_corte = r'(\(comp|\(compa|Álbum|EP|Single|\d{4}|\d{2}:\d{2})'
                            musica_limpa = re.split(padrao_corte, resto, flags=re.IGNORECASE)[0].strip().rstrip('-').strip()
                            instagram = banco_instagram.get(artista_busca, "")
                            linha_final = f"{artista_original} - {musica_limpa} {instagram}".strip()
                            resultado.append(linha_final)
                    
                    texto_formatado = "\n".join(resultado)
                    st.markdown("### 📋 Copiar Conteúdo Formatado")
                    st.text_area(label="Cópia rápida", value=texto_formatado, height=300, label_visibility="collapsed")
                    st.balloons()
