import socket

targer_host = '127.0.0.1'
target_port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto('TEST'.encode(), (targer_host, target_port))
data, addr = client.recvfrom(4096)
print(data)