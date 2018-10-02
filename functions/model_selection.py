import pandas as pd

'''
Função que divide os dados em treino e teste
df -> 
'''
def train_test_split(df, threshold=2017,res='ResultadoArea'):
    # Split data in train and test
    train_ons = set(df[df.Cadencia_Ano <= threshold].Id_ON)
    train_X = df[df.Id_ON.isin(train_ons)]
    test_X = df[~df.Id_ON.isin(train_ons)]

    #train_X = train_X.sort_values(['Id_ON','Id_Cadencia']) \
     #              .drop_duplicates(subset=['Id_ON', 'Area_Unidade_Negocio2'], keep='first')
    test_X = test_X.sort_values(['Id_ON','Id_Cadencia']) \
                   .drop_duplicates(subset=['Id_ON', 'Area_Unidade_Negocio2'], keep='first')

    train_y, test_y = train_X[res], test_X[res]
    train_X = train_X.drop(res,axis=1)
    test_X = test_X.drop(res,axis=1)

    return train_X, test_X, train_y, test_y

'''
Função que faz a seleção das features mais importantes.
input -> clf: modelo que retorne feature_importance
         train_x: dataframe de treino
         train_y: labels/classes
         k: número de features a serem selecionadas

output-> selected_features: lista com as k features mais importantes  
'''
def feature_selection(clf, train_x, train_y, k=31):
    useless_features = ['Cliente', 'Set', 'Gerente_Negocio', 'Data_Cadencia', 'Id_ON', 'Id_Cadencia', 'CnpjCpf',
                        'Cargo', 'IdGerente', 'Resultado', 'ResultadoArea', 'Total_Venda_Final', 'Age']
    kfeatures = [f for f in train_x.columns if
                 f not in useless_features and f.find('Cliente') < 0 and f.find('Gerente') < 0]

    clf.fit(train_x[kfeatures], train_y)
    importances = {f: i for f, i in zip(kfeatures, clf.feature_importances_)}
    selected_features = sorted(importances, key=importances.get, reverse=True)[:k]

    return selected_features

'''
Esta função faz predições dos resultados das ONs baseado nas predições das áreas de negócio
input:
model  -> modelo já treinado
df     -> dataframe das ons

output:
groups -> dataframe do tipo [Id_ON,ResultadoReal,ResultadoPredito]
'''
def predict_on(df):    
    group = df.groupby(['Id_ON']).agg({'Resultado': 'max', 'PredsArea': 'max'}).reset_index()
    group.columns = ['Id_ON','ResultadoReal','ResultadoPredito']
    return group

