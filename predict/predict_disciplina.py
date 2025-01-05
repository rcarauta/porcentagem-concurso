import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

def obter_porcentagens(disciplina):
    url = f'http://localhost:5000/topics/percentages?disciplina={disciplina}'
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Erro ao acessar o serviço Flask: {response.status_code}")
        return None
    
    return response.json()

def treinar_modelo(temas):
    X = np.array([[tema["questoes_count"]] for tema in temas])  
    y = np.array([[tema["percentage"]] for tema in temas]) 
    
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    return modelo

def prever_distribuicao(modelo, total_questoes, temas):
    distribuicao_prevista = modelo.predict(np.array([[tema["questoes_count"] * (total_questoes / 100)] for tema in temas]))
    
    distribucao_adjusted = {temas[i]["title"]: round(distribuicao_prevista[i][0]) for i in range(len(temas))}
    
    total_arredondado = sum(distribucao_adjusted.values())
    diferenca = total_questoes - total_arredondado
    
    # Ajuste para o número total de questões
    if diferenca > 0:
        max_tema = max(distribucao_adjusted, key=lambda x: distribucao_adjusted[x])
        distribucao_adjusted[max_tema] += diferenca
    elif diferenca < 0:
        min_tema = min(distribucao_adjusted, key=lambda x: distribucao_adjusted[x])
        distribucao_adjusted[min_tema] += diferenca

    return distribucao_adjusted

def redistribuir_questoes(temas, total_questoes, escolha):
    distribuicao = prever_distribuicao(treinar_modelo(temas), total_questoes, temas)
    
    if escolha == 'mais_provaveis':
        # Distribuir mais para os temas mais prováveis
        temas_ordenados = sorted(distribuicao.items(), key=lambda x: x[1], reverse=True)
        metade_mais_probavel = temas_ordenados[:len(temas)//2]
        restante = total_questoes - sum([qtd for _, qtd in metade_mais_probavel])
        
        # Redistribuir as questões para a metade mais provável
        for i in range(len(metade_mais_probavel)):
            tema, qtd = metade_mais_probavel[i]
            distribuicao[tema] += restante // len(metade_mais_probavel)
        
    elif escolha == 'menos_provaveis':
        # Redistribuir mais para os temas menos prováveis
        temas_ordenados = sorted(distribuicao.items(), key=lambda x: x[1])  # Ordem crescente
        metade_menos_probavel = temas_ordenados[:len(temas)//2]
        restante = total_questoes - sum([qtd for _, qtd in metade_menos_probavel])
        
        # Redistribuir as questões para a metade menos provável
        for i in range(len(metade_menos_probavel)):
            tema, qtd = metade_menos_probavel[i]
            distribuicao[tema] += restante // len(metade_menos_probavel)
    
    return distribuicao

@app.route('/distribuir_questoes', methods=['GET'])
def distribuir_questoes():
    disciplina = request.args.get('disciplina')
    total_questoes = int(request.args.get('total_questoes', 15))

    if not disciplina:
        return jsonify({"error": "Disciplina não informada"}), 400

    temas = obter_porcentagens(disciplina)
    
    if temas is None:
        return jsonify({"error": "Erro ao acessar os dados dos temas"}), 500
    
    # Distribuição para os mais prováveis
    distribuicao_mais_probaveis = redistribuir_questoes(temas, total_questoes, 'mais_provaveis')

    # Distribuição para os menos prováveis
    distribuicao_menos_probaveis = redistribuir_questoes(temas, total_questoes, 'menos_provaveis')

    # Montando a resposta em formato JSON
    resposta = {
        "mais_provaveis": distribuicao_mais_probaveis,
        "menos_provaveis": distribuicao_menos_probaveis
    }

    return jsonify(resposta)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
