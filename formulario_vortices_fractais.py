# app_vortices_fractais_v2.py
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
import hashlib
import urllib.parse
import hmac

# --- PALETA DE CORES E CONFIGURAÇÃO DA PÁGINA ---
COLOR_PRIMARY = "#70D1C6"
COLOR_TEXT_DARK = "#333333"
COLOR_BACKGROUND = "#FFFFFF"

st.set_page_config(
    page_title="Formulário - Vórtices e Fractais",
    layout="wide"
)

# --- CSS CUSTOMIZADO ---
st.markdown(f"""
    <style>
        div[data-testid="stHeader"], div[data-testid="stDecoration"] {{
            visibility: hidden; height: 0%; position: fixed;
        }}
        
        #autoclick-div {{
            display: none !important; 
        }}
        
        footer {{ visibility: hidden; height: 0%; }}
        .stApp {{ background-color: {COLOR_BACKGROUND}; color: {COLOR_TEXT_DARK}; }}
        h1, h2, h3 {{ color: {COLOR_TEXT_DARK}; }}
        .stApp > header {{
            background-color: {COLOR_PRIMARY}; padding: 1rem;
            border-bottom: 5px solid {COLOR_TEXT_DARK};
        }}
        div.st-emotion-cache-1r4qj8v {{
             background-color: #f0f2f6; border-left: 5px solid {COLOR_PRIMARY};
             border-radius: 5px; padding: 1.5rem; margin-top: 1rem;
             margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        div[data-testid="textInputRootElement"] > label,
        div[data-testid="stTextArea"] > label,
        div[data-testid="stRadioGroup"] > label, 
        div[data-testid="stDateInput"] > label,
        div[data-testid="stSelectbox"] > label,
        div[data-testid="stNumberInput"] > label {{
            color: {COLOR_TEXT_DARK}; font-weight: 600;
        }}
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTextArea"] textarea {{
            border: 1px solid #cccccc;
            border-radius: 5px;
            background-color: #FFFFFF;
        }}
        .stButton button {{
            background-color: {COLOR_PRIMARY}; color: white; font-weight: bold;
            padding: 0.75rem 1.5rem; border-radius: 8px; border: none;
        }}
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM GOOGLE SHEETS (COM CACHE) ---
@st.cache_resource
def connect_to_gsheet():
    try:
        creds_dict = dict(st.secrets["google_credentials"])
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        gc = gspread.service_account_from_dict(creds_dict)
        
        # ##### ATUALIZADO: Planilha 'formularios_pessoais', Aba 'fractais_prioritarios' #####
        spreadsheet = gc.open("formularios_pessoais") 
        return spreadsheet.worksheet("fractais_prioritarios") 
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Sheets: {e}")
        return None

ws_respostas = connect_to_gsheet()

if ws_respostas is None:
    st.error("Não foi possível conectar à aba 'fractais_prioritarios' da planilha 'formularios_pessoais'.")
    st.stop()

# --- CABEÇALHO DA APLICAÇÃO ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo_wedja.jpg", width=120)
    except FileNotFoundError:
        st.warning("Logo 'logo_wedja.jpg' não encontrada.")
with col2:
    st.markdown(f"""
    <div style="display: flex; align-items: center; height: 100%;">
        <h1 style='color: {COLOR_TEXT_DARK}; margin: 0; padding: 0;'>FORMULÁRIO 2 - VÓRTICES E FRACTAIS PRIORITÁRIOS</h1>
    </div>
    """, unsafe_allow_html=True)

# --- SEÇÃO DE IDENTIFICAÇÃO ---
with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Identificação</h3>", unsafe_allow_html=True)
    
    # --- Validação do Link ---
    org_coletora_valida = "Instituto Wedja de Socionomia"
    link_valido = False 

    try:
        query_params = st.query_params
        org_encoded_from_url = query_params.get("org")
        exp_from_url = query_params.get("exp")
        sig_from_url = query_params.get("sig")
        
        if org_encoded_from_url and exp_from_url and sig_from_url:
            org_decoded = urllib.parse.unquote(org_encoded_from_url)
            secret_key = st.secrets["LINK_SECRET_KEY"].encode('utf-8')
            message = f"{org_decoded}|{exp_from_url}".encode('utf-8')
            calculated_sig = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
            
            if hmac.compare_digest(calculated_sig, sig_from_url):
                timestamp_validade = int(exp_from_url)
                timestamp_atual = int(datetime.now().timestamp())
                
                if timestamp_atual <= timestamp_validade:
                    link_valido = True
                    org_coletora_valida = org_decoded
                else:
                    st.error("Link Expirado.")
            else:
                st.error("Link inválido ou adulterado.")
        else:
             if not (org_encoded_from_url or exp_from_url or sig_from_url):
                 link_valido = True
             else:
                 st.error("Link inválido.")
    except Exception:
        link_valido = False

    col1_form, col2_form = st.columns(2)
    
    with col1_form:
        nome_completo = st.text_input("Nome Completo:", key="input_nome")
        data_nascimento = st.date_input(
            "Data de Nascimento:",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.now(),
            format="DD/MM/YYYY"
        )
        contato = st.text_input("Contato (Email/Telefone):", key="input_contato")

    with col2_form:
        area_empresa = st.text_input("Área/Empresa:", key="input_empresa")
        funcao_cargo = st.text_input("Função/Cargo:", key="input_cargo")
        st.text_input("Organização Coletora:", value=org_coletora_valida, disabled=True)

if not link_valido:
    st.error("Acesso bloqueado.")
    st.stop()

# --- INSTRUÇÕES ---
with st.expander("Ver Orientações aos Respondentes", expanded=True):
    st.info(
        """
        - Preencha a tabela abaixo indicando a prioridade e a justificativa para cada Vórtice.
        - **Prioridade:** Use valores de 1 a 3.
        - **Fractal/Comportamento-Alvo:** Selecione a área correspondente.
        """
    )

# --- LISTAS DE OPÇÕES ---
opcoes_fractal = [
    "Selecione...",
    "Físico", "Financeiro", "Parentais", "Amigos", "Linhagem Familiar",
    "Processos de Vida", "Espiritual", "Profissional", "Conjugais",
    "Subordinados", "Social", "Princípios Éticos", "Sentimento",
    "Intelectual", "Filhos", "Parceiros", "Institucional", "Finitude"
]

vortices = ["Consigo", "Com o Outro", "Com o Todo"]

# --- FORMULÁRIO DINÂMICO (TABELA) ---
st.subheader("Quadro de Registro")

respostas_tabela = []

# Cria uma linha para cada Vórtice fixo
for i, vortice in enumerate(vortices):
    with st.container(border=True):
        st.markdown(f"#### Vórtice: {vortice}")
        
        c1, c2, c3 = st.columns([1, 2, 3])
        
        with c1:
            prioridade = st.number_input(f"Prioridade (1-3)", min_value=1, max_value=3, step=1, key=f"prioridade_{i}")
        
        with c2:
            fractal = st.selectbox(f"Fractal / Comportamento-Alvo", options=opcoes_fractal, key=f"fractal_{i}")
            
        with c3:
            justificativa = st.text_input(f"Justificativa", key=f"justificativa_{i}")
            
        respostas_tabela.append({
            "Vortice": vortice,
            "Prioridade": prioridade,
            "Fractal": fractal,
            "Justificativa": justificativa
        })

# --- BOTÃO DE FINALIZAR E ENVIAR ---
if st.button("Finalizar e Enviar Respostas", type="primary"):
    # Validação do Bloco 4 (Hierarquia Única)
    hierarquias_selecionadas = [r["Prioridade"] for r in respostas_tabela]
    fractais_validos = all(r["Fractal"] != "Selecione..." for r in respostas_tabela)
    
    erro_validacao = False
    if not fractais_validos:
        st.warning("Por favor, selecione um 'Fractal/Comportamento-Alvo' para todos os Vórtices.")
        erro_validacao = True
    elif len(set(hierarquias_selecionadas)) != 3:
        st.error("Erro na Prioridade: Você deve selecionar uma prioridade diferente (1, 2, 3) para cada Vórtice. Não repita.")
        erro_validacao = True
    
    if not erro_validacao:
        st.subheader("Enviando Respostas...")
        
        with st.spinner("Enviando dados para a planilha..."):
            try:
                timestamp_str = datetime.now().isoformat(timespec="seconds")
                
                # Gera ID da Organização
                nome_limpo = org_coletora_valida.strip().upper()
                id_organizacao = hashlib.md5(nome_limpo.encode('utf-8')).hexdigest()[:8].upper()
                
                # ##### ALTERAÇÃO: PREPARAÇÃO DE MÚLTIPLAS LINHAS PARA ENVIO #####
                rows_to_append = []
                
                # Itera sobre as 3 respostas (Consigo, Com o Outro, Com o Todo) e cria uma linha para cada
                for registro in respostas_tabela:
                    row_data = [
                        timestamp_str,                          # Timestamp
                        id_organizacao,                         # ID_FORMULARIO
                        nome_completo,                          # NOME_COMPLETO
                        data_nascimento.strftime('%d/%m/%Y'),   # DATA_NASC
                        contato,                                # CONTATO
                        area_empresa,                           # AREA_EMPRESA
                        funcao_cargo,                           # FUNCAO
                        registro["Vortice"],                    # VORTICE (Variável por linha)
                        registro["Prioridade"],                 # PRIORIDADE (Variável por linha)
                        registro["Fractal"],                    # FRACTAL_COMPORTAMENTO (Variável por linha)
                        registro["Justificativa"]               # JUSTIFICATIVA (Variável por linha)
                    ]
                    rows_to_append.append(row_data)

                # Envia as 3 linhas de uma vez para o Google Sheets
                ws_respostas.append_rows(rows_to_append, value_input_option='USER_ENTERED')
                
                st.success("Formulário enviado com sucesso!")
                st.balloons()
                
            except Exception as e:
                st.error(f"Erro ao enviar dados para a planilha: {e}")

# --- BOTÃO INVISÍVEL PARA PINGER ---
placeholder = st.empty()
with placeholder:
    st.markdown('<div id="autoclick-div">', unsafe_allow_html=True) 
    if st.button("Ping Button", key="autoclick_button"):
        print("Ping button clicked by automation.")
    st.markdown('</div>', unsafe_allow_html=True)