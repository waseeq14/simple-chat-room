import threading
import socket
import base64
import json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 4444))
server.listen()

clients = []
clients_name = []


def broadcast_msg(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            message_str = data.decode('ascii')
            try:
                message_contents = json.loads(message_str)
                if message_contents['type'] == 'image':
                    print("Received image message")
                    handle_img(client, message_contents)
                else:
                    broadcast_msg(data)
            except json.JSONDecodeError:
                broadcast_msg(data)
        except Exception as e:
            print("Error occurred:", e)
            index = clients.index(client)
            client.close()
            clients.remove(client)
            name = clients_name[index]
            clients_name.remove(name)
            broadcast_msg(f'{name} left the chat!'.encode('ascii'))
            break


def handle_img(client, msg):
    username = msg['username']
    image_b64 = msg['data']
    image = base64.b64decode(image_b64)
    filename = f'{username}_image.jpg'
    with open(filename, 'wb') as file:
        file.write(image)
    broadcast_msg(f'{username} sent an image: {filename}'.encode('ascii'))




def receive():
    while True:
        client_socket, address = server.accept()
        print("Connected with", address)
        client_socket.send('Name:'.encode('ascii'))
        name = client_socket.recv(1024).decode('ascii')
        clients_name.append(name)
        clients.append(client_socket)
        print(f'Name of the client is {name}!')
        broadcast_msg(f'{name} joined the chat!'.encode('ascii'))
        client_socket.send('Connected to the server!'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client_socket,))
        thread.start()


print("CHAT ROOM SERVER STARTED!")
receive()
