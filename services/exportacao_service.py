


import pandas as pd
import io


def converter_para_excel(df):
        output = io.BytesIO()
        df_excel = df.copy()
        if 'id' in df_excel.columns:
            df_excel = df_excel.drop(columns=['id'])
        if 'Data' in df_excel.columns:
            df_excel['Data'] = df_excel['Data'].dt.strftime('%d/%m/%Y')
        if 'Baixa_Senior' in df_excel.columns:
            df_excel['Baixa_Senior'] = df_excel['Baixa_Senior'].apply(lambda x: 'Sim' if x else 'Não')
            
        # Reordena o Excel também para iniciar com Baixa_Senior
        colunas_restantes = [col for col in df_excel.columns if col != 'Baixa_Senior']
        df_excel = df_excel[['Baixa_Senior'] + colunas_restantes]
            
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_excel.to_excel(writer, index=False, sheet_name='Saidas')
        return output.getvalue()