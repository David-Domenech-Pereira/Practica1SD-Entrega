#!/usr/bin/env python3

#AQUEST FITXER JA NI FA FALTA
import subprocess
import redis
#import time
def start_redis_server():
    try:
        # Inicia el servidor Redis como un proces secundari
        subprocess.Popen(['redis-server'])
        print("Servidor redis iniciat correctament.")
    except Exception as e:
        print("Error al iniciar el servidor Redis:", e)



