import Blockchain
from uuid import uuid4

import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser

from multiprocessing import Semaphore
from threading import Thread

import pandas as pd

# Instancia del nodo
app = Flask(__name__)

# Instanciacion de la aplicacion
blockchain = Blockchain.Blockchain()

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
    index = len(blockchain.cadena_bloques) + 1
    blockchain.nueva_transaccion(values['origen'], values['destino'], values['cantidad'])

    response = {'mensaje': f'La transaccion se incluira en el bloque con indice {index}'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def blockchain_completa():
    response ={
        # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
        'chain': [b.toDict() for b in blockchain.cadena_bloques if b.hash is not None], 
        'longitud': len(blockchain.cadena_bloques)# longitud de la cadena
    }
    return jsonify(response), 200


@app.route('/minar', methods=['GET'])
def minar():
    # No hay transacciones
    if len(blockchain.transacciones_no_confirmadas) ==0:
        response ={
            'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"
        } 
    else:
        # Hay transaccion, por lo tanto ademas de minear el bloque, recibimos recompensa
        previous_hash = blockchain.last_block.hash
        # Recibimos un pago por minar el bloque. Creamos una nueva transaccion con:
        # Dejamos como origen el 0
        # Destino nuestra ip
        # Cantidad = 1
        # [Completar el siguiente codigo]
        response, codigo = nueva_transaccion()
        if codigo == 400:
            return response, codigo

        nuevo_bloque = blockchain.nuevo_bloque(previous_hash)
        hash_prueba = nuevo_bloque.calcular_hash()
        correct = blockchain.integra_bloque(nuevo_bloque, hash_prueba)
        if correct:
            response = {'mensaje': "Se ha integrado correctamente el bloque a la Blockchain"} 
            codigo = 200
        else:
            response = {'mensaje': "No ha sido posible integrar el bloque a la Blockchain"} 
            codigo = 400

        return jsonify(response), codigo


def hilo_copia_seguridad():
    # esta funcion es llamada cada 60 segundos por un hilo
    semaforo_copia_seguridad.acquire() # ESTE SEMAFORO LO VAMOS A PONER EN EL MAINNNNNNN!!!!!!!!!!
    # entro en la zona critica, ninguna peticion puede realizarse a la vez
    # de esta forma nos quedamos con una foto de la blockchain
    response = {
        # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
        'chain': [b.toDict() for b in blockchain.cadena_bloques if b.hash is not None], 
        'longitud': len(blockchain.cadena_bloques),# longitud de la cadena
        'date': pd.to_datetime('today', unit='s')
        }

    with open(f"respaldo-nodo"):
        ...
        # Hasta aqui hemos llegado en la clase del martes




if __name__ =='__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--puerto', default=5000, type=int, help='puerto para escuchar')

    args = parser.parse_args()
    puerto = args.puerto

    app.run(host='0.0.0.0', port=puerto)