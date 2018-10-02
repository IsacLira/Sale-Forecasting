
"""Retorna o dataframe contendo apenas as primeiras cadências de ONS únicas que tiveram resultado.
Como também exclui a presença de on_ultima_parcela_contrato visto que não é necessário.
"""
def get_first_ons(data):
    data = data.dropna(subset=['DataResultado'])
    data = data.sort_values(by=["Id_ON","Id_Cadencia"])
    data = data.drop_duplicates(["Id_ON","Data_Previsao",'Area_Unidade_Negocio','Id_Cadencia'], keep='first')
    #data = data.drop_duplicates(subset=['Id_ON'], keep='first')
    #data.Resultado = data.Resultado.str.rstrip()
    return data
    #return data.drop(data[ (data.Resultado ==  'on_ultima_parcela_contrato')].index )


"""Cria quatro novas colunas, contendo o mês e o ano da criação da cadência e o mês e o ano estimado
pelo gerente de contas. No final da geração, são dropadas as colunas Data_Previsão e Data_Cadencia.
"""
def get_ano_mes(data):
    import pandas as pd
    try:
        data['Cadencia_Ano'] = pd.DatetimeIndex(data['Data_Cadencia']).year
        data['Cadencia_Mes'] = pd.DatetimeIndex(data['Data_Cadencia']).month
    except:
        data['Cadencia_Ano'] = pd.to_datetime((data['Cadencia_Ano'] - 25569) * 86400.0, unit='s')
        data['Cadencia_Ano'] = pd.DatetimeIndex(data['Data_Cadencia']).year
        data['Cadencia_Mes'] = pd.DatetimeIndex(data['Data_Cadencia']).month

    try:
        data['Previsao_Ano'] = pd.DatetimeIndex(data['Data_Previsao']).year
        data['Previsao_Mes'] = pd.DatetimeIndex(data['Data_Previsao']).month
    except:
        data['Data_Previsao'] = pd.to_datetime((data['Data_Previsao'] - 25569) * 86400.0, unit='s')
        data['Previsao_Ano'] = pd.DatetimeIndex(data['Data_Previsao']).year
        data['Previsao_Mes'] = pd.DatetimeIndex(data['Data_Previsao']).month

    columns = ["Data_Previsao", "Data_Cadencia"]
    return data.drop(columns=columns)


"""Essa função cria duas novas colunas:
Unidade_do_Negocio => Primeira string de Unidade_Negocio
Area_Unidade_Negocio => Segunda string.
"""
def fix_unidade_e_area(data):
    data.Unidade_Negocio = data.Unidade_Negocio.str.replace(' ', '')
    data['Unidade_do_Negocio'] = data.Unidade_Negocio.str.split('-').str.get(0)
    data['Sub_Unidade_Negocio'] = data.Unidade_Negocio.str.split('-').str.get(1)
    return data.drop(columns='Unidade_Negocio')

"""Através do campo Unidade_Venda é criado duas novas colunas:
is_Privado -> 1 se for privado, 0 senão.
Cidade -> Contém a cidade.
"""
def get_cidade_e_is_privado(data):
    import numpy as np
    data['isPrivado'] = np.where(data['Unidade_Venda'].str.contains('Privado'), 1, 0)
    data['Cidade'] = data.Unidade_Venda.str.split('(').str.get(0)
    data.Cidade = data.Cidade.str.rstrip()
    return data.drop(columns='Unidade_Venda')

'''Remove as colunas não necessárias.
'''
def drop_unecessary(data):
    must_drop = [ 'DataResultado', 'Contato', 'Total_Venda_Final', 'Total_venda','Id_Unidade_Negocio','Id_ON_Base','Gerente_Negocio',
            'Ultimo_Historico','Usuario_Acao','Data_Limite_Entrega_Proposta','Data_Validade_Mapeamento', 'Estrategias_Cadencia','Controle_Alteracao',
            'Proxima_Acao','Descricao_Cadencia','Descricao_ON','CnpjCpf','Cargo', 'Soma_Rentabilidade','IdGerente']#Probabilidade_ON, Id_ON,,'' Codigo_Mapeamento Id_Cadencia Risco_Oportunidade Gerente, cliente
            # Maybe 'Descricao_ON','Objetivos_Cliente' 'Gerente_Negocio','CnpjCpf','Cargo'
    data = data.drop(columns=must_drop)
    return data


'''

'''
def get_objetivo_client(data):
    import numpy as np
    data.Objetivos_Cliente = data.Objetivos_Cliente.str.lower()
    data['Objetivo_Produtividade'] = np.where(data['Objetivos_Cliente'].str.contains('produt'), 1, 0)
    data['Objetivo_Renovacao'] = np.where(data['Objetivos_Cliente'].str.contains('renov'), 1, 0)
    data['Objetivo_Licenciamento'] = np.where(data['Objetivos_Cliente'].str.contains('licen'), 1, 0)
    data['Objetivo_Reduzir_Custos'] = np.where(data['Objetivos_Cliente'].str.contains('reduz'), 1, 0)

    data['Objetivo_win'] = np.where(data['Objetivos_Cliente'].str.contains('windows'), 1, 0)
    data['Objetivo_Office'] = np.where(data['Objetivos_Cliente'].str.contains('office'), 1, 0)
    data['Objetivo_Servidores'] = np.where(data['Objetivos_Cliente'].str.contains('servidores'), 1, 0)
    data['Objetivo_Suporte'] = np.where(data['Objetivos_Cliente'].str.contains('suporte'), 1, 0)
    data['Objetivo_Nuvem'] = np.where(data['Objetivos_Cliente'].str.contains('nuvem'), 1, 0)
    data['Objetivo_Seguranca'] = np.where(data['Objetivos_Cliente'].str.contains('segurança'), 1, 0)

    return data.drop(columns='Objetivos_Cliente')


def fix_client(data):
    import numpy as np
    data.Cliente = data.Cliente.str.lower()
    data.loc[:,'cliente_ltda'] = 1*data['Cliente'].str.contains('ltda')
    data.loc[:,'cliente_estadual']  = 1*data['Cliente'].str.contains('estado')
    data.loc[:,'cliente_comercio'] = np.where(data['Cliente'].str.contains('comercio'), 1, 0)
    data.loc[:,'cliente_sa'] = (data['Cliente'].str.contains('s/a') | data['Cliente'].str.contains('s.a.'))*1
    data.loc[:,'cliente_secretaria'] = np.where(data['Cliente'].str.contains('secretaria'), 1, 0)
    data.loc[:,'cliente_tribunal'] = np.where(data['Cliente'].str.contains('tribunal'), 1, 0)
    data.loc[:,'cliente_federal'] = np.where(data['Cliente'].str.contains('federal'), 1, 0)

    return data.drop('Cliente',axis=1)

    


'''
Função que faz a imputação de valores nulos.
Area_Unidade_Negocio -> inputa com None

Gera novas variáveis a partir de Nulls:
HasMap -> Nulos de Codigo_Mapeamento indicam que não há mapeamento
Risco_Oportunidade -> Seus nulos indicam o status in_progress
IsAMain -> Nulos de Id_ON_Base indicam que não há referências a ON_Base
'''   
def fill_na(df_all):
    print("Imputing null values...")
    # fill na values for Area_Unidade_Negocio
    df_all['Area_Unidade_Negocio'].fillna('Null', inplace=True)
    #df_all['Unidade_Negocio'].fillna('Null', inplace=True)

    # Add a feature to verify if an ON there is a MAP
    df_all['HasMap'] = df_all['Codigo_Mapeamento'].isnull() * 1

    # Adding IN_Process status to Risk feature
    df_all['Risco_Oportunidade'].fillna('in_progress', inplace=True)

    # Adding ONBase-Dependence feature
    #df_all['IsAMain'] = df_all['Id_ON_Base'].isnull() * 1
    return df_all.drop('Codigo_Mapeamento',axis=1)

'''
Adiciona outras features ao dataframe
IsShared:[0,1] se a ON é compartilhada por mais de um gerente de contas
Year e mounth -> data da cadência
'''
def add_features(df_all):

    # Verify if an ON is shared by sellers
    groups = df_all.groupby(['Id_ON']).Gerente_Negocio.nunique()
    df_all['IsShared'] = df_all['Id_ON'].apply(lambda x: (groups[x] > 1) * 1)
    #print('IsShaped added..')

    # Add month and year features
    #df_all['year'] = df_all.Data_Cadencia.apply(lambda x: x.year)
    #df_all['month'] = df_all.Data_Cadencia.apply(lambda x: x.month)
    #print('Year and mounth added..')
    return df_all
'''
 Alinhas as dummies variables criadas no treino
 Adiona as faltam e preenche com nulo 

 df_ref: df de test ou val
 df_target: df de treinamento
 
'''
def align_dummies(df_ref, df_target):
    _, df_new = df_ref.align(other=df_target, join='left', fill_value=0, axis=1)
    return df_new
# TODO Adicionar descrição  

def get_trimestre(month):
    if month < 4:
        return 1
    elif month < 7:
        return 2
    elif month < 10:
        return 3
    elif month < 13:                
        return 4

    
