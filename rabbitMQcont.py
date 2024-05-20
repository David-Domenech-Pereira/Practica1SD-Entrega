import pika
import sys
import threading
import uuid
import json
import time
import random


# Configura tus credenciales y la dirección del servidor RabbitMQ
rabbitmq_host = 'localhost'  # o la dirección de tu servidor RabbitMQ
rabbitmq_queue = 'nombre_de_tu_cola'  # reemplaza con el nombre de tu cola

# Conecta al servidor RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

def start_connection(nombre):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

def sendMess(exchange, message,author):
    # Posem en un json que envii missatge + author, així el que ho rep ho sap millor
    content_json = {"message": message, "author": author}
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()

    channel.basic_publish(exchange=exchange, routing_key='', properties=pika.BasicProperties(content_type='text/plain',
                                                          delivery_mode=pika.DeliveryMode.Persistent), body=json.dumps(content_json))
   

def send_insult(insult):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='insultQueue')
    channel.basic_publish(exchange='',
                          routing_key='insultQueue',
                          body=insult)
  
   

def subscribeInsults():
    def insult_receiver():
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        #En aquest cas només és necessari crear una cua per tal d'enviar l'insult només a un sol usuari
        channel.queue_declare(queue='insultQueue')

        def on_message(ch, method, properties, body):
            print(f"Received an insult: {body.decode()}")

        #S'ndica el mètode callback i el autoack per a que rabbitMQ envii automaticamnet el ACK al final de la comunicació
        channel.basic_consume(queue='insultQueue', on_message_callback=on_message, auto_ack=True)
        channel.start_consuming()
    thread = threading.Thread(target=insult_receiver)
    thread.start()

def sendDiscoverMessage():

    def on_response(ch, method, properties, body):
        # Process the received response
        print(body.decode())
    # Declare a unique queue for responses
    
    result = channel.queue_declare(queue='',exclusive=True) #Declara la cua per contestar
    callback_queue = result.method.queue #Agafo la cua que he declarat
    # It has to consume, so we get the response message
    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=on_response,
        auto_ack=True
    )
    corr_id = str(uuid.uuid4())
    channel.basic_publish(
        exchange='onlineUsersExchange',
        
        routing_key="", # si posem le routing key buit, ho envia a qualsevol de les cues
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id,
        ),
        body="")
    try: #Com que l'usuari que envia el disciver no sap a quants usuris ho ha enviat no sap quants respondràn, raó per la qual es podria quedar esperant infinitament.
        #Així que esperem els missatges fins que l'usuri faci cnrl+c
        print("Usuaris disponibles, prem ctrl+c per aturar:")
        channel.start_consuming() 
        

    except KeyboardInterrupt:
        # Stop consuming and close connection when done
        channel.stop_consuming()
    
    

def subscribeDiscoverQueue(alias,ip, port):
    def start_consumingDiscover():
        def on_request(ch, method, properties, body):
            
            # We reply with an ip and a port
            response =str(alias)+"=>"+str(ip)+":"+str(port)
            ch.basic_publish(exchange='',
                            routing_key=properties.reply_to,
                            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                            body=response)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        # només pot existir una cua exclusiva amb el mateix nom, fem un nom random
        user_rand_id = alias+str(random.randint(1,6000))
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='onlineUsersExchange', exchange_type='fanout', durable=True)
        # Cada usuari te la seva cua independent
        
        channel.queue_declare(queue='onlineUsers'+user_rand_id, exclusive=True)
        #Es fa per evitar tenir 2 o més exchange amb el mateix nom
        channel.basic_qos(prefetch_count=1) # Limita el número de mensajes que el servidor manejará sin enviar un ack (acuse de recibo)
        channel.basic_consume(queue='onlineUsers'+user_rand_id, on_message_callback=on_request)

        # bindejem la cua al exchange en mode fanout
        channel.queue_bind(exchange='onlineUsersExchange', queue='onlineUsers'+user_rand_id)

      
        channel.start_consuming()
    # Ejecutar start_consuming en un hilo separado
    thread = threading.Thread(target=start_consumingDiscover)
    thread.start()

def subscribeQueue(name, callback, username, durable=False):
    def start_consuming():
            queue_name=username+";"+name
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            channel = connection.channel()
            try:
                channel.exchange_declare(exchange=name, exchange_type='fanout',durable=durable)
            except Exception as e:
                print("Error al conectar-se")
                return -1
            result = channel.queue_declare(queue=queue_name, durable=durable)
            channel.queue_bind(exchange=name, queue=queue_name)
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
      

    # Ejecutar start_consuming en un hilo separado
    thread = threading.Thread(target=start_consuming)
    thread.start()
   