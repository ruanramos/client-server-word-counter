from ..utils.constants import DEFAULT_SERVER_PORT, DEFAULT_HOST, MAX_NUMBER_OF_CLIENTS

import socket
import logging
from logic.MenuOptionHandler import MenuOptionHandler
import json
import re


class ServerConnector():
    """
    This class handles server connection to the clients
    """

    def __init__(self, host, port, numToListenTo):
        super().__init__()
        self.host = host
        self.port = port
        self.numToListenTo = numToListenTo
        self.clientSocket = None
        self.address = None

    def acceptConnections(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
            serverSocket.bind((self.host, self.port))
            serverSocket.listen(self.numToListenTo)

            while True:
                # Listening to connections
                print(
                    f"(CONNECTION) Server is waiting for client connection")
                self.clientSocket, self.address = serverSocket.accept()

                with self.clientSocket:
                    print(f"(CONNECTION) Connected by {self.address}")
                    self.connectionLoop()

                # End of connection with the client
                print("(CONNECTION) Lost connection to client")

    def connectionLoop(self):
        while True:
            # waits for filename
            print("(APP) Filename: ")
            receivedObj = self.clientSocket.recv(1024)
            if not receivedObj:
                break
            
            # unserialize data
            filename: str = json.loads(receivedObj)

            #

    """ class MessageHandler():
        def composeMessage(self, *pairs, **opts):
            message = {}
            for pair in pairs:
                message[pair[0]] = pair[1]
            for key, value in opts.items():
                if key == "encode" and value:
                    return self.encode(message)
            return message

        def updateMessage(self, previousMessage, *pairs, **opts):
            for pair in pairs:
                previousMessage[pair[0]] = pair[1]
            for key, value in opts.items():
                if key == "encode" and value:
                    return self.encode(previousMessage)
            return previousMessage

        def encode(self, obj):
            return str.encode(json.dumps(obj))

        def sendMessage(self, message, clientSocket):
            clientSocket.send(message) """


""" class TextAnalizer():

    def __init__(self, text):
        super().__init__()
        self.text = text

    def getWordsCount(self):
        count = {}
        for word in re.split('[ ,“.!?"”\n-]*', self.text):
            if word.upper() in count:
                count[word.upper()] += 1
            else:
                count[word.upper()] = 1
        return count

    def analize(self, numberOfWords):
        # Analize logic here
        obj = {}
        sortedCount = {k: v for k, v in sorted(
            self.getWordsCount().items(),
            key=lambda item: item[1],
            reverse=True
        )}
        for i, j in enumerate(sortedCount.items()):
            if i >= numberOfWords:
                break
            obj[i] = j
        return obj """


if __name__ == "__main__":
    """Server entry point"""

    serverConnector = ServerConnector(
        DEFAULT_HOST, DEFAULT_SERVER_PORT, MAX_NUMBER_OF_CLIENTS)
    serverConnector.accept_connections()
    print(f"Closed Connection to {serverConnector.address}")
