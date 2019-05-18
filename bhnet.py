#!/bin/python3.7

import argparse
import sys
import socket
import threading
import subprocess

# Define global variables
listen = False
command = False
upload = False
execute = ''
target = ''
upload_destination = ''
port = 0


def server_loop():
    global target

    print('Entering server loop')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Spin off a thread to handle new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):

    # Trim the newline
    command = command.rstrip()

    # Run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

    except:
        output = 'Faild to execute command. \r\n'

    # Send output back to the client
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    # Check for upload
    if upload_destination is not None:

        # Read in all of the bytes and write to destination
        file_buffer = ''

        # Keep reading data until none is available
        while True:
            data = client_socket.recv(1024)

            if not data.decode():
                break
            else:
                file_buffer += data

        # Try to write bytes out
        try:
            file_descriptor = open(upload_destination, 'wb')
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # Acknowledge that file is saved
            client_socket.send(b'Successfully saved file to %s\r\n' % upload_destination)
        except:
            client_socket.send(b'Failed to save file to %s\r\n' % upload_destination)

    # Check for command execution
    if execute is not None:

        # Run the command
        output = run_command(execute).encode()

        client_socket.send(output)

    # Another loop for command shell if requested
    if command:

        print('Shell requested')

        # Show a simple prompt
        client_socket.send('<BHP:#> '.encode())

        while True:

            # Receive until linefeed key spoted (enter key)
            cmd_buffer = ''
            while '\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            # Save the command output
            response = run_command(cmd_buffer)

            # Send back the response
            client_socket.send(response + '<BHP:#> '.encode())


def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:

        # Connect to target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode())

        while True:

            # Wait for data back
            recv_len = 1
            response = ''

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()

                if recv_len < 4096:
                    break

            print(response),

            # Wait for more input
            buffer = input('')
            buffer += '\n'

            # Send it off
            client.send(buffer.encode())
    except:

        print('[*] Exception! Exiting.')

        # Tear down the connection
        client.close()


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    # Set up argument parsing
    # Cloned from github, need to read some more
    parser = argparse.ArgumentParser(description="Simple ncat clone.")
    parser.add_argument("port", type=int, help="target port")
    parser.add_argument("-t", "--target_host", type=str, help="target host", default="0.0.0.0")
    parser.add_argument("-l", "--listen", help="listen on [host]:[port] for incomming connections", action="store_true", default=False)
    parser.add_argument("-e", "--execute", help="--execute=file_to_run execute the given file upn receiving a connection")
    parser.add_argument("-c", "--command", help="initialize a command shell", action="store_true", default=False)
    parser.add_argument("-u", "--upload", help="--upload=destination upon receing connection upload a file and write to [destination]")
    args = parser.parse_args()

    # parse arguements
    target = args.target_host
    port = args.port
    listen = args.listen
    execute = args.execute
    command = args.command
    upload_destination = args.upload

    # Listen or just send data from stdin?
    if not listen and len(target) and port > 0:
        # Read in the buffer from the commandline
        # This will block, so send CTRL-D if not sending input to stdin
        buffer = sys.stdin.read()

        # Senda data off
        client_sender(buffer)

    # Listen and other functions
    if listen:
        server_loop()


main()
