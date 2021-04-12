import socket
import logging
import json
import re
import os

DEFAULT_SERVER_PORT = 9000
# Empty string indicates the server can receive requests from any network interface
DEFAULT_HOST = ''
# Iterative server with no queued clients
MAX_NUMBER_OF_CLIENTS = 1
NUMBER_TO_ANALYZE = 10


class ServerConnector():
    """
    This class handles server connection to the clients
    """

    def __init__(self, host, port, num_to_listen_to):
        super().__init__()
        self.host = host
        self.port = port
        self.num_to_listen_to = num_to_listen_to
        self.client_socket = None
        self.address = None

    def accept_connections(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(self.num_to_listen_to)

            while True:
                # Listening to connections
                print(
                    f"(CONNECTION) Server is waiting for client connection...")
                self.client_socket, self.address = server_socket.accept()

                with self.client_socket:
                    print(f"(CONNECTION) Connected by {self.address}")
                    self.connection_loop()

                # End of connection with the client
                print("(CONNECTION) Lost connection to client")

    def connection_loop(self):
        while True:
            # waits for filename
            print("(APP) Waiting for filename... ")
            received_obj = self.client_socket.recv(1024)
            if not received_obj:
                break

            # unserialize data
            filename = received_obj.decode("utf-8")
            print(
                f"(APP) Received {filename} as input from client {self.address}")

            db_manager = DatabaseManager(
                os.path.abspath(filename).split('/', 1)[0] + 'server/' + filename)

            text = db_manager.getFile()

            if "errno" in text.lower():
                print(f"(ERROR) FILE {} REQUESTED BY {self.client_socket.} WAS NOT FOUND ")
                self.client_socket.send(text.encode())
            else:
                text_analyzer = TextAnalizer(text)
                result = text_analyzer.analyze(NUMBER_TO_ANALYZE)
                self.client_socket.send(json.dumps(
                    list(result.values())).encode())


class DatabaseManager():
    """
    Database logic here. For this application,
    only local saved files
    """

    def __init__(self, path):
        self.path = path

    def getFile(self):
        try:
            with open(f"{self.path}", 'r') as f:
                data = f.read()
            return data
        except FileNotFoundError as e:
            return str(e)


class TextAnalizer():
    """Analisys logic here"""

    def __init__(self, text):
        super().__init__()
        self.text = text

    def get_words_count(self):
        count = {}
        words = re.compile(
            "(?:(?:[^a-zA-Z]+')|(?:'[^a-zA-Z]+))|(?:[^a-zA-Z']+)").split(self.text)
        for word in words:
            if word.upper() in count:
                count[word.upper()] += 1
            else:
                count[word.upper()] = 1
        return count

    def analyze(self, numberOfWords):
        obj = {}
        sortedCount = {k: v for k, v in sorted(
            self.get_words_count().items(),
            key=lambda item: item[1],
            reverse=True
        )}
        for i, j in enumerate(sortedCount.items()):
            if i >= numberOfWords:
                break
            obj[i] = j
        return obj


if __name__ == "__main__":
    """Server entry point"""
    server_connector = ServerConnector(
        DEFAULT_HOST, DEFAULT_SERVER_PORT, MAX_NUMBER_OF_CLIENTS)
    server_connector.accept_connections()
    print(f"Closed Connection to {server_connector.address}")
