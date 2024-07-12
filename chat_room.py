import socket
import threading

name = input("Choose a name: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 4444))

def receive():
    while True:
        try:
            message = client_socket.recv(1024).decode('ascii')
            if message == 'Name:':
                client_socket.send(name.encode('ascii'))
            else:
                print(message)
        except:
            print("ERROR!")
            client_socket.close()
            break

def write():
    while True:
        message = f'{name}: {input("")}'
        client_socket.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
