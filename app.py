import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(
    page_title="Gerenciador de Estoque - CDR",
    page_icon="🛡️",
    layout="wide"
)

# Estilização Customizada via CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stNumberInput div {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

CSV_FILE = "Produtos- CDR.xlsx - Página3.csv"

@st.cache_data
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Seleciona as colunas reais do arquivo enviado
        df_clean = df[['Nome do item', 'Tipo', 'Coluna 1', 'Estoque', 'Status']].dropna(subset=['Nome do item'])
        df_clean.columns = ['Item', 'Tipo', 'Tamanho', 'Estoque', 'Status']
        df_clean['Estoque'] = pd.to_numeric(df_clean['Estoque'], errors='coerce').fillna(0).astype(int)
        return df_clean
    else:
        return pd.DataFrame(columns=['Item', 'Tipo', 'Tamanho', 'Estoque', 'Status'])

# Inicializa o estado do app
if 'df_estoque' not in st.session_state:
    st.session_state.df_estoque = load_data()

df = st.session_state.df_estoque

# --- INTERFACE ---

st.title("🛡️ Gerenciador de Estoque - CDR")
st.markdown("Controle de produtos e tirantes da Atlética.")
st.write("---")

# Métricas Rápidas
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Modelos Cadastrados", len(df))
with col_m2:
    st.metric("Total de Peças Físicas", int(df['Estoque'].sum()))
with col_m3:
    st.metric("Modelos Grossos / Finos", f"{len(df[df['Tamanho']=='Grosso'])} / {len(df[df['Tamanho']=='Fino'])}")

st.write("---")

col_esquerda, col_direita = st.columns([1, 1.5])

with col_esquerda:
    st.subheader("📝 Editar Item")
    
    item_selecionado = st.selectbox("Selecione o Produto:", df['Item'].unique())
    
    sub_df = df[df['Item'] == item_selecionado]
    tamanho_selecionado = st.selectbox("Tamanho/Espessura:", sub_df['Tamanho'].unique())
    
    # Localiza o índice exato na tabela
    idx = df[(df['Item'] == item_selecionado) & (df['Tamanho'] == tamanho_selecionado)].index[0]
    
    estoque_atual = int(df.at[idx, 'Estoque'])
    novo_estoque = st.number_input("Quantidade em Estoque:", min_value=0, value=estoque_atual, step=1)
    
    status_atual = df.at[idx, 'Status']
    opcoes_status = ["Em Estoque", "Quase Acabando", "Esgotado"]
    novo_status = st.selectbox("Status Atual:", opcoes_status, 
                               index=opcoes_status.index(status_atual) if status_atual in opcoes_status else 0)
    
    if st.button("💾 Atualizar Dados", type="primary"):
        st.session_state.df_estoque.at[idx, 'Estoque'] = int(novo_estoque)
        st.session_state.df_estoque.at[idx, 'Status'] = novo_status
        st.success(f"Alterações salvas para {item_selecionado} ({tamanho_selecionado})!")
        st.rerun()

with col_direita:
    st.subheader("📋 Tabela de Inventário")
    
    busca = st.text_input("🔍 Filtrar por nome:")
    df_display = df.copy()
    if busca:
        df_display = df_display[df_display['Item'].str.contains(busca, case=False)]
        
    st.dataframe(
        df_display, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "Estoque": st.column_config.NumberColumn("Quantidade", format="%d"),
        }
    )

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Planilha Atualizada",
        data=csv_data,
        file_name="Estoque_CDR_Atualizado.csv",
        mime="text/csv"
    )