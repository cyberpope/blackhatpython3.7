import socket
import threading
import argparse

# Client-handling thread
def handle_client(client_socket):

    response = 'ACK'
    # Print what client sends
    request = client_socket.recv(1024).decode()

    print('[*] Received: %s' % request)

    # Send back a packet
    client_socket.send(response.encode())

    client_socket.close


def main():

    parser = argparse.ArgumentParser(description='Overkill TCP Server')
    parser.add_argument('bind_ip', type=str)
    parser.add_argument('bind_port', type=int)
    args = parser.parse_args()
    server_open(args.bind_ip, args.bind_port)

def server_open(bind_ip, bind_port):

    # response = 'ACK'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((bind_ip, bind_port))

    server.listen(5)

    print('[*] Listening on %s:%d' % (bind_ip, bind_port))

    while True:

        client,addr = server.accept()

        print('[*] Accepted connection from: %s:%d' % (addr[0], addr[1]))

        # Spin client thread to handle incoming data
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

main()
