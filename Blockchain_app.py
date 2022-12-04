"""
Practica final Fundamentos de los Sistemas Operativos - IMAT
Hecho por: Lara Ocón y Alejandro Martínez de Guinea
Aplicación web básica
"""

# Importamos las librerías necesarias
import Blockchain

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
mi_ip = '192.168.56.1'

# Semáforo para la copia de seguridad
semaforo_copia_seguridad = Semaphore(1)


@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    values = request.get_json()
    # Comprobamos que todos los datos de la transaccion están
    required = ['origen', 'destino', 'cantidad']
    if not all(k in values for k in required):
        return 'Faltan valores', 400
    # Creamos una nueva transaccion, la función nueva transaccion
    # nos devuelve el indice del ultimo bloque
    index = blockchain.nueva_transaccion(
        values['origen'], values['destino'], values['cantidad'])
    # sumamos 1 al indice pues añadiremos la transaccion al siguiente bloque  
    index += 1

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
    # Antes de minar, comprobamos si hay conflictos
    if resuelve_conflictos():
        # Esto obliga al nodo a volver a capturar transacciones si quiere
        # crear el nuevo bloque
        response = {
            'mensaje': "Ha habido un conflicto. Esta cadena se ha actualizado con una version mas larga."
        }
        semaforo_copia_seguridad.release()
        return jsonify(response), 200
    semaforo_copia_seguridad.acquire()
    # No hay transacciones
    if len(blockchain.transacciones_no_confirmadas) == 0:
        response = {
            'mensaje': "No es posible crear un nuevo bloque. No hay transacciones."
        }
        semaforo_copia_seguridad.release()
        return jsonify(response), 200
    else:
        # Hay transaccion, por lo tanto ademas de minar el bloque, recibimos recompensa
        previous_hash = blockchain.last_block().hash
        # Recibimos un pago por minar el bloque. Creamos una nueva transaccion con:
        # Dejamos como origen el 0
        # Destino: nuestra ip
        # Cantidad = 1

        # generamos una nueva transaccion
        blockchain.nueva_transaccion("0", mi_ip, 1)

        nuevo_bloque = blockchain.nuevo_bloque(previous_hash)
        hash_prueba = blockchain.prueba_trabajo(nuevo_bloque)

        correct = blockchain.integra_bloque(nuevo_bloque, hash_prueba)

        # Siempre será correcto, pero lo dejamos por si acaso.
        if correct:
            response = {'hash_bloque': nuevo_bloque.hash, 'hash_previo': previous_hash, 'indice': nuevo_bloque.indice, 'mensaje': 'Nuevo bloque minado',
                        'prueba': nuevo_bloque.prueba, 'timestamp': nuevo_bloque.timestamp, 'transacciones': nuevo_bloque.transacciones}
            codigo = 200
        else:

            response = {
                'mensaje': "No ha sido posible integrar el bloque a la Blockchain."}
            codigo = 400

        semaforo_copia_seguridad.release()
        return jsonify(response), codigo


def hilo_copia_seguridad():
    while True:
        t1 = time.time()

        # esperamos a que pasen 60 segundos para realizar la siguiente copia de seguridad
        t2 = time.time()
        while t2 - t1 < 60:
            t2 = time.time()

        semaforo_copia_seguridad.acquire()
        # entramos en la zona crítica, ninguna petición puede realizarse a la vez
        # de esta forma nos quedamos con una foto de la blockchain
        response = {
            # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
            'chain': [b.toDict() for b in blockchain.cadena_bloques if b.hash is not None],
            # longitud de la cadena
            'longitud': len(blockchain.cadena_bloques),
            'date': str(pd.to_datetime('today'))
        }

        with open(f"respaldo-nodo{mi_ip}-{puerto}.json", "w") as f:
            f.write(json.dumps(response))
        semaforo_copia_seguridad.release()


@app.route('/system', methods=['GET'])
def detalles_nodo_actual():
    # mostramos la información mas importante del nodo
    response = {
        'maquina': pl.machine(),
        'nombre_sistema': pl.system(),
        'version': pl.version(),
    }
    return jsonify(response), 200


@app.route('/nodos/registrar', methods=['POST'])
def registrar_nodos_completo():
    semaforo_copia_seguridad.acquire()
    values = request.get_json()
    global blockchain
    global nodos_red
    nodos_nuevos = values.get('direccion_nodos')
    if nodos_nuevos is None:
        semaforo_copia_seguridad.release()
        return "Error: No se ha proporcionado una lista de nodos", 400
    all_correct = True  # [Codigo a desarrollar]
    for nodo in nodos_nuevos:
        # añadimos el nodo a la red
        nodos_red.add(nodo)
    #  obtenemos una copia de la blockchain
    blockhchain_copy = [b.toDict()
                        for b in blockchain.cadena_bloques if b.hash is not None]
    blockhchain_copy.pop(0)

    # añadimos el nodo del que penden para pasarselo a todos los nodos
    nodos_red.add(f"http://{mi_ip}:{puerto}")

    nodos_red_copy = nodos_red
    for nodo in nodos_red_copy:
        #  le pasamos todos los nodos menos el nodo en cuestión
        data = {
            'nodos_direcciones': [n for n in nodos_red_copy if n != nodo],
            'blockchain': blockhchain_copy
        }

        semaforo_copia_seguridad.release()
        response = requests.post(f"{nodo}/nodos/registro_simple", data=json.dumps(
            data), headers={'Content-Type': "application/json"})
        semaforo_copia_seguridad.acquire()

    if all_correct:
        response = {
            'mensaje': 'Se han incluido nuevos nodos en la red',
            'nodos_totales': list(nodos_red)
        }
    else:
        response = {
            'mensaje': 'Error notificando el nodo estipulado',
        }
    semaforo_copia_seguridad.release()
    return jsonify(response), 201


@app.route('/nodos/registro_simple', methods=['POST'])
def registrar_nodo_actualiza_blockchain():
    semaforo_copia_seguridad.acquire()
    # Obtenemos la variable global de blockchain
    global blockchain
    global nodos_red

    read_json = request.get_json()
    #  actualizamos la lista de nodos red
    nodos_red = set(read_json.get("nodos_direcciones"))

    # obtenemos una cpopia de la blockchain
    blockchain_leida = read_json.get("blockchain")
    
    integrar_cadena(blockchain_leida)

    semaforo_copia_seguridad.release()
    
    if blockchain_leida is None:
        return "El blockchain de la red esta currupto", 400
    else:
        return "La blockchain del nodo" + str(mi_ip) + ":" + str(puerto) + "ha sido \
            correctamente actualizada", 200


def resuelve_conflictos():
    """
    Mecanismo para establecer el consenso y resolver los conflictos.
    Esta función analiza la longitud de la cadena, del nodo. En caso de ser
    la mas larga la deja como está, en caso contrario, la sustituye por la
    cadena mas larga de la red.
    """
    global blockchain
    global nodos_red

    longitud_actual = len(blockchain.cadena_bloques)
    # [Codigo a completar]
    error = False
    #  obtenemos la cadena de cada nodo
    for nodo in nodos_red:
        response = requests.get(f"{nodo}/chain")

        if response.status_code == 200:

            #  obtenemos la cadena
            cadena = response.json()["chain"]

            # obtenemos su longitud
            longitud = len(cadena)

            #  comprobamos que la longitud de la cadena sea mayor que la actual
            if longitud > longitud_actual:
                # Nuestra cadena no es la mas larga, se ha quedado atrás
                error = True
                longitud_actual = longitud
                cadena_actual = cadena
    # despues de comprobar todos los nodos, vemos que no ha conflictos
    if error:
        cadena_actual.pop(0)
        semaforo_copia_seguridad.acquire()
        integrar_cadena(cadena_actual)
        blockchain.transacciones_no_confirmadas = []
        semaforo_copia_seguridad.release()
    return error


def integrar_cadena(cadena):
    global blockchain
    blockchain = Blockchain.Blockchain()
    blockchain.primer_bloque()
    for bloque_leido in cadena:
        bloque = Blockchain.Bloque(bloque_leido["indice"], bloque_leido["transacciones"],
                                    bloque_leido["timestamp"], bloque_leido["hash_previo"], bloque_leido["prueba"])
        #  integra bloque ve si el hash prueba coincide con el hash del bloque
        if not blockchain.integra_bloque(bloque, bloque_leido["hash"]):
            return "Error: La blockchain recibida no es valida", 400


if __name__ == '__main__':
    th = Thread(target=hilo_copia_seguridad)
    th.start()
    parser = ArgumentParser()
    parser.add_argument('-p', '--puerto', default=5000,
                        type=int, help='puerto para escuchar')

    args = parser.parse_args()
    puerto = args.puerto
    print("puerto", puerto)

    app.run(host='0.0.0.0', port=puerto)
    th.join()
