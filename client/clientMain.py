import socket
import sys
import json


DEFAULT_SERVER_PORT = 9002
# Empty string indicates the server can receive requests from any network interface
DEFAULT_HOST = ''
# Iterative server, accepting up to 20 simultaneous client connections
MAX_NUMBER_OF_CLIENTS = 20
NUMBER_TO_ANALYZE = 10


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((DEFAULT_HOST, DEFAULT_SERVER_PORT))
        print("\n(CONNECTION) Client connected to server!")

        # Connection keeps up until client closes it, can ask for n files
        while True:
            try:
                # Send filename from user exactly as it's typed
                filename = input("Filename: ")
                if filename in ["quit", "q", "exit", "close"]:
                    print("(CONNECTION) Closing Program!")
                    exit(0)
                client_socket.send(str.encode(filename))

                # Wait for list of words in order or error
                server_response_message = client_socket.recv(1024)
                decoded_response = server_response_message.decode("utf-8")

                print("\n--------------------------------------------\n")
                print(
                    f"Result of the analysis for file \"{filename}\": \n")
                if "error" in decoded_response:
                    print("(ERROR) File not found")
                    break

                # Print ordered word list
                print(f" {NUMBER_TO_ANALYZE} most used words:\n")
                for word in decoded_response.split():
                    print(word)
                print("\n--------------------------------------------\n")

            except Exception:
                raise Exception(
                    "(ERROR) Lost connection to server. Shutting down")

    print("(CONNECTION) Client is closing connection")
