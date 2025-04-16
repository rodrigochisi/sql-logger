import streamlit as st
from datetime import datetime
import pandas as pd
from supabase import create_client, Client

# Conexão com o Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Editor de Variáveis SQL", layout="wide")
st.title("🧠 Editor de Variáveis SQL - Com Log de Alterações")

# 🔎 Campo de busca
filtro_nome = st.text_input("🔍 Buscar variável por nome (parcial):")
filtro_unidade = st.text_input("🏥 Filtrar por unidade (opcional):")

# 📥 Consulta variáveis do banco
query = supabase.table("variaveis_sql").select("*")

if filtro_nome:
    query = query.ilike("nome", f"%{filtro_nome}%")
if filtro_unidade:
    query = query.ilike("unidade", f"%{filtro_unidade}%")

variaveis = query.order("nome", asc=True).execute()
df_variaveis = pd.DataFrame(variaveis.data)

if df_variaveis.empty:
    st.info("Nenhuma variável encontrada.")
    st.stop()

# 🧾 Seleção da variável
variavel_selecionada = st.selectbox(
    "Selecione a variável para editar:",
    options=df_variaveis["nome"],
    format_func=lambda nome: nome
)

row = df_variaveis[df_variaveis["nome"] == variavel_selecionada].iloc[0]
conteudo_atual = row["conteudo"]
id_variavel = row["id"]

st.subheader(f"✏️ Editando: {variavel_selecionada}")
novo_conteudo = st.text_area("Conteúdo SQL:", value=conteudo_atual, height=300)

col1, col2 = st.columns([2, 1])
with col1:
    nome_autor = st.text_input("👤 Seu nome:")
with col2:
    proposito = st.text_input("📝 Motivo da alteração:")

if st.button("💾 Salvar Alteração"):
    if not nome_autor or not proposito:
        st.warning("Preencha todos os campos para salvar.")
    else:
        supabase.table("variaveis_sql").update({"conteudo": novo_conteudo}).eq("id", id_variavel).execute()

        supabase.table("log_edicoes").insert({
            "variavel_id": id_variavel,
            "variavel": variavel_selecionada,
            "autor": nome_autor,
            "proposito": proposito,
            "data_hora": datetime.now().isoformat()
        }).execute()

        st.success("✅ Alteração salva e registrada com sucesso!")
        st.balloons()

# 📜 Exibir últimos logs dessa variável
st.subheader("📑 Histórico de alterações")
logs = supabase.table("log_edicoes").select("*").eq("variavel_id", id_variavel).order("data_hora", desc=True).limit(10).execute()
df_logs = pd.DataFrame(logs.data)

if not df_logs.empty:
    df_logs["data_hora"] = pd.to_datetime(df_logs["data_hora"]).dt.strftime("%d/%m/%Y %H:%M")
    st.dataframe(df_logs[["data_hora", "autor", "proposito"]])
else:
    st.info("Sem alterações registradas ainda.")
