import subprocess
import platform as pl  #  obtemer informacion del nodo
import re

def detalles_nodo_actual():
    response = {
        'maquina': pl.machine(),
        'nombre_sistema': pl.system(),
        'version': pl.version(),
    }
    return response

system = detalles_nodo_actual()['nombre_sistema']

if system == 'Windows':
    batcmd = "ipconfig"
    result = subprocess.check_output(batcmd, shell=True)
    with open("prueba.txt", "wb") as f:
        f.write(result)
    result = str(result)

    ini = re.search('Ethernet:', result)
    b = re.search('\d+\.\d+\.\d+\.\d+', result[ini.start():])

    print(b.group())

elif system == 'Linux':
    batcmd = "ifconfig"
    result = subprocess.check_output(batcmd, shell=True)
    with open("prueba.txt", "wb") as f:
        f.write(result)
    result = str(result)

    ini = re.search('enp0s3|eth2:', result)
    b = re.search('\d+\.\d+\.\d+\.\d+', result[ini.start():])

    print(b.group())
