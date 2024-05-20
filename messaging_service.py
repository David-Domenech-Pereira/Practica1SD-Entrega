import random



class MessagingService:

    def __init__(self):
        self.messages = []

    def sendMessage(self, message):
        # Per uniformitzar la sortida per pantalla
        m = Message(message.value,message.author)
        print(m)
        return 'Done'

#Aquesta classe sobreescriu la del messagingServer_pb2
class Message():
    def __init__(self,value,author):
        self.value=value
        self.author=author
    def __str__(self):
        return "("+self.author+") "+self.value

messaging_service = MessagingService()
