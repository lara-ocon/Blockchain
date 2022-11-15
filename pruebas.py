<<<<<<< HEAD
conjunto = set()
conjunto.append(1)
print(conjunto)
=======
"""

conjunto = set()
for i in range(4):
    conjunto.add(i)
print(conjunto)
b = conjunto.remove(2)
print(b)
print(conjunto)
"""

class blockchain:  
    def __init__(self):
        self.cadena_bloques = []
    
    def integra_num(self, num):
        if num == 1:
            return False
        self.cadena_bloques.append(num)
        return True

cadena = blockchain()
if not cadena.integra_num(2):
    print(False)
cadena.integra_num(1)
print(cadena.cadena_bloques)
>>>>>>> lara2
