import sys
import socket
import threading
import subprocess
import argparse

LISTEN = False
COMMAND = False
UPLOAD = False
EXECUTE = False
TARGET = ''
UPLOAD_DESTINATION = ''
PORT = 0


def usage():
    print('Usage: netcat.py -t target -p port')
    print('-l --listen                  - listen in [host]:[port] for incoming connections')
    print('-e --execute=file_to_run     - execute the given file upon receiving a connection')
    print('-c --command                 - initialize a command shell')
    print('-u --upload=destination      - upon receiving connection upload a file and write to [destination')

    sys.exit(0)


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((TARGET, PORT))
        if len(buffer):
            client.send(buffer)
            while True:
                recv_len = 1
                response = ''

                while recv_len:
                    data = client.recv(4096)
                    recv_len = len(data)
                    response += data
                    if recv_len < 4096:
                        break

                print(response)
                buffer = input('')
                buffer += '\n'

                client.send(buffer)
    except:
        print('[*] Exception! Exiting.')
        client.close()


def server_loop():
    global TARGET

    if not TARGET:
        TARGET = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((TARGET, PORT))
    server.listen(5)


    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    command = command.strip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = 'Failed to execute command.\r\n'

        return output