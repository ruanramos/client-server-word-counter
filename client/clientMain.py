import socket
import sys
import json


DEFAULT_SERVER_PORT = 9001
# Empty string indicates the server can receive requests from any network interface
DEFAULT_HOST = ''
# Iterative server, accepting up to 20 simultaneous client connections
MAX_NUMBER_OF_CLIENTS = 20
NUMBER_TO_ANALYZE = 10


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
        clientSocket.connect((DEFAULT_HOST, DEFAULT_SERVER_PORT))
        print("\n(CONNECTION) Client connected to server!")
        while True:
            try:
                # Send filename from user exactly as it's typed
                filename = input("Filename: ")
                clientSocket.send(str.encode(filename))

                # Wait for list of words in order or error
                serverResponseMessage = clientSocket.recv(1024)
                decodedResponse = serverResponseMessage.decode("utf-8")

                print("\n--------------------------------------------\n")
                print(
                    f"  Result of the analysis for file \"{filename}\": \n")
                if "error" in decodedResponse:
                    print("(ERROR) File not found")
                    break

                # Print ordered word list
                print(f" {NUMBER_TO_ANALYZE} most used words:\n")
                for word in decodedResponse.split():
                    print(word)

                    ClientScreenPrinter.showAnalysisResult(
                        decodedResponse["result"])
            except Exception:
                raise Exception(
                    "(ERROR) Lost connection to server. Shutting down")

    print("(CONNECTION) Client is closing connection")
