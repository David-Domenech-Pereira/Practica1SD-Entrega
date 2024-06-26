# Aquest main mostrará el menú amb opcions

import multiprocessing
import json
from grpc_server import start_server
from grpc_client import initializeClient, sendMessage
from redisCont import  getUser, setUser
from redisCont import getAllKeys
from rabbitMQcont import subscribeQueue,sendDiscoverMessage, sendMess, subscribeInsults, send_insult


#from redisCont import connect

#menu, inicialitzar el servidor o el client

def main():

    print("Benvingut a la aplicació de missatgeria!")
    # demanem el nom de qui fa servir aquesta consola, perquè no?
    author = input("Introdueix el teu nom: ")

    #createGroups()
    #es crea un proces per encendre el servidor
    server_process = multiprocessing.Process(target=start_server, args=(author,))
    server_process.start()
    def mostrar_menu():
        print("Que vols?")
        print("1. Connect chat")
        print("2. Subscribe to group chat")
        print("3. Discover chats")
        print("4. Access insult channel")
    global group
  
    while(1):
        mostrar_menu()
        opcio = input("Introdueix el número de l'opció que vols: ")
        if opcio == "1": 
            # pos a qui hem d'enviar
            nom = input("Introdueix el nom de l'usuari al que vols enviar el missatge o el nom del grup: \n")
            ipport = getUser(nom) # busquem la ip i el port de l'usuari
            if ipport:  #Si hem trobat l'usuari
                stub = initializeClient(ipport)
                print("Benvingut a la conversa amb "+nom+"!")
                message=""
                while message!="exit":
                    try:
                        message = input() # el missatge que envies
                        sendMessage(author,message,stub) # en efecte, enviem el missatge
                    except:
                        # Per si fa control+c
                        break
            else:
                # Potser és un grup
                # Per decisió de disseny, es crea el grup i es subscriu
                subscriuGrup(nom,author)
                
                print("Benvingut al chat")
                message=""
                while message!="exit":
                    try:
                        message = input() # el missatge que envies
                        sendMess(nom,message,author)
                    except:
                        # Per si fa control + c
                        break
                
        elif opcio=="2":
            #Subscriure grup
            nom=input("Indica el nom del grup")
            subscriuGrup(nom,author)    
        
        elif opcio=="3":
            # Discover chats
            # aixo llista els chats + grups disponivles
            print("Els chats disponibles son:")
            try:
                sendDiscoverMessage()
            except:
                # Per si fa control + c
                print("Discovery finalitzat")
        elif opcio=="4":
            # Access insult channel
            subscribeInsults()
            message=""
            while message!="exit":
                try:
                    message = input() # el missatge que envies
                    send_insult(message) # en efecte, enviem el missatge
                except:
                    break
        else:
            print("Opció incorrecta, torna a intentar-ho")
            #mostrar_menu()

def subscriuGrup(nom,authorname):
    # Mirem a redis si el tenim, marquem amb G per distingir-ho
    if(getUser("G"+nom)=="P"):
        persistent=str(1)
    elif(getUser("G"+nom)=="T"):
        # Transient
        persistent=str(0)
    else:
        # Li preguntem i guardem a Redis
        persistent=input("Vols persistencia? Indica 1 si sí, o si no\n")
        if (persistent==str(1)):
            guardar="P"
        else: guardar="T"
        # Guardem a redis
        setUser("G"+nom,guardar)
        
    #Subscribe to group chat
    # Define la función callback que procesará los mensajes
    def callback(ch, method, properties, body):
        # Desfem el que ens envia, que ho fa amb un json
        # De autor posem el nom @ el grup
        message_data = json.loads(body)
        message_content = message_data["message"]
        autor_missatge = message_data["author"]
        m = Message(message_content,autor_missatge+"@"+nom)
        print(m)
    
    subscribeQueue(nom, callback,authorname, persistent==str(1))
   
    # Posem el grup per a que es pugui descobrir
    from rabbitMQcont import subscribeDiscoverQueue
    subscribeDiscoverQueue("(G) "+nom,"","")


#Aquesta classe sobreescriu la del messagingServer_pb2
class Message():
    def __init__(self,value,author):
        self.value=value
        self.author=author
    def __str__(self):
        return "("+self.author+") "+self.value

main()