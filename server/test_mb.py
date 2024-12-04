import socket
import json
import threading


def send_data_to_server(imsi, rand):
    data = rand+';'+imsi
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8888))
    client_socket.send(data.encode())
    response = client_socket.recv(1024)
    print(f"Received response: {response.decode()}")
    client_socket.close()

if __name__ == "__main__":
    while True:
        user_input = input("Enter RAND and IMSI separated by space (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        imsi, rand = user_input.split()
        send_data_to_server(imsi, rand)
