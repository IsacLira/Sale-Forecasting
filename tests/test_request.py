import pandas as pd
import numpy as np

from functions import tratamento, encoding,model_selection
from tests import test_api

df_original = pd.read_excel('files/DadosCadencia_2018-08-20.xlsx')
#df_original = df_original.sort_values('Id_Cadencia').drop_duplicates('Id_ON',keep='first')
df_original.Resultado = df_original.Resultado.str.rstrip()
df_original = encoding.encoding_resultado(df_original)
df_original = encoding.encoding_area_resultado(df_original)
df_original = df_original.drop('Resultado',axis=1)

df_original.loc[:,'key'] = np.arange(df_original.shape[0])

cols = ['key','Unidade_Venda','Trimestre','Data_Cadencia','Categoria_ON','Foco','Objetivos_Cliente',
'Data_Previsao','Probabilidade_ON','Tipo_ON','Codigo_Mapeamento','Area_Unidade_Negocio',
'Unidade_Negocio','Total_Venda_Original','Risco_Oportunidade']

for col in cols:
    df_original[col] = df_original[col].apply(str)
df = df_original[cols]

lis = []
for i in range(0,df.shape[0]):
    row = df.iloc[i]
    dic = row[cols].to_dict()
    lis.append(dic)

response = test_api.request(lis)
df_result = pd.DataFrame.from_dict(response['Results']['output'])
df_result.key = df_result.key.astype(int)
df_original.key = df_original.key.astype(int)

df_result.Resultado = df_result.Resultado.astype(int)
df_original.ResultadoArea = df_original.ResultadoArea.astype(int)

r = df_result.merge(df_original[['ResultadoArea','key']],on='key',how='left')
np.mean(r.Resultado == r.ResultadoArea)
