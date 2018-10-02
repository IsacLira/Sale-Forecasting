import pandas as pd
import numpy as np

from functions import tratamento, encoding,model_selection
import importlib # to reload
#from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

import pickle 
import json
import time

importlib.reload(tratamento)
importlib.reload(encoding)
importlib.reload(model_selection)

df_origin = pd.read_excel('files/NovosDadosCadencia.xlsx')
df_origin.loc[:,'Resultado'] = df_origin.Resultado.str.rstrip()
df_origin = encoding.encoding_resultado(df_origin)
df_origin = encoding.encoding_area_resultado(df_origin)

df_origin.loc[:,'time_diff'] = df_origin['Data_Cadencia']-df_origin['Data_Previsao']
df_origin.loc[:,'time_diff'] = (df_origin['time_diff'].apply(lambda x: x.days/7))

df_origin.loc[:,'TrimestrePrevisao'] = df_origin['Data_Previsao'].apply(lambda x: tratamento.get_trimestre(x.month))
df_origin.loc[:,'TrimestreResultado'] = df_origin['DataResultado'].apply(lambda x: tratamento.get_trimestre(x.month))
df_origin.loc[:,'ResultadoPrevisao'] = (df_origin.loc[:,'TrimestreResultado']==df_origin.loc[:,'TrimestrePrevisao'])*1
#df_origin.loc[:,'ResultadoPrevisao'] = (df_origin.TrimestrePrevisao!=df_origin.TrimestreResultado) & (df_origin.Data_Previsao<df_origin.DataResultado) 

df_origin.loc[:,'current_tr'] = (df_origin.TrimestrePrevisao == df_origin.Trimestre)*1

start = time.time()
print(start)
df_test = df_origin.drop('Resultado',axis=1)
df_test = tratamento.fill_na(df_test)
df_test = tratamento.add_features(df_test)

#encoder = pickle.load(open('encoder.pkl','rb'))
#df_test.loc[:,'Gerente_Negocio'] = encoder.transform(df_test['Gerente_Negocio'])
df_test = tratamento.get_ano_mes(df_test)
df_test = tratamento.fix_unidade_e_area(df_test)
df_test = tratamento.drop_unecessary(df_test)

df_test = tratamento.get_cidade_e_is_privado(df_test)
df_test = tratamento.get_objetivo_client(df_test)
df_test = encoding.encoding_foco(df_test)

df_test = encoding.get_dummies(df_test)

model1 = pickle.load(open('predictiv_model.pkl','rb'))
features = json.load( open('features.json','r'))
model2 = pickle.load(open('previsao_model.pkl','rb'))
features2 = json.load( open('features2.json','r'))


# predictions for model 1
df = pd.DataFrame(columns=features)
_,df_test2 = df.align(df_test,join='outer',fill_value=0,axis=1)
pred_model1           = model1.predict(df_test2[features])
df_test2['PredsArea'] = pred_model1
df_test2['Resultado'] = df_origin.Resultado
groups                = model_selection.predict_on(df_test2)

accuracy_score(groups.ResultadoReal,groups.ResultadoPredito)
confusion_matrix(groups.ResultadoReal,groups.ResultadoPredito)

# predictions for model 2
df_test2 = df_test.merge(groups,on='Id_ON',how='outer')
df = pd.DataFrame(columns=features2)
_,df_test2 = df.align(df_test2,join='outer',fill_value=0,axis=1)
df_test2['Resultado'] = df_test2.ResultadoPredito

predictions = model2.predict(df_test2[features2])
df_test2['PredsArea'] = predictions
df_test2['Resultado'] = df_test2.ResultadoPrevisao
groups = df_test2.groupby(['Id_ON','TrimestrePrevisao']).agg({'Resultado': 'max', 'PredsArea': 'max'}).reset_index()
groups.columns = ['Id_ON','TrimestreResultado','ResultadoReal','ResultadoPredito']


accuracy_score(groups.ResultadoReal,groups.ResultadoPredito)
confusion_matrix(groups.ResultadoReal,groups.ResultadoPredito)


accuracy_score(df_test2.ResultadoPrevisao,predictions)
confusion_matrix(df_test2.ResultadoPrevisao,predictions)
