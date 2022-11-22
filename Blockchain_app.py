import Blockchain
from uuid import uuid4

import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser

from multiprocessing import Semaphore
from threading import Thread

import pandas as pd
import time
import json

import platform as pl  #  obtemer informacion del nodo

import requests

# Instancia del nodo
app = Flask(__name__)

# Instanciacion de la aplicacion
blockchain = Blockchain.Blockchain()
blockchain.primer_bloque()
nodos_red = set()

# Para saber mi ip
mi_ip = socket.gethostbyname(socket.gethostname())

# Semáforo para la copia de seguridad
semaforo_copia_seguridad = Semaphore(1)


@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    values = request.get_json()
    # Comprobamos que todos los datos de la transaccion estan
    required = ['origen', 'destino', 'cantidad']
    if not all(k in values for k in required):
        return 'Faltan valores', 400
    # Creamos una nueva transaccion aqui
    blockchain.nueva_transaccion(
        values['origen'], values['destino'], values['cantidad'])
    index = len(blockchain.cadena_bloques) + 1

    response = {
        'mensaje': f'La transaccion se incluira en el bloque con indice {index}'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def blockchain_completa():
    response = {
        # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
        'chain': [b.toDict() for b in blockchain.cadena_bloques if b.hash is not None],
        'longitud': len(blockchain.cadena_bloques)  # longitud de la cadena
    }
    return jsonify(response), 200


@app.route('/minar', methods=['GET'])
def minar():
    # No hay transacciones
    if len(blockchain.transacciones_no_confirmadas) == 0:
        response = {
            'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"
        }
    else:
        # Hay transaccion, por lo tanto ademas de minear el bloque, recibimos recompensa
        previous_hash = blockchain.last_block().hash
        # Recibimos un pago por minar el bloque. Creamos una nueva transaccion con:
        # Dejamos como origen el 0
        # Destino nuestra ip
        # Cantidad = 1
        # [Completar el siguiente codigo]

        # generamos una nueva transaccion
        blockchain.nueva_transaccion("0", mi_ip, 1)

        nuevo_bloque = blockchain.nuevo_bloque(previous_hash)
        hash_prueba = blockchain.prueba_trabajo(nuevo_bloque)

        correct = blockchain.integra_bloque(nuevo_bloque, hash_prueba)

        # SIEMPRE ES CORRECTO, PERO POR SI ACASO LO DEJAMOS
        if correct:
            response = {'hash_bloque': nuevo_bloque.hash, 'hash_previo': previous_hash, 'indice': nuevo_bloque.indice, 'mensaje': 'Nuevo blooque minado',
                        'prueba': nuevo_bloque.prueba, 'timestamp': nuevo_bloque.timestamp, 'transacciones': nuevo_bloque.transacciones}
            codigo = 200
        else:

            response = {
                'mensaje': "No ha sido posible integrar el bloque a la Blockchain"}
            codigo = 400

        return jsonify(response), codigo


def hilo_copia_seguridad():
    while True:
        t1 = time.time()

        # POSIBLE MEJORA: SEÑAL EN EL MAIN CADA 60 SEGUNDOS AL HILO

        semaforo_copia_seguridad.acquire()
        # entro en la zona critica, ninguna peticion puede realizarse a la vez
        # de esta forma nos quedamos con una foto de la blockchain
        response = {
            # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
            'chain': [b.toDict() for b in blockchain.cadena_bloques if b.hash is not None],
            # longitud de la cadena
            'longitud': len(blockchain.cadena_bloques),
            'date': pd.to_datetime('today', unit='s')
        }

        with open(f"respaldo-nodo{mi_ip}-{puerto}.json", "w") as f:
            f.write(json.dumps(response))
        semaforo_copia_seguridad.release()

        # esperamos a que pasen 60 segundos para realizar la siguiente copua de seguridad
        t2 = time.time()
        while t2 - t1 < 60:
            t2 = time.time()

        # PREGUNTAR A PABLO: ¿Paramos al resto de hios obligaotriamente en el segundos
        # 60 o esperamos a que termine el que este editando


@app.route('/system', methods=['GET'])
def detalles_nodo_actual():
    response = {
        'maquina': pl.machine(),
        'nombre_sistema': pl.system(),
        'version': pl.version(),
    }
    return jsonify(response), 200


@app.route('/nodos/registrar', methods=['POST'])
def registrar_nodos_completo():
    values = request.get_json()
    global blockchain
    global nodos_red
    nodos_nuevos = values.get('direccion_nodos')
    if nodos_nuevos is None:
        return "Error: No se ha proporcionado una lista de nodos", 400
    all_correct = True  # [Codigo a desarrollar]
    for nodo in nodos_nuevos:
        # añadimos el nodo a la red
        nodos_red.add(nodo)
    #  obtenemos una copia de la blockchain
    blockhchain_copy = [b.toDict() for b in blockchain.cadena_bloques if b.hash is not None]
    blockhchain_copy.pop(0)
    # añadimos el nodo del que pendenpara pasarselo a todos los nodos
    nodos_red.add(f"http://{mi_ip}:{puerto}")
    for nodo in nodos_red:
        #  le pasamos todos los nodos menos el nodo en cuestion
        # nodos_red.remove(nodo)
        data = {
            'nodos_direcciones': [n for n in nodos_red if n != nodo],
            'blockchain': blockhchain_copy
        }
        response = requests.post(f"{nodo}/nodos/registro_simple", data=json.dumps(
            data), headers={'Content-Type': "application/json"})
        # nodos_red.add(nodo)  #  añadimos de nuevo el nodo
    # nodos_red.remove(f"http://{mi_ip}:{puerto}")    # quitamos el nodo local

    # Fin codigo a desarrollar
    if all_correct:
        response = {
            'mensaje': 'Se han incluido nuevos nodos en la red',
            'nodos_totales': list(nodos_red)
        }
    else:
        response = {
            'mensaje': 'Error notificando el nodo estipulado',
        }
    return jsonify(response), 201


@app.route('/nodos/registro_simple', methods=['POST'])
def registrar_nodo_actualiza_blockchain():
    # Obtenemos la variable global de blockchain
    global blockchain
    global nodos_red
    read_json = request.get_json()
    #  actualizamos la lista de nodos red
    nodos_red = set(read_json.get("nodos_direcciones"))
    # [...] Codigo a desarrollar
    blockchain_leida = read_json.get("blockchain")
    blockchain = Blockchain.Blockchain()
    blockchain.primer_bloque()
    for bloque_leido in blockchain_leida:
        bloque = Blockchain.Bloque(bloque_leido["indice"], bloque_leido["transacciones"],
                                   bloque_leido["timestamp"], bloque_leido["hash_previo"], bloque_leido["prueba"])
        #  integra bloque ve si el hash prueba coincide con el hash del bloque
        if not blockchain.integra_bloque(bloque, bloque_leido["hash"]):
            return "Error: La blockchain recibida no es valida", 400

    # [...] fin del codigo a desarrollar
    if blockchain_leida is None:
        return "El blockchain de la red esta currupto", 400
    else:
        return "La blockchain del nodo" + str(mi_ip) + ":" + str(puerto) + "ha sido \
            correctamente actualizada", 200


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--puerto', default=5000,
                        type=int, help='puerto para escuchar')

    args = parser.parse_args()
    puerto = args.puerto

    app.run(host='0.0.0.0', port=puerto)


'''
CAMBIOS REALIZADOS:

- nodos_red.remove(nodo_actual) no es necesario ya que al añadirlo en nodos_red tmbn actualizamos dicho nodo
- al integrar bloque fallaba porq el primer bloque tenia un hash incorrecto (no empezaba por 4 ceros)


FALLOS:

- FALLO MUY MUY GORDO: cuando añadimos un nodo, al integrar los bloques y comprobar el hash,
                       da error porq el hash calculado es distinto al propuesto (como ya habia
                       supuesto yo en clase) y no tengo ni zorra de como solucionarlo

'''