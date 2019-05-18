import socket

target_host = 'www.google.com'
target_port = 80

# Create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send some data

client.sendto(b'AAABBBCCC', (target_host,target_port))

# Receive some data

data, addr = client.recvfrom(4096)

print(data.decode('utf-8'))
