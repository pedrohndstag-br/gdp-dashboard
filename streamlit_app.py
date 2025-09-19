import os
import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from datetime import datetime

st.set_page_config(page_title="Relatório de Faturamento", layout="wide")
st.title("📊 Relatório de Faturamento")

LOCAL_FILE = "Controle_Pedidos.xlsx"
DEFAULT_ONEDRIVE = "https://1drv.ms/x/c/193EB5E7297B4F7D/EZgeF0J4CKVMlKfmZSWahXUBrhXgnl7mbBoVOlpNyWtfXw?e=cciTkd"

def download_excel_bytes(url, timeout=20):
    try:
        resp = requests.get(url, allow_redirects=True, timeout=timeout)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        return None

def load_excel_from_bytes(bts, sheet_name="data"):
    try:
        return pd.read_excel(io.BytesIO(bts), sheet_name=sheet_name)
    except Exception:
        return None

def load_from_local(path, sheet_name="data"):
    try:
        return pd.read_excel(path, sheet_name=sheet_name)
    except Exception:
        return None

# Escolha da fonte de dados
st.sidebar.header("Fonte de dados")
sources = []
if os.path.exists(LOCAL_FILE):
    sources.append("Local")
sources.append("OneDrive (padrão)")
sources.append("Upload")
source = st.sidebar.selectbox("Selecione a fonte", sources)

df = None

if source == "Local":
    df = load_from_local(LOCAL_FILE, sheet_name="data")
    if df is None:
        st.error(f"Erro ao ler {LOCAL_FILE} (verifique se a aba 'data' existe).")
elif source == "OneDrive (padrão)":
    url = st.sidebar.text_input("URL OneDrive", value=DEFAULT_ONEDRIVE)
    if st.sidebar.button("Baixar planilha do OneDrive"):
        st.info("Baixando a planilha...")
        bts = download_excel_bytes(url)
        if bts is None:
            st.error("Falha ao baixar a planilha. Verifique a URL ou a conexão.")
        else:
            df = load_excel_from_bytes(bts, sheet_name="data")
            if df is None:
                st.error("A planilha foi baixada, mas não foi possível ler a aba 'data'.")
elif source == "Upload":
    uploaded = st.file_uploader("Faça upload do arquivo Excel (aba 'data')", type=["xlsx", "xls"])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, sheet_name="data")
        except Exception:
            st.error("Não foi possível ler a aba 'data' do arquivo enviado.")

if df is None:
    st.info("Nenhum dataset carregado ainda. Selecione uma fonte e carregue a planilha.")
    st.stop()

# --- Normalizações e validações ---
df.columns = df.columns.str.strip().str.upper()
required = {"SIGLA", "VALOR TOTAL", "STATUS", "DATA"}
if not required.issubset(set(df.columns)):
    st.error(f"A planilha deve conter as colunas: {', '.join(required)} (colunas atuais: {', '.join(df.columns[:10])}...)")
    st.stop()

df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
df["STATUS"] = df["STATUS"].astype(str).str.upper()
df["SIGLA"] = df["SIGLA"].astype(str).str.strip()

# --- Filtros na sidebar ---
st.sidebar.header("Filtros")
siglas = sorted(df["SIGLA"].dropna().unique().tolist())
siglas_sel = st.sidebar.multiselect("Clientes (SIGLA)", siglas, default=siglas if siglas else [])

data_min = df["DATA"].min()
data_max = df["DATA"].max()
if pd.isna(data_min) or pd.isna(data_max):
    data_min = datetime.today()
    data_max = datetime.today()
data_range = st.sidebar.date_input("Intervalo de Datas", [data_min.date(), data_max.date()])

# normalizar data_range
if isinstance(data_range, list) and len(data_range) == 2:
    dt_start, dt_end = pd.to_datetime(data_range[0]), pd.to_datetime(data_range[1])
else:
    dt_start = pd.to_datetime(data_min)
    dt_end = pd.to_datetime(data_max)

# --- Aplicar filtro ---
df_filt = df[
    (df["STATUS"] == "FATURADO") &
    (df["SIGLA"].isin(siglas_sel)) &
    (df["DATA"].between(dt_start, dt_end))
]

if df_filt.empty:
    st.info("Nenhum pedido FATURADO encontrado para os filtros selecionados.")
    st.stop()

# --- Agrupamento e métricas ---
df_resumo = df_filt.groupby("SIGLA", as_index=False)["VALOR TOTAL"].sum()
df_resumo = df_resumo.sort_values("VALOR TOTAL", ascending=False)
faturamento_total = df_filt["VALOR TOTAL"].sum()

st.subheader("💰 Total Pago por Cliente")
st.dataframe(df_resumo, use_container_width=True)
st.metric("📈 Faturamento Total", f"R$ {faturamento_total:,.2f}")

# --- Gráfico ---
st.subheader("📉 Gráfico de Faturamento")
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(df_resumo["SIGLA"], df_resumo["VALOR TOTAL"], color="steelblue")
ax.set_xlabel("Cliente (SIGLA)")
ax.set_ylabel("Valor Total (R$)")
ax.set_title("Pedidos FATURADOS")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# salvar imagem para PDF
img_bytes = io.BytesIO()
fig.savefig(img_bytes, format="png", bbox_inches="tight")
img_bytes.seek(0)

# --- Gerar PDF ---
def gerar_pdf_bytes(periodo_start, periodo_end, fatur_total, image_bytes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Relatório de Faturamento", ln=True, align="C")
    pdf.ln(4)
    pdf.cell(200, 8, f"Período: {periodo_start.date()} a {periodo_end.date()}", ln=True, align="C")
    pdf.ln(4)
    pdf.cell(200, 8, f"Faturamento Total: R$ {fatur_total:,.2f}", ln=True, align="C")
    # salvar imagem temporária em memória
    img_path = "grafico_temp.png"
    with open(img_path, "wb") as f:
        f.write(image_bytes.read())
    pdf.image(img_path, x=10, y=50, w=190)
    # limpar arquivo temporário
    try:
        os.remove(img_path)
    except Exception:
        pass
    out = pdf.output(dest="S").encode("latin-1")
    return out

pdf_bytes = gerar_pdf_bytes(dt_start, dt_end, faturamento_total, io.BytesIO(img_bytes.getvalue()))

st.download_button("📄 Baixar PDF", data=pdf_bytes, file_name="relatorio.pdf", mime="application/pdf")

# --- Exportar Excel resumo ---
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    df_resumo.to_excel(writer, index=False, sheet_name="Resumo")
excel_buffer.seek(0)
st.download_button("📥 Baixar Excel", data=excel_buffer, file_name="resumo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Enviar por e-mail (opcional) ---
st.subheader("📤 Enviar por E-mail (opcional)")
email_dest = st.text_input("E-mail do destinatário:")
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE") or ""
SENHA_REMETENTE = os.getenv("SENHA_REMETENTE") or ""

def enviar_email(destinatario, remetente, senha, arquivo_bytes):
    if not remetente or not senha:
        return "Variáveis de ambiente EMAIL_REMETENTE e SENHA_REMETENTE não configuradas."
    try:
        msg = EmailMessage()
        msg["Subject"] = "Relatório de Faturamento"
        msg["From"] = remetente
        msg["To"] = destinatario
        msg.set_content(f"Segue em anexo o relatório de faturamento.\n\nTotal: R$ {faturamento_total:,.2f}")
        msg.add_attachment(arquivo_bytes, maintype="application", subtype="pdf", filename="relatorio.pdf")
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(remetente, senha)
            smtp.send_message(msg)
        return True
    except Exception as e:
        return str(e)

if st.button("✉️ Enviar Relatório por E-mail"):
    if not email_dest:
        st.warning("Digite um e-mail válido.")
    else:
        resultado = enviar_email(email_dest, EMAIL_REMETENTE, SENHA_REMETENTE, pdf_bytes)
        if resultado is True:
            st.success("✅ E-mail enviado com sucesso!")
        else:
            st.error(f"Erro ao enviar: {resultado}")
