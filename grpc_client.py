import grpc

# import the generated classes
import messagingServer_pb2
import messagingServer_pb2_grpc

def initializeClient(ipport):

    # open a gRPC channel
    channel = grpc.insecure_channel(ipport)

    # create a stub (client)
    stub = messagingServer_pb2_grpc.MessagingServiceStub(channel) #MessagingServiceStub metode del .proto
    
    return stub

def sendMessage(author,message, stub):

    # create a valid request message
    m = messagingServer_pb2.Message(value=message,author=author) #Message clase del .proto
    stub.sendMessage(m) #sendMessage metode del grpc server



