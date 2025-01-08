import pandas as pd
import camelot
import os

import pandas as pd
import camelot
import os

def processar_tabelas_pdf_camelot(pdf_path: str, pagina_index: int) -> pd.DataFrame:
    try:
        tabelas = camelot.read_pdf(
            pdf_path,
            pages=str(pagina_index),
            flavor="stream",
            row_tol=7.5
        )
        
        if not tabelas or len(tabelas) == 0:
            return None

        # Combinar múltiplas tabelas em um único DataFrame, se necessário
        frames = [tabela.df for tabela in tabelas]
        df = pd.concat(frames, ignore_index=True)

        # Usar a primeira linha como cabeçalho
        df.columns = pd.io.parsers.ParserBase({'names': df.iloc[0]})._maybe_dedup_names(df.iloc[0])
        df = df[1:]  # Excluir a primeira linha do corpo do DataFrame
        df.reset_index(drop=True, inplace=True)
        
        return df
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        return None


def processar_pdf_e_salvar(pdf_path: str, paginas: list, output_dir: str = "."):
    nome_do_arquivo = os.path.splitext(os.path.basename(pdf_path))[0]

    for pagina_index in paginas:
        print(f"Processando página {pagina_index}...")
        df = processar_tabelas_pdf_camelot(pdf_path, pagina_index)

        if df is not None:
            output_file = os.path.join(output_dir, f"{nome_do_arquivo}_pagina{pagina_index}.xlsx")
            df.to_excel(output_file, index=False)
            print(f"Tabela da página {pagina_index} salva como {output_file}.")
        else:
            print(f"Nenhuma tabela foi encontrada na página {pagina_index}.")
