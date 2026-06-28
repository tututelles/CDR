import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(
    page_title="Gerenciador de Estoque - CDR",
    page_icon="🛡️",
    layout="wide"
)

CSV_FILE = "Produtos- CDR.xlsx - Página3.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        # Lê o CSV original
        df = pd.read_csv(CSV_FILE)
        
        # Remove espaços ocultos dos nomes das colunas
        df.columns = df.columns.str.strip()
        
        # Garante que vamos pegar apenas as colunas que importam para a tabela
        # Se 'Nome do item' não for a primeira, filtramos pelas colunas nomeadas
        colunas_uteis = ['Nome do item', 'Tipo', 'Coluna 1', 'Estoque', 'Status']
        
        # Filtrando apenas as linhas onde o 'Nome do item' realmente contém texto válido
        df_clean = df[df['Nome do item'].notna()].copy()
        df_clean = df_clean[colunas_uteis]
        
        # Renomeia para exibição limpa na interface
        df_clean.columns = ['Item', 'Tipo', 'Tamanho', 'Estoque', 'Status']
        
        # Limpa espaços e formata os tipos de dados
        df_clean['Item'] = df_clean['Item'].astype(str).str.strip()
        df_clean['Tamanho'] = df_clean['Tamanho'].astype(str).str.strip()
        df_clean['Status'] = df_clean['Status'].astype(str).str.strip()
        df_clean['Estoque'] = pd.to_numeric(df_clean['Estoque'], errors='coerce').fillna(0).astype(int)
        
        # Remove possíveis linhas de lixo ou títulos duplicados
        df_clean = df_clean[df_clean['Item'] != 'Nome do item']
        
        return df_clean.reset_index(drop=True)
    else:
        st.error(f"Arquivo {CSV_FILE} não encontrado no diretório!")
        return pd.DataFrame(columns=['Item', 'Tipo', 'Tamanho', 'Estoque', 'Status'])

# Inicializa ou força a atualização do estado do app
if 'df_estoque' not in st.session_state:
    st.session_state.df_estoque = load_data()

df = st.session_state.df_estoque

# --- INTERFACE ---

st.title("🛡️ Gerenciador de Estoque - CDR")
st.markdown("Controle de produtos e tirantes da Atlética.")
st.write("---")

# Métricas Rápidas
if not df.empty:
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Modelos Cadastrados", len(df))
    with col_m2:
        st.metric("Total de Peças Físicas", int(df['Estoque'].sum()))
    with col_m3:
        # Conta usando a coluna ajustada 'Tamanho'
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
                st.success(f"Alterações salvas para {item_selecionado} ({tamanho_selecionado})!")
                st.rerun()
        else:
            st.warning("Selecione as características para editar.")
    else:
        st.error("Nenhum dado disponível para edição.")

with col_direita:
    st.subheader("📋 Tabela de Inventário")
    
    if not df.empty:
        busca = st.text_input("🔍 Filtrar por nome:")
        df_display = df.copy()
        if busca:
            df_display = df_display[df_display['Item'].str.contains(busca, case=False)]
            
        st.dataframe(
            df_display, 
            use_container_width=True,
            hide_index=True
        )

        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Planilha Atualizada",
            data=csv_data,
            file_name="Estoque_CDR_Atualizado.csv",
            mime="text/csv"
        )
    else:
        st.warning("Não foi possível renderizar a tabela. Verifique o arquivo CSV.")

# Botão para resetar cache se necessário
st.write("---")
if st.button("🔄 Forçar Recarregamento Total do CSV Original"):
    st.session_state.df_estoque = load_data()
    st.rerun()