import streamlit as st
import pandas as pd
import os
import glob

# Configuração da página
st.set_page_config(
    page_title="Gerenciador de Estoque - CDR",
    page_icon="🛡️",
    layout="wide"
)

# Tenta encontrar o arquivo correto de forma inteligente
def encontrar_arquivo():
    nome_exato = "Produtos- CDR.xlsx - Página3.csv"
    if os.path.exists(nome_exato):
        return nome_exato
    arquivos_csv = glob.glob("*.csv")
    if arquivos_csv:
        return arquivos_csv[0]
    return None

CSV_FILE = encontrar_arquivo()

def load_data():
    if CSV_FILE and os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df.columns = df.columns.str.strip()
        
        colunas_uteis = ['Nome do item', 'Tipo', 'Coluna 1', 'Estoque', 'Status']
        df_clean = df[df['Nome do item'].notna()].copy()
        df_clean = df_clean[colunas_uteis]
        
        df_clean.columns = ['Item', 'Tipo', 'Tamanho', 'Estoque', 'Status']
        
        df_clean['Item'] = df_clean['Item'].astype(str).str.strip()
        df_clean['Tamanho'] = df_clean['Tamanho'].astype(str).str.strip()
        df_clean['Status'] = df_clean['Status'].astype(str).str.strip()
        df_clean['Estoque'] = pd.to_numeric(df_clean['Estoque'], errors='coerce').fillna(0).astype(int)
        
        return df_clean.reset_index(drop=True)
    else:
        return pd.DataFrame(columns=['Item', 'Tipo', 'Tamanho', 'Estoque', 'Status'])

# Inicializa o estado do app
if 'df_estoque' not in st.session_state or st.session_state.df_estoque.empty:
    st.session_state.df_estoque = load_data()

df = st.session_state.df_estoque

# --- INTERFACE ---

st.title("🛡️ Gerenciador de Estoque - CDR")
st.markdown("Controle de produtos e tirantes da Atlética.")
st.write("---")

if not CSV_FILE:
    st.error("❌ Nenhum arquivo CSV foi detectado na pasta atual!")
    st.stop()

# Métricas Rápidas
if not df.empty:
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Modelos Cadastrados", len(df))
    with col_m2:
        st.metric("Total de Peças Físicas", int(df['Estoque'].sum()))
    with col_m3:
        grossos = len(df[df['Tamanho'].str.lower() == 'grosso'])
        finos = len(df[df['Tamanho'].str.lower() == 'fino'])
        st.metric("Modelos Grossos / Finos", f"{grossos} / {finos}")
    st.write("---")

col_esquerda, col_direita = st.columns([1, 1.5])

with col_esquerda:
    st.subheader("📝 Editar Item")
    
    if not df.empty:
        opcoes_itens = sorted(df['Item'].unique())
        item_selecionado = st.selectbox("Selecione o Produto:", opcoes_itens)
        
        sub_df = df[df['Item'] == item_selecionado]
        opcoes_tamanho = sorted(sub_df['Tamanho'].unique())
        tamanho_selecionado = st.selectbox("Tamanho/Espessura:", opcoes_tamanho)
        
        linha_filtrada = df[(df['Item'] == item_selecionado) & (df['Tamanho'] == tamanho_selecionado)]
        
        if not linha_filtrada.empty:
            idx = linha_filtrada.index[0]
            
            estoque_atual = int(df.at[idx, 'Estoque'])
            novo_estoque = st.number_input("Quantidade em Estoque:", min_value=0, value=estoque_atual, step=1, key=f"est_{idx}")
            
            status_atual = df.at[idx, 'Status']
            opcoes_status = ["Em Estoque", "Quase Acabando", "Esgotado"]
            idx_status = opcoes_status.index(status_atual) if status_atual in opcoes_status else 0
            novo_status = st.selectbox("Status Atual:", opcoes_status, index=idx_status, key=f"stat_{idx}")
            
            if st.button("💾 Atualizar Dados", type="primary"):
                st.session_state.df_estoque.at[idx, 'Estoque'] = int(novo_estoque)
                st.session_state.df_estoque.at[idx, 'Status'] = novo_status
                st.success("Alterações salvas!")
                st.rerun()
    else:
        st.error("Nenhum dado disponível.")

with col_direita:
    st.subheader(f"📋 Tabela de Inventário ({CSV_FILE})")
    
    if not df.empty:
        busca = st.text_input("🔍 Filtrar por nome:")
        df_display = df.copy()
        if busca:
            df_display = df_display[df_display['Item'].str.contains(busca, case=False)]
            
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Planilha Atualizada",
            data=csv_data,
            file_name="Estoque_CDR_Atualizado.csv",
            mime="text/csv"
        )

st.write("---")
if st.button("🔄 Forçar Recarregamento"):
    st.session_state.df_estoque = load_data()
    st.rerun()