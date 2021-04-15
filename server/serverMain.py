import socket
import logging
import json
import re
import os
import select
import sys
import threading

"""

Server with concurrency added to the select call

Clients are being treated concurrently, but only in one processor,
by listening connections and threading the response flux for each
client (no sub-processes)

1- Server wont close with 'quit' command until all clients are finished
2- Server wont accept connections after 'quit' command is sent
3- Server can receive multiple connections and treat multiple responses

"""


DEFAULT_SERVER_PORT = 9000
# Empty string indicates the server can receive requests from any network interface
DEFAULT_HOST = ''
MAX_NUMBER_OF_CLIENTS = 5
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

        # Possible interfaces (commands, client request, connection request)
        self.entries = [sys.stdin]
        self.connection_history = {}  # Could receive a timestamp or more data too
        self.client_threads = []  # For join purposes

    def accept_connections(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(self.num_to_listen_to)
            server_socket.setblocking(False)
            self.entries.append(server_socket)

            while True:

                # Listening to connections
                print(
                    f"({bcolors.WARNING}CONNECTION) Server is waiting for commands or connections...{bcolors.ENDC}")
                read, wright, error = select.select(self.entries, [], [])
                for read_ready in read:

                    if read_ready == server_socket:  # New connection request
                        client_socket, address = server_socket.accept()
                        self.connection_history[client_socket] = address
                        print(
                            f"{bcolors.OKCYAN}(CONNECTION) Connected by {address}{bcolors.ENDC}")
                        client_thread = threading.Thread(
                            target=self.answer_requests, args=(client_socket, address))
                        self.client_threads.append(
                            client_thread)  # References for join
                        client_thread.start()

                    elif read_ready == sys.stdin:
                        # Command line input from server user
                        command = input()
                        if command in ["quit", "q", "exit", "close"]:  # End server
                            for client_thread in self.client_threads:
                                client_thread.join()
                                self.client_threads.remove(client_thread)
                            server_socket.close()
                            exit(0)

                        elif command == 'hist':  # Connections history requested
                            print(
                                f"(CONNECTION) {str(self.connections.values())}")

    def answer_requests(self, client_socket, address):
        while True:
            # waits for filename
            print(
                f"{bcolors.OKCYAN}(APP) Waiting for filenames from {address}{bcolors.ENDC}")
            received_obj = client_socket.recv(1024)
            if not received_obj:
                # End of connection with the client
                print(
                    f"{bcolors.WARNING}(CONNECTION) Lost connection to client {address}{bcolors.ENDC}")
                break

            # unserialize data
            filename = received_obj.decode("utf-8")
            print(
                f"{bcolors.OKBLUE}(APP) Received {filename} as input from client {address}{bcolors.ENDC}")

            db_manager = DatabaseManager(
                os.path.abspath(filename).split('/', 1)[0] + 'server/' + filename)

            text = db_manager.getFile()

            if "errno" in text.lower():
                print(
                    f"{bcolors.FAIL}(ERROR) FILE{bcolors.BOLD} {filename}{bcolors.ENDC}{bcolors.FAIL} REQUESTED BY {address} WAS NOT FOUND{bcolors.ENDC}")
                client_socket.send(text.encode())
            else:
                text_analyzer = TextAnalizer(text)
                result = text_analyzer.analyze(NUMBER_TO_ANALYZE)
                print(
                    f"{bcolors.OKGREEN}(APP) FILE {filename} ANALYSIS SENT BACK TO {address}{bcolors.ENDC}")
                client_socket.send(json.dumps(
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


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if __name__ == "__main__":
    """Server entry point"""
    server_connector = ServerConnector(
        DEFAULT_HOST, DEFAULT_SERVER_PORT, MAX_NUMBER_OF_CLIENTS)
    server_connector.accept_connections()
    print(f"Closed Connection to {server_connector.address}")
