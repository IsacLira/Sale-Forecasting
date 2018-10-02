'''Apenas encoda a função Foco para 1 ou 0.
'''
def encoding_foco(data):
    from sklearn import preprocessing
    one_hot = preprocessing.LabelEncoder()
    data.Foco = one_hot.fit_transform(data.Foco)
    return data


'''Encodar o resultado
Considerar como positivo: 'aceita' 'on_contrato_base' 'registropreco'
Considerar como negativo: 'cancelada', 'desistiu', 'nao_participamos',  'orcamento', 'recusada'
'''
def encoding_resultado(data):
    data.Resultado = data.Resultado.apply((lambda x: 1 if (x == "aceita" or x == 'on_contrato_base' or x == 'registropreco') else 0))
    return data


'''Codifica o Probabilidade_ON em dois Buckets, o primeiro, chamado de ON's avançadas possuem
a probabilidade de ON acima de 0.7, o segundo abaixo disso.
'''
def encoding_prob(data,eps=0.7):
    import numpy as np
    data['Andamento_ON'] = np.where(data['Probabilidade_ON'] >= eps, "Final", "Comeco")
    return data.drop(columns='Probabilidade_ON')
 
def save_df(data, filename="out.xlsx"):
    import pandas as pd
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    data.to_excel(writer)
    writer.save()

'''
Função que lista todas as áreas de negócio da ultima cadência de uma ON Aceita

input: dataframe com ONs aceitas (positive set)
output: dicionário com as áreas fechadas por ON
'''
def deals_closed(pos_set):
    # return a dict with Areas from the last candencia

    pos_set = pos_set.sort_values(['Id_ON', 'Data_Cadencia']) \
        .drop_duplicates(['Id_ON', 'Id_Cadencia', 'Area_Unidade_Negocio'], keep='first')

    dic = {}
    for on in pos_set.Id_ON.unique():
        data = pos_set.loc[(pos_set.Id_ON == on)]
        last_cadencia = data['Id_Cadencia'].max()
        dic[on] = data[data.Id_Cadencia == last_cadencia].Area_Unidade_Negocio.unique().tolist()
    return dic

'''
Função que retorna os labels/resultados das áreas de negócio de uma ON.
ResultadoArea:
1 -> área fechada
0 -> área recusada
input -> dataframe original
output -> dataframe original contendo o campo ResultadoArea
'''
def encoding_area_resultado(df):
    import pandas as pd

    pos_set = df[df.Resultado == 1]
    neg_set = df[df.Resultado == 0]

    dic = deals_closed(pos_set)
    pos_set['ResultadoArea'] = pos_set[['Id_ON', 'Area_Unidade_Negocio']]\
                                     .apply(lambda x: (x['Area_Unidade_Negocio'] in dic[x['Id_ON']]) * 1, axis=1)
    neg_set.loc[:, 'ResultadoArea'] = 0
    df = pd.concat([neg_set, pos_set], axis=0)
    return df

def get_dummies(df):
    import pandas as pd
    # Encode categorical variables

    catVars = [feature for feature in df.columns if df[feature].dtype=='O' and feature not in ['Id_ON','Id_Cadencia','Area_Unidade_Negocio2']]
    df = pd.get_dummies(data=df, columns=catVars)
    return df

'''
Função que aplica codificação bináriana variável Cliente
input: dataframe original
output: dataframe original contendo os códigos binários
code -> b1 b2 ... b11
'''
def encode_cliente(df_all):
    import pandas as pd
    import numpy as np
    base = 11
    unique_clients = df_all['CnpjCpf'].unique()
    idc = np.arange(1, len(unique_clients) + 1)

    bin_codes = []
    for code in idc:
        bin_codes.append([code] + list(bin(code)[2:].zfill(base)))

    df = pd.DataFrame(bin_codes, columns=['idc'] + ['b' + str(i) for i in range(1, 12)])
    dic_clients = {c: idc for c, idc in zip(unique_clients, idc)}
    df_all['idc'] = df_all['CnpjCpf'].map(dic_clients)
    df = df_all.merge(df, on='idc', how='left')
    return df

'''
codifica a variável gerente  
'''
def encode_gerente(df_all, encode_type='numerical'):
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder
    encoder = LabelEncoder()
    
    if encode_type == 'numerical':
        #df_all.loc[:, 'Gerente_Negocio'] = df_all.Gerente_Negocio.astype('category').cat.codes
        encoder.fit(df_all['Gerente_Negocio'])
        return encoder
    elif encode_type == 'one_hot':
        df_all = pd.get_dummies(df_all, columns=['Gerente_Negocio'])
    return df_all