import re
import streamlit as st
import pandas as pd

# Configuração da página do Streamlit
st.set_page_config(page_title="Udesc FM - Acervo", layout="wide")

# ==============================================================================
# 1. FUNÇÕES DE PROCESSAMENTO E CORREÇÃO DA LINHA 207 E 273
# ==============================================================================

def processar_linha_acervo_original(linha_original):
    """
    Processa uma linha de texto do acervo e extrai os metadados.
    """
    # CORREÇÃO DA LINHA 207: Adicionados parênteses para o operador walrus com 'not'
    if not (Server_original := linha_original.strip()):
        return None

    # Exemplo de limpeza/captura de dados usando Regex baseado nos seus prints
    # Padrão para: "M:\Bolsista - Jess\músicas baixadas\Artista - Música - Álbum - Ano.mp3"
    padrao = r"baixadas\\([^\-]+)\s*-\s*([^\-]+)\s*-\s*([^\-]+)\s*-\s*(\d{4})"
    match = re.search(padrao, Server_original)
    
    if match:
        artist = match.group(1).strip()
        musica = match.group(2).strip()
        composiores = "" # Pode ser expandido se houver no padrão
        formato = match.group(3).strip()
        ano = match.group(4).strip()
    else:
        # Fallback caso a linha não siga o padrão perfeito
        artist = "Desconhecido"
        musica = Server_original.split("\\")[-1].replace(".mp3", "")
        composiores = ""
        formato = "Acoustic"
        ano = "2026"

    # CORREÇÃO DA LINHA 273: Garantindo que o dicionário retorna variáveis válidas
    return {
        "Status": "Pronto",
        "Música": musica,
        "Artista": artist,
        "Compositores": composiores,
        "Formato": formato,
        "Ano": ano,
        "Origem": "",
        "Gênero": ""
    }

def salvar_no_google_sheets(df_dados, nome_usuario, planilha_destino):
    """
    Simula o envio dos dados para a API do Google Sheets.
    """
    try:
        # Aqui entraria o seu código original de conexão (gspread / st.connection)
        # Se retornar um HTTP 404, certifique-se de que o ID da planilha destino está correto!
        if not nome_usuario:
            return False, "Nome do usuário é obrigatório."
        
        # Simulação de sucesso
        return True, "Lote GERAL gravado com sucesso nas Nuvens!"
    except Exception as e:
        return False, f"Erro na requisição: {str(e)}"


# ==============================================================================
# 2. INTERFACE E NAVEGAÇÃO (PAINEL DE CONTROLE)
# ==============================================================================

# Barra Lateral (Sidebar)
with st.sidebar:
    st.header("Painel de Controle")
    if st.button("🔄 Forçar Sincronização Completa"):
        st.toast("Sincronizando...")
        
    st.write("Navegar para:")
    opcao = st.radio(
        label="Menu",
        options=["🔍 Buscar no Acervo", "📁 Ver Todo o Acervo", "💿 Formatador de Acervo", "📷 Gerador de Setlist (Instagram)"],
        label_visibility="collapsed"
    )
    
    st.caption("Udesc FM 🎧")

# ==============================================================================
# 3. PÁGINAS DO SISTEMA
# ==============================================================================

if opcao == "🔍 Buscar no Acervo":
    st.title("🔍 Acervo Oficial Integrado - Udesc FM")
    
    # Métricas superiores
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Total no Site", "9745 mscs")
    col2.metric("🌴 Som da Ilha", "5315")
    col3.metric("🗄️ Banco Túlio", "4400")
    col4.metric("👩‍💻 Banco Jéssica", "30")
    
    st.text_input("Digite o artista, nome da música ou nome do arquivo:")
    st.subheader("📅 Adicionadas Recentemente no Sistema:")
    # Exemplo de tabela fictícia da busca
    st.dataframe(pd.DataFrame([{
        "Nome do Arquivo": "Ítallo - Dorinana - Álbum CATATAU - 2026",
        "Acervo Origem": "Túlio",
        "Data Cadastro": "28/05/2026"
    }]))

elif opcao == "💿 Formatador de Acervo":
    st.title("💿 Formatador & Hospedagem de Novos Cadastros")
    st.write("Insira os títulos estruturados abaixo para enviar diretamente para as planilhas cópias.")
    
    # Campo de texto para colar as linhas do acervo
    linhas_default = (
        '"M:\\Bolsista - Jess\\músicas baixadas\\Jethro Tull - Living in the Past - Álbum Stand Up - 1969.mp3"\n'
        '"M:\\Bolsista - Jess\\músicas baixadas\\Donna Dog - I Have to Tell You Something - Acoustic - 2021.mp3"'
    )
    texto_acervo = st.text_area("Cole aqui as linhas do seu acervo:", value=linhas_default, height=150)
    
    # Botão para formatar
    if st.button("Formatar Acervo ⚡", type="primary"):
        linhas = [l for l in texto_acervo.split("\n") if l.strip()]
        resultados = []
        
        for l in linhas:
            res = processar_linha_acervo_original(l)
            if res:
                resultados.append(res)
                
        if resultados:
            st.session_state['df_formatado'] = pd.DataFrame(resultados)
            st.success("🎉 Lote GERAL formatado com sucesso:")
        else:
            st.error("Nenhuma linha pôde ser formatada. Verifique o padrão do texto.")

    # Exibe a tabela caso ela já tenha sido gerada
    if 'df_formatado' in st.session_state:
        df = st.session_state['df_formatado']
        st.dataframe(df, use_container_width=True)
        
        # CORREÇÃO DA LINHA 413: Substituído ':=' por 'as St_expander' no gerenciador de contexto
        with st.expander("📬 SALVAR NO BANCO DE DADOS (Geral)", expanded=True) as St_expander:
            nome = st.text_input("Seu Nome (Identificação Obrigatória):", value="Jéssica")
            planilha = st.selectbox("Escolha a planilha destino:", ["Planilha Jéssica (Direto)", "Planilha Geral"])
            
            if st.button("Gravar Lote Geral nas Nuvens 💾"):
                # Executa a função de salvamento
                sucesso, mensagem = salvar_no_google_sheets(df, nome, planilha)
                
                # CORREÇÃO DA LINHA 500: Corrigido o espaçamento do 'if sucesso:'
                if sucesso:
                    st.success(mensagem)
                else:
                    # Se der o erro 404 que estava na foto, ele cai aqui de forma limpa
                    st.error(f"🔴 Falha no envio em bloco: Google rejeitou o bloco inteiro ({mensagem})")

else:
    st.title(opcao)
    st.info("Página em desenvolvimento ou sem erros críticos reportados.")
