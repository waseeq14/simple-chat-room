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

def handle_img(msg):
    username = msg['username']
    image_b64 = msg['data']
    image = base64.b64decode(image_b64)
    path = f'{username}_image.jpg'
    with open(path, 'wb') as file:
        file.write(image)
    broadcast_msg(f'{username} sent an image: {path}'.encode('ascii'))

# def handle(client):
#     rcv = b""
#     while True:
#         try:
#             data = client.recv(1024)
#             rcv += data
#             if not data:
#                 break
#             print("Recieved Data: ", data)
#             try:
#                 message_contents = json.loads(rcv.decode('ascii'))
#                 if message_contents['type'] == 'image':
#                     print("Received image message")
#                     handle_img(message_contents)
#                 else:
#                     broadcast_msg(data)
#             except json.JSONDecodeError:
#                 print("DECODE MASLA")
#                 broadcast_msg(data)
#             except ValueError:
#                 continue
#         except Exception as e:
#             print("Error occurred:", e)
#             index = clients.index(client)
#             client.close()
#             clients.remove(client)
#             name = clients_name[index]
#             clients_name.remove(name)
#             broadcast_msg(f'{name} left the chat!'.encode('ascii'))
#             break

def handle(client):
    data_rcv = b""
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            data_rcv += data
            try:
                contents = json.loads(data_rcv.decode('ascii'))
                if contents['type'] == 'image':
                    print("Image Received")
                    handle_img(contents)
                else:
                    username = contents['username']
                    text = contents['text']
                    message = f'{username}: {text}'
                    broadcast_msg(message.encode('ascii'))
                    data_rcv = b""
            except json.JSONDecodeError as e:
                continue
        except ValueError:
            continue
        except Exception as e:
            print("Error occurred:", e)
            index = clients.index(client)
            client.close()
            clients.remove(client)
            name = clients_name[index]
            clients_name.remove(name)
            broadcast_msg(f'{name} left the chat!'.encode('ascii'))
            break



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
