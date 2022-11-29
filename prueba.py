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
        blockchain.cadena_bloques = cadena_actual
        blockchain.transacciones_no_confirmadas = []
    return error
