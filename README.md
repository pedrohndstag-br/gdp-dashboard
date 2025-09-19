# dashboard template (adaptado)

App Streamlit para geração de relatório de faturamento a partir de um Excel.

Como rodar (passos exatos)

1. Abra um terminal no container/workspace.
2. Instale dependências:
   pip install streamlit pandas matplotlib fpdf2 openpyxl requests
   ou, se tiver requirements.txt:
   pip install -r requirements.txt
3. Rode o app:
   streamlit run streamlit_app.py
4. No navegador (Chrome) abra:
   http://localhost:8501
5. No app:
   - Seleccione "OneDrive (padrão)" na sidebar e confirme/edite a URL se necessário.
   - O app tentará baixar automaticamente a aba "data" da URL fornecida.
   - Se a opção "Salvar cópia local em Controle_Pedidos.xlsx" estiver marcada, uma cópia será salva na raiz do projeto e aparecerá no explorador do workspace.
   - Se preferir, você também pode colocar um arquivo chamado `Controle_Pedidos.xlsx` manualmente na raiz do projeto ou usar o uploader.

Observações
- Colunas esperadas: SIGLA, VALOR TOTAL, STATUS, DATA
- Para envio por e-mail via Gmail, defina as variáveis de ambiente:
  EMAIL_REMETENTE e SENHA_REMETENTE (use senha de app se necessário).

Nota
- Eu não consigo executar comandos nem abrir o Chrome por você. Siga os passos acima no seu ambiente. Se aparecer qualquer erro no terminal ou no Streamlit, cole aqui a mensagem e eu ajudo a corrigir.