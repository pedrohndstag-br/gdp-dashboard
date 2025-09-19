# :earth_americas: GDP dashboard template

A simple Streamlit app showing the GDP of different countries in the world.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gdp-dashboard-template.streamlit.app/)

### How to run it on your own machine
pip install streamlit pandas matplotlib fpdf2 openpyxl
1. Install the requirements

   $ pip install -r requirements.txt
   ```streamlit
pandas
matplotlib
fpdf2
openpyxl


2. Run the app

   ```import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

# ---------------- CONFIGURAÇÕES ----------------
st.set_page_config(page_title="Relatório de Faturamento", layout="wide")
st.title("📊 Relatório de Faturamento - Venditx | McDonald's")

# ---------------- LEITURA DA PLANILHA ----------------
ARQUIVO_EXCEL = "Controle_Pedidos.xlsx"  # renomeie aqui seu arquivo

if not os.path.exists(ARQUIVO_EXCEL):
    st.error(f"⚠️ Arquivo '{ARQUIVO_EXCEL}' não encontrado.")
    st.stop()

df = pd.read_excel(ARQUIVO_EXCEL)
df.columns = df.columns.str.strip().str.upper()

# Verificação mínima
if not {"SIGLA", "VALOR TOTAL", "STATUS", "DATA"}.issubset(df.columns):
    st.error("⚠️ A planilha deve conter: SIGLA, VALOR TOTAL, STATUS e DATA.")
    st.stop()

df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
df["STATUS"] = df["STATUS"].str.upper()

# ---------------- FILTROS ----------------
st.sidebar.header("Filtros")
siglas = sorted(df["SIGLA"].dropna().unique())
siglas_sel = st.sidebar.multiselect("Clientes (SIGLA)", siglas, default=siglas)

data_min, data_max = df["DATA"].min(), df["DATA"].max()
data_inicio, data_fim = st.sidebar.date_input("Intervalo de Datas", [data_min, data_max])

# ---------------- FILTRO APLICADO ----------------
df_filt = df[
    (df["STATUS"] == "FATURADO") &
    (df["SIGLA"].isin(siglas_sel)) &
    (df["DATA"].between(pd.to_datetime(data_inicio), pd.to_datetime(data_fim)))
]

# ---------------- AGRUPAMENTO ----------------
df_resumo = df_filt.groupby("SIGLA")["VALOR TOTAL"].sum().reset_index()
df_resumo = df_resumo.sort_values(by="VALOR TOTAL", ascending=False)
faturamento_total = df_filt["VALOR TOTAL"].sum()

# ---------------- RESULTADOS ----------------
st.subheader("💰 Total Pago por Cliente")
st.dataframe(df_resumo, use_container_width=True)
st.metric("📈 Faturamento Total", f"R$ {faturamento_total:,.2f}")

# ---------------- GRÁFICO ----------------
st.subheader("📉 Gráfico de Faturamento")
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(df_resumo["SIGLA"], df_resumo["VALOR TOTAL"], color="steelblue")
ax.set_xlabel("Cliente (SIGLA)")
ax.set_ylabel("Valor Total (R$)")
ax.set_title("Pedidos FATURADOS")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# ---------------- EXPORTAÇÃO PDF ----------------
fig.savefig("grafico.png")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Relatório de Faturamento - Venditx", ln=True, align="C")
    pdf.cell(200, 10, f"Período: {data_inicio} a {data_fim}", ln=True, align="C")
    pdf.cell(200, 10, f"Faturamento Total: R$ {faturamento_total:,.2f}", ln=True, align="C")
    pdf.image("grafico.png", x=10, y=40, w=180)
    pdf.output("relatorio.pdf")

gerar_pdf()
with open("relatorio.pdf", "rb") as f:
    st.download_button("📄 Baixar PDF", f, file_name="relatorio.pdf")

# ---------------- EXPORTAÇÃO EXCEL ----------------
df_resumo.to_excel("resumo.xlsx", index=False)
with open("resumo.xlsx", "rb") as f:
    st.download_button("📥 Baixar Excel", f, file_name="resumo.xlsx")

# ---------------- ENVIO DE E-MAIL ----------------
st.subheader("📤 Enviar por E-mail")
email_dest = st.text_input("E-mail do destinatário:")

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE") or "seu_email@gmail.com"
SENHA_REMETENTE = os.getenv("SENHA_REMETENTE") or "sua_senha_de_app"

def enviar_email(destinatario, arquivo_pdf):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Relatório de Faturamento - Venditx"
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = destinatario
        msg.set_content(f"Segue em anexo o relatório de faturamento.\n\nTotal: R$ {faturamento_total:,.2f}")

        with open(arquivo_pdf, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="relatorio.pdf")

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_REMETENTE, SENHA_REMETENTE)
            smtp.send_message(msg)
        return True
    except Exception as e:
        return str(e)

if st.button("✉️ Enviar Relatório por E-mail"):
    if email_dest:
        resultado = enviar_email(email_dest, "relatorio.pdf")
        if resultado is True:
            st.success("✅ E-mail enviado com sucesso!")
        else:
            st.error(f"Erro: {resultado}")
    else:
        st.warning("⚠️ Digite um e-mail válido.")

   $ streamlit run streamlit_app.py
   ```
  
run.bat
@echo off
echo 🚀 Instalando dependencias...
pip install -r requirements.txt

echo ▶️ Iniciando o Streamlit...
streamlit run app.py
pause