#!/bin/python3.7

import sys
import socket
import threading
import argparse

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_host, local_port))
    print('[*] Listening on %s:%d' % (local_host,local_port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Print connection information
        print('[==>] Received incoming connection from %s:%d' % (addr[0], addr[1]))

        # Start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))

        proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    # Connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # Receive data from the remote end if necesary
    if receive_first:

        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # Send it to response handler
        remote_buffer = response_handler(remote_buffer)

        # Send data to local client
        if remote_buffer is not None:
            print('[<==] Sending %d bytes to localhost.' % len(remote_buffer))
            client_socket.send(remote_buffer)

    # Loop, read from local, send to remot, send to local
    # Rinse, wash, repeat
    while True:

        # Read from local host
        local_buffer = receive_from(client_socket)

        if local_buffer is not None:
            print('[==>] Received %d bytes from localhost.' % len(local_buffer))
            hexdump(local_buffer)

            # Send it to request handler
            local_buffer = request_handler(local_buffer)

            # Send data to remote host
            remote_socket.send(local_buffer)
            print('[==>] Sent to remot.')

            # Receive back the response
            remote_buffer = receive_from(remote_socket)

            if remote_buffer is not None:

                print('[<==] Received %d bytes from remote.' % len(remote_buffer))
                hexdump(remote_buffer)

                # Send to out response handler
                remote_buffer = response_handler(remote_buffer)

                # Send the response to the local socket
                client_socket.send(remote_buffer)

                print('[<==] Sent to localhost.')

            # If no more data, close the connection
            if local_buffer is None or remote_buffer is None:
                client_socket.close()
                remote_socket.close()
                print('[*] No more data. Closing connections')

                break

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X".encode() % (digits, ord(x)) for x in s])
        text = b''.join([x.encode() if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text))

    print(b'\n'.join(result))

def receive_from(connection):

    buffer = ''.encode()

    connection.settimeout(10)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

def request_handler(buffer):
    # Perform packet modifications
    return buffer


def response_handler(buffer):
    return buffer

def main():

    parser = argparse.ArgumentParser(description='TCP Proxy')
    parser.add_argument('local_host', type=str)
    parser.add_argument('local_port',type=int)
    parser.add_argument('remote_host', type=str)
    parser.add_argument('remote_port', type=str)
    parser.add_argument('receive_first', type=str)
    args = parser.parse_args()

    receive_first = True if 'True' in args.receive_first else False
    server_loop(args.local_host, args.local_port, args.remote_host, args.remote_port, receive_first)


main()
