import json
from flask import jsonify

response = {'mensaje': f'La transaccion se incluira en el bloque con indice {1}'}

# with open('response.json', 'w') as f:
#     json.dump(jsonify(response), f)

jsonify(response)
