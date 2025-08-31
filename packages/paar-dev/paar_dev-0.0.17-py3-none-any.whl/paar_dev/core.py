import pandas as pd
import mysql.connector
import decimal
import gspread
from google.oauth2 import service_account
from typing import Optional
from st_aggrid import AgGrid, GridOptionsBuilder
from google.cloud import secretmanager, bigquery
from pandas.api.types import is_period_dtype
import re
import json

# Função para gerar DataFrame a partir de uma view do Phoenix

def gerar_df_phoenix(
        db_phoenix: str, # Nome do banco de dados Phoenix
        request_select: str, # Comando SQL para seleção
        user_phoenix: str, # Nome de usuário do banco de dados
        password_phoenix: str, # Senha do banco de dados
        host_phoenix: str # Host do banco de dados
    ) -> pd.DataFrame:
    
    config = {
        'user': user_phoenix, 
        'password': password_phoenix, 
        'host': host_phoenix, 
        'database': db_phoenix
    }

    conexao = mysql.connector.connect(**config)

    cursor = conexao.cursor()

    request_name = request_select

    cursor.execute(request_name)

    resultado = cursor.fetchall()
    
    cabecalho = [desc[0] for desc in cursor.description]

    cursor.close()

    conexao.close()

    df = pd.DataFrame(
        resultado, 
        columns=cabecalho
    )

    df = df.applymap(
        lambda x: float(x) 
        if isinstance(x, decimal.Decimal) 
        else (
            x.decode() 
            if isinstance(x, (bytes, bytearray)) 
            else x
        )
    )

    return df

# Função para abrir uma planilha do Google Sheets

def abrir_planilha(
        id_gsheet: str, # ID da planilha do Google Sheets
        credenciais: dict # Credenciais do Google Sheets
    ) -> gspread.Spreadsheet:

    credentials = service_account.Credentials.from_service_account_info(credenciais)

    scope = ['https://www.googleapis.com/auth/spreadsheets']

    credentials = credentials.with_scopes(scope)

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(id_gsheet)

    return spreadsheet

# Função para tratar colunas de um DataFrame

def tratar_colunas_df(
        df: pd.DataFrame, # DataFrame a ser tratado
        lista_colunas_numero: Optional[list] = None, # Lista de colunas numéricas
        nome_coluna_ref_ano_mes: Optional[str] = None, # Nome da coluna de referência para ano e mês
        lista_colunas_vazia_ou_none: Optional[list] = None, # Lista de colunas string p/ tratamento de ''
        lista_colunas_data: Optional[list] = None, # Lista de colunas de data
        formato_colunas_data: Optional[str] = None, # Formato das colunas de data
        lista_colunas_hora: Optional[list] = None, # Lista de colunas de hora
        formato_colunas_hora: Optional[str] = None, # Formato das colunas de hora
        lista_colunas_data_hora: Optional[list] = None, # Lista de colunas de data e hora
        formato_colunas_data_hora: Optional[str] = None # Formato das colunas de data e hora
    ) -> pd.DataFrame:

    # Função para adicionar colunas de ano, mês e mês/ano

    def adicionar_colunas_ano_mes(
            df: pd.DataFrame, # DataFrame a ser tratado
            coluna_data: Optional[str] = None # Nome da coluna de referência para ano e mês
        ) -> pd.DataFrame:

        if coluna_data is None:

            df['Mes_Ano'] = pd.to_datetime(
                df['Ano'].astype(int).astype(str) 
                + '-' 
                + df['Mes'].astype(int).astype(str) + '-01'
            ).dt.to_period('M')

        elif coluna_data != 'Nenhuma':

            df['Ano'] = pd.to_datetime(df[coluna_data]).dt.year

            df['Mes'] = pd.to_datetime(df[coluna_data]).dt.month

            df['Mes_Ano'] = pd.to_datetime(
                df['Ano'].astype(int).astype(str) 
                + '-' 
                + df['Mes'].astype(int).astype(str) + '-01'
            ).dt.to_period('M')

        return df

    if lista_colunas_vazia_ou_none:
        
        for coluna in lista_colunas_vazia_ou_none:

            df[coluna] = df[coluna].replace('', None)

    if lista_colunas_numero:

        if lista_colunas_numero=='Todas':

            lista_colunas_numero = df.columns.tolist()
        
        for coluna in lista_colunas_numero:

            df[coluna] = (
                df[coluna]
                .astype(str)
                .str.replace(',', '.', regex=False)
            )

            df[coluna] = pd.to_numeric(
                df[coluna], 
                errors='coerce'
            )

    if lista_colunas_data:

        for coluna in lista_colunas_data:

            df[coluna] = pd.to_datetime(
                df[coluna], 
                format=formato_colunas_data, 
                errors='coerce'
            ).dt.date

    if lista_colunas_data_hora:

        for coluna in lista_colunas_data_hora:

            df[coluna] = pd.to_datetime(
                df[coluna], 
                format=formato_colunas_data_hora, 
                errors='coerce'
            )

    if lista_colunas_hora:

        for coluna in lista_colunas_hora:

            df[coluna] = pd.to_datetime(
                df[coluna], 
                format=formato_colunas_hora, 
                errors='coerce'
            ).dt.time

    df = adicionar_colunas_ano_mes(
        df=df,
        coluna_data=nome_coluna_ref_ano_mes
    )

    return df

# Função para converter a aba do Google Sheets em um DataFrame

def gsheet_to_df(
        spread_sheet: gspread.Spreadsheet, # Planilha do Google
        nome_aba: str, # Nome da aba a ser convertida
        lista_colunas_numero: Optional[list] = None, # Lista de colunas numéricas
        nome_coluna_ref_ano_mes: Optional[str] = None, # Nome da coluna de referência para ano e mês
        lista_colunas_vazia_ou_none: Optional[list] = None, # Lista de colunas string p/ tratamento de ''
        lista_colunas_data: Optional[list] = None, # Lista de colunas de data
        formato_colunas_data: Optional[str] = None, # Formato das colunas de data
        lista_colunas_hora: Optional[list] = None, # Lista de colunas de hora
        formato_colunas_hora: Optional[str] = None, # Formato das colunas de hora
        lista_colunas_data_hora: Optional[list] = None, # Lista de colunas de data e hora
        formato_colunas_data_hora: Optional[str] = None # Formato das colunas de data e hora
    ) -> pd.DataFrame:

    sheet = spread_sheet.worksheet(nome_aba)

    sheet_data = sheet.get_all_values()

    df = pd.DataFrame(
        sheet_data[1:], 
        columns=sheet_data[0]
    )

    df = tratar_colunas_df(
        df=df,
        lista_colunas_numero=lista_colunas_numero,
        nome_coluna_ref_ano_mes=nome_coluna_ref_ano_mes,
        lista_colunas_vazia_ou_none=lista_colunas_vazia_ou_none,
        lista_colunas_data=lista_colunas_data,
        formato_colunas_data=formato_colunas_data,
        lista_colunas_hora=lista_colunas_hora,
        formato_colunas_hora=formato_colunas_hora,
        lista_colunas_data_hora=lista_colunas_data_hora,
        formato_colunas_data_hora=formato_colunas_data_hora
    )

    return df

# Função para plotar tabela interativa e colher a seleção do usuário

def plotar_tabela_aggrid_colher_selecao(
        df: pd.DataFrame,
        df_plotagem: pd.DataFrame,
        config_selection: str,
        use_checkbox: bool,
        header_checkbox: bool,
        autoHeight: bool,
        autoWidth: bool,
        height: Optional[int] = None,
    ) -> list:

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_selection(
        config_selection, 
        use_checkbox=use_checkbox, 
        header_checkbox=header_checkbox
    )

    if autoHeight:

        gb.configure_grid_options(domLayout='autoHeight')

    if autoWidth:

        gb.configure_grid_options(domLayout='autoWidth')

    gridOptions = gb.build()

    if autoHeight==False and height:

        grid_response = AgGrid(
            df_plotagem, 
            gridOptions=gridOptions, 
            enable_enterprise_modules=False, 
            fit_columns_on_grid_load=True,
            height=height
        )

    else:

        grid_response = AgGrid(
            df_plotagem, 
            gridOptions=gridOptions, 
            enable_enterprise_modules=False, 
            fit_columns_on_grid_load=True
        )

    selected_rows = grid_response['selected_rows']

    return selected_rows

# Função para inserir um dataframe em uma planilha do Google Sheets, 
# podendo substituir os dados ou inserir na última linha

def tratar_colunas_df_para_insercao_gsheet(
        df_insercao: pd.DataFrame, # DataFrame a ser inserido
        lista_colunas_data: Optional[list] = None, # Lista de colunas de data
        lista_colunas_data_hora: Optional[list] = None, # Lista de colunas de data e hora
        lista_colunas_hora: Optional[list] = None, # Lista de colunas de hora
        lista_colunas_str: Optional[list] = None, # Lista de colunas string
        lista_colunas_int: Optional[list] = None, # Lista de colunas inteiras
        lista_colunas_float: Optional[list] = None # Lista de colunas float
    ) -> pd.DataFrame:

    if lista_colunas_data:

        for coluna in lista_colunas_data:

            if coluna in df_insercao.columns:

                df_insercao[coluna] = pd.to_datetime(
                    df_insercao[coluna],
                    errors='coerce'
                ).dt.strftime('%Y-%m-%d').fillna('')

    if lista_colunas_data_hora:

        for coluna in lista_colunas_data_hora:

            if coluna in df_insercao.columns:

                df_insercao[coluna] = pd.to_datetime(
                    df_insercao[coluna],
                    errors='coerce'
                ).dt.strftime('%Y-%m-%d %H:%M:%S').fillna('')

    if lista_colunas_hora:

        for coluna in lista_colunas_hora:

            if coluna in df_insercao.columns:

                df_insercao[coluna] = pd.to_datetime(
                    df_insercao[coluna],
                    errors='coerce'
                ).dt.strftime('%H:%M:%S').fillna('')

    if lista_colunas_str:

        for coluna in lista_colunas_str:

            if coluna in df_insercao.columns:

                df_insercao[coluna] = df_insercao[coluna].fillna('').astype(str)

    if lista_colunas_int:

        for coluna in lista_colunas_int:

            if coluna in df_insercao.columns:

                df_insercao[coluna] = df_insercao[coluna].fillna(0).astype(int).astype(str)

    if lista_colunas_float:

        for coluna in lista_colunas_float:

            if coluna in df_insercao.columns:

                df_insercao[coluna] = df_insercao[coluna].fillna(0).astype(float).round(2).astype(str)

                df_insercao[coluna] = df_insercao[coluna].apply(lambda x: x.replace('.', ','))

    return df_insercao

# Função para inserir dataframe em um bigquery

def salvar_dados_bigquery(
        df_dados_atualizados: pd.DataFrame, 
        tabela_destino: str,
        project_id: str,
        secret_id: str
    ) -> bigquery.LoadJob:

    df_dados_atualizados.replace('', pd.NA, inplace=True)

    print("Autenticando no Secret Manager...")

    secret_client = secretmanager.SecretManagerServiceClient()

    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    response = secret_client.access_secret_version(request={"name": secret_name})

    secret_payload = response.payload.data.decode("UTF-8")
    
    credentials_info = json.loads(secret_payload)

    autenticar = service_account.Credentials.from_service_account_info(credentials_info)
    
    bq_client = bigquery.Client(credentials=autenticar, project=autenticar.project_id)

    for col in df_dados_atualizados.columns:
        if is_period_dtype(df_dados_atualizados[col]):
            print(f"Convertendo coluna '{col}' de Period[M] para string.")
            df_dados_atualizados[col] = df_dados_atualizados[col].astype(str)

    df_dados_atualizados.columns = (
        df_dados_atualizados.columns
        .str.strip()
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
        .map(lambda x: re.sub('[^0-9a-zA-Z_]', '_', x))
        .map(lambda x: re.sub('_+', '_', x))
    )

    print("Enviando dados para o BigQuery...")

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    job = bq_client.load_table_from_dataframe(df_dados_atualizados, tabela_destino, job_config=job_config)

    print("Dados enviados com sucesso!")

    job.result()

    return job