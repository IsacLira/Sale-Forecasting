from functions import tratamento, encoding,model_selection
import pandas as pd
import importlib # to reload
from xgboost import XGBClassifier
#from sklearn. import train_test_split,KFold, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.ensemble import GradientBoostingClassifier, BaggingClassifier,RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
import pickle 
import json
from sklearn.externals import joblib
from sklearn.metrics import confusion_matrix
from tests import test_api
importlib.reload(tratamento)
importlib.reload(encoding)
importlib.reload(model_selection) 
importlib.reload(test_api)
import time

df_original = pd.read_excel('files/brutos.xlsx')
df_treino = df_original[~df_original.DataResultado.isnull()]
df_treino = tratamento.get_first_ons(df_treino)
df_treino = df_treino.drop(df_treino[(df_treino.Resultado ==  'on_ultima_parcela_contrato')].index )
df_treino.Resultado = df_treino.Resultado.str.rstrip()
df_treino = encoding.encoding_resultado(df_treino)

#df_treino = df_treino.drop('Resultado',axis=1)
df_treino.loc[:,'time_diff'] = (df_treino.Data_Previsao-df_treino.Data_Cadencia)
df_treino.loc[:,'time_diff'] = (df_treino['time_diff'].apply(lambda x: x.days/7))


df_treino.loc[:,'TrimestrePrevisao'] = df_treino['Data_Previsao'].apply(lambda x: tratamento.get_trimestre(x.month))
df_treino.loc[:,'TrimestreResultado'] = df_treino['DataResultado'].apply(lambda x: tratamento.get_trimestre(x.month))
df_treino.loc[:,'ResultadoPrevisao'] = (df_treino.loc[:,'TrimestreResultado'] == df_treino.loc[:,'TrimestrePrevisao'])*1
#df_treino.loc[:,'ResultadoPrevisao'] = (df_treino.TrimestrePrevisao!=df_treino.TrimestreResultado) & (df_treino.Data_Previsao<df_treino.DataResultado) 

df_treino.loc[:,'current_tr'] = (df_treino.TrimestrePrevisao == df_treino.Trimestre)*1



df_treino = tratamento.fill_na(df_treino)
df_treino = tratamento.get_ano_mes(df_treino)

#encoder = encoding.encode_gerente(df_treino,'numerical')
#df_treino.loc[:,'Gerente_Negocio'] = encoder.fit_transform(df_treino['Gerente_Negocio'])


df_treino = tratamento.fix_unidade_e_area(df_treino)
df_treino = tratamento.add_features(df_treino)
df_treino = tratamento.drop_unecessary(df_treino)
df_treino = tratamento.get_cidade_e_is_privado(df_treino)
df_treino = tratamento.get_objetivo_client(df_treino)
df_treino = encoding.encoding_foco(df_treino)


df_treino.loc[:,'Area_Unidade_Negocio2'] = df_treino['Area_Unidade_Negocio']
df_treino = encoding.get_dummies(df_treino)

df_treino1  = df_treino[df_treino.Resultado==1]

X_train, X_test, y_train, y_test =  model_selection.train_test_split(df_treino1,res='ResultadoPrevisao')
all_feats = [f for f in X_train.columns if f not in ['Id_ON','Id_Cadencia','Area_Unidade_Negocio2','ResultadoPrevisao','TrimestreResultado']]
clf = RandomForestClassifier(n_estimators=500,max_features=1,random_state=30)
selected_features = all_feats#model_selection.feature_selection(clf,X_train[all_feats],y_train,k=40)

model = GradientBoostingClassifier(max_features=0.7,random_state=10)
model.fit(X_train[selected_features], y_train)
model.fit(df_treino1[selected_features], df_treino1.ResultadoPrevisao)

df = X_test.copy()
predictions           = model.predict(df[selected_features])
df['PredsArea'] = predictions
df['Resultado'] = y_test

groups = df.groupby(['Id_ON','TrimestrePrevisao']).agg({'Resultado': 'max', 'PredsArea': 'max'}).reset_index()
groups.columns = ['Id_ON','TrimestrePrevisao','ResultadoReal','ResultadoPredito']
accuracy_score(groups.ResultadoReal,groups.ResultadoPredito)
confusion_matrix(groups.ResultadoReal,groups.ResultadoPredito)

train_predict = model.predict(X_train[selected_features])
test_predict = (model.predict_proba(X_test[selected_features])[:,1]>0.5)*1
accuracy_score(y_train,train_predict),accuracy_score(y_test,test_predict)
confusion_matrix(y_train,train_predict)
 
v = {a:b for a,b in zip(selected_features,model.feature_importances_)}
v = [(a,v[a]) for a in sorted(v,key=v.get,reverse=True)]

filename = 'previsao_model.pkl'
f = open(filename,'wb')
pickle_file = pickle.dump(model,f)
f.close()

with open('features2.json','w') as outfile:
    json.dump(selected_features,outfile)

