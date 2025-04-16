import streamlit as st
from datetime import datetime
import pandas as pd
from supabase import create_client, Client
import os

# Inicialização do Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("📝 Editor de Scripts SQL com Log no Supabase")

# Interface para registrar alteração
arquivo = st.text_input("📄 Nome do arquivo SQL (ex: Financeiro/INS_CC.sql)")
autor = st.text_input("👤 Seu nome")
proposito = st.text_input("✏️ Propósito da alteração")

if st.button("💾 Salvar alteração"):
    if not arquivo or not autor or not proposito:
        st.warning("Preencha todos os campos.")
    else:
        response = supabase.table("log_edicoes").insert({
            "data_hora": datetime.now().isoformat(),
            "variavel": arquivo,
            "autor": autor,
            "proposito": proposito
        }).execute()

    if response.data and not response.error:
       st.success("✅ Alteração registrada com sucesso no banco de dados.")
    else:
       st.error(f"❌ Erro ao registrar: {response.error}")


# Mostrar os últimos logs
st.subheader("📑 Últimos registros")
logs = supabase.table("log_edicoes").select("*").order("data_hora", desc=True).limit(10).execute()
df = pd.DataFrame(logs.data)
if not df.empty:
    st.dataframe(df)
else:
    st.info("Nenhum registro encontrado.")