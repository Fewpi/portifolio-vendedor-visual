import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# Configuração da Página (Para ocupar toda a largura)
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Carregamento dos Dados
df = conn.read()

df['Data'] = pd.to_datetime(df['Data']) # Garante que a data é lida corretamente
df = df.sort_values('Data')

# 2. Barra Lateral (Filtros)
st.sidebar.header("Filtros")

vendedor_selecionado = st.sidebar.multiselect(
    "Filtrar por Vendedor:",
    options=df['Vendedor'].unique(),
    default=df['Vendedor'].unique() # Por padrão, seleciona todos
)

# Aplicando o filtro na tabela
df_filtrado = df[df['Vendedor'].isin(vendedor_selecionado)]

# 3. Título e KPIs (Indicadores Principais)
st.title("📊 Vendedor Visual - Análise de Performance")
st.markdown("---")

total_vendas = df_filtrado['Valor Total'].sum()
total_qtd = df_filtrado['Quantidade'].sum()
ticket_medio = total_vendas / df_filtrado.shape[0]

# Colunas para exibir os números grandes
col1, col2, col3 = st.columns(3)
col1.metric("Faturamento Total", f"R$ {total_vendas:,.2f}")
col2.metric("Vendas Realizadas", total_qtd)
col3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

st.markdown("---")

# 4. Gráficos (A parte visual que vende)
col_graf1, col_graf2 = st.columns(2)

# Gráfico de Linha: Vendas por Mês
vendas_mensais = df_filtrado.set_index('Data').resample('M')['Valor Total'].sum().reset_index()

fig_linha = px.line(vendas_mensais, x='Data', y='Valor Total', title="Evolução do Faturamento Mensal", color_discrete_sequence=['#00FF7F'])
fig_linha.update_traces(line_shape='spline', line_width=4) # Deixa a linha curva e grossa
col_graf1.plotly_chart(fig_linha, use_container_width=True)

# Gráfico de Barras: Top Produtos
top_produtos = df_filtrado.groupby('Produto')['Valor Total'].sum().reset_index().sort_values('Valor Total', ascending=False)
fig_barras = px.bar(top_produtos, x='Valor Total', y='Produto', orientation='h', title="Ranking de Produtos Mais Vendidos", color_discrete_sequence=['#00FF7F']
    )
col_graf2.plotly_chart(fig_barras, use_container_width=True)

# 5. Tabela de Dados (Para quem gosta de ver o detalhe)
with st.expander("Ver Base de Dados Completa"):
    st.dataframe(df_filtrado)