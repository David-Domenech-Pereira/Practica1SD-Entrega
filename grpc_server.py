import grpc
from concurrent import futures
import time
import random

# import the generated classes
import messagingServer_pb2
import messagingServer_pb2_grpc

# import the original MessagingServer.py
from messaging_service import messaging_service

from redisCont import  setUser


# create a class to define the server functions, derived from
# MessagingServer_pb2_grpc.MessagingServiceServicer
class MessagingServiceServicer(messagingServer_pb2_grpc.MessagingServiceServicer):

    def sendMessage(self, message, context):
        messaging_service.sendMessage(message)
        response = messagingServer_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
        return response

def start_server(alias):
    #crear un thread    
    # create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # use the generated function `add_MessagingServiceServicer_to_server`
    # to add the defined class to the server
    messagingServer_pb2_grpc.add_MessagingServiceServicer_to_server(
        MessagingServiceServicer(), server)
    #we find the first free port
    port = random.randint(5000,6000)
    while True:
        try:
            # we try to bind the server to the port
            server.add_insecure_port('0.0.0.0:'+str(port))
            server.start()
            break
        except Exception as e:
            # if the port is already in use, we try the next one
            port += 1
            if port > 6000:
                # we rise an exception
                raise Exception("No free ports available "+str(e))
                return
            #nothing
    
    #guardem IP:port a redis
    setUser(alias,'localhost:'+str(port))
    
    #We subscribe to the rabbitMQcont queue, we reply with our ip and port
    from rabbitMQcont import subscribeDiscoverQueue
    subscribeDiscoverQueue(alias,"localhost",str(port))
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)



   


   
