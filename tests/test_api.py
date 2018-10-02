import urllib.request
import json
import time
import pandas as pd

def request(d):
    dic =  {                'key': '1',
                            'Unidade_Venda': "Salvador",   
                            'Trimestre': "3",   
                            'Data_Cadencia': "24/08/2018",   
                            'Categoria_ON': "Serviço Recorrente",   
                            'Foco': 'SIM',    
                            'Objetivos_Cliente': "CONTRATAÇÃO DE CENTRAL DE SERVIÇO CONTINUADO.",   
                            'Data_Previsao': "2018-09-30 00:00:00",   
                            'Probabilidade_ON': "0",   
                            'Tipo_ON': "Pré-Edital",   
                            "Codigo_Mapeamento": "nan",   
                            'Area_Unidade_Negocio': "Serviço Lanlink",     
                            'Unidade_Negocio': "SERVIÇOS - Pós-Venda",   
                            'Total_Venda_Original': "600000.0",                             
                            'Risco_Oportunidade': "1",                               
                    }
    v = [dic for _ in range(10)]                    
    data = {
            "Inputs": {
                "input": d
            },
    "GlobalParameters":  {}
    }

    body = str.encode(json.dumps(data))

    url = 'https://ussouthcentral.services.azureml.net/workspaces/9a237f2890a648908296062f974dffbd/services/4e0857c14da148c3a92da0df3e9c75be/execute?api-version=2.0&format=swagger'
    api_key = 'lpTcSKZBrIkkjQM7wbma5MCRhMW3F4nSnt00vNK81tpKdjak2wTdyK6xkbXSY7vqEZ+iGbwWrEZPvpTz2BBtDg==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        encoding = response.info().get_content_charset('utf-8')
        JSON_object = json.loads(result.decode(encoding))

        return JSON_object
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))