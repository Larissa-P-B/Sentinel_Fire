#Nome: Larissa Pereira Biusse
#RM: 564068

import os

from flask import Flask, jsonify, request, send_from_directory, send_file
from Sentinel_Fire import SistemaEmergencia
import threading
import time
from sistema_alerta import ContatoEmergencia
from  modelos import Ocorrencia


app = Flask(__name__)
sistema = SistemaEmergencia()


@app.route('/')
def home():
    return (f"Sentinel Fire\n"
            + "Sistema de Gerenciamento de Queimadas")


@app.route('/ocorrencias', methods=['GET'])
def listar_ocorrencias():
    ocorrencias = [{
        "id": oc.id,
        "local": oc.local,
        "severidade": oc.severidade,
        "regiao": oc.regiao,
        "status": oc.status,
        "fogo_confirmado": oc.fogo_confirmado,
        "fogo_apagado": oc.fogo_apagado,
        "tempo_ativo": f"{(time.time() - oc.tempo_inicio_fogo):.1f}s" if oc.tempo_inicio_fogo > 0 else "Não ativo"
    } for oc in sistema.fila_prioritaria]
    return jsonify({"ocorrencias": ocorrencias})


@app.route('/historico', methods=['GET'])
def historico():
    return jsonify({"historico": sistema.historico.to_list()})



@app.route('/historico_drones', methods=['GET'])
def historico_drones():
    try:
        historico = sistema.drone_tracker.obter_historico()
        return jsonify({
            "historico": historico,
            "total_acoes": len(historico)
        })
    except Exception as e:
        return jsonify({
            "historico": [],
            "total_acoes": 0,
            "error": str(e)
        }), 500

@app.route('/simular', methods=['POST'])
def simular():
    quantidade = request.json.get('quantidade', 1)
    sistema.simular_ocorrencias(quantidade)
    return jsonify({"status": "success", "msg": "Nova ocorrência simulada"})



@app.route('/atender', methods=['POST'])
def atender():
    try:
        resultado = sistema.atender_ocorrencia()
        if resultado:
            return jsonify({
                "status": "success",
                "resultado": resultado
            })
        return jsonify({
            "status": "error",
            "message": "Nenhuma ocorrência para atender"
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/contatos', methods=['GET'])
def listar_contatos():
    contatos = []
    current = sistema.sistema_alerta.contatos.head
    while current:
        contato = current.data
        contatos.append({
            'nome': contato.nome,
            'email': contato.email,
            'telefone': contato.telefone,
            'tipo': contato.tipo,
            'regioes': contato.regioes
        })
        current = current.next
    return jsonify({"contatos": contatos})


@app.route('/contatos/adicionar', methods=['POST'])
def adicionar_contato():
    data = request.json
    try:
        novo_contato = ContatoEmergencia(
            nome=data['nome'],
            email=data['email'],
            telefone=data['telefone'],
            tipo=data['tipo'],
            regioes=data['regioes']
        )
        sistema.sistema_alerta.adicionar_contato(novo_contato)
        return jsonify({"status": "success"})
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Campo faltando: {str(e)}"}), 400


@app.route('/testar_sms', methods=['POST'])
def testar_sms():
    data = request.json
    try:
        ocorrencia_teste = Ocorrencia(
            prioridade=0,
            local=data.get('local', 'Área de Teste'),
            severidade=4,
            regiao=data.get('regiao', 'Amazônia')
        )
        sistema.sistema_alerta.enviar_alertas(ocorrencia_teste, 'alerta')
        return jsonify({"status": "success", "message": "SMS de teste enviado para contatos da região"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/mapa')
def mostrar_mapa():
    try:
        # Verifica se o diretório templates existe
        os.makedirs('templates', exist_ok=True)

        # Gera o mapa com as ocorrências atuais
        sistema.monitoramento.limpar_marcadores()

        for ocorrencia in sistema.fila_prioritaria:
            if hasattr(ocorrencia, 'local') and isinstance(ocorrencia.local, (list, tuple)):
                if ocorrencia.status == "Fogo ativo":
                    sistema.monitoramento.adicionar_marcador(
                        ocorrencia.local[0], ocorrencia.local[1],
                        cor='red',
                        popup=f"Fogo ativo - {ocorrencia.regiao} (Severidade: {ocorrencia.severidade})"
                    )
                elif ocorrencia.status == "Fogo apagado":
                    sistema.monitoramento.adicionar_marcador(
                        ocorrencia.local[0], ocorrencia.local[1],
                        cor='green',
                        popup=f"Fogo apagado - {ocorrencia.regiao}"
                    )

        arquivo = sistema.monitoramento.salvar_mapa()
        return send_file(arquivo)

    except Exception as e:
        print(f"ERRO DETALHADO: {str(e)}")
        return jsonify({"error": str(e)}), 500
def simular_ocorrencias_periodicamente():
    while True:
        time.sleep(5)
        sistema.simular_ocorrencias(1)
        print(f"[{time.strftime('%H:%M:%S')}] Nova ocorrência simulada")


if __name__ == '__main__':
    print("Iniciando serviços...")
    sistema.iniciar_servicos()
    threading.Thread(target=simular_ocorrencias_periodicamente, daemon=True).start()

    print("API disponível em http://localhost:5000/")
    print("Mapa disponível em http://localhost:5000/mapa")
    app.run(host='0.0.0.0', port=5000, debug=True)