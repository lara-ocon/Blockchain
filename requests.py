import requests
import requests
import json
import json

# Cabecera JSON (comun a todas)
cabecera ={'Content-type': 'application/json', 'Accept': 'text/plain'}

print("\nGeneramos nueva transacción en el puerto 5000.")
# datos transaccion
transaccion_nueva ={'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
r = requests.post('http://127.0.0.1:5000/transacciones/nueva', data =json.dumps(
                                         transaccion_nueva), headers=cabecera)
print(r.text)

print("\nMinamos un bloque en el puerto 5000.")
# minamos un bloque
r = requests.get('http://127.0.0.1:5000/minar')
print(r.text)

print("\nObtenemos la cadena del puerto 5000.")
# obtenemos su cadena
r = requests.get('http://127.0.0.1:5000/chain')
print(r.text)

print("\nRegistramos al nodo 5001 en el puerto 5000.")
# registramos un nodo
r = requests.post('http://127.0.0.1:5000/nodos/registrar', 
                    body =json.dumps({"direccion_nodos": ["http://127.0.0.1:5001"]}),
                    headers=cabecera)
print(r.text)

print("\nObtenemos la cadena del puerto 5001.")
# vemos la cadena del nodo en el puerto 5001
r = requests.get('http://127.0.0.1:5000/chain')
print(r.text)

print("\nVamos a probar a generar un conflicto.")
# Hacemos que tanto el nodo 5000 como el 5001 resuelvan conflicto
# Para eello, hacemos que cualquiera de los dos mine un bloque, 
# de forma que al intentar minar un bloque el otro nodo, salte el
# conflicto y se resuelva

print("\nPrimero, generamos transacciones en el puerto 5001 y las minamos.")
# datos transaccion
transaccion_nueva ={'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
r = requests.post('http://127.0.0.1:5001/transacciones/nueva', data =json.dumps(
                                         transaccion_nueva), headers=cabecera)
print(r.text)

# minamos un bloque en el 5000
r = requests.get('http://127.0.0.1:5001/minar')
print(r.text)

# obtenemos su cadena
r = requests.get('http://127.0.0.1:5001/chain')
print(r.text)

print("\nAhora, generamos transacciones en el puerto 5000 y las minamos.")
# datos transaccion
transaccion_nueva ={'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
r = requests.post('http://127.0.0.1:5000/transacciones/nueva', data =json.dumps(
                                         transaccion_nueva), headers=cabecera)
print(r.text)

# minamos bloque en el 5001
r = requests.get('http://127.0.0.1:5000/minar')
print(r.text)

# Aquí debería haber un conflicto, y el nodo 5000 debería heredar la 
# cadena del 5001, pues es la más larga hasta el momento.

# obtenemos su cadena
r = requests.get('http://127.0.0.1:5000/chain')
print(r.text)










