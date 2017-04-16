import sys
import socket
import threading
import subprocess
import argparse

LISTEN = False
COMMAND = False
UPLOAD = False
EXECUTE = ''
TARGET = ''
UPLOAD_DESTINATION = ''
PORT = 0


def main():
    global LISTEN
    global TARGET
    global PORT
    global EXECUTE
    global COMMAND
    global UPLOAD_DESTINATION

    parser = argparse.ArgumentParser(description='Python netcat implementation')
    parser.add_argument('-l', dest='listen', action='store_true', help='listen in [host]:[port] for incoming connections')
    parser.add_argument('-p', dest='port', action='store', help='listen in [host]:[port] for incoming connections')
    parser.add_argument('-t', dest='target', action='store', help='listen in [host]:[port] for incoming connections')
    parser.add_argument('-e', dest='execute', action='store', help='execute the given file upon receiving a connection')
    parser.add_argument('-c', dest='command', action='store_true', help='initialize a command shell')
    parser.add_argument('-u', dest='upload', action='store', help='upon receiving connection upload a file and write to [destination]')

    args = parser.parse_args()

    if args.listen:
        LISTEN = True
    if args.execute:
        EXECUTE = args.execute
    if args.command:
        COMMAND = True
    if args.upload:
        UPLOAD_DESTINATION = args.upload
    if args.target:
        TARGET = args.target
    if args.port:
        PORT = int(args.port)

    if not LISTEN and TARGET and PORT > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)
    if LISTEN:
        server_loop()


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


def client_handler(client_socket):
    global UPLOAD_DESTINATION
    global EXECUTE
    global COMMAND

    if len(UPLOAD_DESTINATION):
        file_buffer = ''
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        try:
            with open(UPLOAD_DESTINATION, 'wb') as file_descriptor:
                file_descriptor.write(file_buffer)

            client_socket.send('Successfully saved file to %s\r\n' % UPLOAD_DESTINATION)
        except:
            client_socket.send('Failed to save file to %s\r\n' % UPLOAD_DESTINATION)

    if len(EXECUTE):
        output = run_command(EXECUTE)
        client_socket.send(output)
        if COMMAND:
            while True:
                client_socket.send('<BHP:#> ')
                cmd_buffer = ''
                while '\n' not in cmd_buffer:
                    cmd_buffer += client_socket
                response = run_command(cmd_buffer)
                client_socket.send(response)

main()