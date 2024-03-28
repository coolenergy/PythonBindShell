"""
You can test this script with ncat -v 127.0.0.1 3002
"""
import os
import platform
import socket
import subprocess
import threading


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 3002))
server_socket.listen(0)
client_socket, address = server_socket.accept()


def read_process_output(proc):
    buffer = bytearray(1)

    try:
        while True:
            # Approach 1: read 1 byte at a time
            # proc.stdout.readinto(buffer)
            # sys.stdout.write(buffer.decode())

            # Approach 2, read up to 1024(max), if 0 then it blocks, perfect
            buffer2 = proc.stdout.read1(1024)
            client_socket.send(buffer2)
    except OSError as err:
        print(err)


console_event = threading.Event()

operating_system = platform.system()
if operating_system == 'Windows':
    command = 'cmd'
# elif operating_system == 'Linux':
else:
    if os.path.isfile('/bin/sh'):
        command = '/bin/sh'
    elif os.path.isfile('/bin/bash'):
        command = '/bin/bash'
    else:
        raise OSError("Shell not found, please fix this before proceeding")

# Notice stderr=STDOUT, we are piping the Standard error descriptor to Output so we can read error and output
# from a single handle
process = subprocess.Popen([command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
process_output_reader = threading.Thread(target=read_process_output, args=[process])
process_output_reader.start()

try:
    while True:
        data = client_socket.recv(1024)
        process.stdin.write(data)
        process.stdin.flush()
except OSError as e:
    print(e)
    print('[+] Closing ...')
    process.stdin.close()
    process.stdout.close()
    exit(1)
