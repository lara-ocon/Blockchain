"""
Practica final Fundamentos de los Sistemas Operativos - IMAT
Hecho por: Lara Ocón y Alejandro Martínez de Guinea
Librería Blockchain
"""

from typing import List, Dict
import json
import hashlib
import time


class Bloque:
    def __init__(self, indice: int, transacciones: List[Dict], timestamp: float,
                 hash_previo: str, prueba: int = 0):
        """
        Constructor de la clase `Bloque`.
        :param indice: ID unico del bloque.
        :param transacciones: Lista de transacciones.
        :param timestamp: Momento en que el bloque fue generado.
        :param hash_previo hash previo
        :param prueba: prueba de trabajo
        """
        # Codigo a completar (inicializacion de los elementos del bloque)
        self.indice = indice
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_previo = hash_previo          # clave criptográfica del anterior bloque
        self.prueba = prueba  #  "lo detallaremos mas adelante"
        self.hash = None                        # inicializamos a None el hash del bloque

    def calcular_hash(self):
        """
        Metodo que devuelve el hash de un bloque
        Devuelve una cadena de 256 caracteres (hash) codificando toda la
        información del bloque.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()

    def toDict(self):
        """
        Metodo que devuelve un diccionario con la informacion del bloque
        """
        # return {'indice': self.indice, 'transacciones': self.transacciones,
        #         'timestamp': self.timestamp, 'hash_previo': self.hash_previo,
        #         'prueba': self.prueba, 'hash': self.hash}
        return dict(sorted(self.__dict__.items()))

class Blockchain(object):
    def __init__(self):
        self.dificultad = 4
        # debe se capaz de mantener una lista de bloques
        # y además debe almacenar en otra lista aquellas transacciones que
        # todavía no están confirmadas para ser introducidas en un bloque

        # Codigo a completar (inicializacion de las listas de transacciones y de bloques)
        self.cadena_bloques = []                # aqui empezara la lista enlazada de bloques
        self.transacciones_no_confirmadas = []             # lista con transacciones aun no confirmadas
    

    def primer_bloque(self):
        # establecemos el primer bloque de la Blockchain

        bloque = Bloque(1, [], 0, "1", 0)

        # bloque = Bloque(1, [], 0, '1', 0) preguntar a los profesores

        bloque.hash = bloque.calcular_hash()
        while bloque.hash[0:self.dificultad] != "0" * self.dificultad:
            bloque.prueba += 1
            bloque.hash = bloque.calcular_hash()
        self.cadena_bloques.append(bloque)

    def nuevo_bloque(self, hash_previo: str) -> Bloque:
        """
        Crea un nuevo bloque a partir de las transacciones que no estan
        confirmadas
        :param prueba: el valor de prueba a insertar en el bloque
        :param hash_previo: el hash del bloque anterior de la cadena
        :return: el nuevo gloque
        """
        # [...] Codigo a completar
        # indice sera el indice del ultimo bloque de la blockchain +1 no?
        # prueba = 0, inicializamos los parametros de prueba siempre a 0
        
        bloque = Bloque(len(self.cadena_bloques) + 1, self.transacciones_no_confirmadas, time.time(), hash_previo, 0)

        return bloque

    def nueva_transaccion(self, origen: str, destino: str, cantidad: int) -> int:
        """
        Crea una nueva transaccion a partir de un origen, un destino y una
        cantidad y la incluye en las
        listas de transacciones
        :param origen: <str> el que envia la transaccion
        :param destino: <str> el que recibe la transaccion
        :param cantidad: <int> la candidad
        :return: <int> el indice del bloque que va a almacenar la transaccion
        """
        # [...] Codigo a completar

        transaccion = {'origen': origen, 'destino': destino, 'cantidad' : cantidad, 'tiempo': time.time()}
        # esto lo metemos en la lista de transacciones sin cofirmar
        self.transacciones_no_confirmadas.append(transaccion)

        # devolvemos el indice del ultimo bloque de la blockchain
        return self.cadena_bloques[-1].indice


    def prueba_trabajo(self, bloque: Bloque) -> str:
        """
        Algoritmo simple de prueba de trabajo:
        - Calculara el hash del bloque hasta que encuentre un hash que empiece
        por tantos ceros como dificultad
        - Cada vez que el bloque obtenga un hash que no sea adecuado,
        incrementara en uno el campo de ``prueba del bloque''
        :param bloque: objeto de tipo bloque
        :return: el hash del nuevo bloque (dejara el campo de hash del bloque sin modificar)
        """
        # [Codificar el resto del metodo]
        hash_bloque = bloque.calcular_hash()
        while hash_bloque[0:self.dificultad] != "0"*self.dificultad:
            bloque.prueba += 1
            hash_bloque = bloque.calcular_hash()
        # dejamos sin modificar el hash del bloque

        return hash_bloque

    def prueba_valida(self, bloque: Bloque, hash_bloque: str) -> bool:
        """
        Metodo que comprueba si el hash_bloque comienza con tantos ceros como la
        dificultad estipulada en el blockchain
        Ademas comprobara que hash_bloque coincide con el valor devuelvo del
        metodo de calcular hash del bloque.
        Si cualquiera de ambas comprobaciones es falsa, devolvera falso y en caso
        contrario, verdarero
        :param bloque:
        :param hash_bloque:
        :return:
        """
        #  [Codificar el resto del metodo]
        if hash_bloque[0:4] != "0"*self.dificultad:
            return False
        if hash_bloque != bloque.calcular_hash():
            return False
        return True

    def integra_bloque(self, bloque_nuevo: Bloque, hash_prueba: str) -> bool:
        """
        Metodo para integran correctamente un bloque a la cadena de bloques.
        Debe comprobar que la prueba de hash es valida y que el hash del bloque
        ultimo de la cadena coincida con el hash_previo del bloque que se va a 
        integrar. Si pasa las comprobaciones, actualiza el hash del bloque a 
        integrar, lo inserta en la cadena y hace un reset de las transacciones 
        no confirmadas (vuelve a dejar la lista de transacciones no confirmadas 
        a una lista vacia)
        :param bloque_nuevo: el nuevo bloque que se va a integrar
        :param hash_prueba: la prueba de hash
        :return: True si se ha podido ejecutar bien y False en caso contrario 
        (si no ha pasado alguna prueba)
        """
        # [Codificar el resto del metodo]

        # Comprobaciones:
        if not self.prueba_valida(bloque_nuevo, hash_prueba):
            return False
        if bloque_nuevo.hash_previo != self.cadena_bloques[-1].hash:
            return False

        # Añadimos el bloque:
        bloque_nuevo.hash = hash_prueba
        self.cadena_bloques.append(bloque_nuevo)
        self.transacciones_no_confirmadas = []
        
        return True
    

    def last_block(self):
        # Esta funcion devuelve el ultimo bloque
        return self.cadena_bloques[-1]
    



