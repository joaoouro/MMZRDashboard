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
        df.columns = pd.io.parsers._maybe_dedup_names(df.iloc[0])
        df = df[1:]  # Excluir a primeira linha do corpo do DataFrame
        df.reset_index(drop=True, inplace=True)
        
        return df
    except AttributeError as e:
        # Lidar com versões mais recentes do pandas que não têm _maybe_dedup_names
        if "maybe_dedup_names" in str(e):
            # Renomear manualmente colunas duplicadas
            def rename_duplicates(columns):
                seen = {}
                new_columns = []
                for col in columns:
                    if col in seen:
                        seen[col] += 1
                        new_columns.append(f"{col}.{seen[col]}")
                    else:
                        seen[col] = 0
                        new_columns.append(col)
                return new_columns

            tabelas = camelot.read_pdf(
                pdf_path,
                pages=str(pagina_index),
                flavor="stream",
                row_tol=7.5
            )
            frames = [tabela.df for tabela in tabelas]
            df = pd.concat(frames, ignore_index=True)
            df.columns = rename_duplicates(df.iloc[0])
            df = df[1:]
            df.reset_index(drop=True, inplace=True)
            return df
        else:
            raise e
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        return None
