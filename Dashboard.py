import streamlit as st
import pandas as pd
import os
from pdf_to_excel import processar_tabelas_pdf_camelot

# Configuração do layout do Streamlit
st.set_page_config(
    page_title="PDF to Excel Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 PDF para Excel - Dashboard")

# Sidebar para configurações
st.sidebar.header("Configurações")
uploaded_file = st.sidebar.file_uploader("Carregue o arquivo PDF", type=["pdf"])

# Entrada de texto para as páginas
paginas_input = st.sidebar.text_input("Insira as páginas a serem processadas (separe por vírgulas):")

if uploaded_file is not None:
    # Salvar o arquivo PDF carregado em um diretório temporário
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)

    with open(temp_pdf_path, "wb") as temp_file:
        temp_file.write(uploaded_file.getbuffer())

    st.sidebar.success(f"Arquivo {uploaded_file.name} carregado com sucesso!")

    if st.sidebar.button("Processar PDF"):
        try:
            # Processar a entrada das páginas
            if not paginas_input.strip():
                raise ValueError("A lista de páginas está vazia.")
            
            # Limpar a entrada e converter em uma lista de inteiros
            pagina_indices = [int(p.strip()) for p in paginas_input.split(",") if p.strip().isdigit()]

            if not pagina_indices:
                raise ValueError("Nenhuma página válida foi encontrada.")

            nome_do_arquivo = os.path.splitext(uploaded_file.name)[0]
            tabelas_processadas = []

            # Processar cada página
            for pagina_index in pagina_indices:
                st.write(f"Processando página {pagina_index}...")
                df = processar_tabelas_pdf_camelot(temp_pdf_path, pagina_index)

                if df is not None:
                    tabelas_processadas.append((pagina_index, df))
                else:
                    st.warning(f"Nenhuma tabela encontrada na página {pagina_index}.")

            # Exibir as tabelas no dashboard
            if tabelas_processadas:
                st.header("📋 Dados Extraídos")
                for pagina_index, df in tabelas_processadas:
                    st.subheader(f"Dados da Página {pagina_index}")
                    st.dataframe(df)

                    # Salvar o arquivo Excel
                    output_file = os.path.join(temp_dir, f"{nome_do_arquivo}_pagina{pagina_index}.xlsx")
                    df.to_excel(output_file, index=False)

                    # Botão de download
                    with open(output_file, "rb") as excel_file:
                        st.download_button(
                            label=f"Baixar Excel - Página {pagina_index}",
                            data=excel_file,
                            file_name=f"{nome_do_arquivo}_pagina{pagina_index}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.error("Nenhuma tabela foi encontrada nas páginas especificadas.")
        except ValueError as e:
            st.sidebar.error(f"Erro: {e}")
else:
    st.sidebar.info("Carregue um PDF para começar.")
