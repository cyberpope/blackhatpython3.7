import socket

target_host = '0.0.0.0'
target_port = 9999
message = 'AAABBBCCCC'

# Create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to client

client.connect((target_host, target_port))

# Send some data

client.sendto(message.encode(), (target_host,target_port))

# Receive some data

response = client.recv(4096).decode()

print(response)
