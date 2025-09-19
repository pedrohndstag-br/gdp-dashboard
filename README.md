# dashboard template (adaptado)

App Streamlit para geração de relatório de faturamento a partir de um Excel.

Como rodar

1. Crie/ative um ambiente Python (recomendado).
2. Instale dependências:
   pip install streamlit pandas matplotlib fpdf2 openpyxl
3. Coloque seu arquivo Excel chamado `Controle_Pedidos.xlsx` na raiz do projeto
   ou use o uploader dentro do app.
4. Rode:
   streamlit run streamlit_app.py

Abrir no navegador

- O Streamlit inicia em <http://localhost:8501>
- Há uma configuração de depuração em .vscode/launch.json para abrir o Chrome automaticamente na URL acima (após iniciar o streamlit).

Observações

- Colunas esperadas: SIGLA, VALOR TOTAL, STATUS, DATA
- Para envio por e-mail via Gmail, defina as variáveis de ambiente:
  EMAIL_REMETENTE e SENHA_REMETENTE (use senha de app se necessário).