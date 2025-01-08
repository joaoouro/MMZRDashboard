from typing import List, Tuple, Optional
import streamlit as st
import pandas as pd
import io
from pdf_to_excel import processar_tabelas_pdf_camelot

TITULO = "📊 PDF para Excel - Dashboard"
CONFIGURACAO_PAGINA = {
    "page_title": "PDF para Excel Dashboard",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
TIPOS_ARQUIVO_PERMITIDOS = ["pdf"]

class EstadoDashboard:
    """Gerencia as variáveis de estado do dashboard."""
    
    def __init__(self):
        if "resetar" not in st.session_state:
            st.session_state["resetar"] = False
        if "chave_widget" not in st.session_state:
            st.session_state["chave_widget"] = 0
        if "dados_processados" not in st.session_state:
            st.session_state["dados_processados"] = None

    def resetar(self) -> None:
        """Reseta o estado do dashboard."""
        st.session_state["resetar"] = True
        st.session_state["chave_widget"] += 1
        st.session_state["dados_processados"] = None

def configurar_pagina() -> None:
    """Configura as definições iniciais da página."""
    st.set_page_config(**CONFIGURACAO_PAGINA)
    st.title(TITULO)

def processar_pdf(arquivo_carregado: io.BytesIO, paginas_input: str) -> Optional[List[Tuple[int, pd.DataFrame]]]:
    """
    Processa o arquivo PDF carregado e extrai tabelas.
    
    Args:
        arquivo_carregado: O arquivo PDF carregado
        paginas_input: String contendo números de página separados por vírgula
        
    Returns:
        Lista de tuplas contendo número da página e DataFrame correspondente
    """
    try:
        if not paginas_input.strip():
            raise ValueError("A lista de páginas está vazia.")
        
        indices_pagina = [int(p.strip()) for p in paginas_input.split(",") if p.strip().isdigit()]
        
        if not indices_pagina:
            raise ValueError("Nenhuma página válida foi encontrada.")

        nome_arquivo = arquivo_carregado.name.replace(".pdf", "")
        tabelas_processadas = []

        for indice_pagina in indices_pagina:
            st.write(f"Processando página {indice_pagina}...")
            df = processar_tabelas_pdf_camelot(arquivo_carregado, indice_pagina)
            
            if df is not None:
                tabelas_processadas.append((indice_pagina, df))
            else:
                st.warning(f"Nenhuma tabela encontrada na página {indice_pagina}.")

        st.session_state["nome_arquivo"] = nome_arquivo
        return tabelas_processadas

    except ValueError as e:
        st.sidebar.error(f"Erro: {e}")
        return None

def exibir_resultados(dados_processados: List[Tuple[int, pd.DataFrame]]) -> None:
    """Exibe os dados processados e botões de download."""
    st.header("📋 Dados Extraídos")
    for indice_pagina, df in dados_processados:
        st.subheader(f"Dados da Página {indice_pagina}")
        st.dataframe(df)

        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        st.download_button(
            label=f"Baixar Excel - Página {indice_pagina}",
            data=buffer,
            file_name=f"{st.session_state['nome_arquivo']}_pagina{indice_pagina}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def principal():
    """Função principal do aplicativo."""
    configurar_pagina()
    estado_dashboard = EstadoDashboard()

    # Configuração da barra lateral
    st.sidebar.header("Configurações")
    arquivo_carregado = st.sidebar.file_uploader(
        "Carregue o arquivo PDF",
        type=TIPOS_ARQUIVO_PERMITIDOS,
        key=f"carregador_arquivo_{st.session_state['chave_widget']}"
    )
    paginas_input = st.sidebar.text_input(
        "Insira as páginas a serem processadas (separe por vírgulas):",
        key=f"entrada_texto_{st.session_state['chave_widget']}"
    )

    if arquivo_carregado is not None and st.session_state["dados_processados"] is None:
        st.sidebar.success(f"Arquivo {arquivo_carregado.name} carregado com sucesso!")
        
        if st.sidebar.button("Processar PDF"):
            st.session_state["dados_processados"] = processar_pdf(arquivo_carregado, paginas_input)

    if st.session_state["dados_processados"]:
        exibir_resultados(st.session_state["dados_processados"])
        
        st.markdown("---")
        if st.button("Iniciar Novo Processo"):
            estado_dashboard.resetar()
            st.rerun()

if __name__ == "__main__":
    principal()
